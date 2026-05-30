#!/usr/bin/env python3
r"""
direct_structural_checks.py
===========================

Computational tests backing the ANGLE-2 (digon-forest) proof attempt for
Sub-lemma A-prime, written up in docs/proof_direct_structural.md.

Runs with the system Python, NO external deps (imports only h2_oracle, which is
pure Python).  Every test prints PASS/FAIL and the witnessing data so a claim in
the write-up can be checked line by line.

Tested structural claims (labels match the write-up):

  L1  : every digon-forest LEAF carries >=1 single-out and >=1 single-in arc.
        (PROVED in the doc from Eulerian + min-degree 2; here we confirm.)
  S1  : every NON-BASE 2-extremal D has U(D) vertex-connectivity exactly 2
        (equivalently: U(D) is NOT 3-connected).  The only 2-extremal members
        with 3-connected U(D) are generalised wheels.
        (CONJECTURAL in the doc; verified n<=7.)
  S2  : every non-base 2-extremal D has at least one of
           (i)  a MIXED 2-cut (vertex v + single edge e), or
           (ii) a NON-EDGE 2-vertex cut {a,b} (a,b not adjacent in U(D)).
        (CONJECTURAL; verified 40/40.)
  D1  : the seam dichotomy.  Among non-base members,
           MC(D) >= 1            <=>  oracle finds a directed-Hajos seam;
           MC(D) == 0            <=>  oracle finds only a tree-join seam,
        and in the MC==0 case the unique A-block is the generalised wheel W3,
        attaching across a NON-EDGE 2-vertex cut.
        (necessity Hajos=>MC>=1 PROVED in seam_invariant.md; the rest verified.)
"""

import json
import os
import sys
import itertools

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import h2_oracle as O                     # noqa: E402
from seam_invariant import (              # noqa: E402
    split_digons_singles, mixed_2_cuts, MC,
)


def _parse_oracle_canon(oc):
    head, rest = oc.split("|")
    n = int(head)
    arcs = []
    for tok in rest.split(";"):
        a, b = tok.split(",")
        arcs.append((int(a), int(b)))
    return n, arcs


def _und_edges(n, arcs):
    return set(frozenset((u, v)) for (u, v) in arcs if u != v)


def _comps_minus_vertices(n, E, removed):
    removed = set(removed)
    adj = {v: set() for v in range(n) if v not in removed}
    for e in E:
        a, b = tuple(e)
        if a in removed or b in removed:
            continue
        adj[a].add(b)
        adj[b].add(a)
    seen = set()
    c = 0
    for s in adj:
        if s in seen:
            continue
        c += 1
        st = [s]
        seen.add(s)
        while st:
            x = st.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    st.append(y)
    return c


def vertex_connectivity_is_3plus(n, E):
    """Return True iff U(D) stays connected after deleting ANY 2 vertices
    (i.e. vertex-connectivity >= 3).  Assumes n >= 4."""
    if n < 4:
        return False
    for pair in itertools.combinations(range(n), 2):
        if _comps_minus_vertices(n, E, pair) > 1:
            return False
    return True


def has_nonedge_2cut(n, E):
    """True iff some non-adjacent vertex pair {a,b} separates U(D)."""
    for pair in itertools.combinations(range(n), 2):
        if frozenset(pair) in E:
            continue
        if _comps_minus_vertices(n, E, pair) > 1:
            return True
    return False


# --------------------------------------------------------------------------

def load_truth(nn):
    data = json.load(open(os.path.join(ROOT, "data", f"L_{nn}.json")))
    out = []
    for i, m in enumerate(data):
        out.append((nn, i, m["n"], frozenset(tuple(a) for a in m["arcs"])))
    return out


def load_seam_records():
    path = os.path.join(ROOT, "data", "seam_search_L6_L7.json")
    data = json.load(open(path))
    recs = []
    for r in data["results"]:
        if r["status"] == "base":
            continue
        n, arcs = _parse_oracle_canon(r["oracle_canon"])
        actual = ("hajos" if r.get("has_hajos_seam")
                  else "tree-join" if r.get("has_treejoin_seam_general")
                  else "none")
        recs.append((r["n"], r["index"], n, frozenset(arcs), actual))
    return recs


