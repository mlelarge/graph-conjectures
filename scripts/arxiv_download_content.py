#!/usr/bin/env python3
"""
scripts/arxiv_download_content.py — download HTML (PDF fallback) for every
unique paper across cache/arxiv/*/papers.json.

The OAI-PMH fetcher writes metadata-only manifests with html_cached=False /
pdf_cached=False. This script does the polite content download in a second
phase: 5 seconds between paper downloads, idempotent, dedup by safe_id.

After downloading, each manifest is rewritten with up-to-date cached flags so
arxiv_partition.py can filter on them.

Usage
-----
    # Pilot: download just one author's papers
    python scripts/arxiv_download_content.py --only aboulker

    # Full run
    python scripts/arxiv_download_content.py

    # Don't try PDF when HTML is missing
    python scripts/arxiv_download_content.py --no-pdf-fallback
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))

from scraper import arxiv_fetch  # noqa: E402

log = logging.getLogger("arxiv_download_content")


def load_manifest(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_manifest(path: Path, papers: list[dict]) -> None:
    path.write_text(json.dumps(papers, indent=2, ensure_ascii=False),
                    encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache-root", type=Path, default=PROJECT / "cache" / "arxiv")
    ap.add_argument("--only", default=None, metavar="SLUG_SUBSTR",
                    help="Process only authors whose slug contains SLUG_SUBSTR")
    ap.add_argument("--no-pdf-fallback", action="store_true",
                    help="Skip PDF download when HTML is unavailable")
    ap.add_argument("--refresh", action="store_true",
                    help="Re-download even if files are already cached")
    ap.add_argument("--limit", default=None, type=int, metavar="N",
                    help="Stop after N successful downloads (smoke-test)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )

    if not args.cache_root.exists():
        log.error("cache root not found: %s — run scripts/arxiv_oai_fetch.py first",
                  args.cache_root)
        return 1

    # ── gather unique work items across all manifests ──────────────────────────
    # The output is: ordered list of (slug, paper_dict) — first author wins for
    # cache location. Same paper appearing in multiple manifests is downloaded
    # exactly once.
    seen: dict[str, tuple[str, dict, Path]] = {}
    manifest_paths: list[Path] = []
    for manifest_path in sorted(args.cache_root.glob("*/papers.json")):
        slug = manifest_path.parent.name
        if args.only and args.only.lower() not in slug.lower():
            continue
        manifest_paths.append(manifest_path)
        for p in load_manifest(manifest_path):
            sid = p["safe_id"]
            if sid in seen:
                continue
            seen[sid] = (slug, p, manifest_path.parent)

    log.info("Cache root      : %s", args.cache_root)
    log.info("Manifests       : %d", len(manifest_paths))
    log.info("Unique papers   : %d", len(seen))

    # ── download each unique paper into its first-seen author's cache dir ──────
    n_html = n_pdf = n_none = 0
    n_done = 0
    for i, (sid, (slug, paper, cache_dir)) in enumerate(seen.items(), 1):
        html_path = cache_dir / f"{sid}.html"
        pdf_path  = cache_dir / f"{sid}.pdf"

        if args.refresh:
            html_path.unlink(missing_ok=True)
            pdf_path.unlink(missing_ok=True)

        if html_path.exists():
            n_html += 1
            continue
        if pdf_path.exists():
            n_pdf += 1
            continue

        log.info("[%d/%d] %s  %s", i, len(seen), paper["arxiv_id"],
                 paper.get("title", "")[:55])
        ok = arxiv_fetch._download_html(paper["arxiv_id"], sid, html_path)
        if ok:
            n_html += 1
        elif not args.no_pdf_fallback:
            if arxiv_fetch._download_pdf(paper["arxiv_id"], sid, pdf_path):
                n_pdf += 1
            else:
                n_none += 1
        else:
            n_none += 1

        n_done += 1
        if args.limit and n_done >= args.limit:
            log.info("--limit reached, stopping after %d downloads", args.limit)
            break

    log.info("Downloaded: html=%d  pdf=%d  neither=%d  (of %d unique)",
             n_html, n_pdf, n_none, len(seen))

    # ── rewrite every manifest with up-to-date cached flags ────────────────────
    # A paper may live in cache/arxiv/<other_slug>/ from a different author's
    # manifest; check ALL author dirs when setting flags.
    cache_dirs = [m.parent for m in manifest_paths]

    def file_exists_anywhere(sid: str, suffix: str) -> bool:
        for d in cache_dirs:
            if (d / f"{sid}{suffix}").exists():
                return True
        return False

    for manifest_path in manifest_paths:
        papers = load_manifest(manifest_path)
        for p in papers:
            p["html_cached"] = file_exists_anywhere(p["safe_id"], ".html")
            p["pdf_cached"]  = file_exists_anywhere(p["safe_id"], ".pdf")
        save_manifest(manifest_path, papers)
    log.info("Updated %d manifest(s) with cached flags", len(manifest_paths))

    return 0


if __name__ == "__main__":
    sys.exit(main())
