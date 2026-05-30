#!/usr/bin/env python3
"""
Adversarial audit of docs/proof_minimal_counterexample.md.

Tests each load-bearing STRUCTURAL claim against every member of L_3..L_7,
reusing the sound primitives in h2_oracle.py and seam_invariant.py.

A single failing member kills a "verified n<=7" claim.  We DEFAULT TO SKEPTICAL:
we do not trust the proof's run-log assertions; we recompute everything.
"""
import json
import os
import sys
import itertools

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import h2_oracle as O
import seam_invariant as SI


def load_all():
    members = []  # (n, index, arcs frozenset)
    for n in range(3, 8):
        data = json.load(open(os.path.join(ROOT, "data", f"L_{n}.json")))
        for i, m in enumerate(data):
            members.append((m["n"], i, frozenset(tuple(a) for a in m["arcs"])))
    return members


def is_base(n, arcs):
    return O.is_symmetric_odd_cycle(n, arcs) or O._is_generalised_wheel(n, arcs)


def underlying_adj(n, arcs):
    a = [set() for _ in range(n)]
    for (i, j) in arcs:
        a[i].add(j)
        a[j].add(i)
    return a


def vertex_connectivity_at_least_3(n, arcs):
    """True iff U(D) is 3-connected (no vertex set of size <3 disconnects, n>=4)."""
    adj = underlying_adj(n, arcs)
    if n < 4:
        return False

    def connected_after(removed):
        rem = set(removed)
        start = next((v for v in range(n) if v not in rem), None)
        if start is None:
            return True
        seen = {start}
        st = [start]
        while st:
            x = st.pop()
            for y in adj[x]:
                if y not in rem and y not in seen:
                    seen.add(y)
                    st.append(y)
        return len(seen) == n - len(rem)
    # 3-connected: every pair removal keeps it connected
    for pair in itertools.combinations(range(n), 2):
        if not connected_after(pair):
            return False
    return True


def vertex_2cuts(n, arcs):
    """All vertex pairs {a,b} whose deletion disconnects U(D)."""
    adj = underlying_adj(n, arcs)
    cuts = []
    for pair in itertools.combinations(range(n), 2):
        rem = set(pair)
        start = next((v for v in range(n) if v not in rem), None)
        if start is None:
            continue
        seen = {start}
        st = [start]
        while st:
            x = st.pop()
            for y in adj[x]:
                if y not in rem and y not in seen:
                    seen.add(y)
                    st.append(y)
        if len(seen) != n - 2:
            cuts.append(frozenset(pair))
    return cuts


def digon_forest_degrees(n, arcs):
    dedges, singles = SI.split_digons_singles(n, arcs)
    deg = [0] * n
    for e in dedges:
        a, b = tuple(e)
        deg[a] += 1
        deg[b] += 1
    return deg, dedges, singles


def single_in_out(n, arcs):
    _, singles = SI.split_digons_singles(n, arcs)
    sin = [0] * n
    sout = [0] * n
    for (u, v) in singles:
        sout[u] += 1
        sin[v] += 1
    return sin, sout


def single_arc_cycle_decomp_min_len(n, arcs):
    """Find the minimum-length closed simple directed cycle in the single-arc
    subdigraph, and also test whether the single arcs decompose into simple
    directed cycles (i.e. each vertex has single-in == single-out)."""
    _, singles = SI.split_digons_singles(n, arcs)
    sset = set(singles)
    if not sset:
        return None, True, []
    oadj = [set() for _ in range(n)]
    for (u, v) in singles:
        oadj[u].add(v)
    # min cycle length via BFS-based shortest cycle on single-arc digraph
    INF = float("inf")
    best = INF
    for s in range(n):
        # BFS shortest path from each out-neighbor back to s
        # shortest directed cycle through s
        from collections import deque
        dist = {s: 0}
        dq = deque([s])
        while dq:
            u = dq.popleft()
            for w in oadj[u]:
                if w == s:
                    best = min(best, dist[u] + 1)
                elif w not in dist:
                    dist[w] = dist[u] + 1
                    dq.append(w)
    sin, sout = single_in_out(n, arcs)
    balanced = all(sin[v] == sout[v] for v in range(n))
    return (None if best == INF else best), balanced, singles


# ----------------------------------------------------------------------------
# CLAIM TESTS
# ----------------------------------------------------------------------------

def test_S1_leaf_lemma(members):
    """S1: every digon-forest leaf has single-in == single-out >= 1."""
    fails = []
    for (n, i, arcs) in members:
        if O.is_symmetric_odd_cycle(n, arcs):
            continue  # SOC has no single arcs; the lemma is about non-SOC, but
            # the proof says it holds for every forest leaf via P2+P3+Eulerian.
            # SOC: every vertex is a forest vertex with deg 2, no leaves with
            # single arcs needed.  Skip SOC since it has no single arcs at all.
        deg, dedges, singles = digon_forest_degrees(n, arcs)
        sin, sout = single_in_out(n, arcs)
        for v in range(n):
            if deg[v] == 1:  # leaf of F_D
                if not (sin[v] == sout[v] and sin[v] >= 1):
                    fails.append((n, i, v, sin[v], sout[v]))
    return fails


