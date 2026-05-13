#!/usr/bin/env python3
"""
scraper/arxiv_fetch.py  —  Phase 1 of the arxiv_author_conjectures pipeline.

Queries the arXiv API for all papers by a given author published since a given
year, downloads the HTML full-text (with PDF fallback for older papers), and
writes a papers.json manifest to cache/arxiv/<author_slug>/.

Usage
-----
    python scraper/arxiv_fetch.py --author "Jean-Pierre Mere" --since 2010 --limit 5


Outputs
-------
    cache/arxiv/<slug>/papers.json          manifest of all matched papers
    cache/arxiv/<slug>/<safe_id>.html       HTML full-text (when available)
    cache/arxiv/<slug>/<safe_id>.pdf        PDF fallback (when HTML unavailable)

The run is fully idempotent: files already on disk are not re-downloaded unless
--refresh is given.  The manifest is merged on each run so partial runs are safe
to resume.

Notes on author search
----------------------
arXiv author search is imprecise: the same person may appear under multiple
name variants, and a common name may match several distinct researchers.  This
script generates several query variants (LastName_Fi, "lastname firstname", …),
runs them all, deduplicates by arXiv ID, and writes every result to the
manifest with a flag `needs_disambiguation = true` when the author list does NOT
contain a name that matches the requested author — these rows can be pruned
manually or by a later disambiguation pass.
"""

import argparse
import json
import logging
import re
import sys
import time
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

import requests


# ── constants ──────────────────────────────────────────────────────────────────

ARXIV_API  = "https://export.arxiv.org/api/query"
ARXIV_HTML = "https://arxiv.org/html/{id}"
ARXIV_PDF  = "https://arxiv.org/pdf/{id}"

API_DELAY        = 16.0  # seconds between arXiv API calls (~3–4 req/min, well within limits)
DOWNLOAD_DELAY   = 5.0   # seconds between HTML/PDF downloads
RATE_LIMIT_SLEEP = 120.0 # seconds to wait after a 429 if it still occurs
PAGE_SIZE        = 100   # results per API page
MAX_PAGES        = 30    # hard safety cap = 3 000 papers per query variant

# Atom namespace map used throughout
NS = {
    "atom":  "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
    "os":    "http://a9.com/-/spec/opensearch/1.1/",
}

USER_AGENT = "GraphConjectures-research/0.1 (mailto:marc.lelarge@gmail.com)"

logger = logging.getLogger(__name__)


# ── name helpers ───────────────────────────────────────────────────────────────

def _to_ascii_lower(s: str) -> str:
    """'Jean-Pierre Élouard' → 'jean-pierre elouard' (NFD, strip combining marks)."""
    nfd = unicodedata.normalize("NFD", s)
    return nfd.encode("ascii", "ignore").decode().lower()


def _slug_part(s: str) -> str:
    """Turn one name component into a URL-safe slug token: 'Jean-Pierre' → 'jean-pierre'."""
    ascii_lower = _to_ascii_lower(s)
    # Replace any run of characters that are not alphanumeric or hyphen with a hyphen,
    # then strip leading/trailing hyphens.
    slug = re.sub(r"[^a-z0-9\-]+", "-", ascii_lower).strip("-")
    return slug


def parse_author_name(full_name: str) -> dict:
    """
    Parse 'FirstName [Middle…] LastName' into useful components.

    The last whitespace-delimited token is taken as the last name; everything
    before it is the first (+middle) name(s).  Hyphenated names like
    'Jean-Pierre' are treated as a single token.

    Returns a dict:
        display          original string, stripped
        first            first token(s) before the last name
        last             last token
        slug             'mere_jean_pierre'  (used as cache directory name)
        query_variants   list of arXiv au: strings to try, in priority order
    """
    parts = full_name.strip().split()
    if len(parts) < 2:
        raise ValueError(
            f"Author name must be at least 'FirstName LastName', got: {full_name!r}"
        )

    last  = parts[-1]
    first = " ".join(parts[:-1])   # everything before the last token

    al = _slug_part(last)          # ascii last name slug,  e.g. 'mere'
    af = _slug_part(first)[0]      # first initial,          e.g. 'j'

    # Single query: au:"Lastname, Firstname" — this matches the format arXiv
    # uses internally to index author names, and is precise enough for most cases.
    af_full = _slug_part(first)
    query_variants = [f'"{al}, {af_full}"']

    # author_slug is used for the cache directory
    author_slug = f"{al}_{_slug_part(first).replace('-', '_')}"

    return {
        "display":       full_name.strip(),
        "first":         first,
        "last":          last,
        "slug":          author_slug,
        "arxiv_last":    al,
        "arxiv_fi":      af,
        "query_variants": query_variants,
    }


