"""H8: which bounded-twin-width tournaments lie OUTSIDE the {TT1,TT2,C3}
substitution closure (the class Thm 3.9 of arXiv:2310.04265 already settles)?

Conj 3.12 asks: tww<=k tournaments are chiVec-bounded.  Thm 3.9 ALREADY proves
chiVec-boundedness on the {TT1,TT2,C3}-substitution closure (= hereditary closure
of the S~_n family).  So the OPEN part of Conj 3.12 at twin-width <=k lives
EXACTLY on tww<=k tournaments that are NOT in that closure.  This script measures,
for each small n and each tww<=W class member, whether it is in the closure --
pinpointing where (and whether) the open conjecture has any room below the
Neumann-Lara n>=11 barrier.

Membership test (modular decomposition):
  The substitution closure of {TT1,TT2,C3} = all tournaments whose modular
  decomposition tree has EVERY quotient being a substitution of TT1/TT2/C3.
  TT2-substitutions build any transitive (linear/"series") composition; C3 is
  the unique prime tournament on 3 vertices; TT1 is the base.  Hence:

      T (|T|>=2) is in the closure  iff  it has a nontrivial module partition
      whose QUOTIENT is either a transitive tournament (any size, built from
      TT2) or exactly C3, AND every part (induced sub-tournament) is itself in
      the closure.

  Equivalently: T is in the closure iff its modular decomposition has NO prime
  quotient on >=4 vertices.  A prime tournament on >=4 vertices (no nontrivial
  module) is therefore the minimal obstruction and lies OUTSIDE the closure.

We compute membership directly by the recursive characterization, using an exact
modular-decomposition partition finder (maximal-module partition).

Usage:
  .venv/bin/python scripts/h8_closure_membership.py <n> [--tww-max W]
"""
from __future__ import annotations
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
import oracle
from collections import Counter
from functools import lru_cache


def _is_module(A, S, n):
    """S (a set of vertices) is a module iff every outside vertex z relates the
    SAME way to all of S: either z->all of S or all of S->z."""
    Sset = set(S)
    for z in range(n):
        if z in Sset:
            continue
        it = iter(S)
        first = A[z][next(it)]   # True iff z->that vertex
        for v in S:
            if A[z][v] != first:
                return False
    return True


def _closure_module(A, n, seed):
    """Smallest module (subset of {0..n-1}) containing `seed`: grow S until every
    outside vertex relates uniformly to all of S."""
    S = set(seed)
    changed = True
    while changed:
        changed = False
        for z in range(n):
            if z in S:
                continue
            vals = {A[z][v] for v in S}
            if len(vals) > 1:
                S.add(z)
                changed = True
    return S


def _maximal_modular_partition(A, n):
    """Top-level modular decomposition partition of {0..n-1}.

    Returns a list of parts.  Three regimes (standard modular-decomposition
    theory for tournaments, which have no parallel/non-edge case):
      * len == n  : T is PRIME (only trivial modules) -> n singletons.
      * len  < n  : the maximal proper modules partition V; the quotient on the
                    parts is either C3 (the unique prime 3-tournament that admits
                    a modular partition into >=2 strong modules) or a transitive
                    composition (series).  For a transitive (linear) T the
                    maximal proper modules are NOT all of V either; we return the
                    finest faithful top split.

    Method: the maximal MODULES that are proper and pairwise non-overlapping.
    Two vertices are co-modular if the smallest module containing both is a
    proper subset of V.  But that over-merges in the SERIES (transitive) case,
    where every interval is a module and the smallest module of two vertices can
    still be proper while their union spans V.  To get the genuine TOP quotient
    we instead take the partition into the maximal STRONG modules: a strong
    module is one that does not overlap any other module.  For small n we find
    the maximal proper strong modules directly.
    """
    # All proper modules (2 <= size < n), as frozensets.
    mods = set()
    # seed every pair, take its closure module
    for u in range(n):
        for v in range(u + 1, n):
            M = _closure_module(A, n, {u, v})
            if 2 <= len(M) < n:
                mods.add(frozenset(M))
    if not mods:
        # prime: no nontrivial proper module
        return [[v] for v in range(n)]
    # Maximal strong modules: a module M is strong if it does not OVERLAP
    # (partially intersect) any other module.  The maximal strong proper modules
    # partition V (modular decomposition theorem).
    mod_list = list(mods)

    def overlaps(X, Y):
        inter = X & Y
        return len(inter) > 0 and not (X <= Y) and not (Y <= X)

    strong = []
    for M in mod_list:
        if not any(overlaps(M, N) for N in mod_list if N != M):
            strong.append(M)
    # maximal strong proper modules (not contained in a larger strong proper one)
    maximal = [M for M in strong
               if not any((M < N) for N in strong)]
    # cover V: remaining vertices are singleton strong modules
    covered = set()
    parts = []
    for M in sorted(maximal, key=lambda s: -len(s)):
        if M & covered:
            continue
        parts.append(sorted(M))
        covered |= M
    for v in range(n):
        if v not in covered:
            parts.append([v])
            covered.add(v)
    if len(parts) <= 1:
        # over-merged into a single part == V: fall back to prime treatment
        return [[v] for v in range(n)]
    return parts


