"""Empirical sweep: decide MFAS/PFAS/LFFAS/Forest-FAS on every
non-isomorphic tournament for n <= nmax.

For each n we generate tournaments by iterating over the 2^{C(n,2)}
orientations of K_n, deduplicate by canonical form (using the
permutation-of-rows minimum), and run the brute-force decider on each.

Output: data/sweep_results.json with a per-n breakdown and example
tournaments for both YES and NO buckets.
"""
from __future__ import annotations
import argparse, itertools, json, os, sys, time
from typing import Iterator

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify import verify                # noqa: E402
from brute import decide                 # noqa: E402


def all_tournaments(n: int) -> Iterator[list[list[int]]]:
    """Yield every tournament on n vertices (as a 0/1 matrix). Iterates
    over the 2^{C(n,2)} orientations of K_n.
    """
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for bits in itertools.product((0, 1), repeat=len(pairs)):
        T = [[0] * n for _ in range(n)]
        for (i, j), b in zip(pairs, bits):
            if b == 1:
                T[i][j] = 1
            else:
                T[j][i] = 1
        yield T


def canonical_key(T: list[list[int]]) -> tuple:
    """Return a canonical form for T under vertex relabeling.

    Brute force: try every permutation. OK for n <= 8 (40320 perms).
    """
    n = len(T)
    best = None
    for P in itertools.permutations(range(n)):
        # Relabel: new vertex i corresponds to old P[i]; the new adjacency
        # is T[P[i]][P[j]].
        key = tuple(T[P[i]][P[j]] for i in range(n) for j in range(n))
        if best is None or key < best:
            best = key
    return best


def sweep_n(n: int) -> dict:
    """Return statistics for all non-isomorphic tournaments on n vertices."""
    t0 = time.time()
    seen: set[tuple] = set()
    matching_yes = 0
    path_yes = 0
    lin_forest_yes = 0
    forest_yes = 0
    total = 0
    # Save a few NO examples for inspection.
    matching_no_examples: list[list[list[int]]] = []
    path_no_examples: list[list[list[int]]] = []
    forest_no_examples: list[list[list[int]]] = []
    matching_yes_examples: list[list[list[int]]] = []

    for T in all_tournaments(n):
        key = canonical_key(T)
        if key in seen:
            continue
        seen.add(key)
        total += 1

        results = {tgt: decide(T, tgt) for tgt in
                   ("matching", "path", "linear_forest", "forest")}
        if results["matching"]["found"]:
            matching_yes += 1
            if len(matching_yes_examples) < 6:
                matching_yes_examples.append(T)
        else:
            if len(matching_no_examples) < 4:
                matching_no_examples.append(T)
        if results["path"]["found"]:
            path_yes += 1
        else:
            if len(path_no_examples) < 4:
                path_no_examples.append(T)
        if results["linear_forest"]["found"]:
            lin_forest_yes += 1
        if results["forest"]["found"]:
            forest_yes += 1
        else:
            if len(forest_no_examples) < 4:
                forest_no_examples.append(T)
    dt = time.time() - t0
    return {
        "n": n,
        "non_iso_total": total,
        "matching_yes": matching_yes,
        "matching_no": total - matching_yes,
        "path_yes": path_yes,
        "path_no": total - path_yes,
        "linear_forest_yes": lin_forest_yes,
        "forest_yes": forest_yes,
        "matching_yes_examples": matching_yes_examples,
        "matching_no_examples": matching_no_examples,
        "path_no_examples": path_no_examples,
        "forest_no_examples": forest_no_examples,
        "seconds": round(dt, 3),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--nmax", type=int, default=6)
    p.add_argument("--nmin", type=int, default=3)
    p.add_argument(
        "--out",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "data", "sweep_results.json"),
    )
    args = p.parse_args()

    all_results = []
    for n in range(args.nmin, args.nmax + 1):
        print(f"==> n={n}")
        r = sweep_n(n)
        all_results.append(r)
        print(f"   total non-iso: {r['non_iso_total']}")
        print(f"   matching_yes : {r['matching_yes']} (/ {r['non_iso_total']})")
        print(f"   path_yes     : {r['path_yes']} (/ {r['non_iso_total']})")
        print(f"   linear_forest: {r['linear_forest_yes']} (/ {r['non_iso_total']})")
        print(f"   forest_yes   : {r['forest_yes']} (/ {r['non_iso_total']})")
        print(f"   elapsed      : {r['seconds']}s")

    out_path = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