def _name_matches_author(paper_authors: list[str], author: dict) -> bool:
    """
    Return True if at least one entry in paper_authors looks like it could be
    the requested author (last name matches, first initial matches).
    Case- and accent-insensitive.
    """
    al = author["arxiv_last"]   # ascii-lower last name slug
    af = author["arxiv_fi"]     # first initial

    for name in paper_authors:
        name_l = _to_ascii_lower(name)
        # The name is typically stored as "Mere, Jean-Pierre" or "Jean-Pierre Mere"
        # Check that the last name appears and that the string contains the first initial.
        if al in name_l and af in name_l:
            return True
    return False


# ── arXiv API ──────────────────────────────────────────────────────────────────

_session = requests.Session()
_session.headers["User-Agent"] = USER_AGENT


def _http_get(url: str, _retries: int = 5, **kwargs) -> requests.Response:
    """
    GET with automatic retry on transient errors and 429 rate-limit responses.

    On 429 the arXiv API sets a Retry-After header (seconds).  We honour it,
    falling back to RATE_LIMIT_SLEEP when the header is absent.  Other 5xx
    errors use exponential back-off.  Non-retryable errors (4xx except 429)
    are raised immediately.
    """
    delay = 4.0   # initial back-off for 5xx
    for attempt in range(1, _retries + 1):
        try:
            resp = _session.get(url, timeout=60, **kwargs)
        except requests.RequestException as exc:
            if attempt == _retries:
                raise
            wait = delay * (2 ** (attempt - 1))
            logger.warning("  request error (%s) — retry %d/%d in %.0fs",
                           exc, attempt, _retries, wait)
            time.sleep(wait)
            continue

        if resp.status_code == 429:
            retry_after = float(resp.headers.get("Retry-After", RATE_LIMIT_SLEEP))
            if attempt == _retries:
                resp.raise_for_status()
            logger.warning(
                "  429 rate-limit — sleeping %.0fs before retry %d/%d",
                retry_after, attempt, _retries,
            )
            time.sleep(retry_after)
            continue

        if resp.status_code >= 500:
            if attempt == _retries:
                resp.raise_for_status()
            wait = delay * (2 ** (attempt - 1))
            logger.warning("  HTTP %d — retry %d/%d in %.0fs",
                           resp.status_code, attempt, _retries, wait)
            time.sleep(wait)
            continue

        resp.raise_for_status()   # raises immediately for other 4xx
        return resp

    # unreachable, but keeps type-checkers happy
    raise RuntimeError("_http_get exhausted retries")


def _api_page(au_query: str, start: int) -> ET.Element:
    """Fetch one page from the arXiv API.  Respects CRAWL_DELAY before the call."""
    time.sleep(API_DELAY)
    params = {
        "search_query": f"au:{au_query}",
        "start":        start,
        "max_results":  PAGE_SIZE,
        "sortBy":       "submittedDate",
        "sortOrder":    "descending",
    }
    logger.debug("  GET %s  start=%d", ARXIV_API, start)
    resp = _http_get(ARXIV_API, params=params)
    return ET.fromstring(resp.text)


def _total_results(root: ET.Element) -> int:
    el = root.find("os:totalResults", NS)
    return int(el.text) if el is not None and el.text else 0


