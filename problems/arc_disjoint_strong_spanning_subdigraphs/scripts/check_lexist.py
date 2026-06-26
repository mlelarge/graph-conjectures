"""check_lexist.py -- red-team the (L-exist) rescue of refuted Conjecture L.

CRUX-A lever. Conjecture L (UNIVERSAL form) is REFUTED (G1). The
existential form over arbitrary 3-arc-strong multidigraphs is also FALSE,
even in the intermediate-cut regime: see `lexist_path_counterexample.py`.
The surviving rescue is restricted to genuine chord-contraction
multidigraphs:

  (L-exist)  For every in-class chord-contraction multidigraph D and every arc
             a = (u, v) in A(D), there EXISTS a pair of arc-disjoint
             spanning in-arborescences (T-, U-) rooted at r := v = head(a),
             with a in T-, such that SOME U--exit b from X = X_a^{T-} has
                 X_b^{U-} cap X  STRICTLY contained in  X.

Here, for an in-arborescence S- rooted at r, every w != r has a unique
out-arc to its S--parent; X_e^{S-} for e = (x,y) in S- is the set of
S--descendants of x (incl. x) -- exactly the vertices whose unique
S--walk to r traverses e. delta^+(X) = arcs with tail in X, head not in X.

This module is a BESPOKE structural checker (the SAD oracle does NOT
decide funnel/strict-subset properties). It enumerates ALL arc-disjoint
spanning-in-arborescence pairs rooted at r and tests the strict-subset
exit property at the fixed arc a.

L-exist FAILS at (D, a) iff EVERY arc-disjoint pair (T-,U-) with a in T-
has the funnel failure at a (no strict exit). Such a (D, a) is a finite,
checkable REFUTATION of L-exist -> would kill the H2 rescue of CRUX-A.

Logical form: For a FIXED (D,a), L-exist(D,a) is an EXISTENTIAL claim
(some good pair exists); we verify it by EXHAUSTIVE pair enumeration, so
the per-instance verdict is exact (not a sample). The OVERALL L-exist is
UNIVERSAL over (D, a) in the class of 3-arc-strong multidigraphs; to
red-team it honestly we run over a GENERIC census of small 3-arc-strong
digraphs (geng -d3 | directg -T), NOT a structured sub-family, plus the
named hard host K_4^* and its small multi-arc thickenings.
"""
from __future__ import annotations

import itertools
import json
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from digraph import Digraph  # noqa: E402


# --------------------------------------------------------------------------- #
#  In-arborescence enumeration over a multidigraph
# --------------------------------------------------------------------------- #
#  Arcs are carried as a list of (u, v, idx) triples; idx is a unique label so
#  parallel arcs are distinguishable (arc-disjointness is by label).

def _spanning_in_arborescences(n, arcs, r):
    """Yield every spanning in-arborescence rooted at r, as a frozenset of
    arc labels. Each non-root vertex chooses exactly one out-arc; the chosen
    arcs must form a single tree oriented toward r (acyclic, every vertex
    reaches r)."""
    out_by_tail = {w: [] for w in range(n)}
    for (u, v, idx) in arcs:
        out_by_tail[u].append((u, v, idx))
    nonroot = [w for w in range(n) if w != r]
    # every non-root vertex needs >=1 out-arc, else no arborescence at all
    for w in nonroot:
        if not out_by_tail[w]:
            return
    choice_lists = [out_by_tail[w] for w in nonroot]
    for combo in itertools.product(*choice_lists):
        parent = {}
        labels = []
        for (u, v, idx) in combo:
            parent[u] = v
            labels.append(idx)
        # validity: following parents from every w must reach r without cycle
        ok = True
        for w in nonroot:
            seen = set()
            cur = w
            while cur != r:
                if cur in seen:        # cycle -> not an arborescence
                    ok = False
                    break
                seen.add(cur)
                cur = parent[cur]
            if not ok:
                break
        if ok:
            yield frozenset(labels), dict(parent)


