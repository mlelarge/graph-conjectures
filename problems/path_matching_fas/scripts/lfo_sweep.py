"""Exhaustive LFO (linear-forest ordering) sweep.

Sweep all non-isomorphic tournaments at n in [3..7]. For each:
  - Decide path-FAS (= LFO) by brute force.
  - For NO instances, record min FAS size, score sequence, and the
    degree-only / forest-only relaxation data.

Output a JSON file with summary stats and full enumeration of NO
instances at small n.
"""
from __future__ import annotations
import argparse, json, os, sys, time
from itertools import permutations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify import verify       # noqa: E402
from sweep import all_tournaments, canonical_key  # noqa: E402


def analyze_T(T):
    n = len(T)
    min_fas = None
    min_max_degree = None
    min_max_degree_order = None
    degree2_order = None
    forest_order = None
    lfo_order = None
    for P in permutations(range(n)):
        info = verify(T, list(P))
        if min_fas is None or info["count"] < min_fas:
            min_fas = info["count"]
        if min_max_degree is None or info["max_degree"] < min_max_degree:
            min_max_degree = info["max_degree"]
            min_max_degree_order = list(P)
        if degree2_order is None and info["max_degree"] <= 2:
            degree2_order = list(P)
        if forest_order is None and info["is_forest"]:
            forest_order = list(P)
        if lfo_order is None and info["is_linear_forest"]:
            lfo_order = list(P)
    score_seq = sorted([sum(T[i]) for i in range(n)])
    return {
        "n": n,
        "lfo_exists": lfo_order is not None,
        "lfo_order": lfo_order,
        "min_fas": min_fas,
        "min_max_back_degree": min_max_degree,
        "min_max_back_degree_order": min_max_degree_order,
        "degree2_relaxation_exists": degree2_order is not None,
        "degree2_order": degree2_order,
        "forest_ordering_exists": forest_order is not None,
        "forest_order": forest_order,
        "score_sequence": score_seq,
        "T": T,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--nmin", type=int, default=3)
    p.add_argument("--nmax", type=int, default=7)
    p.add_argument("--out", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "data",
        "lfo_sweep.json"))
    args = p.parse_args()

    results = []
    for n in range(args.nmin, args.nmax + 1):
        t0 = time.time()
        seen = set()
        no_instances = []
        yes_count = 0
        total = 0
        for T in all_tournaments(n):
            key = canonical_key(T)
            if key in seen:
                continue
            seen.add(key)
            total += 1
            a = analyze_T(T)
            if a["lfo_exists"]:
                yes_count += 1
            else:
                no_instances.append(a)
        dt = time.time() - t0
        print(f"n={n}: total non-iso = {total}, LFO YES = {yes_count}, "
              f"LFO NO = {len(no_instances)}, {dt:.1f}s")
        results.append({
            "n": n,
            "total": total,
            "lfo_yes": yes_count,
            "lfo_no": len(no_instances),
            "no_instances": no_instances,
            "seconds": round(dt, 2),
        })

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
