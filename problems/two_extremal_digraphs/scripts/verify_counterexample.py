#!/usr/bin/env python3
"""
Counterexample triage verifier.  Given a candidate digraph (arc set, or read from
a disproof checkpoint's `counterexamples`), run the full battery and print an
auditable certificate.  Lightweight; runs only on the one candidate.

If the run ever prints `!!! COUNTEREXAMPLE`, this turns it into a saved, checkable
record.  A digraph that is **2-extremal AND non-planar** refutes Conjecture 9.2
(because H₂ ⇒ planar is proved, docs/planarity_of_2extremal.md).

What it reports (each clause individually, nothing blurred):
  * the 2-extremality clauses: Eulerian(min-deg 2), strong, U 2-connected,
    λ≤2, λ=2, χ⃗=3  — and the overall is_2extremal verdict;
  * planarity of U(D) (+ a Kuratowski K5/K3,3-subgraph note if non-planar);
  * F_D (digon graph): forest? number of components;
  * repo-λ value and MC value;
  * H₂ oracle status — **SOUND when True** (a real decomposition exists),
    **PROVISIONAL when False** (the recogniser caps max_internal, so "not in H₂"
    is not certified);
  * canonical label.

Usage:
    .venv/bin/python verify_counterexample.py --arcs '[[0,1],[1,0],...]'
    .venv/bin/python verify_counterexample.py --g6 'G...' --orient '[[0,1],...]'  (arcs override)
    .venv/bin/python verify_counterexample.py --from-checkpoint data/n9_disproof_ckpt.json
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import h2_oracle as H  # noqa: E402
from seam_invariant import split_digons_singles, mixed_2_cuts, underlying_edges  # noqa: E402

try:
    import networkx as nx
except Exception:
    nx = None


def report(n, arcs):
    arcs = frozenset((int(u), int(v)) for u, v in arcs)
    print(f"# candidate digraph  n={n}  |A|={len(arcs)}")
    print(f"  arcs: {sorted(arcs)}")

    print("\n## 2-extremality clauses (each independent)")
    cl = {
        "Eulerian (in=out, min-deg≥2)": H.is_eulerian_deg(n, arcs, min_deg=2),
        "strong": H.is_strong(n, arcs),
        "U(D) 2-connected": H.is_2connected(n, arcs),
        "λ ≤ 2": H.lambda_at_most(n, arcs, 2),
        "λ == 2": H.lambda_D(n, arcs) == 2,
        "χ⃗ == 3": H.chi_vec(n, arcs) == 3,
    }
    for k, v in cl.items():
        print(f"  {'PASS' if v else 'fail'}  {k}")
    is2e = H.is_2extremal(n, arcs)
    print(f"  => is_2extremal: {is2e}   (repo-λ={H.lambda_D(n,arcs)}, "
          f"χ⃗={H.chi_vec(n,arcs)}, MC={len(mixed_2_cuts(n,arcs))})")

    print("\n## underlying graph U(D)")
    de, si = split_digons_singles(n, arcs)
    print(f"  |E(U)|={len(underlying_edges(n,arcs))}  digons={len(de)}  singles={len(si)}")
    # F_D forest?
    if nx is not None:
        Gf = nx.Graph()
        Gf.add_nodes_from(range(n))
        Gf.add_edges_from(tuple(e) for e in de)
        ncomp = nx.number_connected_components(Gf)
        print(f"  F_D (digon graph): forest={nx.is_forest(Gf)}  components={ncomp}")
        GU = nx.Graph()
        GU.add_nodes_from(range(n))
        for e in underlying_edges(n, arcs):
            a, b = tuple(e)
            GU.add_edge(a, b)
        planar, _ = nx.check_planarity(GU)
        print(f"  planar(U): {planar}  edge-connectivity κ'(U)={nx.edge_connectivity(GU)}")
        if not planar:
            # extract a Kuratowski subgraph as the non-planarity certificate
            try:
                from networkx.algorithms.planarity import (
                    get_counterexample)  # type: ignore
                kur = get_counterexample(GU)
                print(f"  non-planarity certificate (Kuratowski subgraph edges): "
                      f"{sorted(tuple(sorted(e)) for e in kur.edges())}")
            except Exception:
                print("  (non-planar; Kuratowski extractor unavailable)")
    else:
        print("  [networkx unavailable: planarity / F_D-forest not checked]")

    print("\n## H₂ oracle")
    in_h2 = H.is_in_H2(n, arcs)
    if in_h2:
        print("  is_in_H2 = True  [SOUND: a real H₂ decomposition was found]")
    else:
        print("  is_in_H2 = False [PROVISIONAL: recogniser caps max_internal=2; "
              "'not in H₂' is NOT certified]")

    print(f"\n## canonical label\n  {H.canon(n, arcs)}")

    print("\n## verdict")
    nonplanar = (nx is not None) and (not nx.check_planarity(
        nx.Graph(list(tuple(e) for e in underlying_edges(n, arcs))))[0])
    if is2e and nonplanar:
        print("  *** GENUINE COUNTEREXAMPLE to Conjecture 9.2: 2-extremal AND "
              "non-planar (H₂⇒planar is proved, so this digraph is not in H₂). ***")
    elif is2e and in_h2:
        print("  2-extremal and in H₂ — consistent with 9.2 (not a counterexample).")
    elif is2e and not in_h2:
        print("  2-extremal, planar, is_in_H2=False — but that False is PROVISIONAL "
              "(max_internal cap). Re-check with a deeper recogniser before any claim.")
    else:
        print("  NOT 2-extremal — not a counterexample (a clause above failed).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arcs", help="JSON list of [u,v] arcs")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--from-checkpoint", help="path to n*_disproof_ckpt.json")
    args = ap.parse_args()

    cands = []
    if args.from_checkpoint:
        ck = json.load(open(args.from_checkpoint))
        for c in ck.get("counterexamples", []):
            cands.append((c.get("n"), c["arcs"]))
        if not cands:
            print(f"[no counterexamples in {args.from_checkpoint}]")
            return 0
    elif args.arcs:
        arcs = json.loads(args.arcs)
        n = args.n or (max(max(u, v) for u, v in arcs) + 1)
        cands.append((n, arcs))
    else:
        ap.error("provide --arcs or --from-checkpoint")

    for n, arcs in cands:
        report(n, arcs)
        print("\n" + "=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
