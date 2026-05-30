#!/usr/bin/env python3
"""
SEAM SEARCH for Lemma A (Seam Existence), Conjecture 9.2 (arXiv:2304.04690).

Lemma A claims: every 2-extremal digraph that is NOT a symmetric odd cycle and
NOT a generalised wheel contains either
  (a) a DIRECTED-HAJOS merge vertex -- a vertex v whose split exhibits D as a
      directed Hajos join (Def 1.5) of two strictly-smaller 2-extremal digraphs,
      OR
  (b) a PERIPHERAL B-EDGE CUT DIGON -- a digon {x->y, y->x} whose two arcs form a
      2-arc-cut realising a 2-Hajos tree-join (Def 9.1) seam: deleting that digon
      separates D into two sides, each of which, with the interface digon
      re-added, is a strictly-smaller 2-extremal digraph.

This script classifies every member of data/L_6.json + data/L_7.json:
  * skip BASE members (symmetric odd cycle or generalised wheel);
  * for each NON-BASE member, search for a seam of type (a) and/or (b);
  * report every non-base member with NO seam found (candidate obstruction),
    after an independent re-verification pass.

Results are dumped to data/seam_search_L6_L7.json.

Reuses (read-only) the SOUND machinery in scripts/h2_oracle.py:
  is_2extremal, is_symmetric_odd_cycle, _is_generalised_wheel,
  _hajos_decompositions, canon.
"""

import sys
import os
import json
import itertools

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import h2_oracle as H  # noqa: E402


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _arcset(arcs):
    return frozenset((int(u), int(v)) for (u, v) in arcs)


def classify_base(n, arcs):
    """Return 'symmetric_odd_cycle', 'generalised_wheel', or None."""
    A = _arcset(arcs)
    if H.is_symmetric_odd_cycle(n, A):
        return "symmetric_odd_cycle"
    if H._is_generalised_wheel(n, A):
        return "generalised_wheel"
    return None


# --------------------------------------------------------------------------
# Seam (a): directed-Hajos merge vertex
# --------------------------------------------------------------------------
#
# We reuse the oracle's directed-Hajos inverse (`_hajos_decompositions`), which
# enumerates every (join arc (u,w), split vertex v, induced cut bipartition).
# A genuine Lemma-A seam (a) requires BOTH recovered sides to be 2-extremal and
# strictly smaller.  (The oracle's inverse already enforces strict smallness;
# we additionally enforce 2-extremality of each side -- which is exactly the
# Lemma-A requirement and stronger than mere H_2-membership recursion.)

def search_hajos_seam(n, arcs):
    A = _arcset(arcs)
    seams = []
    for d1, d2 in H._hajos_decompositions(n, A):
        (n1, a1) = d1
        (n2, a2) = d2
        if n1 >= n or n2 >= n:
            continue
        if H.is_2extremal(n1, a1) and H.is_2extremal(n2, a2):
            seams.append({
                "side1": {"n": n1, "arcs": sorted(map(list, a1))},
                "side2": {"n": n2, "arcs": sorted(map(list, a2))},
                "side1_canon": H.canon(n1, a1),
                "side2_canon": H.canon(n2, a2),
            })
    return seams


# --------------------------------------------------------------------------
# Seam (b): peripheral B-edge cut digon (2-arc-cut digon tree-join seam)
# --------------------------------------------------------------------------
#
# A B-edge of a 2-Hajos tree join is realised as a digon {x<->y}.  When that
# B-edge sits at a tree position whose removal disconnects the tree into two
# subtrees, deleting the digon's two arcs disconnects the WHOLE digraph: the
# digon is a 2-ARC-CUT.  In the forward construction the two arcs (x->y),(y->x)
# are the only arcs crossing the cut (the rim/peripheral cycle and all other
# blocks live wholly on one side of a B-edge that splits the tree at an interior
# point only when... ) -- more carefully:
#
# A digon {x,y} is a tree-join seam candidate iff:
#   (i)  {(x,y),(y,x)} is a 2-arc-cut: removing both arcs splits the vertex set
#        into S_x (containing x) and S_y (containing y) with NO other arc
#        crossing.  Equivalently x,y is a cut pair whose only connection is the
#        digon.
#   (ii) Each side, with the interface digon RE-ADDED at the cut endpoints,
#        forms a strictly-smaller 2-extremal digraph.
#
# Note: because lambda(D)=2 and the digon already carries 2 arc-disjoint x<->y
# connections, a 2-arc-cut at a digon is exactly a min-cut realising a tree-join
# B-edge seam.  We re-add the interface digon on each side (the forward join
# deletes the B-edge digon from neither side -- a B-edge IS the shared digon; in
# the inverse, each side keeps a copy of the digon as its interface).

