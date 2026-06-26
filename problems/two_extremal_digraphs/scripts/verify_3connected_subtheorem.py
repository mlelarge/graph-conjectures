#!/usr/bin/env python3
"""
Verify the 3-connected sub-theorem "3-connected 2-extremal ⇒ generalised wheel"
by exhaustive enumeration at a given n.

For every 3-connected graph (geng -C, filtered by node-connectivity ≥ 3):
  * if max-local-edge-connectivity λ'(U) ≥ 5, the λ'≤4 lemma (T2) certifies it
    cannot host a 2-extremal orientation — skipped with no search;
  * otherwise enumerate all 2-extremal orientations (exact Eulerian-pruned +
    forest-restricted digon search), and for each check it is a generalised wheel
    with connected F_D.

Reports counts; any NON-generalised-wheel or disconnected-F_D 2-extremal would be a
counterexample to the sub-theorem (none expected).

Result of record:
  n=4..7: only the wheels W_{n-1} admit; all generalised wheels, F_D connected.
  n=8   : 2388 three-connected graphs; 2036 lemma-skipped (λ'≥5); 352 searched;
          only W₇ admits (2 labelled orientations), generalised wheels,
          F_D connected; 0 non-gen-wheel, 0 disconnected-F_D.

Usage:
    PYTHONPATH=problems/two_extremal_digraphs/scripts \
      .venv/bin/python problems/two_extremal_digraphs/scripts/verify_3connected_subtheorem.py [--n 8] [--budget B]
"""

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import h2_oracle as H  # noqa: E402
from seam_invariant import split_digons_singles  # noqa: E402
import planarity_search as PS  # noqa: E402
import n8_disproof as N  # noqa: E402

try:
    import networkx as nx
except Exception:
    nx = None


def fd_connected(n, arcs):
    de, _ = split_digons_singles(n, arcs)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(tuple(e) for e in de)
    return nx.is_connected(G)


def verify(n, budget):
    GENG = N.geng_path()
    out = subprocess.run([GENG, "-C", str(n)], capture_output=True, text=True).stdout
    tot3 = skip = admit = nongw = fdd = capped = 0
    bad = []
    for line in out.splitlines():
        G = nx.from_graph6_bytes(line.strip().encode())
        if nx.node_connectivity(G) < 3:
            continue
        tot3 += 1
        if N.max_local_edge_conn(G) >= 5:    # T2 lemma: cannot be 2-extremal
            skip += 1
            continue
        E = [tuple(sorted(e)) for e in G.edges()]
        # exhaustive (budget guards against pathological grind)
        cnt = 0
        for arcs in PS.two_extremal_orientations(n, E):
            cnt += 1
            admit += 1
            gw = H._is_generalised_wheel(n, arcs)
            fc = fd_connected(n, arcs)
            if not gw:
                nongw += 1
                bad.append(("NON-GEN-WHEEL", sorted(arcs)))
            if not fc:
                fdd += 1
                bad.append(("F_D-DISCONNECTED", sorted(arcs)))
        # (budget not wired into the generator; this is exhaustive for n≤8)
    print(f"n={n}: 3-connected graphs={tot3}  lemma-skipped(λ'≥5)={skip}  "
          f"searched={tot3-skip}")
    print(f"  2-extremal orientations admitted={admit}  "
          f"NON-generalised-wheel={nongw}  disconnected-F_D={fdd}")
    if bad:
        print("  !!! SUB-THEOREM VIOLATIONS:")
        for tag, a in bad[:10]:
            print(f"    {tag}: {a}")
        return 1
    print(f"  => sub-theorem holds at n={n}: every 3-connected 2-extremal is a "
          f"generalised wheel with connected F_D.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--budget", type=int, default=2_000_000)
    args = ap.parse_args()
    if nx is None:
        print("networkx required (root .venv)")
        return 1
    return verify(args.n, args.budget)


if __name__ == "__main__":
    raise SystemExit(main())