def test_S1_including_SOC(members):
    """Stronger reading: across ALL members (incl SOC), every forest leaf has
    single-in==single-out>=1.  The proof's run log claims '0 leaves with no
    single arc across all L_3..L_7'."""
    fails = []
    for (n, i, arcs) in members:
        deg, dedges, singles = digon_forest_degrees(n, arcs)
        sin, sout = single_in_out(n, arcs)
        for v in range(n):
            if deg[v] == 1:
                if not (sin[v] == sout[v] and sin[v] >= 1):
                    fails.append((n, i, v, sin[v], sout[v], "SOC" if O.is_symmetric_odd_cycle(n, arcs) else ""))
    return fails


def test_S2_min_trail(members):
    """S2: minimal single trail is a simple directed cycle of length 3,4, or 5;
    no single 2-cycle anywhere; single arcs balanced (decompose into trails)."""
    fails = []
    lens = {}
    for (n, i, arcs) in members:
        if is_base(n, arcs):
            # base may be SOC (no singles) or wheel (singles form rim cycle)
            pass
        minlen, balanced, singles = single_arc_cycle_decomp_min_len(n, arcs)
        if not balanced:
            fails.append((n, i, "single arcs NOT balanced"))
        # 2-cycle of single arcs check
        sset = set(singles)
        for (u, v) in sset:
            if (v, u) in sset:
                fails.append((n, i, f"single 2-cycle {u}->{v}->{u}"))
        if singles and minlen is not None:
            lens.setdefault(minlen, 0)
            lens[minlen] += 1
            if minlen < 3:
                fails.append((n, i, f"min single cycle len {minlen} < 3"))
    return fails, lens


def test_G1_2cut_existence(members):
    """G1: non-base 2-extremal => U(D) NOT 3-connected (has a vertex 2-cut)."""
    fails = []
    counterex_3conn_nonbase = []
    base_3conn = []
    for (n, i, arcs) in members:
        base = is_base(n, arcs)
        three = vertex_connectivity_at_least_3(n, arcs)
        if not base:
            if three:
                counterex_3conn_nonbase.append((n, i))
                fails.append((n, i, "non-base but 3-connected"))
            else:
                cuts = vertex_2cuts(n, arcs)
                if not cuts:
                    fails.append((n, i, "non-base, not 3-conn, but no 2-cut?!"))
        else:
            if three:
                base_3conn.append((n, i))
    return fails, counterex_3conn_nonbase, base_3conn


def test_S4_MC0_no_hajos(members):
    """S4 / 1.2': MC(D)=0 => no Hajos decomposition exists (proved necessity,
    contrapositive).  Also: which non-base members have MC=0."""
    fails = []
    mc0_nonbase = []
    for (n, i, arcs) in members:
        mc = SI.MC(n, arcs)
        haj = any(True for _ in O._hajos_decompositions(n, arcs))
        # proved necessity: hajos merge => MC=1, i.e. MC=0 => no hajos.
        if (not mc) and haj:
            fails.append((n, i, "MC=0 but a hajos decomposition exists -> kills S4"))
        if (not is_base(n, arcs)) and (not mc):
            mc0_nonbase.append((n, i))
    return fails, mc0_nonbase


def test_G2_smallside_2extremal(members):
    """G2 (THE CRUX): for non-base members, is there SOME vertex 2-cut {a,b}
    such that the SMALL side closed with interface digon {a,b} is 2-extremal and
    strictly smaller?  Test the actual decomposition direction.

    For each non-base member, for each vertex 2-cut {a,b}, for each side S,
    build block = D[S u {a,b}] + digon{a,b}, test is_2extremal and < n.
    Report: members where NO 2-cut yields ANY 2-extremal smaller block on its
    small side -> would break G2-as-stated.
    Also report whether the LARGE side is ever simultaneously 2-extremal.
    """
    results = []
    for (n, i, arcs) in members:
        if is_base(n, arcs):
            continue
        cuts = vertex_2cuts(n, arcs)
        per_member = {"n": n, "i": i, "cuts": [], "any_smallside_2extremal": False}
        adj = underlying_adj(n, arcs)
        for cut in cuts:
            a, b = sorted(cut)
            rem = {a, b}
            # components of U(D) - {a,b}
            comps = []
            seen = set(rem)
            for start in range(n):
                if start in seen:
                    continue
                comp = {start}
                seen.add(start)
                st = [start]
                while st:
                    x = st.pop()
                    for y in adj[x]:
                        if y not in rem and y not in comp:
                            comp.add(y)
                            seen.add(y)
                            st.append(y)
                comps.append(comp)
            # sides: each component union {a,b}
            side_info = []
            for comp in comps:
                S = comp | {a, b}
                block = build_block(n, arcs, S, a, b)
                nb = len(S)
                ex = O.is_2extremal(*block) if nb < n else False
                gw = O._is_generalised_wheel(*block) if ex else False
                side_info.append({
                    "size": nb, "strictly_smaller": nb < n,
                    "is_2extremal": bool(ex), "is_gen_wheel": bool(gw),
                })
            # small side = smallest component
            comp_sizes = [len(c) for c in comps]
            small_idx = comp_sizes.index(min(comp_sizes))
            small = side_info[small_idx]
            if small["is_2extremal"] and small["strictly_smaller"]:
                per_member["any_smallside_2extremal"] = True
            per_member["cuts"].append({
                "cut": [a, b], "ncomp": len(comps), "sides": side_info,
            })
        results.append(per_member)
    return results


