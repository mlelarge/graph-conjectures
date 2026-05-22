"""Generate compact non-isomorphic tournament representatives by extension.

This is the exact representative-generation half of the n=9 pipeline.
It starts from the exact n=7 census, extends representatives one vertex
at a time, and deduplicates with `tournament_canonical.canonical_key`.

Representatives are stored as JSONL records containing the canonical
flattened adjacency matrix string:

    {"n": 9, "key": "010..."}

The full key is used rather than an upper-triangle bitstring so that it
can be reconstructed without remembering the canonical order convention.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Iterable, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lfo_extend_census import extend_by_one  # noqa: E402
from tournament_canonical import canonical_key, key_to_string, string_to_matrix  # noqa: E402


def load_n7_keys(path: str) -> list[str]:
    with open(path) as f:
        data = json.load(f)
    keys = []
    for bucket in data["buckets"]:
        for record in bucket["records"]:
            keys.append(key_to_string(canonical_key(record["T"])))
    return sorted(set(keys))


def load_jsonl_keys(path: str) -> list[str]:
    keys = []
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            keys.append(json.loads(line)["key"])
    return keys


def write_jsonl(path: str, n: int, keys: Sequence[str]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        for key in keys:
            f.write(json.dumps({"n": n, "key": key}, separators=(",", ":")))
            f.write("\n")


def extend_keys(keys: Sequence[str], progress: int = 250) -> list[str]:
    reps: dict[str, None] = {}
    t0 = time.time()
    for idx, raw in enumerate(keys, start=1):
        T = string_to_matrix(raw)
        for U in extend_by_one(T):
            reps.setdefault(key_to_string(canonical_key(U)), None)
        if progress and idx % progress == 0:
            print(f"extended {idx}/{len(keys)} base reps; "
                  f"unique next reps = {len(reps)}; "
                  f"elapsed = {round(time.time() - t0, 1)}s",
                  flush=True)
    return sorted(reps)


def default_path(data_dir: str, n: int) -> str:
    return os.path.join(data_dir, f"lfo_reps_n{n}.jsonl")


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(here, "..", "data"))
    default_seed = os.path.join(data_dir, "lfo_full_n7.json")

    p = argparse.ArgumentParser()
    p.add_argument("--target-n", type=int, required=True, choices=(8, 9))
    p.add_argument("--seed-n7", default=default_seed)
    p.add_argument("--data-dir", default=data_dir)
    p.add_argument("--progress", type=int, default=250)
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    t0 = time.time()
    n7_keys = load_n7_keys(args.seed_n7)
    if len(n7_keys) != 456:
        raise RuntimeError(f"expected 456 n=7 representatives, got {len(n7_keys)}")

    current_n = 7
    current_keys = n7_keys
    summaries = [{
        "n": 7,
        "representatives": len(current_keys),
        "source": os.path.relpath(args.seed_n7, os.path.join(here, "..")),
    }]

    while current_n < args.target_n:
        next_n = current_n + 1
        out_path = default_path(args.data_dir, next_n)
        if os.path.exists(out_path) and not args.force:
            next_keys = load_jsonl_keys(out_path)
            print(f"loaded existing n={next_n} reps from {out_path}: {len(next_keys)}",
                  flush=True)
        else:
            print(f"generating n={next_n} reps from {len(current_keys)} n={current_n} reps",
                  flush=True)
            next_keys = extend_keys(current_keys, args.progress)
            write_jsonl(out_path, next_n, next_keys)
            print(f"wrote {out_path}", flush=True)

        summaries.append({
            "n": next_n,
            "representatives": len(next_keys),
            "path": os.path.relpath(out_path, os.path.join(here, "..")),
        })
        current_n = next_n
        current_keys = next_keys

    summary = {
        "target_n": args.target_n,
        "seconds": round(time.time() - t0, 2),
        "levels": summaries,
    }
    summary_path = os.path.join(args.data_dir, f"lfo_reps_n{args.target_n}_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
    print(f"wrote {summary_path}")


if __name__ == "__main__":
    main()
