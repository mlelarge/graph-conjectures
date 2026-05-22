"""Test the hypothesis: if T contains a vertex v whose in-neighborhood
and out-neighborhood both induce cyclic 3-cycles, then T has no
linear-forest ordering.

We construct every n=7 tournament with this local structure (vertex 0 as
the hub), enumerate all 2^9 = 512 X<->Y orientation patterns, and brute-
force-check each one for an LFO.

If every such tournament has no LFO, the local structure is a sufficient
obstruction. We separately report the degree-only relaxation
(`max_degree <= 2`) because it is weaker than LFO: LFO additionally
requires the back-arc graph to be acyclic.
"""
from __future__ import annotations
import argparse, json, os, sys
from itertools import product, permutations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify import verify  # noqa: E402


def make_T(orientations):
    """Build the n=7 tournament with:
      - vertex 0 = hub
      - N^+(0) = {1,2,3}, cycle 1->2->3->1
      - N^-(0) = {4,5,6}, cycle 4->5->6->4
      - X<->Y orientations from the 9-bit input.
    orientations: 9-bit tuple (b_{x,y}) where x in {1,2,3}, y in {4,5,6}.
        b=1 means x -> y, b=0 means y -> x.
    """
    n = 7
    T = [[0] * n for _ in range(n)]
    # Hub arcs
    for x in (1, 2, 3):
        T[0][x] = 1
    for y in (4, 5, 6):
        T[y][0] = 1
    # Cyclic triangle on N^+ = {1,2,3}: 1->2, 2->3, 3->1
    T[1][2] = 1; T[2][3] = 1; T[3][1] = 1
    # Cyclic triangle on N^- = {4,5,6}: 4->5, 5->6, 6->4
    T[4][5] = 1; T[5][6] = 1; T[6][4] = 1
    # X<->Y arcs
    pairs = [(x, y) for x in (1, 2, 3) for y in (4, 5, 6)]
    for (x, y), b in zip(pairs, orientations):
        if b == 1:
            T[x][y] = 1
        else:
            T[y][x] = 1
    return T


PERMS_BY_N: dict[int, list[tuple[int, ...]]] = {}


def perms(n: int) -> list[tuple[int, ...]]:
    if n not in PERMS_BY_N:
        PERMS_BY_N[n] = list(permutations(range(n)))
    return PERMS_BY_N[n]


def analyze_tournament(T):
    """Analyze true LFO and its two natural relaxations."""
    n = len(T)
    min_max_d = None
    min_max_info = None
    has_degree2 = False
    has_forest = False
    has_lfo = False
    has_matching = False

    for P in perms(n):
        info = verify(T, list(P))
        if min_max_d is None or info["max_degree"] < min_max_d:
            min_max_d = info["max_degree"]
            min_max_info = (list(P), info)
        has_degree2 = has_degree2 or info["max_degree"] <= 2
        has_forest = has_forest or info["is_forest"]
        has_lfo = has_lfo or info["is_linear_forest"]
        has_matching = has_matching or info["is_matching"]
        if has_lfo and has_forest and has_degree2 and has_matching and min_max_d <= 1:
            break

    return {
        "has_lfo": has_lfo,
        "has_degree2_relaxation": has_degree2,
        "has_forest_ordering": has_forest,
        "has_matching_fas": has_matching,
        "min_max_back_degree": min_max_d,
        "min_max_order": min_max_info[0],
        "min_max_arcs": min_max_info[1]["arcs"],
        "min_max_is_forest": min_max_info[1]["is_forest"],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=None,
                   help="Optional JSON output path for the full 512-instance summary.")
    args = p.parse_args()

    total = 0
    yes_lfo = 0
    no_lfo = 0
    yes_degree2 = 0
    yes_forest = 0
    yes_matching = 0
    min_max_histogram: dict[int, int] = {}
    no_bitcount_histogram: dict[int, int] = {}
    records = []

    for orientations in product((0, 1), repeat=9):
        T = make_T(orientations)
        a = analyze_tournament(T)
        total += 1
        bitcount = sum(orientations)
        min_max_histogram[a["min_max_back_degree"]] = (
            min_max_histogram.get(a["min_max_back_degree"], 0) + 1
        )
        if a["has_lfo"]:
            yes_lfo += 1
        else:
            no_lfo += 1
            no_bitcount_histogram[bitcount] = no_bitcount_histogram.get(bitcount, 0) + 1
        if a["has_degree2_relaxation"]:
            yes_degree2 += 1
        if a["has_forest_ordering"]:
            yes_forest += 1
        if a["has_matching_fas"]:
            yes_matching += 1

        if args.out is not None:
            records.append({
                "orientations": list(orientations),
                "bitcount": bitcount,
                **a,
            })

    summary = {
        "total": total,
        "lfo_yes": yes_lfo,
        "lfo_no": no_lfo,
        "degree2_relaxation_yes": yes_degree2,
        "forest_ordering_yes": yes_forest,
        "matching_fas_yes": yes_matching,
        "min_max_back_degree_histogram": dict(sorted(min_max_histogram.items())),
        "lfo_no_bitcount_histogram": dict(sorted(no_bitcount_histogram.items())),
    }

    print(f"Total double-cycle tournaments tested: {total}")
    print(f"With true LFO (linear forest): {yes_lfo}")
    print(f"Without true LFO: {no_lfo}")
    print(f"With degree-only relaxation (min max back-deg <= 2): {yes_degree2}")
    print(f"With forest-ordering relaxation: {yes_forest}")
    print(f"With matching-FAS: {yes_matching}")
    print(f"Min max-deg distribution: {sorted(min_max_histogram.items())}")
    print(f"LFO-NO bit-count distribution: {sorted(no_bitcount_histogram.items())}")

    if args.out is not None:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w") as f:
            json.dump({"summary": summary, "records": records}, f, indent=2)
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