def build_block(n, arcs, S, a, b):
    """Induced subdigraph on S relabelled to 0..|S|-1, plus interface digon
    {a,b}."""
    S = sorted(S)
    idx = {v: i for i, v in enumerate(S)}
    new = set()
    for (x, y) in arcs:
        if x in idx and y in idx:
            new.add((idx[x], idx[y]))
    new.add((idx[a], idx[b]))
    new.add((idx[b], idx[a]))
    return len(S), frozenset(new)


def test_G2_oracle_confirms(members):
    """Cross-check: does the FULL oracle (is_in_H2) actually certify every
    non-base member?  And does the seam search record a tree-join seam for the
    MC=0 members?  This tests whether the *forward* construction holds, even if
    the *decomposition soundness* (G2) is unproved."""
    rows = []
    for (n, i, arcs) in members:
        if is_base(n, arcs):
            continue
        O.clear_cache()
        in_h2 = O.is_in_H2(n, arcs, _max_internal=3)
        rows.append((n, i, in_h2))
    return rows


def main():
    members = load_all()
    nb = [(n, i) for (n, i, a) in members if not is_base(n, a)]
    print(f"Loaded {len(members)} members; non-base: {len(nb)}")

    print("\n=== S1 leaf lemma (non-SOC) ===")
    f = test_S1_leaf_lemma(members)
    print("FAILS:", f if f else "NONE (survives)")

    print("\n=== S1 leaf lemma (ALL members incl SOC) ===")
    f = test_S1_including_SOC(members)
    print("FAILS:", f if f else "NONE (survives)")

    print("\n=== S2 minimal trail = simple cycle k>=3, no single 2-cycle ===")
    f, lens = test_S2_min_trail(members)
    print("min single-cycle length distribution:", dict(sorted(lens.items())))
    print("FAILS:", f if f else "NONE (survives)")

    print("\n=== G1 non-base => not 3-connected (vertex 2-cut exists) ===")
    f, ce, base3 = test_G1_2cut_existence(members)
    print("non-base 3-connected counterexamples:", ce if ce else "NONE")
    print("base members that ARE 3-connected:", base3)
    print("FAILS:", f if f else "NONE (survives over n<=7)")

    print("\n=== S4 / 1.2' MC=0 => no hajos decomposition (proved direction) ===")
    f, mc0 = test_S4_MC0_no_hajos(members)
    print("non-base MC=0 members:", mc0)
    print("FAILS (MC=0 with hajos):", f if f else "NONE (survives)")

    print("\n=== G2 small-side 2-extremality (decomposition direction) ===")
    res = test_G2_smallside_2extremal(members)
    no_smallside = [(r["n"], r["i"]) for r in res if not r["any_smallside_2extremal"]]
    print(f"non-base members tested: {len(res)}")
    print("members where NO vertex-2-cut gives a 2-extremal STRICTLY-SMALLER small side:",
          no_smallside if no_smallside else "NONE (every non-base has one)")
    # detail: how often is the LARGE side simultaneously 2-extremal (clean split)?
    both_sides = []
    for r in res:
        for c in r["cuts"]:
            sides = c["sides"]
            ex = [s for s in sides if s["is_2extremal"] and s["strictly_smaller"]]
            if len(ex) >= 2:
                both_sides.append((r["n"], r["i"], c["cut"]))
    print("cuts where BOTH sides are 2-extremal & smaller (clean 2-block split):",
          len(both_sides), "examples", both_sides[:5])

    print("\n=== G2 cross-check: full oracle certifies every non-base in H2? ===")
    rows = test_G2_oracle_confirms(members)
    bad = [(n, i) for (n, i, ok) in rows if not ok]
    print(f"non-base certified in H2 by oracle: {sum(1 for _,_,ok in rows if ok)}/{len(rows)}")
    print("NOT certified:", bad if bad else "NONE")

    # Detailed dump for the three MC=0 members for S3 verification
    print("\n=== S3 detail for MC=0 members (7.7,7.14,7.36 expected) ===")
    for r in res:
        if (r["n"], r["i"]) in mc0:
            print(f"  member {r['n']}.{r['i']}:")
            for c in r["cuts"]:
                print(f"    cut {c['cut']} ncomp={c['ncomp']} sides={c['sides']}")


if __name__ == "__main__":
    main()