def _parse_entry(entry: ET.Element) -> dict:
    """Convert one Atom <entry> element to a plain dict."""

    def txt(tag: str, ns: str = "atom") -> str:
        el = entry.find(f"{ns}:{tag}", NS)
        return (el.text or "").strip() if el is not None else ""

    # arXiv canonical ID: strip URL prefix and version suffix
    raw_id   = txt("id")                               # e.g. https://arxiv.org/abs/2401.12345v2
    arxiv_id = re.sub(r"v\d+$", "", raw_id.split("/abs/")[-1])

    published = txt("published")[:10]   # YYYY-MM-DD
    updated   = txt("updated")[:10]

    authors = [
        (a.findtext("atom:name", namespaces=NS) or "").strip()
        for a in entry.findall("atom:author", NS)
    ]

    categories = [c.get("term", "") for c in entry.findall("atom:category", NS)]

    primary_el  = entry.find("arxiv:primary_category", NS)
    primary_cat = primary_el.get("term", "") if primary_el is not None else ""

    # Journal reference and DOI (may be absent)
    journal_ref = txt("journal_ref", "arxiv")
    doi         = txt("doi",         "arxiv")

    title    = re.sub(r"\s+", " ", txt("title"))
    abstract = re.sub(r"\s+", " ", txt("summary"))

    # arXiv ID safe for use in filenames (old-style IDs contain "/")
    safe_id = arxiv_id.replace("/", "_")

    return {
        "arxiv_id":    arxiv_id,
        "safe_id":     safe_id,
        "title":       title,
        "authors":     authors,
        "published":   published,
        "updated":     updated,
        "abstract":    abstract,
        "categories":  categories,
        "primary_cat": primary_cat,
        "journal_ref": journal_ref,
        "doi":         doi,
        "abs_url":     f"https://arxiv.org/abs/{arxiv_id}",
        "html_cached": False,
        "pdf_cached":  False,
        "needs_disambiguation": False,  # set below if author match is uncertain
    }


def fetch_paper_list(
    author: dict,
    since_year: int,
    limit: Optional[int] = None,
) -> list[dict]:
    """
    Query the arXiv API for all papers by `author` published >= `since_year`.

    Runs each query variant in sequence, deduplicates by arxiv_id, and returns
    a list sorted by published date descending.  Papers whose author list does
    not clearly match the requested author are flagged with
    needs_disambiguation=True rather than dropped, so the caller can inspect them.
    """
    seen:    set[str]   = set()
    results: list[dict] = []

    for variant in author["query_variants"]:
        logger.info("arXiv query: au:%s", variant)
        page_count = 0

        for start in range(0, MAX_PAGES * PAGE_SIZE, PAGE_SIZE):
            root    = _api_page(variant, start)
            total   = _total_results(root)
            entries = root.findall("atom:entry", NS)

            if not entries:
                logger.debug("  no entries at start=%d (total=%d) — done", start, total)
                break

            stop_early = False
            for entry in entries:
                paper = _parse_entry(entry)
                year  = int(paper["published"][:4])

                # Results are sorted newest-first; once we fall below since_year
                # there's nothing more to collect from this variant.
                if year < since_year:
                    logger.debug(
                        "  reached %s (%s) — before %d, stopping pagination",
                        paper["arxiv_id"], paper["published"], since_year,
                    )
                    stop_early = True
                    break

                if paper["arxiv_id"] in seen:
                    continue   # duplicate across variants

                # Flag papers where the author list doesn't clearly match
                if not _name_matches_author(paper["authors"], author):
                    paper["needs_disambiguation"] = True
                    logger.debug(
                        "  ? disambiguation needed: %s  authors=%s",
                        paper["arxiv_id"], paper["authors"][:2],
                    )

                seen.add(paper["arxiv_id"])
                results.append(paper)
                logger.debug("  + %s  %s", paper["arxiv_id"], paper["title"][:60])

                if limit and len(results) >= limit:
                    stop_early = True
                    break

            page_count += 1
            if stop_early or start + PAGE_SIZE >= total:
                break

        logger.info("  → %d unique papers collected so far", len(results))
        if limit and len(results) >= limit:
            break

    # Sort by published date descending (stable merge across variants)
    results.sort(key=lambda p: p["published"], reverse=True)
    if limit:
        results = results[:limit]

    n_ambiguous = sum(1 for p in results if p["needs_disambiguation"])
    logger.info(
        "Collected %d papers (%d flagged for disambiguation)",
        len(results), n_ambiguous,
    )
    return results


# ── content download ───────────────────────────────────────────────────────────

