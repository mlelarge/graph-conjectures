#!/usr/bin/env python3
"""
scripts/arxiv_disambig.py — manual-review gate between arxiv_fetch and arxiv_extract.

For each author manifest in cache/arxiv/<slug>/papers.json, emit a side-car file
cache/arxiv/<slug>/disambig.txt listing every paper flagged with
`needs_disambiguation: true` by arxiv_fetch (arXiv author search is fuzzy; the
flag means "last name + first initial match did not find the requested author
in the paper's author list"). The user inspects that file and either:

  (a) does nothing — flagged papers stay in the manifest and will be passed to
      arxiv_extract (potentially wasting `claude -p` calls on the wrong author);
  (b) opens papers.json and removes false positives by hand;
  (c) runs this script with --prune which drops every still-flagged paper from
      the manifest in place.

Usage
-----
    # report only (default)
    python scripts/arxiv_disambig.py

    # one author
    python scripts/arxiv_disambig.py --only "Aboulker"

    # destructive: drop everything still flagged
    python scripts/arxiv_disambig.py --prune

Idempotent: the report is regenerated from the current manifest each run.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
CACHE   = PROJECT / "cache" / "arxiv"

log = logging.getLogger("arxiv_disambig")


def _report_lines(papers: list[dict]) -> list[str]:
    rows = []
    for p in papers:
        if not p.get("needs_disambiguation"):
            continue
        authors_short = "; ".join(p.get("authors", [])[:3])
        rows.append(
            f"{p['arxiv_id']:<20}  {p.get('published','??'):<10}  "
            f"{authors_short:<60.60}  {p.get('title','')[:80]}"
        )
    return rows


def process_one(manifest_path: Path, prune: bool) -> tuple[int, int]:
    """Return (n_flagged_before, n_kept_after)."""
    if not manifest_path.exists():
        log.warning("no manifest at %s — skip", manifest_path)
        return 0, 0
    papers = json.loads(manifest_path.read_text(encoding="utf-8"))
    flagged = [p for p in papers if p.get("needs_disambiguation")]

    report_path = manifest_path.parent / "disambig.txt"
    if flagged:
        header = (
            f"# Disambiguation review for {manifest_path.parent.name}\n"
            f"# {len(flagged)} of {len(papers)} papers flagged.\n"
            "# Delete any false-positive lines, then either re-run with --prune\n"
            "# or edit papers.json directly.\n"
            f"# {'ARXIV_ID':<20}  {'PUBLISHED':<10}  {'AUTHORS (first 3)':<60}  TITLE\n"
        )
        report_path.write_text(header + "\n".join(_report_lines(papers)) + "\n",
                               encoding="utf-8")
        log.info("[%s] %d/%d flagged → %s",
                 manifest_path.parent.name, len(flagged), len(papers), report_path.name)
    else:
        if report_path.exists():
            report_path.unlink()
        log.info("[%s] clean (no flags)", manifest_path.parent.name)

    if prune and flagged:
        kept = [p for p in papers if not p.get("needs_disambiguation")]
        manifest_path.write_text(
            json.dumps(kept, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        log.warning("[%s] PRUNED — manifest now has %d papers (was %d)",
                    manifest_path.parent.name, len(kept), len(papers))
        return len(flagged), len(kept)

    return len(flagged), len(papers)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache-root", type=Path, default=CACHE,
                    help="Root of arxiv caches (default: %(default)s)")
    ap.add_argument("--only", default=None, metavar="SLUG_SUBSTR",
                    help="Process only authors whose slug contains SLUG_SUBSTR")
    ap.add_argument("--prune", action="store_true",
                    help="Destructive: drop flagged papers from papers.json in place")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )

    if not args.cache_root.exists():
        log.error("cache root not found: %s — run scripts/arxiv_fetch_all.py first",
                  args.cache_root)
        return 1

    manifests = sorted(args.cache_root.glob("*/papers.json"))
    if args.only:
        needle = args.only.lower()
        manifests = [m for m in manifests if needle in m.parent.name.lower()]
    if not manifests:
        log.error("no manifests matched (cache_root=%s, only=%r)",
                  args.cache_root, args.only)
        return 1

    n_flag_total = n_keep_total = 0
    for m in manifests:
        f, k = process_one(m, prune=args.prune)
        n_flag_total += f
        n_keep_total += k

    log.info("Done.  authors=%d  flagged_total=%d  kept_total=%d",
             len(manifests), n_flag_total, n_keep_total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
