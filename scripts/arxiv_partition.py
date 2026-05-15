#!/usr/bin/env python3
"""
scripts/arxiv_partition.py — flatten all (author_slug, safe_id) extraction
work items across cache/arxiv/*/papers.json into round-robin buckets under
data/arxiv_buckets/bucket-NN.txt.

Each bucket line is `<author_slug>/<safe_id>` — the format expected by
scripts/arxiv_run_worker.sh.

Skips papers whose output JSON at data/arxiv/<author_slug>/<safe_id>.json
already exists (idempotent — partition is cheap to re-run after extraction).

Usage
-----
    python scripts/arxiv_partition.py --workers 8
    python scripts/arxiv_partition.py --workers 1 --only seymour_paul    # stragglers pass
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
CACHE   = PROJECT / "cache" / "arxiv"
DATA    = PROJECT / "data"  / "arxiv_extracted"
BUCKETS = PROJECT / "data"  / "arxiv_buckets"

log = logging.getLogger("arxiv_partition")


def gather_work(cache_root: Path, data_root: Path,
                only: str | None, include_disambig: bool) -> list[str]:
    """
    Walk all author manifests; return UNIQUE safe_ids that still need
    extraction. A paper co-authored by N curated authors appears once.

    Filter --only applies to the source author whose manifest is examined;
    use it for piloting (e.g. --only aboulker → only papers in Aboulker's
    manifest, even if they were also matched to other curated authors).
    """
    seen: set[str] = set()
    items: list[str] = []
    for manifest in sorted(cache_root.glob("*/papers.json")):
        slug = manifest.parent.name
        if only and only.lower() not in slug.lower():
            continue
        try:
            papers = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            log.warning("[%s] malformed manifest: %s — skip", slug, exc)
            continue
        for p in papers:
            if p.get("needs_disambiguation") and not include_disambig:
                continue
            if not (p.get("html_cached") or p.get("pdf_cached")):
                continue   # no content cached — extractor would skip anyway
            safe_id = p["safe_id"]
            if safe_id in seen:
                continue   # dedup across authors
            seen.add(safe_id)
            out_json = data_root / f"{safe_id}.json"
            if out_json.exists():
                continue   # already extracted
            items.append(safe_id)
    return items


def write_buckets(items: list[str], n: int, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for existing in out_dir.glob("bucket-*.txt"):
        existing.unlink()
    buckets: list[list[str]] = [[] for _ in range(n)]
    for i, item in enumerate(items):
        buckets[i % n].append(item)
    for i, bucket in enumerate(buckets, 1):
        p = out_dir / f"bucket-{i:02d}.txt"
        p.write_text("\n".join(bucket) + ("\n" if bucket else ""),
                     encoding="utf-8")
        log.info("  bucket-%02d.txt  %d items", i, len(bucket))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workers", "-w", type=int, default=8,
                    help="Number of buckets to produce (default: 8)")
    ap.add_argument("--cache-root", type=Path, default=CACHE)
    ap.add_argument("--data-root",  type=Path, default=DATA)
    ap.add_argument("--out-dir",    type=Path, default=BUCKETS)
    ap.add_argument("--only", default=None, metavar="SLUG_SUBSTR",
                    help="Restrict to author slugs containing this substring")
    ap.add_argument("--include-disambig", action="store_true",
                    help="Include papers still flagged needs_disambiguation:true")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )

    if args.workers < 1:
        log.error("--workers must be >= 1")
        return 1
    if not args.cache_root.exists():
        log.error("cache root not found: %s", args.cache_root)
        return 1

    items = gather_work(args.cache_root, args.data_root,
                        args.only, args.include_disambig)
    log.info("Found %d outstanding extraction items across %s",
             len(items), args.cache_root)

    write_buckets(items, args.workers, args.out_dir)
    log.info("Buckets written to %s", args.out_dir)
    if items:
        log.info("Launch with: WORKER=01 bash scripts/arxiv_run_worker.sh "
                 "(repeat for WORKER=02..%02d in separate terminals)", args.workers)
    return 0


if __name__ == "__main__":
    sys.exit(main())
