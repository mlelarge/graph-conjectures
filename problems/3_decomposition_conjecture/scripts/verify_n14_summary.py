"""Independent verifier for the n=14 milestone.

Recomputes every load-bearing statistic from the raw n=14 JSONL archive
WITHOUT trusting the precomputed summary JSON. Exits 0 iff every
expected invariant holds.

Usage:
  python verify_n14_summary.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


EXPECTED = {
    "total_records": 15178,
    "status_counts": {
        "trace_contained": 15176,
        "compat_universal_not_contained": 2,
    },
    "structural_counts": {
        "bridge": 1370,
        "essentially_3conn": 7120,
        "non_port_2cut": 6688,
    },
    "absorber_top": {
        "C0": 10474,
        "C6": 3248,
        "C8": 768,
        "C7": 296,
        "C2": 124,
        "C3": 104,
        "C4": 104,
        "C5": 26,
        "C22": 26,
        "C23": 6,
    },
    "distinct_absorbing_classes": 10,
    "neither_count": 0,
    "compat_only_records": [
        {
            "graph6": "M??CB?W`cKKGF?WG?",
            "ports": [3, 4],
            "structural_class": "bridge",
        },
        {
            "graph6": "M??CB?W`cKKGF?WG?",
            "ports": [4, 3],
            "structural_class": "bridge",
        },
    ],
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def verify(jsonl_path: Path) -> tuple[bool, list[str]]:
    failures: list[str] = []

    total = 0
    status_counts: Counter = Counter()
    structural_counts: Counter = Counter()
    absorber_counts: Counter = Counter()
    compat_only_records: list = []
    neither_records: list = []
    duplicate_keys: set = set()
    seen_keys: set = set()

    with jsonl_path.open() as f:
        for line in f:
            r = json.loads(line)
            total += 1
            key = (r["graph6"], tuple(r["ports"]))
            if key in seen_keys:
                duplicate_keys.add(key)
            seen_keys.add(key)

            status_counts[r["status"]] += 1
            structural_counts[r["structural_class"]] += 1
            if r.get("absorbing_class_id"):
                absorber_counts[r["absorbing_class_id"]] += 1
            if r["status"] == "compat_universal_not_contained":
                compat_only_records.append(
                    {
                        "graph6": r["graph6"],
                        "ports": list(r["ports"]),
                        "structural_class": r["structural_class"],
                    }
                )
            elif r["status"] == "neither":
                neither_records.append(r)

    # Invariants
    if total != EXPECTED["total_records"]:
        failures.append(f"total {total} != {EXPECTED['total_records']}")

    for k, v in EXPECTED["status_counts"].items():
        if status_counts.get(k, 0) != v:
            failures.append(f"status[{k}] = {status_counts.get(k, 0)} != {v}")
    if "neither" not in EXPECTED["status_counts"] and status_counts.get("neither", 0) != 0:
        failures.append(f"neither = {status_counts.get('neither', 0)} != 0")

    for k, v in EXPECTED["structural_counts"].items():
        if structural_counts.get(k, 0) != v:
            failures.append(f"structural[{k}] = {structural_counts.get(k, 0)} != {v}")

    if len(absorber_counts) != EXPECTED["distinct_absorbing_classes"]:
        failures.append(
            f"distinct absorbers {len(absorber_counts)} != "
            f"{EXPECTED['distinct_absorbing_classes']}"
        )

    for cid, count in EXPECTED["absorber_top"].items():
        if absorber_counts.get(cid, 0) != count:
            failures.append(f"absorber[{cid}] = {absorber_counts.get(cid, 0)} != {count}")

    if neither_records:
        failures.append(f"NEITHER records found: {len(neither_records)}")

    if len(compat_only_records) != len(EXPECTED["compat_only_records"]):
        failures.append(
            f"compat-only count {len(compat_only_records)} != "
            f"{len(EXPECTED['compat_only_records'])}"
        )
    expected_set = {
        (r["graph6"], tuple(r["ports"]), r["structural_class"])
        for r in EXPECTED["compat_only_records"]
    }
    actual_set = {
        (r["graph6"], tuple(r["ports"]), r["structural_class"])
        for r in compat_only_records
    }
    if expected_set != actual_set:
        failures.append(
            f"compat-only records differ: expected={expected_set} actual={actual_set}"
        )

    if duplicate_keys:
        failures.append(f"DUPLICATE (graph6, ports) keys: {len(duplicate_keys)}")

    return len(failures) == 0, failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jsonl", type=Path, default=ROOT / "data" / "n14_full.jsonl")
    parser.add_argument("--show-hash", action="store_true")
    args = parser.parse_args()

    if args.show_hash:
        print(f"sha256({args.jsonl}) = {sha256(args.jsonl)}")

    ok, failures = verify(args.jsonl)
    if ok:
        print(f"OK — all n=14 invariants verified against {args.jsonl}")
        return 0
    print(f"FAIL — {len(failures)} invariant(s) violated:")
    for f in failures:
        print(f"  {f}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
