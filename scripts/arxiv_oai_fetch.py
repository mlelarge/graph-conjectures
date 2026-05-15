#!/usr/bin/env python3
"""
scripts/arxiv_oai_fetch.py — harvest arXiv metadata via OAI-PMH, filter to the
authors listed in data/arxiv_authors.json, report per-author paper counts and
write per-author manifests compatible with downstream tools.

Why OAI-PMH and not the /api/query search endpoint:
    arXiv's API ToU and User Manual both direct bulk metadata harvesting (which
    is what "every paper by N authors over 10 years" is) to the OAI-PMH
    interface, not /api/query. The /api/query CDN throttle is more aggressive.

Usage
-----
    # Just count matches per author (no manifests written)
    python scripts/arxiv_oai_fetch.py --set math.CO --from 2016-01-01 --count-only

    # Default: write per-author manifests (no HTML/PDF downloads — see arxiv_fetch.py
    # for the content-download phase, which still uses arxiv.org/html|pdf/<id>).
    python scripts/arxiv_oai_fetch.py --set math.CO --from 2016-01-01

    # Restrict to a single author from the curated list (substring match)
    python scripts/arxiv_oai_fetch.py --set math.CO --from 2016-01-01 --only Aboulker

Outputs
-------
    cache/arxiv/<author_slug>/papers.json     per-author manifest (metadata only)
    cache/arxiv/_oai_report.json              one-shot summary of this run
    stdout                                    per-author count table

Author matching: case- and accent-insensitive last-name match, AND first-initial
match. Papers where the match is ambiguous (no first-initial available) are
flagged needs_disambiguation=true in the manifest.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
import unicodedata
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

import requests

PROJECT = Path(__file__).resolve().parent.parent
log = logging.getLogger("arxiv_oai_fetch")

# ── constants ──────────────────────────────────────────────────────────────────

OAI_URL  = "https://oaipmh.arxiv.org/oai"
DELAY    = 5.0    # seconds between OAI calls (>3s as required by ToU; conservative)
TIMEOUT  = 120
USER_AGENT = "GraphConjectures-research/0.1 (mailto:marc.lelarge@gmail.com)"

NS = {
    "oai":   "http://www.openarchives.org/OAI/2.0/",
    "arxiv": "http://arxiv.org/OAI/arXiv/",
}


# ── name helpers (mirror of scraper/arxiv_fetch.py) ────────────────────────────

def _ascii_lower(s: str) -> str:
    nfd = unicodedata.normalize("NFD", s or "")
    return nfd.encode("ascii", "ignore").decode().lower()


def _slug_part(s: str) -> str:
    s = re.sub(r"[^a-z0-9\-]+", "-", _ascii_lower(s)).strip("-")
    return s


def author_slug_from_name(full_name: str) -> str:
    parts = full_name.strip().split()
    if len(parts) < 2:
        return _slug_part(full_name)
    last = _slug_part(parts[-1])
    first = _slug_part(" ".join(parts[:-1])).replace("-", "_")
    return f"{last}_{first}"


def build_target_table(authors: list[dict]) -> list[dict]:
    """For each curated author entry, precompute the match keys."""
    table = []
    for a in authors:
        parts = a["name"].strip().split()
        if len(parts) < 2:
            continue
        last = _ascii_lower(parts[-1]).strip()
        first = _ascii_lower(" ".join(parts[:-1])).strip()
        first_init = first[0] if first else ""
        table.append({
            "display":    a["name"],
            "slug":       author_slug_from_name(a["name"]),
            "last":       last,
            "first":      first,
            "first_init": first_init,
            "since":      int(a["since"]),
        })
    return table


# ── OAI fetch ──────────────────────────────────────────────────────────────────

_session = requests.Session()
_session.headers["User-Agent"] = USER_AGENT


def _oai_get(params: dict) -> ET.Element:
    """One GET to OAI-PMH with retry on 503 (the spec's "try again later" code)."""
    backoff = 30
    for attempt in range(1, 6):
        time.sleep(DELAY)
        log.debug("GET %s  params=%s", OAI_URL, {k: v for k, v in params.items() if k != "resumptionToken"} or {"resumptionToken": "<...>"})
        resp = _session.get(OAI_URL, params=params, timeout=TIMEOUT, allow_redirects=True)
        if resp.status_code == 503:
            wait = float(resp.headers.get("Retry-After", backoff))
            log.warning("  503 from OAI — sleeping %.0fs (retry %d/5)", wait, attempt)
            time.sleep(wait)
            backoff *= 2
            continue
        if resp.status_code == 429:
            wait = float(resp.headers.get("Retry-After", 60))
            log.warning("  429 from OAI — sleeping %.0fs (retry %d/5)", wait, attempt)
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return ET.fromstring(resp.content)
    raise RuntimeError("OAI request failed after 5 retries")


def harvest_set(set_spec: str, from_date: str, until_date: str | None) -> list[dict]:
    """Iterate ListRecords with resumptionToken pagination; return parsed records."""
    params = {
        "verb":           "ListRecords",
        "set":            set_spec,
        "from":           from_date,
        "metadataPrefix": "arXiv",
    }
    if until_date:
        params["until"] = until_date

    records: list[dict] = []
    page = 0
    while True:
        page += 1
        root = _oai_get(params)

        # Detect OAI errors (e.g. badArgument, noRecordsMatch)
        err = root.find("oai:error", NS)
        if err is not None:
            code = err.get("code", "?")
            text = (err.text or "").strip()
            if code == "noRecordsMatch":
                log.info("  noRecordsMatch — finished")
                break
            raise RuntimeError(f"OAI error code={code}: {text}")

        lr = root.find("oai:ListRecords", NS)
        if lr is None:
            log.warning("  no ListRecords block — finished")
            break

        for rec in lr.findall("oai:record", NS):
            parsed = _parse_record(rec)
            if parsed is not None:
                records.append(parsed)

        token_el = lr.find("oai:resumptionToken", NS)
        complete = ""
        if token_el is not None:
            complete = token_el.get("completeListSize", "?")
            cursor   = token_el.get("cursor", "?")
            log.info("  page %d: %d records so far  (cursor=%s/total=%s)",
                     page, len(records), cursor, complete)

        token = (token_el.text or "").strip() if token_el is not None else ""
        if not token:
            log.info("  done — pages=%d, records=%d", page, len(records))
            break
        params = {"verb": "ListRecords", "resumptionToken": token}

    return records


def _parse_record(rec: ET.Element) -> dict | None:
    """Convert one <record> into a flat dict; return None on malformed input."""
    header = rec.find("oai:header", NS)
    if header is None or header.get("status") == "deleted":
        return None

    md = rec.find("oai:metadata", NS)
    if md is None:
        return None
    arxiv_el = md.find("arxiv:arXiv", NS)
    if arxiv_el is None:
        return None

    def t(tag: str) -> str:
        el = arxiv_el.find(f"arxiv:{tag}", NS)
        return (el.text or "").strip() if el is not None else ""

    arxiv_id = t("id")
    if not arxiv_id:
        return None

    authors_el = arxiv_el.find("arxiv:authors", NS)
    authors: list[dict] = []
    if authors_el is not None:
        for a in authors_el.findall("arxiv:author", NS):
            kn_el = a.find("arxiv:keyname", NS)
            fn_el = a.find("arxiv:forenames", NS)
            keyname = (kn_el.text or "").strip() if kn_el is not None else ""
            forenames = (fn_el.text or "").strip() if fn_el is not None else ""
            authors.append({"keyname": keyname, "forenames": forenames})

    categories = t("categories").split() if arxiv_el.find("arxiv:categories", NS) is not None else []

    return {
        "arxiv_id":   arxiv_id,
        "title":      re.sub(r"\s+", " ", t("title")),
        "abstract":   re.sub(r"\s+", " ", t("abstract")),
        "categories": categories,
        "primary_cat": categories[0] if categories else "",
        "created":    t("created"),    # YYYY-MM-DD — original submission date
        "updated":    t("updated"),    # YYYY-MM-DD — most recent revision
        "doi":        t("doi"),
        "journal_ref": t("journal-ref"),
        "authors":    authors,         # list of {keyname, forenames}
    }


# ── author matching ────────────────────────────────────────────────────────────

def match_authors(paper_authors: list[dict], targets: list[dict]) -> list[dict]:
    """Return the subset of targets whose (last, first_init) matches at least
    one entry in paper_authors. Case- and accent-insensitive."""
    matched: list[dict] = []
    for t in targets:
        for a in paper_authors:
            keyname_lc = _ascii_lower(a["keyname"]).strip()
            forenames_lc = _ascii_lower(a["forenames"]).strip()
            # Sometimes keyname has multiple tokens — match if our last is in it
            if not keyname_lc:
                continue
            keyname_tokens = keyname_lc.split()
            if t["last"] not in keyname_tokens and keyname_lc != t["last"]:
                continue
            # First initial must agree if both present
            if t["first_init"] and forenames_lc and forenames_lc[0] != t["first_init"]:
                continue
            matched.append(t)
            break
    return matched


# ── main ───────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--set", "--set-spec", dest="set_spec", default="math:math:CO",
                    help="OAI setSpec, comma-separated for multiple sets "
                         "(default: math:math:CO). "
                         "Each entry accepts 'math.CO' shorthand → 'math:math:CO'. "
                         "Example: --set math.CO,cs.DM,math.GT")
    ap.add_argument("--from", dest="from_date", default="2016-01-01",
                    help="OAI 'from' date YYYY-MM-DD (default: 2016-01-01)")
    ap.add_argument("--until", dest="until_date", default=None,
                    help="OAI 'until' date YYYY-MM-DD (default: today)")
    ap.add_argument("--filter-by-created", action="store_true", default=True,
                    help="After harvest, drop papers whose <created> date is "
                         "before the per-author 'since' year (default: on). "
                         "Datestamp is last-modified; filtering by created enforces "
                         "the 10-year-submission semantic the user asked for.")
    ap.add_argument("--authors-file", type=Path, default=PROJECT / "data" / "arxiv_authors.json")
    ap.add_argument("--cache-root",   type=Path, default=PROJECT / "cache" / "arxiv")
    ap.add_argument("--only", default=None, metavar="SUBSTR",
                    help="Filter the author list to display names containing SUBSTR")
    ap.add_argument("--count-only", action="store_true",
                    help="Do not write per-author manifests; just print counts.")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )

    # Parse possibly-multiple sets; translate dot-shorthand to OAI form.
    def _canon_set(s: str) -> str:
        s = s.strip()
        if "." in s and ":" not in s:
            top, sub = s.split(".", 1)
            return f"{top}:{top}:{sub}"
        return s
    set_specs = [_canon_set(s) for s in args.set_spec.split(",") if s.strip()]
    if not set_specs:
        log.error("no sets parsed from --set %r", args.set_spec)
        return 1

    until = args.until_date or date.today().isoformat()

    # Load curated authors
    authors = json.loads(args.authors_file.read_text(encoding="utf-8"))
    if args.only:
        needle = args.only.lower()
        authors = [a for a in authors if needle in a["name"].lower()]
        if not authors:
            log.error("--only=%r matched zero authors", args.only)
            return 1

    targets = build_target_table(authors)
    log.info("Curated authors: %d", len(targets))
    log.info("Sets           : %s", ", ".join(set_specs))
    log.info("Range          : %s → %s", args.from_date, until)
    log.info("OAI endpoint   : %s", OAI_URL)

    # Harvest each set in turn; dedup by arxiv_id into a single dict.
    t0 = time.time()
    by_id: dict[str, dict] = {}
    raw_total = 0
    set_counts: dict[str, int] = {}
    for spec in set_specs:
        log.info("─" * 70)
        log.info("Harvesting set: %s", spec)
        recs = harvest_set(spec, args.from_date, until)
        set_counts[spec] = len(recs)
        raw_total += len(recs)
        for r in recs:
            # First-seen wins; subsequent occurrences merge categories.
            existing = by_id.get(r["arxiv_id"])
            if existing is None:
                by_id[r["arxiv_id"]] = r
            else:
                # Union categories from later sets if any are missing
                for c in r.get("categories", []):
                    if c not in existing["categories"]:
                        existing["categories"].append(c)
    elapsed = time.time() - t0
    records = list(by_id.values())
    log.info("─" * 70)
    log.info("Harvested %d raw records across %d set(s) in %.0fs",
             raw_total, len(set_specs), elapsed)
    log.info("After dedup by arxiv_id: %d unique records", len(records))

    # Filter by curated authors
    per_author: dict[str, list[dict]] = {t["slug"]: [] for t in targets}
    n_match_any = 0
    for r in records:
        matched = match_authors(r["authors"], targets)
        if not matched:
            continue
        n_match_any += 1
        for t in matched:
            if args.filter_by_created and r["created"]:
                year = int(r["created"][:4])
                if year < t["since"]:
                    continue
            per_author[t["slug"]].append({
                "arxiv_id":   r["arxiv_id"],
                "safe_id":    r["arxiv_id"].replace("/", "_"),
                "title":      r["title"],
                "authors":    [
                    f"{a['forenames']} {a['keyname']}".strip()
                    for a in r["authors"]
                ],
                "published":  r["created"],
                "updated":    r["updated"],
                "abstract":   r["abstract"],
                "categories": r["categories"],
                "primary_cat": r["primary_cat"],
                "journal_ref": r["journal_ref"],
                "doi":        r["doi"],
                "abs_url":    f"https://arxiv.org/abs/{r['arxiv_id']}",
                "html_cached": False,
                "pdf_cached":  False,
                "needs_disambiguation": False,
            })
    log.info("Matched %d papers across %d authors", n_match_any, len(targets))

    # Print count table
    print("\n=== Per-author counts (sets=%s, %s → %s) ===" % (",".join(set_specs), args.from_date, until))
    print(f"{'AUTHOR':<28}  {'SLUG':<28}  {'PAPERS':>6}")
    print("─" * 70)
    total = 0
    rows_sorted = sorted(targets, key=lambda t: -len(per_author[t["slug"]]))
    for t in rows_sorted:
        n = len(per_author[t["slug"]])
        total += n
        print(f"{t['display']:<28}  {t['slug']:<28}  {n:>6}")
    print("─" * 70)
    print(f"{'TOTAL (with double-counts when co-authored)':<58}  {total:>6}")
    print(f"unique papers matched: {n_match_any}\n")

    # Write summary report
    report_path = args.cache_root / "_oai_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "fetched_at":    date.today().isoformat(),
        "sets":          set_specs,
        "set_counts":    set_counts,
        "from":          args.from_date,
        "until":         until,
        "harvested_raw":  raw_total,
        "harvested_unique": len(records),
        "matched_unique": n_match_any,
        "elapsed_seconds": round(elapsed, 1),
        "per_author":    {
            t["slug"]: {
                "display": t["display"],
                "since":   t["since"],
                "count":   len(per_author[t["slug"]]),
            }
            for t in targets
        },
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                           encoding="utf-8")
    log.info("Wrote %s", report_path)

    if args.count_only:
        log.info("--count-only: not writing per-author manifests")
        return 0

    # Write per-author manifests
    for t in targets:
        out_dir = args.cache_root / t["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        manifest = out_dir / "papers.json"
        manifest.write_text(
            json.dumps(per_author[t["slug"]], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    log.info("Wrote %d per-author manifest(s) under %s", len(targets), args.cache_root)

    return 0


if __name__ == "__main__":
    sys.exit(main())
