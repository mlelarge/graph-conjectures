"""Merge shard JSONL checkpoints into the main checkpoint.

Reads main + N shard files; emits one merged main JSONL with deduplication
on (graph6, ports). Optionally regenerates the summary JSON.

Usage:
  python merge_shards.py \
    --main data/n14_essentially_3conn_full.jsonl \
    --shards data/n14_essentially_3conn.shard*.jsonl \
    --summary-output data/n14_essentially_3conn_full.summary.json \
    --lattice data/gadget_lattice_2pole_n12_both.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--main", type=Path, required=True, help="Main JSONL checkpoint (in-place merge)")
    parser.add_argument("--shards", nargs="+", type=Path, required=True, help="Shard JSONL files to merge")
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=None,
        help="Optional: regenerate summary JSON",
    )
    parser.add_argument(
        "--lattice",
        type=Path,
        default=None,
        help="Lattice JSON (for summary metadata)",
    )
    args = parser.parse_args()

    # Read main
    main_records = {}
    if args.main.exists():
        with args.main.open() as f:
            for line in f:
                r = json.loads(line)
                key = (r["graph6"], tuple(r["ports"]))
                main_records[key] = r
    print(f"main: {len(main_records)} records", file=sys.stderr)

    # Read shards
    added = 0
    for shard in args.shards:
        if not shard.exists():
            print(f"shard {shard} missing, skipping", file=sys.stderr)
            continue
        n = 0
        new = 0
        with shard.open() as f:
            for line in f:
                r = json.loads(line)
                n += 1
                key = (r["graph6"], tuple(r["ports"]))
                if key not in main_records:
                    main_records[key] = r
                    new += 1
        print(f"  {shard}: {n} records ({new} new)", file=sys.stderr)
        added += new

    # Rewrite main JSONL (sorted by graph6 then ports for stability)
    with args.main.open("w") as f:
        for key in sorted(main_records):
            f.write(json.dumps(main_records[key], sort_keys=True) + "\n")
    print(f"merged: {len(main_records)} total records ({added} new)", file=sys.stderr)

    # Optional summary
    if args.summary_output:
        if args.lattice is None:
            print("--summary-output requires --lattice for metadata", file=sys.stderr)
            return 2
        lattice_meta = json.loads(args.lattice.read_text())["meta"]
        status_counts: Counter = Counter()
        structural_counts: Counter = Counter()
        absorber_counts: Counter = Counter()
        neither: list = []
        compat_univ_not_contained: list = []
        for r in main_records.values():
            status_counts[r["status"]] += 1
            structural_counts[r["structural_class"]] += 1
            if r["absorbing_class_id"]:
                absorber_counts[r["absorbing_class_id"]] += 1
            if r["status"] == "neither":
                neither.append(r)
            elif r["status"] == "compat_universal_not_contained":
                compat_univ_not_contained.append(r)
        summary = {
            "lattice_meta": lattice_meta,
            "total_oriented_sides_processed": sum(status_counts.values()),
            "status_counts": dict(status_counts),
            "structural_counts": dict(structural_counts),
            "top_absorbing_classes": absorber_counts.most_common(20),
            "distinct_absorbing_classes": len(absorber_counts),
            "neither_count": len(neither),
            "neither_records": neither,
            "compat_universal_not_contained_count": len(compat_univ_not_contained),
            "compat_universal_not_contained_records": compat_univ_not_contained,
        }
        args.summary_output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        print(f"summary -> {args.summary_output}", file=sys.stderr)
        print(json.dumps(summary["status_counts"]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
