#!/usr/bin/env python3
"""scripts/arxiv_name_partition.py — partition review_ids for the naming pass."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
log = logging.getLogger("arxiv_name_partition")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workers", "-w", type=int, default=8)
    ap.add_argument("--states-file", type=Path,
                    default=PROJECT / "data" / "arxiv_conjectures.json")
    ap.add_argument("--names-dir",   type=Path,
                    default=PROJECT / "data" / "arxiv_names")
    ap.add_argument("--out-dir",     type=Path,
                    default=PROJECT / "data" / "arxiv_name_buckets")
    ap.add_argument("--verbose","-v", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )

    states = json.loads(args.states_file.read_text(encoding="utf-8"))

    # Same review_id scheme as arxiv_review_partition.py.
    review_ids: list[str] = []
    counters: dict[str, int] = {}
    for s in states:
        sid = s.get("safe_id") or s.get("arxiv_id","").replace("/","_")
        if not sid:
            continue
        idx = counters.get(sid, 0)
        review_ids.append(f"{sid}__{idx:02d}")
        counters[sid] = idx + 1

    pending = []
    for rid in review_ids:
        if not (args.names_dir / f"{rid}.json").exists():
            pending.append(rid)

    log.info("Total states     : %d", len(review_ids))
    log.info("Already named    : %d", len(review_ids) - len(pending))
    log.info("Pending          : %d", len(pending))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for old in args.out_dir.glob("bucket-*.txt"):
        old.unlink()

    n = max(1, args.workers)
    buckets: list[list[str]] = [[] for _ in range(n)]
    for i, rid in enumerate(pending):
        buckets[i % n].append(rid)

    for i, bucket in enumerate(buckets, 1):
        p = args.out_dir / f"bucket-{i:02d}.txt"
        p.write_text("\n".join(bucket) + ("\n" if bucket else ""), encoding="utf-8")
        log.info("  bucket-%02d.txt  %d items", i, len(bucket))

    if pending:
        log.info("Launch with: WORKER=01 bash scripts/arxiv_name_run_worker.sh")
        log.info("            (repeat for WORKER=02..%02d in parallel)", n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