def _subtree_below(arc_uv, parent, n, r):
    """X_e^{S-} for e=(x,y) in S- with parent map: S--descendants of x incl x.
    A vertex w (w != r) is a descendant of x iff x lies on w's parent-walk to
    r (and w==x trivially)."""
    x, y = arc_uv
    desc = {x}
    for w in range(n):
        if w == r:
            continue
        cur = w
        while cur != r:
            if cur == x:
                desc.add(w)
                break
            cur = parent[cur]
    return desc


def _strict_exit_exists(X, Uparent, n, r, arc_by_label, U_labels):
    """Does SOME U--exit b from X have X_b^{U-} cap X STRICTLY < X?
    U--exits = arcs of U- with tail in X, head not in X."""
    Xset = set(X)
    for lab in U_labels:
        (u, v, _idx) = arc_by_label[lab]
        if u in Xset and v not in Xset:           # b = (u,v) is a U--exit
            Xb = _subtree_below((u, v), Uparent, n, r)
            inter = Xb & Xset
            if inter < Xset:                       # strict subset
                return True
    return False


def lexist_at_arc(n, arcs_labeled, a):
    """Decide L-exist at a FIXED arc a=(u,v,idx). Root r := v = head(a).
    Returns dict with verdict 'HOLDS' (a good pair found) | 'FAILS'
    (no arc-disjoint pair with a in T- has a strict exit) | 'NO_PAIR'
    (no arc-disjoint in-arb pair with a in T- exists at all)."""
    (au, av, aidx) = a
    r = av
    arc_by_label = {idx: (u, v, idx) for (u, v, idx) in arcs_labeled}
    arbs = list(_spanning_in_arborescences(n, arcs_labeled, r))
    # T- candidates: those USING arc a (i.e. aidx in the label set, which
    # forces a to be u's chosen out-arc).
    T_cands = [(lab, par) for (lab, par) in arbs if aidx in lab]
    if not T_cands:
        return {"verdict": "NO_T", "n_arbs": len(arbs)}
    n_pairs = 0
    for (Tlabs, Tpar) in T_cands:
        X = _subtree_below((au, av), Tpar, n, r)   # X = X_a^{T-}
        for (Ulabs, Upar) in arbs:
            if Tlabs & Ulabs:                       # not arc-disjoint
                continue
            n_pairs += 1
            if _strict_exit_exists(X, Upar, n, r, arc_by_label, Ulabs):
                return {"verdict": "HOLDS", "n_arbs": len(arbs),
                        "n_pairs_tested": n_pairs, "X_size": len(X)}
    if n_pairs == 0:
        return {"verdict": "NO_PAIR", "n_arbs": len(arbs)}
    return {"verdict": "FAILS", "n_arbs": len(arbs), "n_pairs_tested": n_pairs}


# --------------------------------------------------------------------------- #
#  Per-digraph driver: test L-exist at EVERY arc
# --------------------------------------------------------------------------- #

def label_arcs(arcs):
    return [(int(u), int(v), i) for i, (u, v) in enumerate(arcs)]


def check_digraph(n, arcs, name="D"):
    """Test L-exist at every arc of a 3-arc-strong D. Returns the list of
    arcs at which L-exist FAILS (empty => L-exist holds for this D)."""
    arcs_labeled = label_arcs(arcs)
    fails, nopair = [], []
    for a in arcs_labeled:
        res = lexist_at_arc(n, arcs_labeled, a)
        if res["verdict"] == "FAILS":
            fails.append({"arc": [a[0], a[1]], "label": a[2], **res})
        elif res["verdict"] == "NO_PAIR":
            nopair.append({"arc": [a[0], a[1]], "label": a[2], **res})
    return {"name": name, "n": n, "m": len(arcs),
            "fails": fails, "nopair": nopair}


# --------------------------------------------------------------------------- #
#  Generic census of small 3-arc-strong simple digraphs (geng -d3 | directg -T)
# --------------------------------------------------------------------------- #

def _arc_conn(n, arcs):
    return Digraph.from_arcs(range(n), [(u, v) for (u, v) in arcs]).arc_connectivity()


