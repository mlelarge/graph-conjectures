#!/usr/bin/env python3
"""Split the still-unreviewed OPG slugs into N round-robin buckets.

Each bucket is written to data/agent_buckets/bucket-NN.txt (one slug per line).
Workers consume one bucket each via scripts/run_worker.sh.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    project = here.parent
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workers", type=int, default=8, help="number of buckets / parallel workers")
    p.add_argument("--data-dir", type=Path, default=project / "data")
    args = p.parse_args(argv)

    queue_path = args.data_dir / "agent_queue.txt"
    reviews_dir = args.data_dir / "reviews"
    out_dir = args.data_dir / "agent_buckets"
    out_dir.mkdir(parents=True, exist_ok=True)

    queue = [s.strip() for s in queue_path.read_text().splitlines() if s.strip()]
    done = {f.stem for f in reviews_dir.glob("*.json") if not f.name.endswith(".raw.json")}
    remaining = [s for s in queue if s not in done]

    # Wipe any stale buckets so we never reuse a previous (now-stale) partition.
    for f in out_dir.glob("bucket-*.txt"):
        f.unlink()

    if not remaining:
        print("nothing to partition — all slugs are reviewed.")
        return 0

    n = max(1, args.workers)
    buckets: list[list[str]] = [[] for _ in range(n)]
    for i, slug in enumerate(remaining):
        buckets[i % n].append(slug)

    for idx, bucket in enumerate(buckets, start=1):
        path = out_dir / f"bucket-{idx:02d}.txt"
        path.write_text("\n".join(bucket) + ("\n" if bucket else ""), encoding="utf-8")

    print(f"queued: {len(queue)}, done: {len(done)}, remaining: {len(remaining)}")
    print(f"workers: {n}, bucket size avg: {len(remaining) // n}")
    print(f"buckets written to {out_dir}/")
    for idx, bucket in enumerate(buckets, start=1):
        print(f"  bucket-{idx:02d}.txt: {len(bucket)} slugs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
