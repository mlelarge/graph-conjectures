#!/usr/bin/env python3
"""
scripts/arxiv_review_partition.py — partition the 762 'states' records into N
buckets for the Phase-2 web-search review.

Each bucket line is `<safe_id>` (the conjecture's identifier in
data/arxiv_conjectures.json). Workers consume `<safe_id>` lines and produce
`data/arxiv_reviews/<safe_id>.json`. Already-reviewed safe_ids are skipped.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
log = logging.getLogger("arxiv_review_partition")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workers", "-w", type=int, default=8)
    ap.add_argument("--states-file", type=Path,
                    default=PROJECT / "data" / "arxiv_conjectures.json")
    ap.add_argument("--reviews-dir", type=Path,
                    default=PROJECT / "data" / "arxiv_reviews")
    ap.add_argument("--out-dir", type=Path,
                    default=PROJECT / "data" / "arxiv_review_buckets")
    ap.add_argument("--only-with-internal-refs", action="store_true",
                    help="Only include safe_ids that have ≥1 internal cross-reference")
    ap.add_argument("--internal-refs", type=Path,
                    default=PROJECT / "data" / "arxiv_internal_refs.json")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )

    states = json.loads(args.states_file.read_text(encoding="utf-8"))

    # Each safe_id (= arxiv_id with '/' replaced by '_') may correspond to multiple
    # states records when a single paper states multiple conjectures. The review key
    # is "<safe_id>__<NN>" where NN is the conjecture's position within the paper
    # (deterministic from the order in arxiv_conjectures.json).
    review_ids: list[str] = []
    counters: dict[str, int] = {}
    for s in states:
        sid = s.get("safe_id") or s.get("arxiv_id","").replace("/","_")
        if not sid:
            continue
        idx = counters.get(sid, 0)
        review_ids.append(f"{sid}__{idx:02d}")
        counters[sid] = idx + 1

    if args.only_with_internal_refs:
        refs = json.loads(args.internal_refs.read_text(encoding="utf-8"))
        # Internal refs are keyed by safe_id, not review_id; we keep all conjectures
        # from any paper that has internal refs (their other conjectures may also
        # benefit from the same context).
        review_ids = [rid for rid in review_ids if rid.split("__")[0] in refs]
        log.info("filtered to %d review_ids in papers with ≥1 internal ref", len(review_ids))

    # Drop already-reviewed
    pending = []
    for rid in review_ids:
        out = args.reviews_dir / f"{rid}.json"
        if not out.exists():
            pending.append(rid)
    log.info("Total states         : %d", len(review_ids))
    log.info("Already reviewed     : %d", len(review_ids) - len(pending))
    log.info("Pending              : %d", len(pending))

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
        log.info("Launch with: WORKER=01 bash scripts/arxiv_review_run_worker.sh")
        log.info("            (repeat for WORKER=02..%02d in parallel)", n)

    return 0


if __name__ == "__main__":
    sys.exit(main())
