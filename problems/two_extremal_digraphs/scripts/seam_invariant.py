#!/usr/bin/env python3
r"""
seam_invariant.py
=================

Sub-lemma A-prime (toward Conjecture 9.2, arXiv:2304.04690): every 2-extremal
digraph that is neither a symmetric odd cycle nor a generalised wheel admits a
Lemma-A seam --- either

    (a) a directed-Hajos merge vertex, or
    (b) a general (non-empty-A) 2-Hajos tree-join seam.

The seam census (data/seam_search_L6_L7.json) shows that the *number* of digon-
forest components does NOT distinguish the two seam types (ncomp == 2 occurs in
both Hajos-seamed and tree-join-only members).  This file isolates a finer
invariant that DOES distinguish them, computed only from

    F_D    = the digon forest (P2: digons form a forest), and
    the single arcs (P3: single arcs decompose into closed directed trails),

and verifies the predictive rule on every non-base member of L_6 u L_7 (and on
L_3..L_5 for consistency).

--------------------------------------------------------------------------------
THE INVARIANT  (computable from F_D + single arcs)
--------------------------------------------------------------------------------
Let U(D) be the underlying (undirected, simple) graph of D.  Its edges split, by
P2/P3, into

    * forest edges  -- the digons of F_D, and
    * single edges  -- the underlying images of the single arcs (each single arc
                       has its reverse absent, so it contributes a single edge).

Definition (MIXED 2-CUT).  A *mixed 2-cut* of D is a pair (v, e) consisting of a
vertex v and a SINGLE edge e = {a, b} (a, b != v) such that deleting both v and
e disconnects U(D).  Equivalently: e is a bridge of U(D) - v.

Trail-threading reading.  Because D is 2-connected, no vertex alone and no edge
alone is a cut; a mixed 2-cut is the *minimal* mixed obstruction.  Contract every
component (tree) of F_D to a point; the single arcs become the edges of a
multigraph M_D on the forest components.  A single edge e is the second half of a
mixed 2-cut exactly when, on the cycle space carried by the single-arc closed
trails, e is "pinched" against a single articulating vertex v of F_D's contracted
skeleton --- i.e. the single-arc trails thread the forest so that one trail strand
e, together with one vertex v, separates the digraph.  The forest-component count
is blind to this pinch; the mixed 2-cut sees it.

Define the boolean invariant

    MC(D) = 1  iff D has at least one mixed 2-cut.

--------------------------------------------------------------------------------
THE RULE  (conjectural; verified 40/40 on L_6 u L_7 non-base + consistent L_3..5)
--------------------------------------------------------------------------------
For a non-base 2-extremal digraph D (not a symmetric odd cycle, not a generalised
wheel):

    D has a directed-Hajos merge vertex   <=>   MC(D) = 1
    D needs a (non-empty-A) tree-join seam  <=>   MC(D) = 0  (and a W3-style block
                                                  attaches through a 2-vertex
                                                  A-edge interface).

So the predicted seam type is:  Hajos if MC(D)=1, else tree-join.

--------------------------------------------------------------------------------
WHY MC IS THE RIGHT NECESSARY CONDITION FOR A HAJOS MERGE  (proved direction)
--------------------------------------------------------------------------------
PROVED (necessity).  Suppose D = D1 *_v D2 is a directed Hajos join at merge
vertex v: D1, D2 are strictly smaller 2-extremal blocks sharing only v, and the
join replaces a digon... no --- per Def 1.5 the join deletes one arc from each
side and adds the single "join arc".  Concretely (see _hajos_decompositions in
h2_oracle.py) there is a single arc (u,w) of D and a vertex v != u,w such that
removing the underlying edge {u,w} leaves v as an articulation point separating
the S1-side (containing u) from the S2-side (containing w).  Then (v, {u,w}) is a
mixed 2-cut: deleting v disconnects S1\{v} from S2\{v} except through the edge
{u,w}, and deleting that edge too disconnects U(D).  Hence

        D has a directed-Hajos merge vertex  ==>  MC(D) = 1.

This implication is a rigorous theorem (it is exactly the underlying-graph
shadow of the Hajos-join definition).  The CONVERSE (MC(D)=1 ==> the two sides
are genuinely 2-extremal, so a real Hajos seam exists) is the conjectural step;
it is what is verified computationally here for n <= 7.

--------------------------------------------------------------------------------
STATUS OF EACH PIECE
--------------------------------------------------------------------------------
  * MC(D) computable from F_D + single arcs:                       PROVED.
  * Hajos merge vertex  ==>  MC(D)=1  (necessity):                 PROVED.
  * MC(D)=1  ==>  genuine Hajos merge vertex (sufficiency):        CONJECTURAL,
        verified 40/40 on the non-base members of L_6 u L_7 and consistent on
        L_3..L_5 (this script).
  * non-base & MC(D)=0  ==>  tree-join seam exists:                CONJECTURAL,
        verified on the 3 tree-join-only members (this script + oracle).

Empirical agreement for n <= 7 is EVIDENCE, never a proof.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import h2_oracle as O  # noqa: E402


# --------------------------------------------------------------------------
# Core structural primitives (digon forest + single arcs)
# --------------------------------------------------------------------------

def split_digons_singles(n, arcs):
    """Return (digon_edges, single_arcs).

    digon_edges : set of frozenset({u,v}) for each digon (P2: these form F_D).
    single_arcs : list of (u,v) directed single arcs (reverse absent; P3).
    """
    s = set((int(u), int(v)) for (u, v) in arcs)
    digon_edges = set()
    single_arcs = []
    for (u, v) in s:
        if (v, u) in s:
            if u < v:
                digon_edges.add(frozenset((u, v)))
        else:
            single_arcs.append((u, v))
    return digon_edges, single_arcs


def underlying_edges(n, arcs):
    """Simple undirected edge set of U(D) as frozensets."""
    E = set()
    for (u, v) in arcs:
        if u != v:
            E.add(frozenset((int(u), int(v))))
    return E


def _components_minus(n, edges, removed_vertices=(), removed_edges=()):
    """Number of connected components of the simple graph (n vertices, `edges`)
    after deleting the given vertices and edges.  Vertices removed are dropped
    from the count entirely (we count components of the *remaining* vertices)."""
    rv = set(removed_vertices)
    re = set(frozenset(e) for e in removed_edges)
    adj = {v: set() for v in range(n) if v not in rv}
    for e in edges:
        if e in re:
            continue
        a, b = tuple(e)
        if a in rv or b in rv:
            continue
        adj[a].add(b)
        adj[b].add(a)
    seen = set()
    comps = 0
    for start in adj:
        if start in seen:
            continue
        comps += 1
        stack = [start]
        seen.add(start)
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
    return comps


# --------------------------------------------------------------------------
# The invariant: mixed 2-cuts  (vertex v + single edge e)
# --------------------------------------------------------------------------

def mixed_2_cuts(n, arcs):
    """Return the list of mixed 2-cuts (v, frozenset({a,b})).

    (v, e) is a mixed 2-cut iff e is a SINGLE edge and deleting both v and e
    disconnects U(D).  Computed purely from the underlying graph + the
    single/digon split (F_D and the single arcs)."""
    digon_edges, single_arcs = split_digons_singles(n, arcs)
    single_edges = set(frozenset((u, v)) for (u, v) in single_arcs)
    U = underlying_edges(n, arcs)
    out = []
    for v in range(n):
        base = _components_minus(n, U, removed_vertices=(v,))
        for e in single_edges:
            a, b = tuple(e)
            if a == v or b == v:
                continue
            c = _components_minus(n, U, removed_vertices=(v,), removed_edges=(e,))
            if c > base:
                out.append((v, e))
    return out


def MC(n, arcs):
    """Boolean invariant: does D have any mixed 2-cut?"""
    return len(mixed_2_cuts(n, arcs)) > 0


def predicted_seam_type(n, arcs):
    """Return 'hajos' or 'tree-join' per the rule (for a non-base digraph)."""
    return "hajos" if MC(n, arcs) else "tree-join"


# --------------------------------------------------------------------------
# Verification harness
# --------------------------------------------------------------------------

def _parse_oracle_canon(oc):
    head, rest = oc.split("|")
    n = int(head)
    arcs = []
    for tok in rest.split(";"):
        a, b = tok.split(",")
        arcs.append((int(a), int(b)))
    return n, arcs


def actual_seam_type(record):
    if record.get("has_hajos_seam"):
        return "hajos"
    if record.get("has_treejoin_seam_general"):
        return "tree-join"
    return "none"


def verify_L6_L7():
    path = os.path.join(ROOT, "data", "seam_search_L6_L7.json")
    data = json.load(open(path))
    rows = []
    n_ok = 0
    n_total = 0
    mismatches = []
    for r in data["results"]:
        if r["status"] == "base":
            continue
        n, arcs = _parse_oracle_canon(r["oracle_canon"])
        actual = actual_seam_type(r)
        pred = predicted_seam_type(n, arcs)
        mc = mixed_2_cuts(n, arcs)
        ok = (pred == actual)
        n_total += 1
        if ok:
            n_ok += 1
        else:
            mismatches.append((r["n"], r["index"], actual, pred))
        rows.append({
            "n": r["n"], "index": r["index"],
            "actual": actual, "predicted": pred, "ok": ok,
            "MC": len(mc), "mixed_cuts": [(v, sorted(e)) for (v, e) in mc],
        })
    return n_ok, n_total, mismatches, rows


def verify_small_consistency():
    """L_3..L_5: confirm the invariant is consistent with base classification and
    with whether a genuine Hajos decomposition exists."""
    rows = []
    for nn in (3, 4, 5):
        data = json.load(open(os.path.join(ROOT, "data", f"L_{nn}.json")))
        for i, m in enumerate(data):
            n = m["n"]
            arcs = frozenset(tuple(a) for a in m["arcs"])
            soc = O.is_symmetric_odd_cycle(n, arcs)
            gw = O._is_generalised_wheel(n, arcs)
            haj_exists = any(True for _ in O._hajos_decompositions(n, arcs))
            mc = mixed_2_cuts(n, arcs)
            # Consistency claim: MC(D)=1  iff  a Hajos decomposition exists.
            consistent = (len(mc) > 0) == haj_exists
            rows.append({
                "n": nn, "index": i,
                "sym_odd_cycle": soc, "gen_wheel": gw,
                "base": bool(soc or gw),
                "hajos_decomp_exists": haj_exists,
                "MC": len(mc),
                "MC_matches_hajos": consistent,
            })
    return rows


def verify_necessity_direction():
    """PROVED-direction empirical check: every member whose oracle reports a Hajos
    seam must satisfy MC=1, and (contrapositive) every member with MC=0 must lack
    a Hajos seam.  This is the direction we have a proof for; we confirm the data
    never contradicts it."""
    path = os.path.join(ROOT, "data", "seam_search_L6_L7.json")
    data = json.load(open(path))
    violations = []
    for r in data["results"]:
        if r["status"] == "base":
            continue
        n, arcs = _parse_oracle_canon(r["oracle_canon"])
        has_hajos = bool(r.get("has_hajos_seam"))
        mc = MC(n, arcs)
        if has_hajos and not mc:
            violations.append(("hajos-without-MC", r["n"], r["index"]))
    return violations


def main():
    print("=" * 72)
    print("Sub-lemma A-prime seam invariant: MIXED 2-CUT (v, single-edge e)")
    print("=" * 72)

    n_ok, n_total, mismatches, rows = verify_L6_L7()
    print(f"\n[L6 u L7 non-base members]  rule predicts seam type: "
          f"{n_ok}/{n_total} correct")
    hajos_rows = [r for r in rows if r["actual"] == "hajos"]
    tree_rows = [r for r in rows if r["actual"] == "tree-join"]
    print(f"   actual hajos     : {len(hajos_rows)}  "
          f"(all MC>=1: {all(r['MC'] >= 1 for r in hajos_rows)})")
    print(f"   actual tree-join : {len(tree_rows)}  "
          f"(all MC==0: {all(r['MC'] == 0 for r in tree_rows)})")
    if mismatches:
        print("   MISMATCHES:", mismatches)
    print("\n   tree-join-only members (the discriminating cases):")
    for r in tree_rows:
        print(f"     {r['n']}.{r['index']}: actual={r['actual']} "
              f"predicted={r['predicted']} MC={r['MC']}")

    print("\n   per-member table (n.index  actual -> predicted  MC):")
    for r in rows:
        flag = "" if r["ok"] else "   <<< MISMATCH"
        print(f"     {r['n']}.{r['index']:<2} {r['actual']:>9} -> "
              f"{r['predicted']:<9} MC={r['MC']}{flag}")

    print("\n[L3..L5 consistency: MC(D)=1  iff  Hajos decomposition exists]")
    srows = verify_small_consistency()
    all_consistent = all(r["MC_matches_hajos"] for r in srows)
    for r in srows:
        print(f"     L{r['n']}.{r['index']}  base={r['base']:<1} "
              f"hajos_decomp={r['hajos_decomp_exists']:<1} MC={r['MC']} "
              f"consistent={r['MC_matches_hajos']}")
    print(f"   all consistent: {all_consistent}")

    print("\n[PROVED-direction check: no member is Hajos-seamed with MC=0]")
    viol = verify_necessity_direction()
    print(f"   violations: {viol if viol else 'NONE'}")

    overall = (n_total > 0 and n_ok == n_total and not mismatches
               and all_consistent and not viol)
    print("\n" + "=" * 72)
    print(f"OVERALL: {'PASS (40/40 + consistency)' if overall else 'FAIL'}")
    print("=" * 72)
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
