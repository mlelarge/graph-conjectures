"""Post-sweep analysis: for each LFO NO instance, characterize:

  - score sequence
  - min FAS size
  - location of "double-cyclic-triangle hub" vertices (vertices v whose
    in-neighborhood and out-neighborhood each induce a cyclic triangle)
  - number of cyclic 3-cycles
  - subtournament containment relations

Reads `data/lfo_sweep.json` and emits a per-n summary plus a flat
listing of NO instances at each size.
"""
from __future__ import annotations
import argparse, json, os, sys
from collections import Counter
from itertools import permutations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from structural import cyclic_3_cycles  # noqa: E402


def is_cyclic_triangle_on(T, V):
    V = list(V)
    if len(V) != 3:
        return False
    a, b, c = V
    # cyclic = either a->b->c->a or a->c->b->a
    if T[a][b] and T[b][c] and T[c][a]:
        return True
    if T[a][c] and T[c][b] and T[b][a]:
        return True
    return False


def double_triangle_hubs(T):
    n = len(T)
    hubs = []
    for v in range(n):
        Np = [u for u in range(n) if T[v][u]]
        Nm = [u for u in range(n) if T[u][v]]
        if len(Np) == 3 and len(Nm) == 3:
            if is_cyclic_triangle_on(T, Np) and is_cyclic_triangle_on(T, Nm):
                hubs.append(v)
    return hubs


def analyze_no_instance(T):
    n = len(T)
    return {
        "n": n,
        "score_sequence": sorted([sum(T[i]) for i in range(n)]),
        "n_cyclic_3cycles": len(cyclic_3_cycles(T)),
        "double_triangle_hubs": double_triangle_hubs(T),
        "T": T,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "data",
        "lfo_sweep_3_6_corrected.json"))
    args = p.parse_args()

    with open(args.input) as f:
        sweep = json.load(f)

    smallest_no_n = None
    for entry in sweep:
        n = entry["n"]
        if entry["lfo_no"] > 0 and smallest_no_n is None:
            smallest_no_n = n
        print(f"\n=== n={n}: {entry['total']} non-iso, "
              f"LFO YES {entry['lfo_yes']}, LFO NO {entry['lfo_no']} ===")
        if entry["lfo_no"] == 0:
            continue
        for inst in entry["no_instances"]:
            T = inst["T"]
            a = analyze_no_instance(T)
            print(f"  T={T}")
            print(f"    score seq: {a['score_sequence']}")
            print(f"    cyclic 3-cycles: {a['n_cyclic_3cycles']}")
            print(f"    double-triangle hubs: {a['double_triangle_hubs']}")
            print(f"    min FAS: {inst.get('min_fas')}")
            print(f"    min max back-deg: {inst['min_max_back_degree']}")

    if smallest_no_n is not None:
        print(f"\n*** Smallest n with LFO NO: {smallest_no_n} ***")


if __name__ == "__main__":
    main()