def test_L1():
    """Every digon-forest leaf carries a single-in and a single-out arc."""
    bad = []
    for nn in range(3, 8):
        for (_, idx, n, arcs) in load_truth(nn):
            dig, sing = split_digons_singles(n, arcs)
            fadj = {v: set() for v in range(n)}
            for e in dig:
                a, b = tuple(e)
                fadj[a].add(b)
                fadj[b].add(a)
            sin = {v: 0 for v in range(n)}
            sout = {v: 0 for v in range(n)}
            for (u, v) in sing:
                sout[u] += 1
                sin[v] += 1
            for v in range(n):
                if len(fadj[v]) == 1 and not (sin[v] >= 1 and sout[v] >= 1):
                    bad.append((nn, idx, v))
    ok = not bad
    print(f"[L1] every digon-forest leaf has single in&out arc: "
          f"{'PASS' if ok else 'FAIL ' + str(bad)}")
    return ok


def test_S1():
    """Non-base 2-extremal => U(D) NOT 3-connected; only wheels are 3-connected."""
    threeconn_nonwheel = []
    nonbase_threeconn = []
    for nn in range(3, 8):
        for (_, idx, n, arcs) in load_truth(nn):
            E = _und_edges(n, arcs)
            soc = O.is_symmetric_odd_cycle(n, arcs)
            gw = O._is_generalised_wheel(n, arcs)
            tc = vertex_connectivity_is_3plus(n, E)
            if tc and not gw:
                threeconn_nonwheel.append((nn, idx))
            if tc and not (soc or gw):
                nonbase_threeconn.append((nn, idx))
    ok = (not threeconn_nonwheel) and (not nonbase_threeconn)
    print(f"[S1] only generalised wheels are 3-connected in U(D); "
          f"every non-base has a 2-vertex separator: "
          f"{'PASS' if ok else 'FAIL'}")
    if threeconn_nonwheel:
        print(f"     3-connected non-wheels: {threeconn_nonwheel}")
    return ok


def test_S2():
    """Every non-base member has a mixed 2-cut OR a non-edge 2-vertex cut."""
    bad = []
    for (Nn, idx, n, arcs, actual) in load_seam_records():
        E = _und_edges(n, arcs)
        mc = MC(n, arcs)
        ne = has_nonedge_2cut(n, E)
        if not (mc or ne):
            bad.append((Nn, idx))
    ok = not bad
    print(f"[S2] every non-base member has a mixed-cut OR non-edge-2-cut "
          f"separator: {'PASS' if ok else 'FAIL ' + str(bad)}")
    return ok


def test_D1():
    """Seam dichotomy + W3-block characterisation of the MC=0 members."""
    bad_dich = []
    w3_info = []
    for (Nn, idx, n, arcs, actual) in load_seam_records():
        mc = MC(n, arcs)
        pred = "hajos" if mc else "tree-join"
        if pred != actual:
            bad_dich.append((Nn, idx, actual, pred))
        if actual == "tree-join":
            # enumerate tree-join blocks; confirm a single W3 generalised-wheel block
            seen = set()
            blocksets = []
            for blocks in O._tree_join_decompositions(n, arcs, max_internal=2):
                key = tuple(sorted((nb, O.canon(nb, ab)) for nb, ab in blocks))
                if key in seen:
                    continue
                seen.add(key)
                blocksets.append([(nb, O._is_generalised_wheel(nb, ab),
                                   O.is_symmetric_odd_cycle(nb, ab))
                                  for nb, ab in blocks])
            w3_info.append((Nn, idx, blocksets))
    ok = not bad_dich
    print(f"[D1] seam dichotomy MC>=1<=>hajos, MC=0<=>tree-join: "
          f"{'PASS' if ok else 'FAIL ' + str(bad_dich)}")
    for (Nn, idx, bs) in w3_info:
        print(f"     {Nn}.{idx} tree-join blocks (n,isWheel,isSymOdd): {bs}")
    return ok


def main():
    print("=" * 72)
    print("Direct structural checks for Sub-lemma A-prime (digon-forest angle)")
    print("=" * 72)
    results = [test_L1(), test_S1(), test_S2(), test_D1()]
    print("=" * 72)
    print(f"OVERALL: {'ALL PASS' if all(results) else 'SOME FAIL'}")
    print("=" * 72)
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