def _generic_3arcstrong_simple(n):
    """Yield arc-lists of all 3-arc-strong SIMPLE digraphs on n vertices via
    nauty geng -d3 n | directg -T, oracle-exact lambda>=3 filter."""
    geng = subprocess.Popen(["geng", "-q", "-d3", str(n)], stdout=subprocess.PIPE)
    directg = subprocess.Popen(["directg", "-q", "-T"], stdin=geng.stdout,
                               stdout=subprocess.PIPE, text=True)
    geng.stdout.close()
    for line in directg.stdout:
        line = line.strip()
        if not line:
            continue
        toks = line.split()
        # directg -T format: "n m  u1 v1 u2 v2 ..."
        nn = int(toks[0])
        flat = list(map(int, toks[2:]))
        arcs = [(flat[i], flat[i + 1]) for i in range(0, len(flat), 2)]
        if nn != n:
            continue
        if _arc_conn(n, arcs) >= 3:
            yield arcs
    directg.wait()


def K_star(n):
    return [(i, j) for i in range(n) for j in range(n) if i != j]


def K4star_thickenings(max_mult=2):
    """K_4^* (the named hard host for Conjecture L) and small multi-arc
    thickenings: add up to (max_mult-1) parallel copies of single arcs."""
    base = K_star(4)
    yield ("K4star", 4, list(base))
    # one doubled arc, each choice (structured but the explicit hard host)
    for (u, v) in base:
        yield (f"K4star+dbl({u},{v})", 4, list(base) + [(u, v)])


# --------------------------------------------------------------------------- #
#  CLI
# --------------------------------------------------------------------------- #

def main():
    import argparse
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("census", help="generic 3-arc-strong simple census")
    p1.add_argument("n", type=int)
    p1.add_argument("--limit", type=int, default=0,
                    help="stop after this many 3-arc-strong digraphs (0=all)")

    p2 = sub.add_parser("k4star", help="K_4^* + small thickenings (hard host)")
    p2.add_argument("--max-mult", type=int, default=2)

    p3 = sub.add_parser("one", help="single explicit digraph")
    p3.add_argument("n", type=int)
    p3.add_argument("arcs", help="JSON [[u,v],...]")

    args = ap.parse_args()

    if args.cmd == "one":
        arcs = json.loads(args.arcs)
        lam = _arc_conn(args.n, arcs)
        res = check_digraph(args.n, arcs, name="explicit")
        res["lambda"] = lam
        print(json.dumps(res, indent=2))
        return

    if args.cmd == "k4star":
        n_d = 0
        fail_d = 0
        nopair_d = 0
        examples = []
        for (name, n, arcs) in K4star_thickenings(args.max_mult):
            lam = _arc_conn(n, arcs)
            if lam < 3:
                continue
            n_d += 1
            res = check_digraph(n, arcs, name=name)
            if res["fails"]:
                fail_d += 1
                examples.append(res)
            if res["nopair"]:
                nopair_d += 1
        print(json.dumps({"scope": "K4star+thickenings",
                          "n_3arcstrong_tested": n_d,
                          "n_with_Lexist_FAILS": fail_d,
                          "n_with_NO_PAIR": nopair_d,
                          "fail_examples": examples[:5]}, indent=2))
        return

    # census
    n = args.n
    n_d = 0
    fail_d = 0
    nopair_d = 0
    examples = []
    nopair_examples = []
    for arcs in _generic_3arcstrong_simple(n):
        n_d += 1
        res = check_digraph(n, arcs, name=f"g{n_d}")
        if res["fails"]:
            fail_d += 1
            if len(examples) < 5:
                examples.append({"arcs": arcs, **res})
        if res["nopair"]:
            nopair_d += 1
            if len(nopair_examples) < 5:
                nopair_examples.append({"arcs": arcs, **res})
        if args.limit and n_d >= args.limit:
            break
    print(json.dumps({"scope": f"generic simple n={n}",
                      "n_3arcstrong_tested": n_d,
                      "n_with_Lexist_FAILS": fail_d,
                      "n_with_NO_PAIR": nopair_d,
                      "fail_examples": examples,
                      "nopair_examples": nopair_examples}, indent=2))


if __name__ == "__main__":
    main()