def _quotient_arcs(A, parts):
    """Build the quotient tournament on the parts (each part is a module, so the
    relation between two parts is uniform). Returns (k, arcs)."""
    k = len(parts)
    reps = [p[0] for p in parts]
    arcs = []
    for i in range(k):
        for j in range(k):
            if i == j:
                continue
            if A[reps[i]][reps[j]]:
                arcs.append((i, j))
    # dedup undirected: keep one direction
    seen = set()
    out = []
    for (u, v) in arcs:
        key = frozenset((u, v))
        if key in seen:
            continue
        seen.add(key)
        out.append((u, v))
    return k, out


def _is_transitive(k, arcs):
    """True iff the tournament (k,arcs) is acyclic (transitive)."""
    if k <= 1:
        return True
    return core.chi_vec(k, arcs) == 1


def _is_C3(k, arcs):
    return k == 3 and core.chi_vec(k, arcs) == 2  # C3 is the only non-transitive 3-tournament


def _sub_adj(A, verts):
    """Induced adjacency matrix on `verts` (relabeled 0..len-1) and arc list."""
    m = len(verts)
    idx = {v: i for i, v in enumerate(verts)}
    arcs = []
    for a in range(m):
        for b in range(m):
            if a == b:
                continue
            if A[verts[a]][verts[b]]:
                arcs.append((a, b))
    seen = set(); out = []
    for (u, v) in arcs:
        key = frozenset((u, v))
        if key in seen:
            continue
        seen.add(key); out.append((u, v))
    return m, out


def in_closure(n, arcs):
    """True iff (n,arcs) is in the {TT1,TT2,C3}-substitution closure."""
    A = core._adj(n, arcs)

    def rec(verts):
        m = len(verts)
        if m <= 1:
            return True
        sub_n, sub_arcs = _sub_adj(A, verts)
        # remap into a local adjacency for module finding
        subA = core._adj(sub_n, sub_arcs)
        parts = _maximal_modular_partition(subA, sub_n)
        # guard against a degenerate single part spanning everything
        if len(parts) <= 1:
            parts = [[i] for i in range(sub_n)]
        if len(parts) == sub_n:
            # No nontrivial module: the whole sub-tournament IS its own quotient.
            # In closure iff it is an iterated TT2-substitution (transitive) or C3.
            if sub_n <= 2:
                return True                       # TT1, TT2 base
            if _is_transitive(sub_n, sub_arcs):
                return True                       # TT_n = iterated TT2 substitution
            if _is_C3(sub_n, sub_arcs):
                return True
            return False      # genuinely prime on >=4 (or non-C3 prime 3) => OUTSIDE
        # not prime: quotient must be transitive (TT2-substitutions) or C3,
        # AND every part must itself be in closure
        qk, qarcs = _quotient_arcs(subA, parts)
        quotient_ok = _is_transitive(qk, qarcs) or _is_C3(qk, qarcs)
        if not quotient_ok:
            # quotient is a prime/non-closure tournament on the parts
            # recurse on the quotient itself (it may decompose further) --
            # but a quotient at the modular-decomp top level is PRIME by
            # definition, so non-transitive non-C3 quotient => outside.
            return False
        # recurse into parts (map local part indices back to original verts)
        for p in parts:
            real = [verts[i] for i in p]
            if not rec(real):
                return False
        return True

    return rec(list(range(n)))


def run(n, tww_max=1):
    in_cnt = Counter()       # (tww,omega,chi) -> count IN closure
    out_cnt = Counter()      # (tww,omega,chi) -> count OUTSIDE closure
    out_examples = []
    scanned = 0
    kept = 0
    for (_n, arcs) in oracle._all_tournaments(n):
        scanned += 1
        w = core.tww(n, arcs, ub=tww_max + 1)
        if w > tww_max:
            continue
        kept += 1
        om = core.omega_vec(n, arcs)
        ch = core.chi_vec(n, arcs)
        inc = in_closure(n, arcs)
        key = (w, om, ch)
        if inc:
            in_cnt[key] += 1
        else:
            out_cnt[key] += 1
            if len(out_examples) < 30:
                out_examples.append({"tww": w, "omega_vec": om, "chi_vec": ch,
                                     "arcs": list(arcs)})
    return {
        "n": n, "tww_max": tww_max, "n_scanned": scanned, "kept_tww<=max": kept,
        "in_closure_dist": {f"{k[0]},{k[1]},{k[2]}": v for k, v in sorted(in_cnt.items())},
        "outside_closure_dist": {f"{k[0]},{k[1]},{k[2]}": v for k, v in sorted(out_cnt.items())},
        "num_outside_closure": sum(out_cnt.values()),
        "num_in_closure": sum(in_cnt.values()),
        "outside_examples": out_examples,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("n", type=int)
    ap.add_argument("--tww-max", type=int, default=1)
    a = ap.parse_args()
    print(json.dumps(run(a.n, a.tww_max), indent=2, default=str))