def _download_html(arxiv_id: str, safe_id: str, dest: Path) -> bool:
    """
    Try to fetch arxiv.org/html/<id> (the LaTeXML-rendered full-text).

    Available for most papers submitted with LaTeX since ~2022.  When
    unavailable, arXiv redirects to the abstract page — we detect this by
    checking that the final URL still contains '/html/'.

    Returns True on success.
    """
    if dest.exists():
        logger.debug("  HTML cached: %s", dest.name)
        return True

    url = ARXIV_HTML.format(id=arxiv_id)
    time.sleep(DOWNLOAD_DELAY)
    try:
        resp = _session.get(url, timeout=90, allow_redirects=True)
        if resp.status_code == 200 and "/html/" in resp.url:
            dest.write_bytes(resp.content)
            logger.info("  HTML ✓  %s  (%d kB)", arxiv_id, len(resp.content) // 1024)
            return True
        logger.debug(
            "  HTML unavailable for %s (status=%d, final url=%s)",
            arxiv_id, resp.status_code, resp.url,
        )
        return False
    except requests.RequestException as exc:
        logger.warning("  HTML fetch error for %s: %s", arxiv_id, exc)
        return False


def _download_pdf(arxiv_id: str, safe_id: str, dest: Path) -> bool:
    """
    Download the PDF from arxiv.org/pdf/<id>.
    Returns True on success.
    """
    if dest.exists():
        logger.debug("  PDF cached: %s", dest.name)
        return True

    url = ARXIV_PDF.format(id=arxiv_id)
    time.sleep(DOWNLOAD_DELAY)
    try:
        resp = _http_get(url)
        dest.write_bytes(resp.content)
        logger.info("  PDF  ✓  %s  (%d kB)", arxiv_id, len(resp.content) // 1024)
        return True
    except requests.RequestException as exc:
        logger.warning("  PDF fetch error for %s: %s", arxiv_id, exc)
        return False


def download_papers(
    papers:      list[dict],
    cache_dir:   Path,
    pdf_fallback: bool = True,
    refresh:     bool  = False,
) -> list[dict]:
    """
    For each paper attempt HTML download, then optionally PDF fallback.
    Updates html_cached / pdf_cached flags in-place.
    Papers flagged needs_disambiguation=True are still downloaded; the caller
    decides whether to keep them.
    """
    total = len(papers)
    for i, paper in enumerate(papers, 1):
        aid     = paper["arxiv_id"]
        safe_id = paper["safe_id"]
        logger.info("[%d/%d] %s  %s", i, total, aid, paper["title"][:55])

        html_path = cache_dir / f"{safe_id}.html"
        pdf_path  = cache_dir / f"{safe_id}.pdf"

        # --refresh: delete existing files so they are re-fetched
        if refresh:
            html_path.unlink(missing_ok=True)
            pdf_path.unlink(missing_ok=True)
            paper["html_cached"] = False
            paper["pdf_cached"]  = False

        # Keep existing state if already cached (idempotent)
        if paper["html_cached"] and html_path.exists():
            pass
        else:
            paper["html_cached"] = _download_html(aid, safe_id, html_path)

        if not paper["html_cached"]:
            if paper["pdf_cached"] and pdf_path.exists():
                pass
            elif pdf_fallback:
                paper["pdf_cached"] = _download_pdf(aid, safe_id, pdf_path)

    return papers


# ── manifest I/O ───────────────────────────────────────────────────────────────

def load_manifest(path: Path) -> dict[str, dict]:
    """Load an existing papers.json as a dict keyed by arxiv_id."""
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        return {p["arxiv_id"]: p for p in json.load(fh)}


def save_manifest(path: Path, papers: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(papers, fh, indent=2, ensure_ascii=False)
    logger.info("Manifest written: %s  (%d papers)", path, len(papers))


def merge_with_existing(
    fetched:  list[dict],
    existing: dict[str, dict],
    refresh:  bool,
) -> list[dict]:
    """
    Merge freshly fetched paper metadata with the existing manifest.
    Existing entries keep their html_cached / pdf_cached state unless --refresh.
    New papers are appended.
    """
    merged = []
    for paper in fetched:
        aid = paper["arxiv_id"]
        if aid in existing and not refresh:
            # Preserve cached state; update metadata fields in case they changed
            old = existing[aid]
            paper["html_cached"] = old.get("html_cached", False)
            paper["pdf_cached"]  = old.get("pdf_cached",  False)
        merged.append(paper)
    return merged


# ── main ───────────────────────────────────────────────────────────────────────

def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Fetch arXiv papers for an author since a given year and cache "
            "their full text for conjecture extraction."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument(
        "--author", required=True, metavar="NAME",
        help='Full name as "FirstName [Middle] LastName", e.g. "Jean-Pierre Mere"',
    )
    ap.add_argument(
        "--since", required=True, type=int, metavar="YEAR",
        help="Include only papers published in YEAR or later",
    )
    ap.add_argument(
        "--out", default=None, metavar="DIR",
        help="Cache directory (default: cache/arxiv/<author_slug>)",
    )
    ap.add_argument(
        "--limit", default=None, type=int, metavar="N",
        help="Stop after N papers — useful for smoke-testing",
    )
    ap.add_argument(
        "--no-pdf-fallback", action="store_true",
        help="Skip PDF download when HTML is unavailable",
    )
    ap.add_argument(
        "--refresh", action="store_true",
        help="Re-download cached files (re-query API + re-fetch content)",
    )
    ap.add_argument(
        "--dry-run", action="store_true",
        help="Query API and print the paper list; do not download any content",
    )
    ap.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable DEBUG logging",
    )
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )

    # ── parse author name ──────────────────────────────────────────────────────
    try:
        author = parse_author_name(args.author)
    except ValueError as exc:
        logger.error("%s", exc)
        return 1

    logger.info("Author   : %s  →  slug '%s'", author["display"], author["slug"])
    logger.info("Since    : %d", args.since)
    logger.info("Variants : %s", "  |  ".join(f"au:{v}" for v in author["query_variants"]))

    # ── paths ──────────────────────────────────────────────────────────────────
    cache_dir     = Path(args.out) if args.out else Path("cache/arxiv") / author["slug"]
    manifest_path = cache_dir / "papers.json"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # ── fetch paper list from API ──────────────────────────────────────────────
    existing = load_manifest(manifest_path)
    papers   = fetch_paper_list(author, args.since, limit=args.limit)
    papers   = merge_with_existing(papers, existing, refresh=args.refresh)

    # ── dry-run: just print and exit ───────────────────────────────────────────
    if args.dry_run:
        n_ambiguous = sum(1 for p in papers if p["needs_disambiguation"])
        print(f"\n{'ArXiv ID':<20}  {'Published':<12}  {'?':1}  Title")
        print("─" * 85)
        for p in papers:
            flag = "?" if p["needs_disambiguation"] else " "
            print(f"{p['arxiv_id']:<20}  {p['published']:<12}  {flag}  {p['title'][:50]}")
        print(f"\nTotal: {len(papers)} papers  ({n_ambiguous} flagged for disambiguation)")
        print(f"Cache dir would be: {cache_dir}")
        return 0

    # ── download HTML / PDF ────────────────────────────────────────────────────
    papers = download_papers(
        papers,
        cache_dir,
        pdf_fallback=not args.no_pdf_fallback,
        refresh=args.refresh,
    )

    # ── save manifest ──────────────────────────────────────────────────────────
    save_manifest(manifest_path, papers)

    # ── final summary ──────────────────────────────────────────────────────────
    n_html  = sum(1 for p in papers if p["html_cached"])
    n_pdf   = sum(1 for p in papers if p["pdf_cached"])
    n_none  = sum(1 for p in papers if not p["html_cached"] and not p["pdf_cached"])
    n_disamb = sum(1 for p in papers if p["needs_disambiguation"])
    logger.info(
        "Done.  total=%d  html=%d  pdf=%d  neither=%d  needs_disambiguation=%d",
        len(papers), n_html, n_pdf, n_none, n_disamb,
    )
    if n_disamb:
        logger.warning(
            "%d papers could not be confirmed as authored by '%s' — "
            "inspect papers.json and remove false positives before running extract.",
            n_disamb, author["display"],
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
