"""Randomly test whether n=7 LFO obstructions explain larger NO instances.

LFO is hereditary: restricting a linear-forest ordering to an induced
subtournament leaves a subgraph of a linear forest. Therefore any
tournament containing an induced n=7 LFO NO subtournament is itself LFO NO.

This script tests the converse empirically:

    if a random n-vertex tournament is LFO NO, does it contain one of the
    exact n=7 LFO NO tournaments as an induced subtournament?

Any NO instance with no induced n=7 NO is a new larger obstruction
candidate.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import random
import sys
import time
from collections import Counter
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lfo_obstruction_analysis import dual, full_canonical_key, induced  # noqa: E402
from lfo_score_bucket import analyze_lfo, score_sequence  # noqa: E402


def random_tournament(n: int, rng: random.Random) -> list[list[int]]:
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.getrandbits(1):
                T[i][j] = 1
            else:
                T[j][i] = 1
    return T


def load_no7_keys(path: str) -> tuple[set[tuple[int, ...]], set[tuple[int, ...]], set[tuple[int, ...]]]:
    with open(path) as f:
        data = json.load(f)
    all_no: set[tuple[int, ...]] = set()
    size_no: set[tuple[int, ...]] = set()
    combinatorial_no: set[tuple[int, ...]] = set()
    for bucket in data["buckets"]:
        for record in bucket["records"]:
            if record["has_lfo"]:
                continue
            key = full_canonical_key(record["T"])
            all_no.add(key)
            if record["no_kind"] == "size":
                size_no.add(key)
            elif record["no_kind"] == "combinatorial":
                combinatorial_no.add(key)
    return all_no, size_no, combinatorial_no


def contained_no7_kind(
    T: Sequence[Sequence[int]],
    all_no: set[tuple[int, ...]],
    size_no: set[tuple[int, ...]],
    combinatorial_no: set[tuple[int, ...]],
) -> dict:
    hits = []
    for keep in itertools.combinations(range(len(T)), 7):
        key = full_canonical_key(induced(T, keep))
        if key in all_no:
            if key in size_no:
                kind = "size"
            elif key in combinatorial_no:
                kind = "combinatorial"
            else:
                kind = "unknown"
            hits.append({"vertices": list(keep), "kind": kind})
    return {
        "contains_no7": bool(hits),
        "hit_count": len(hits),
        "hit_kind_hist": dict(sorted(Counter(h["kind"] for h in hits).items())),
        "first_hits": hits[:10],
    }


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    default_full = os.path.join(here, "..", "data", "lfo_full_n7.json")
    default_out = os.path.join(here, "..", "data", "lfo_forbidden7_random.json")

    p = argparse.ArgumentParser()
    p.add_argument("--full-n7", default=default_full)
    p.add_argument("--n", type=int, default=8)
    p.add_argument("--samples", type=int, default=200)
    p.add_argument("--seed", type=int, default=20260521)
    p.add_argument("--out", default=default_out)
    p.add_argument("--progress", type=int, default=25)
    args = p.parse_args()

    all_no, size_no, combinatorial_no = load_no7_keys(args.full_n7)
    rng = random.Random(args.seed)
    t0 = time.time()

    confusion: Counter[str] = Counter()
    no_score_hist: Counter[str] = Counter()
    new_obstructions = []
    false_positive = []

    for sample_id in range(args.samples):
        T = random_tournament(args.n, rng)
        lfo = analyze_lfo(T)
        hit = contained_no7_kind(T, all_no, size_no, combinatorial_no)
        has_lfo = lfo["has_lfo"]
        contains = hit["contains_no7"]

        if has_lfo and contains:
            confusion["contains_no7_but_lfo_yes"] += 1
            false_positive.append({
                "sample_id": sample_id,
                "score_sequence": list(score_sequence(T)),
                "T": T,
                "hit": hit,
                "lfo": lfo,
            })
        elif has_lfo:
            confusion["no7_free_lfo_yes"] += 1
        elif contains:
            confusion["contains_no7_lfo_no"] += 1
            no_score_hist[str(score_sequence(T))] += 1
        else:
            confusion["no7_free_lfo_no"] += 1
            no_score_hist[str(score_sequence(T))] += 1
            new_obstructions.append({
                "sample_id": sample_id,
                "score_sequence": list(score_sequence(T)),
                "T": T,
                "lfo": lfo,
                "hit": hit,
            })

        if args.progress and (sample_id + 1) % args.progress == 0:
            print(f"processed {sample_id + 1}/{args.samples}: {dict(confusion)}",
                  flush=True)

    new_keys = [full_canonical_key(x["T"]) for x in new_obstructions]
    new_dual_orbits = {
        min(key, full_canonical_key(dual(x["T"])))
        for key, x in zip(new_keys, new_obstructions)
    }

    out = {
        "n": args.n,
        "samples": args.samples,
        "seed": args.seed,
        "seconds": round(time.time() - t0, 2),
        "n7_no_key_count": len(all_no),
        "n7_size_no_key_count": len(size_no),
        "n7_combinatorial_no_key_count": len(combinatorial_no),
        "confusion": dict(sorted(confusion.items())),
        "no_score_hist": dict(sorted(no_score_hist.items())),
        "false_positive_count": len(false_positive),
        "new_obstruction_candidate_count": len(new_obstructions),
        "new_obstruction_unique_iso_count": len(set(new_keys)),
        "new_obstruction_dual_orbit_count": len(new_dual_orbits),
        "new_obstruction_no_kind_hist": dict(sorted(Counter(
            x["lfo"]["no_kind"] for x in new_obstructions
        ).items())),
        "new_obstruction_relaxation_hist": dict(sorted(Counter(
            (
                "coupling"
                if x["lfo"]["has_degree2_relaxation"] and x["lfo"]["has_forest_ordering"]
                else "cycle_obstruction"
                if x["lfo"]["has_degree2_relaxation"]
                else "degree_obstruction"
                if x["lfo"]["has_forest_ordering"]
                else "both_relaxations_fail"
            )
            for x in new_obstructions
        ).items())),
        "false_positives": false_positive,
        "new_obstruction_candidates": new_obstructions,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({
        k: out[k]
        for k in (
            "n",
            "samples",
            "seed",
            "seconds",
            "confusion",
            "new_obstruction_candidate_count",
            "new_obstruction_unique_iso_count",
            "new_obstruction_dual_orbit_count",
            "false_positive_count",
            "no_score_hist",
        )
    }, indent=2))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