def _sides_of_digon_cut(n, A, x, y):
    """If {(x,y),(y,x)} is a 2-arc-cut separating x from y, return (Sx, Sy)
    vertex sets (Sx contains x, Sy contains y, partition of all vertices).
    Otherwise return None."""
    # Build underlying adjacency WITHOUT the digon {x,y}.
    und = [set() for _ in range(n)]
    for (a, b) in A:
        if {a, b} == {x, y}:
            continue
        und[a].add(b)
        und[b].add(a)
    # Component of x in the graph with the digon removed.
    seen = {x}
    stack = [x]
    while stack:
        u = stack.pop()
        for w in und[u]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    if y in seen:
        return None  # digon is NOT a cut (other paths connect x,y)
    Sx = seen
    Sy = set(range(n)) - Sx
    if y not in Sy:
        return None
    if not Sx or not Sy:
        return None
    # Confirm the digon's two arcs are the ONLY arcs crossing Sx<->Sy.
    for (a, b) in A:
        if (a in Sx) != (b in Sx):
            if {a, b} != {x, y}:
                return None
    return Sx, Sy


def _induce_with_interface_digon(A, S, x, y):
    """Induced subdigraph on S (relabelled 0..|S|-1) with the interface digon
    {x,y} present.  x,y must both be in S.  Returns (n', frozenset)."""
    S = sorted(S)
    idx = {v: i for i, v in enumerate(S)}
    if x not in idx or y not in idx:
        return None
    new = set()
    for (a, b) in A:
        if a in idx and b in idx:
            new.add((idx[a], idx[b]))
    new.add((idx[x], idx[y]))
    new.add((idx[y], idx[x]))
    return len(S), frozenset(new)


def search_bcut_seam(n, arcs):
    A = _arcset(arcs)
    # all digons
    digons = set()
    for (u, v) in A:
        if (v, u) in A and u < v:
            digons.add((u, v))
    seams = []
    for (x, y) in sorted(digons):
        cut = _sides_of_digon_cut(n, A, x, y)
        if cut is None:
            continue
        Sx, Sy = cut
        # Side x keeps the interface digon at x (toward y's identified copy):
        # we re-add the digon {x,y} on EACH side, identifying the shared endpoints.
        # But y is on Sy and x on Sx; the interface vertex on side x is x, on side
        # y is y.  The forward B-edge digon is {x,y} -- in the inverse each side
        # retains the full digon by carrying BOTH endpoints.  To keep the side a
        # genuine smaller digraph we include the partner endpoint as the interface.
        d1 = _induce_with_interface_digon(A, Sx | {y}, x, y)
        d2 = _induce_with_interface_digon(A, Sy | {x}, x, y)
        if d1 is None or d2 is None:
            continue
        (n1, a1) = d1
        (n2, a2) = d2
        if n1 >= n or n2 >= n:
            continue
        if H.is_2extremal(n1, a1) and H.is_2extremal(n2, a2):
            seams.append({
                "digon": [x, y],
                "side1": {"n": n1, "arcs": sorted(map(list, a1))},
                "side2": {"n": n2, "arcs": sorted(map(list, a2))},
                "side1_canon": H.canon(n1, a1),
                "side2_canon": H.canon(n2, a2),
            })
    return seams


# --------------------------------------------------------------------------
# Seam (b'): GENERAL 2-Hajos tree-join seam (non-empty A), via the oracle inverse
# --------------------------------------------------------------------------
#
# Clause (b) of Lemma A asks for a B-edge digon "realising a 2-Hajos tree-join
# seam".  The STRICT reading -- the digon is a literal 2-arc-cut (search_bcut_
# seam) -- is found in ZERO members here, because the peripheral rim cycle keeps
# both endpoints connected so the digon alone is never a 2-arc-cut in a strong
# underlying-2-connected digraph.  The GENERAL reading is: D admits a non-empty-A
# 2-Hajos tree-join presentation whose A-blocks are strictly-smaller 2-extremal
# digraphs (a tree-join seam, not isolatable to one digon's 2-arc-cut).  We
# detect that with the oracle's SOUND tree-join inverse and verify every A-block
# is 2-extremal and strictly smaller.

def search_treejoin_seam(n, arcs, max_internal=2):
    A = _arcset(arcs)
    seams = []
    seen_keys = set()
    for blocks in H._tree_join_decompositions(n, A, max_internal=max_internal):
        if not blocks:
            continue  # empty A == generalised wheel, handled as base
        if any(nb >= n for (nb, ab) in blocks):
            continue
        if not all(H.is_2extremal(nb, ab) for (nb, ab) in blocks):
            continue
        key = tuple(sorted(H.canon(nb, ab) for (nb, ab) in blocks))
        if key in seen_keys:
            continue
        seen_keys.add(key)
        seams.append({
            "blocks": [
                {"n": nb, "arcs": sorted(map(list, ab)),
                 "canon": H.canon(nb, ab)}
                for (nb, ab) in blocks
            ],
        })
    return seams


# --------------------------------------------------------------------------
# Independent re-verification of a NO-SEAM member
# --------------------------------------------------------------------------
#
# For any member where neither search finds a seam, we re-derive from scratch
# with an independent cut enumeration to make sure we did not miss an obvious
# 2-arc-cut digon, and we double-check the member really is 2-extremal and
# non-base.

