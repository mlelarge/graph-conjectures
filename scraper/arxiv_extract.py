#!/usr/bin/env python3
"""
scraper/arxiv_extract.py  —  Phase 2 of the arxiv_author_conjectures pipeline.

For each paper in cache/arxiv/<author_slug>/papers.json, preprocesses the cached
HTML (or PDF fallback) into a compact structured representation, then calls
`claude -p` via scripts/timeout_claude.py to extract conjectures.

Usage
-----
    # Process all papers for an author:
    python scraper/arxiv_extract.py --author "Jean-Pierre Serre" --since 2018

    # Process a single paper (smoke-test):
    python scraper/arxiv_extract.py --author "Jean-Pierre Serre" --since 2018 \\
        --paper 2407.19270

    # Reprocess papers whose JSON is already present:
    python scraper/arxiv_extract.py --author "Jean-Pierre Serre" --since 2018 \\
        --refresh

Outputs
-------
    data/arxiv/<slug>/<safe_id>.json   per-paper list of extracted conjecture records
    data/arxiv/<slug>/conjectures.json flat aggregate (written by arxiv_aggregate.py)

Each record includes provenance fields added by this script (not by Claude):
    arxiv_id       arXiv identifier of the source paper
    paper_title    title of the source paper
    paper_authors  author list of the source paper
    published      ISO date of first submission
    abs_url        https://arxiv.org/abs/<id>
    source         "html" or "pdf"

Dependencies
------------
    pip install beautifulsoup4 lxml pdfminer.six
"""

import argparse
import json
import logging
import re
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup, NavigableString, Tag

logger = logging.getLogger(__name__)

# ── constants ──────────────────────────────────────────────────────────────────

SYSTEM_PROMPT_PATH = Path(__file__).parent / "arxiv_system_prompt.md"
TIMEOUT_SCRIPT     = Path(__file__).parent.parent / "scripts" / "timeout_claude.py"
PER_PAPER_TIMEOUT  = int(__import__("os").environ.get("PER_PAPER_TIMEOUT", 600))

# LaTeXML environment types we care about
CONJECTURE_TYPES = {
    # Full names
    "conjecture", "question", "problem", "openquestion", "openproblem",
    # Short-form aliases used by some LaTeXML versions / journal styles
    "conj", "ques", "prob", "quest",
}
# All theorem-like types (we extract ALL for context, then filter)
THEOREM_TYPES = CONJECTURE_TYPES | {
    "theorem", "lemma", "corollary", "proposition", "claim",
    "definition", "remark", "example", "observation",
}

# How many characters of surrounding prose to include as context
CONTEXT_CHARS = 600


# ── HTML preprocessing ─────────────────────────────────────────────────────────

def _latex(math_el: Tag) -> str:
    """Extract the LaTeX source from a <math> element."""
    ann = math_el.find("annotation", {"encoding": "application/x-tex"})
    if ann:
        return ann.get_text()
    return math_el.get("alttext", "?")


def _node_to_text(node) -> str:
    """
    Recursively convert a BS4 node to plain text with LaTeX math inline.

    <math display="inline"> → $...$
    <math display="block">  → $$...$$
    All other tags: recurse into children.
    Nodes inside <annotation> / <semantics> subtrees are skipped (already
    captured via the <math> handler above).
    """
    if isinstance(node, NavigableString):
        parent = node.parent
        if parent and parent.name in ("annotation", "annotation-xml",
                                      "semantics", "math"):
            return ""
        return str(node)
    if not isinstance(node, Tag):
        return ""
    if node.name == "math":
        latex = _latex(node)
        display = node.get("display", "inline")
        return f"$${latex}$$" if display == "block" else f"${latex}$"
    if node.name in ("annotation", "annotation-xml", "semantics"):
        return ""
    return "".join(_node_to_text(c) for c in node.children)


