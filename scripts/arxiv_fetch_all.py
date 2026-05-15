#!/usr/bin/env python3
"""
scripts/arxiv_fetch_all.py — drive scraper/arxiv_fetch.py over the curated
author list at data/arxiv_authors.json.

Sequential by design: arxiv_fetch.py already sleeps 16 s between API calls and
5 s between content downloads (arXiv's robots.txt convention). Running authors
in parallel would not save wall-clock time and might trip rate-limits.

Usage
-----
    # full run
    python scripts/arxiv_fetch_all.py

    # smoke test (no network, just print what would be fetched)
    python scripts/arxiv_fetch_all.py --dry-run --limit 3

    # only one author from the file (substring match on display name)
    python scripts/arxiv_fetch_all.py --only "Aboulker"

    # force re-download even if cached
    python scripts/arxiv_fetch_all.py --refresh

Outputs (per author): cache/arxiv/<slug>/papers.json + <safe_id>.html / .pdf
Idempotent — every call to arxiv_fetch.main is safe to resume.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))

from scraper import arxiv_fetch  # noqa: E402

log = logging.getLogger("arxiv_fetch_all")


def load_authors(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"Author list not found: {path}\n"
            "Create it as a JSON list of objects: "
            '[{"name": "...", "since": 2016, "notes": ""}, ...]'
        )
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a JSON array of author objects")
    cleaned: list[dict] = []
    for i, entry in enumerate(data):
        if not isinstance(entry, dict) or "name" not in entry or "since" not in entry:
            raise ValueError(
                f"{path}[{i}]: each entry must be a dict with 'name' and 'since' keys"
            )
        cleaned.append({
            "name":  entry["name"].strip(),
            "since": int(entry["since"]),
            "notes": entry.get("notes", "") or "",
        })
    return cleaned


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--authors-file", default=PROJECT / "data" / "arxiv_authors.json",
                    type=Path, help="Path to curated author list (default: %(default)s)")
    ap.add_argument("--only", default=None, metavar="SUBSTR",
                    help="Process only authors whose display name contains SUBSTR (case-insensitive)")
    ap.add_argument("--limit", default=None, type=int, metavar="N",
                    help="Per-author cap on papers fetched (passes through to arxiv_fetch)")
    ap.add_argument("--no-pdf-fallback", action="store_true",
                    help="Skip PDF download when HTML is unavailable")
    ap.add_argument("--refresh", action="store_true",
                    help="Re-query API and re-download cached content")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print the paper list for each author; do not download content")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )

    authors = load_authors(args.authors_file)
    if args.only:
        needle = args.only.lower()
        authors = [a for a in authors if needle in a["name"].lower()]
        if not authors:
            log.error("--only=%r matched zero authors in %s", args.only, args.authors_file)
            return 1

    log.info("Loaded %d author(s) from %s", len(authors), args.authors_file)

    failed: list[tuple[str, str]] = []
    for i, a in enumerate(authors, 1):
        log.info("─" * 70)
        log.info("[%d/%d] %s (since %d)", i, len(authors), a["name"], a["since"])
        argv_a = [
            "--author", a["name"],
            "--since",  str(a["since"]),
        ]
        if args.limit:           argv_a += ["--limit", str(args.limit)]
        if args.no_pdf_fallback: argv_a += ["--no-pdf-fallback"]
        if args.refresh:         argv_a += ["--refresh"]
        if args.dry_run:         argv_a += ["--dry-run"]
        if args.verbose:         argv_a += ["--verbose"]

        try:
            rc = arxiv_fetch.main(argv_a)
        except Exception as exc:  # noqa: BLE001
            log.exception("[%s] crashed: %s", a["name"], exc)
            failed.append((a["name"], str(exc)))
            continue
        if rc != 0:
            log.warning("[%s] arxiv_fetch returned non-zero (%d)", a["name"], rc)
            failed.append((a["name"], f"rc={rc}"))

    log.info("─" * 70)
    log.info("Done.  authors=%d  failed=%d", len(authors), len(failed))
    for name, reason in failed:
        log.warning("  failed: %s  (%s)", name, reason)
    return 0 if not failed else 2


if __name__ == "__main__":
    sys.exit(main())