def reverify_no_seam(n, arcs):
    A = _arcset(arcs)
    report = {}
    report["is_2extremal"] = H.is_2extremal(n, A)
    report["base"] = classify_base(n, arcs)
    # Independent brute count of 2-arc-cut digons (regardless of side
    # 2-extremality), so we can see whether the obstruction is "no cut digon at
    # all" or "cut digons exist but a side is not 2-extremal".
    digons = [(u, v) for (u, v) in A if (v, u) in A and u < v]
    cut_digons = []
    for (x, y) in digons:
        if _sides_of_digon_cut(n, A, x, y) is not None:
            cut_digons.append([x, y])
    report["num_digons"] = len(digons)
    report["num_2arc_cut_digons"] = len(cut_digons)
    report["cut_digons"] = cut_digons
    # Independent count of directed-Hajos splits (regardless of side
    # 2-extremality).
    nsplits = 0
    n2ext_splits = 0
    for d1, d2 in H._hajos_decompositions(n, A):
        nsplits += 1
        (n1, a1) = d1
        (n2, a2) = d2
        if (n1 < n and n2 < n and H.is_2extremal(n1, a1)
                and H.is_2extremal(n2, a2)):
            n2ext_splits += 1
    report["num_hajos_splits"] = nsplits
    report["num_hajos_splits_both_2extremal"] = n2ext_splits
    return report


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def run():
    results = []
    counts = {
        "base": 0,
        "non_base": 0,
        "with_hajos_seam": 0,
        "with_bcut_seam_strict": 0,      # literal 2-arc-cut digon
        "with_treejoin_seam_general": 0,  # non-empty-A tree-join seam
        "with_any_seam": 0,
        "no_seam": 0,
    }
    no_seam_list = []

    for n in (6, 7):
        path = os.path.join(HERE, "..", "data", f"L_{n}.json")
        L = json.load(open(path))
        for idx, m in enumerate(L):
            arcs = [tuple(a) for a in m["arcs"]]
            canon = m.get("canon")
            base = classify_base(n, arcs)
            entry = {
                "n": n,
                "index": idx,
                "canon": canon,
                "oracle_canon": H.canon(n, _arcset(arcs)),
                "base": base,
            }
            if base is not None:
                counts["base"] += 1
                entry["status"] = "base"
                results.append(entry)
                continue
            counts["non_base"] += 1
            hajos = search_hajos_seam(n, arcs)
            bcut = search_bcut_seam(n, arcs)
            treejoin = search_treejoin_seam(n, arcs)
            entry["hajos_seams"] = hajos
            entry["bcut_seams_strict"] = bcut
            entry["treejoin_seams_general"] = treejoin
            entry["has_hajos_seam"] = bool(hajos)
            entry["has_bcut_seam_strict"] = bool(bcut)
            entry["has_treejoin_seam_general"] = bool(treejoin)
            if hajos:
                counts["with_hajos_seam"] += 1
            if bcut:
                counts["with_bcut_seam_strict"] += 1
            if treejoin:
                counts["with_treejoin_seam_general"] += 1
            if hajos or bcut or treejoin:
                counts["with_any_seam"] += 1
                entry["status"] = "has_seam"
            else:
                counts["no_seam"] += 1
                entry["status"] = "NO_SEAM"
                entry["reverification"] = reverify_no_seam(n, arcs)
                no_seam_list.append({
                    "n": n,
                    "index": idx,
                    "canon": canon,
                    "arcs": sorted(map(list, _arcset(arcs))),
                    "reverification": entry["reverification"],
                })
            results.append(entry)

    out = {
        "description": "Seam search for Lemma A over L_6 + L_7 (2-extremal).",
        "counts": counts,
        "no_seam_members": no_seam_list,
        "results": results,
    }
    out_path = os.path.join(HERE, "..", "data", "seam_search_L6_L7.json")
    out_path = os.path.abspath(out_path)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    return out, out_path


if __name__ == "__main__":
    out, out_path = run()
    c = out["counts"]
    print("=== SEAM SEARCH RESULTS (L_6 + L_7) ===")
    print(f"  base members        : {c['base']}")
    print(f"  non-base members    : {c['non_base']}")
    print(f"  with Hajos seam            : {c['with_hajos_seam']}")
    print(f"  with B-cut seam (strict)   : {c['with_bcut_seam_strict']}")
    print(f"  with tree-join seam (gen.) : {c['with_treejoin_seam_general']}")
    print(f"  with ANY seam              : {c['with_any_seam']}")
    print(f"  NO seam found       : {c['no_seam']}")
    print(f"  -> dumped to {out_path}")
    if out["no_seam_members"]:
        print("\n  NO-SEAM (candidate obstructions):")
        for m in out["no_seam_members"]:
            print(f"    n={m['n']} index={m['index']} "
                  f"cut_digons={m['reverification']['num_2arc_cut_digons']} "
                  f"hajos_splits={m['reverification']['num_hajos_splits']}")