def _clean(text: str) -> str:
    """Collapse whitespace, strip excess blank lines."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _el_text(el: Tag) -> str:
    return _clean(_node_to_text(el))


def _surrounding_context(div: Tag, n_chars: int = CONTEXT_CHARS) -> tuple[str, str]:
    """
    Return up to n_chars of prose immediately before and after a theorem div,
    walking siblings in the same parent.
    """
    def _collect(siblings, reverse=False):
        parts = []
        for sib in siblings:
            if isinstance(sib, Tag) and "ltx_theorem" in (sib.get("class") or []):
                break   # stop at the next theorem environment
            t = _clean(_node_to_text(sib))
            if t:
                parts.append(t)
            if sum(len(p) for p in parts) >= n_chars:
                break
        if reverse:
            parts.reverse()
        return " ".join(parts)[:n_chars]

    before_sibs = list(div.previous_siblings)
    after_sibs  = list(div.next_siblings)
    return _collect(before_sibs, reverse=True), _collect(after_sibs)


def _extract_theorem_environments(soup: BeautifulSoup) -> list[dict]:
    """
    Find all ltx_theorem_* divs and return structured dicts.
    Only environments of interest (conjecture, question, …) are returned
    in full; others are included in compact form so Claude has context
    about the numbering scheme.
    """
    envs = []
    for div in soup.find_all("div", class_=True):
        classes = div.get("class", [])
        env_type = None
        for cls in classes:
            if cls.startswith("ltx_theorem_"):
                env_type = cls[len("ltx_theorem_"):]
                break
        if env_type is None:
            continue

        # Label (e.g. "Conjecture 1.5") and optional attribution
        title_h = div.find(class_="ltx_tag_theorem")
        label = _clean(title_h.get_text()) if title_h else ""

        # Attribution: look for parenthesised text after the label in the h6
        h6 = div.find(["h6"])
        attribution_raw = ""
        if h6:
            full_header = _clean(h6.get_text())
            # e.g. "Conjecture 1 (Machin and Lebrun [6])."
            m = re.search(r"\(([^)]+)\)", full_header)
            if m:
                attribution_raw = m.group(1).strip()

        # Statement text: all paragraphs inside the theorem div
        stmt_parts = []
        for p in div.find_all("p"):
            stmt_parts.append(_el_text(p))
        statement = " ".join(stmt_parts)

        ctx_before, ctx_after = _surrounding_context(div)

        of_interest = env_type in CONJECTURE_TYPES

        envs.append({
            "env_type":        env_type,
            "label":           label,
            "attribution_raw": attribution_raw,
            "statement":       statement,
            "context_before":  ctx_before if of_interest else "",
            "context_after":   ctx_after  if of_interest else "",
            "of_interest":     of_interest,
        })

    return envs


def _extract_section_text(soup: BeautifulSoup, section_id: str,
                           max_chars: int = 4000) -> str:
    """Extract plain text from a named section (e.g. 'S1' for Introduction)."""
    sec = soup.find(id=section_id)
    if sec is None:
        return ""
    return _clean(_node_to_text(sec))[:max_chars]


def _extract_bibliography(soup: BeautifulSoup) -> str:
    """
    Extract bibliography entries as plain text.
    Useful for resolving attribution years.
    """
    bib = soup.find(id="bib")
    if bib is None:
        bib = soup.find(class_="ltx_bibliography")
    if bib is None:
        return ""
    lines = []
    for item in bib.find_all("li", class_="ltx_bibitem"):
        lines.append(_clean(item.get_text()))
    return "\n".join(lines[:80])   # cap at 80 references


def preprocess_html(html_path: Path, paper: dict) -> str:
    """
    Parse a LaTeXML HTML file and produce a compact structured text
    representation for the Claude prompt.
    """
    soup = BeautifulSoup(html_path.read_bytes(), "lxml")

    # ── paper metadata ─────────────────────────────────────────────────────────
    title_el = soup.find(class_="ltx_title_document")
    title = _clean(title_el.get_text()) if title_el else paper.get("title", "")

    authors = [_clean(a.get_text())
               for a in soup.find_all("span", class_="ltx_personname")]

    abstract_el = soup.find(id="abstract") or soup.find(class_="ltx_abstract")
    abstract = _clean(_node_to_text(abstract_el))[:1200] if abstract_el else \
               paper.get("abstract", "")[:1200]

    # ── theorem environments ───────────────────────────────────────────────────
    envs = _extract_theorem_environments(soup)

    # ── introduction ──────────────────────────────────────────────────────────
    intro = _extract_section_text(soup, "S1", max_chars=4000)

    # ── bibliography ──────────────────────────────────────────────────────────
    bib = _extract_bibliography(soup)

    # ── assemble text ──────────────────────────────────────────────────────────
    lines = [
        f"ARXIV_ID: {paper['arxiv_id']}",
        f"TITLE: {title}",
        f"AUTHORS: {', '.join(authors) or ', '.join(paper.get('authors', []))}",
        f"DATE: {paper.get('published', '')}",
        "",
        "=== ABSTRACT ===",
        abstract,
        "",
        "=== THEOREM ENVIRONMENTS ===",
        "(All labelled theorem-like blocks; those of interest are shown in full.)",
        "",
    ]

    for env in envs:
        if env["of_interest"]:
            lines += [
                f"[{env['env_type'].upper()}]  {env['label']}"
                + (f"  (attributed to: {env['attribution_raw']})"
                   if env["attribution_raw"] else ""),
                f"STATEMENT: {env['statement']}",
                f"CONTEXT_BEFORE: {env['context_before']}",
                f"CONTEXT_AFTER:  {env['context_after']}",
                "",
            ]
        else:
            # Compact: just label so Claude knows the numbering context
            lines.append(
                f"[{env['env_type']}]  {env['label']}"
                + (f"  (attrib: {env['attribution_raw']})"
                   if env["attribution_raw"] else "")
            )

    lines += [
        "",
        "=== INTRODUCTION (first 4000 chars) ===",
        intro,
        "",
        "=== BIBLIOGRAPHY ===",
        bib,
    ]

    return "\n".join(lines)


def preprocess_pdf(pdf_path: Path, paper: dict) -> str:
    """
    Extract plain text from a PDF using pdfminer.six.
    Math will be garbled; Claude is told to flag confidence=low.
    """
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(str(pdf_path))
    except Exception as exc:
        logger.warning("pdfminer failed for %s: %s", pdf_path.name, exc)
        text = ""

    header = textwrap.dedent(f"""\
        ARXIV_ID: {paper['arxiv_id']}
        TITLE: {paper.get('title', '')}
        AUTHORS: {', '.join(paper.get('authors', []))}
        DATE: {paper.get('published', '')}
        SOURCE: PDF (math notation may be garbled — set confidence=low for any
                extracted statement where the LaTeX cannot be read cleanly)

        === FULL TEXT (PDF extraction) ===
    """)
    return header + text[:20000]


# ── Claude invocation ──────────────────────────────────────────────────────────

def _build_user_prompt(content: str) -> str:
    return (
        "Extract all conjectures, open problems, and open questions from the "
        "following paper content and return them as a JSON array following the "
        "schema in your instructions.\n\n"
        + content
    )


def run_claude(user_prompt: str, system_prompt: str,
               timeout: int = PER_PAPER_TIMEOUT) -> list[dict]:
    """
    Call `claude -p` via timeout_claude.py.  Returns the parsed JSON list.
    Raises RuntimeError on failure.
    """
    cmd = [
        sys.executable, str(TIMEOUT_SCRIPT),
        str(timeout),                          # <-- timeout seconds (was missing)
        "claude", "-p", user_prompt,
        "--system-prompt", system_prompt,
        "--output-format", "text",
        "--model", "claude-sonnet-4-6",
    ]
    logger.debug("Running claude (timeout=%ds) …", timeout)
    env = __import__("os").environ.copy()

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout + 30, env=env
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("claude timed out")

    if result.returncode != 0:
        raise RuntimeError(
            f"claude exited {result.returncode}: {result.stderr[:300]}"
        )

    raw = result.stdout.strip()

    # Strip accidental markdown fences
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"JSON parse error: {exc}\nraw output:\n{raw[:500]}")

    if not isinstance(data, list):
        raise RuntimeError(f"Expected a JSON array, got {type(data).__name__}")

    return data


# ── per-paper orchestration ────────────────────────────────────────────────────

def extract_paper(
    paper:         dict,
    cache_dir:     Path,
    data_dir:      Path,
    system_prompt: str,
    refresh:       bool = False,
    dry_run:       bool = False,
) -> Optional[list[dict]]:
    """
    Extract conjectures from one paper.  Returns the list of records, or None
    if the paper was skipped (already done, or no content cached).
    """
    safe_id  = paper["safe_id"]
    out_path = data_dir / f"{safe_id}.json"

    if out_path.exists() and not refresh:
        logger.info("  skip (already extracted): %s", safe_id)
        return None

    html_path = cache_dir / f"{safe_id}.html"
    pdf_path  = cache_dir / f"{safe_id}.pdf"

    if html_path.exists():
        logger.info("  preprocessing HTML: %s", html_path.name)
        content = preprocess_html(html_path, paper)
        source  = "html"
    elif pdf_path.exists():
        logger.info("  preprocessing PDF:  %s", pdf_path.name)
        content = preprocess_pdf(pdf_path, paper)
        source  = "pdf"
    else:
        logger.warning("  no content cached for %s — skipping", safe_id)
        return None

    if dry_run:
        logger.info("  [dry-run] would call claude for %s (%s, %d chars)",
                    safe_id, source, len(content))
        return []

    user_prompt = _build_user_prompt(content)

    try:
        records = run_claude(user_prompt, system_prompt)
    except RuntimeError as exc:
        logger.error("  claude failed for %s: %s", safe_id, exc)
        return None

    # Annotate every record with paper provenance.
    # These fields are added here (not by Claude) so the aggregator can always
    # recover which paper each conjecture came from.
    for rec in records:
        rec["arxiv_id"]      = paper["arxiv_id"]
        rec["paper_title"]   = paper.get("title", "")
        rec["paper_authors"] = paper.get("authors", [])
        rec["published"]     = paper.get("published", "")
        rec["abs_url"]       = paper.get("abs_url", "")
        rec["source"]        = source

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(records, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    logger.info("  wrote %d record(s) → %s", len(records), out_path)
    return records


# ── manifest helpers ───────────────────────────────────────────────────────────

def load_manifest(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"Manifest not found: {path}\n"
            "Run arxiv_fetch.py first."
        )
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _slug_from_name(full_name: str) -> str:
    """Quick slug: 'Jean-Pierre Serre' → 'serre_jean-pierre'."""
    import unicodedata
    def asc(s):
        return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()
    parts = full_name.strip().split()
    last  = asc(parts[-1]).replace(" ", "-")
    first = "_".join(asc(p) for p in parts[:-1])
    return f"{last}_{first}"


# ── main ───────────────────────────────────────────────────────────────────────

def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Extract conjectures from cached arXiv papers using Claude.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("--author",  required=False, metavar="NAME", default=None,
                    help='Curated-author display name (e.g. "Pierre Aboulker"). '
                         'Optional when --paper is given: extractor will search '
                         'cache/arxiv/*/papers.json to locate the paper.')
    ap.add_argument("--since",   required=False, type=int, metavar="YEAR", default=2000)
    ap.add_argument("--cache",   default=None, metavar="DIR",
                    help="Cache directory (default: cache/arxiv/<slug> or auto-detect)")
    ap.add_argument("--out",     default=None, metavar="DIR",
                    help="Output directory (default: data/arxiv_extracted, flat)")
    ap.add_argument("--paper",   default=None, metavar="ARXIV_ID",
                    help="Process only this paper ID")
    ap.add_argument("--system-prompt", default=None, metavar="FILE",
                    help=f"System prompt file (default: {SYSTEM_PROMPT_PATH})")
    ap.add_argument("--refresh",  action="store_true",
                    help="Re-extract even if output JSON already exists")
    ap.add_argument("--dry-run",  action="store_true",
                    help="Preprocess and print content but do not call Claude")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )

    # ── paths ──────────────────────────────────────────────────────────────────
    # Output directory is FLAT by default so each unique safe_id is extracted at
    # most once across the whole corpus (per the user's "dedup by paper, credit
    # all co-authors at aggregation time" decision).
    data_dir = Path(args.out) if args.out else Path("data/arxiv_extracted")
    data_dir.mkdir(parents=True, exist_ok=True)

    # ── resolve which author's cache to read from ──────────────────────────────
    # Two modes:
    #   1) --author NAME  → use that author's cache directly.
    #   2) --paper ID without --author → scan cache/arxiv/*/papers.json to find
    #      the first manifest containing the paper, use that for HTML/PDF lookup.
    slug = None
    cache_dir: Path | None = None
    if args.author:
        slug = _slug_from_name(args.author)
        cache_dir = Path(args.cache) if args.cache else Path("cache/arxiv") / slug
    elif args.paper:
        target_safe = args.paper.replace("/", "_")
        for manifest_path in sorted(Path("cache/arxiv").glob("*/papers.json")):
            try:
                ms = json.loads(manifest_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            for p in ms:
                if p.get("safe_id") == target_safe or p.get("arxiv_id") == args.paper:
                    slug = manifest_path.parent.name
                    cache_dir = manifest_path.parent
                    break
            if cache_dir is not None:
                break
        if cache_dir is None:
            logger.error("Paper %s not found in any cache/arxiv/*/papers.json", args.paper)
            return 1
    else:
        logger.error("Either --author or --paper must be given.")
        return 1

    # ── system prompt ──────────────────────────────────────────────────────────
    sp_path = Path(args.system_prompt) if args.system_prompt else SYSTEM_PROMPT_PATH
    if not sp_path.exists():
        logger.error("System prompt not found: %s", sp_path)
        return 1
    system_prompt = sp_path.read_text(encoding="utf-8")

    # ── load manifest ──────────────────────────────────────────────────────────
    try:
        papers = load_manifest(cache_dir / "papers.json")
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return 1

    # Filter by since year and optional single-paper flag
    papers = [p for p in papers if int(p.get("published", "0")[:4]) >= args.since]
    if args.paper:
        papers = [p for p in papers if p["arxiv_id"] == args.paper
                  or p["safe_id"] == args.paper.replace("/", "_")]
        if not papers:
            logger.error("Paper %s not found in manifest.", args.paper)
            return 1

    logger.info("Source cache : %s  (slug: %s)", cache_dir, slug)
    logger.info("Output dir   : %s", data_dir)
    logger.info("Papers       : %d to process", len(papers))

    # ── process ────────────────────────────────────────────────────────────────
    n_ok = n_skip = n_fail = 0
    all_records: list[dict] = []

    for i, paper in enumerate(papers, 1):
        logger.info("[%d/%d] %s  %s",
                    i, len(papers), paper["arxiv_id"], paper.get("title", "")[:55])
        result = extract_paper(
            paper, cache_dir, data_dir, system_prompt,
            refresh=args.refresh, dry_run=args.dry_run,
        )
        if result is None:
            n_skip += 1
        elif result is False:
            n_fail += 1
        else:
            n_ok += 1
            all_records.extend(result)

    # ── summary ────────────────────────────────────────────────────────────────
    logger.info(
        "Done.  processed=%d  skipped=%d  failed=%d  records=%d",
        n_ok, n_skip, n_fail, len(all_records),
    )
    if args.dry_run:
        logger.info("(dry-run: no files written, no Claude calls made)")

    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
