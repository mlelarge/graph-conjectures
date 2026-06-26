"""H6 CRITICALITY-BARRIER experiment (next_action PRIMARY, D3).

CLAIM TO TEST (H6): a 3-connected, lambda_D=2, Eulerian digraph whose digon
forest F_D has a digon-free cut (k(F_D) >= 2 components) is necessarily
2-DICOLOURABLE (chi_vec <= 2), hence NOT 2-extremal. Equivalently chi_vec=3
forces F_D connected (k=1).

This script
  (1) GENERATES genuine digon-free-cut outputs by hub-cut surgery on the
      directed wheels W7 (m=6) and W9 (m=8): delete ONE hub-digon (-> k=2)
      or TWO non-adjacent hub-digons (-> k=3), then rebalance Eulerian with
      single arcs (no new digon, no loop, no parallel) over ALL completions.
  (2) FILTERS to the H6 regime: Eulerian (in=out>=2), strong, underlying-2-conn,
      underlying-3-connected, lambda_D == 2, k(F_D) >= 2.
  (3) For every such output computes chi_vec.
        * chi_vec == 3  =>  KILL of H6: a Step-1 counterexample candidate
          (3-conn lambda=2 Eulerian, digon-free cut, chi=3 == 2-EXTREMAL).
          Reported + hand-verify is_in_H2 (oracle incompleteness).
        * chi_vec == 2  =>  CONFIRM, and we EXTRACT an explicit 2-dicolouring.
  (4) EXTRACTS / TESTS the SHARP structural prediction that the cut ITSELF is
      the 2-colouring split: colour each whole F_D component with one of two
      colours (then place the digon-free vertices), search over the 2^{k}
      component-colour assignments for an acyclic-class 2-dicolouring. This is
      the "which side gets which colour as a function of the cut" the proof
      needs to be seeded with. We report whether a *cut-respecting* 2-colouring
      (every digon monochromatic, i.e. colour is constant on each F_D
      component) exists -- the strongest possible form of the lemma.

Run with the project venv from the problem dir:
  .venv/bin/python scripts/h6_criticality_dicolour.py
"""
import sys, os, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import h2_oracle as H


# --------------------------------------------------------------------------
def directed_wheel(m):
    """Standard generalised wheel: hub=m, rim cycle 0->1->...->m-1->0,
    digon hub<->r for every rim r. 2-extremal for odd... actually verified
    2-extremal for m=6 (n=7) and m=8 (n=9)."""
    hub = m
    arcs = set()
    for i in range(m):
        arcs.add((i, (i + 1) % m))
        arcs.add((hub, i)); arcs.add((i, hub))
    return m + 1, sorted(arcs)


def balance(n, arcs):
    ind = [0] * n; outd = [0] * n
    for (u, v) in arcs:
        outd[u] += 1; ind[v] += 1
    return ind, outd


def digon_components(n, arcs):
    """k(F_D) = #components of the digon graph restricted to digon-incident
    vertices; also return the full vertex->component map padding isolated
    (digon-free) vertices as singletons (needed for the cut-colouring test)."""
    arcset = set(arcs)
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(a, b):
        parent[find(a)] = find(b)
    touched = set()
    for (u, v) in arcs:
        if (v, u) in arcset and u < v:
            union(u, v); touched.add(u); touched.add(v)
    if not touched:
        return 0, touched, {v: v for v in range(n)}
    roots = set(find(x) for x in touched)
    comp_of = {v: find(v) for v in range(n)}
    return len(roots), touched, comp_of


def is_3connected(n, arcs):
    adj = [set() for _ in range(n)]
    for (u, v) in arcs:
        adj[u].add(v); adj[v].add(u)
    def connected(removed):
        start = next((x for x in range(n) if x not in removed), None)
        if start is None:
            return True
        seen = {start}; stack = [start]
        while stack:
            u = stack.pop()
            for w in adj[u]:
                if w not in removed and w not in seen:
                    seen.add(w); stack.append(w)
        return len(seen) == n - len(removed)
    if n <= 3:
        return n >= 1 and connected(set())
    for pair in itertools.combinations(range(n), 2):
        if not connected(set(pair)):
            return False
    return True


def gen_completions(n, base_arcs, max_add=3):
    """All sets of <=max_add SINGLE arcs added to base so the result is
    Eulerian (in=out>=2), no new digon, no loop, no parallel."""
    base = set(base_arcs)
    ind, outd = balance(n, base_arcs)
    cands = []
    for u in range(n):
        for v in range(n):
            if u == v or (u, v) in base or (v, u) in base:
                continue
            cands.append((u, v))
    out = []; seen = set()
    for sz in range(1, max_add + 1):
        for combo in itertools.combinations(cands, sz):
            cs = set(combo)
            if any((v, u) in cs for (u, v) in combo):  # internal digon
                continue
            i2 = ind[:]; o2 = outd[:]
            for (u, v) in combo:
                o2[u] += 1; i2[v] += 1
            if all(i2[v] == o2[v] and o2[v] >= 2 for v in range(n)):
                key = frozenset(combo)
                if key in seen:
                    continue
                seen.add(key)
                out.append(list(base_arcs) + list(combo))
    return out


# --------------------------------------------------------------------------
def has_dicycle_in_subset(oadj, subset):
    """True if the induced subdigraph on `subset` contains a directed cycle."""
    sub = set(subset)
    color = {}
    def dfs(u):
        color[u] = 1
        for w in oadj[u]:
            if w not in sub:
                continue
            if color.get(w, 0) == 1:
                return True
            if color.get(w, 0) == 0 and dfs(w):
                return True
        color[u] = 2
        return False
    for v in sub:
        if color.get(v, 0) == 0:
            if dfs(v):
                return True
    return False


def find_2dicolouring(n, arcs):
    """Return an explicit acyclic-class 2-colouring (list of colours in {0,1})
    or None. (Each colour class induces an acyclic subdigraph.)"""
    oadj = H.out_adj(n, arcs)
    classes = [[], []]
    col = [None] * n
    def ok(v, c):
        return not has_dicycle_in_subset(oadj, set(classes[c]) | {v})
    def bt(v):
        if v == n:
            return True
        for c in (0, 1):
            if ok(v, c):
                classes[c].append(v); col[v] = c
                if bt(v + 1):
                    return True
                classes[c].pop(); col[v] = None
        return False
    if bt(0):
        return col[:]
    return None


def cut_respecting_2colouring(n, arcs, comp_of):
    """Test the SHARP H6 prediction: does there exist a 2-colouring that is
    CONSTANT on every F_D component (every digon monochromatic) and whose two
    classes are each acyclic? Search over the 2^{#comp} component assignments.
    Returns (colour-list, comp_assignment) or None."""
    oadj = H.out_adj(n, arcs)
    comps = sorted(set(comp_of[v] for v in range(n)))
    if len(comps) > 18:
        return None  # avoid blow-up; never hit at these n
    idx = {c: i for i, c in enumerate(comps)}
    for bits in range(1 << len(comps)):
        assign = {c: (bits >> idx[c]) & 1 for c in comps}
        col = [assign[comp_of[v]] for v in range(n)]
        c0 = {v for v in range(n) if col[v] == 0}
        c1 = {v for v in range(n) if col[v] == 1}
        if (not has_dicycle_in_subset(oadj, c0)
                and not has_dicycle_in_subset(oadj, c1)):
            return col, assign
    return None


# --------------------------------------------------------------------------
def run(n, wheel_arcs, hub, rim, max_add=4, do_k3=True):
    """Generate genuine digon-free-cut outputs. To create a digon-free cut we
    must REMOVE a set of rim vertices' hub-digons AND re-attach them into their
    OWN digon component (a rim digon among the removed set), so that set becomes
    an F_D component disjoint from the hub component. (Single-deletion leaves the
    rim vertex digon-FREE, which does NOT raise k(F_D); that is why the original
    hub_cut_surgery.py produced 0 k>=2 outputs.)"""
    arcset0 = set(wheel_arcs)
    rows = []
    base_descrs = []  # (base_arcs, label, target_k)
    rl = list(rim)

    # ---- k=2: delete hub-digons of {r,s}; optionally join them by a rim digon
    for i in range(len(rl)):
        for j in range(i + 1, len(rl)):
            r, s = rl[i], rl[j]
            base = [a for a in wheel_arcs
                    if a not in {(r, hub), (hub, r), (s, hub), (hub, s)}]
            base_descrs.append((base, f"cut{{{r},{s}}}", 2))
            if (r, s) not in arcset0 and (s, r) not in arcset0:
                base_descrs.append((base + [(r, s), (s, r)],
                                    f"cut{{{r},{s}}}+digon", 2))

    # ---- k=3: delete hub-digons of three rim vertices and join them into a
    #            single F_D component (a digon path), separate from the hub.
    if do_k3 and len(rl) >= 4:
        for i in range(len(rl)):
            for j in range(i + 1, len(rl)):
                for kk in range(j + 1, len(rl)):
                    r, s, t = rl[i], rl[j], rl[kk]
                    base = [a for a in wheel_arcs if a not in {
                        (r, hub), (hub, r), (s, hub), (hub, s),
                        (t, hub), (hub, t)}]
                    # join s into its own comp with a digon to r OR t
                    add = []
                    if (r, s) not in arcset0 and (s, r) not in arcset0:
                        add = [(r, s), (s, r)]
                    base_descrs.append((base + add,
                                        f"cut{{{r},{s},{t}}}", 3))

    seen_out = set()
    for base, lbl, tgt_k in base_descrs:
        for cand in gen_completions(n, base, max_add=max_add):
            key = frozenset(cand)
            if key in seen_out:
                continue
            seen_out.add(key)
            ind, outd = balance(n, cand)
            eul = all(ind[v] == outd[v] and outd[v] >= 2 for v in range(n))
            if not eul:
                continue
            if not H.is_strong(n, cand):
                continue
            if not H.is_2connected(n, cand):
                continue
            k, touched, comp_of = digon_components(n, cand)
            if k < 2:
                continue  # not a genuine digon-free cut
            three = is_3connected(n, cand)
            lam = H.lambda_D(n, cand)
            # record EVERY genuine digon-free-cut output (3-conn or not) with its
            # lambda, so we can see whether lambda=2 is ever reached at all.
            chi = H.chi_vec(n, cand)
            twoext = H.is_2extremal(n, cand)
            in_regime = (three and lam == 2)
            col = find_2dicolouring(n, cand) if (in_regime and chi == 2) else None
            cutcol = (cut_respecting_2colouring(n, cand, comp_of)
                      if (in_regime and chi == 2) else None)
            rows.append(dict(label=lbl, target_k=tgt_k, kFD=k, lam=lam, chi=chi,
                             three=three, in_regime=in_regime, twoext=twoext,
                             n=n, arcs=sorted(cand), dicol=col, cutcol=cutcol))
    return rows


def report(tag, rows):
    from collections import Counter
    print(f"\n===== {tag} =====")
    print(f"genuine digon-free-cut outputs (Eulerian, strong, 2-conn, k(F_D)>=2): {len(rows)}")
    # joint (3conn, lambda) distribution -- the load-bearing question is whether
    # any 3-connected genuine-cut output reaches lambda=2.
    jd = Counter((r['three'], r['lam']) for r in rows)
    print("  joint (3-connected, lambda_D) distribution:")
    for (th, lam), c in sorted(jd.items()):
        print(f"    3conn={th} lambda={lam}: {c}")
    regime = [r for r in rows if r['in_regime']]  # 3conn AND lambda=2
    print(f"  H6 regime (3-conn AND lambda=2 AND k>=2): {len(regime)}")
    by_k = {}
    for r in regime:
        by_k.setdefault(r['kFD'], []).append(r)
    for k in sorted(by_k):
        sub = by_k[k]
        chi2 = sum(1 for r in sub if r['chi'] == 2)
        chi3 = [r for r in sub if r['chi'] == 3]
        cutok = sum(1 for r in sub if r['chi'] == 2 and r['cutcol'] is not None)
        dicok = sum(1 for r in sub if r['chi'] == 2 and r['dicol'] is not None)
        print(f"    k(F_D)={k}: total={len(sub)}  chi=2:{chi2}  chi=3(KILL):{len(chi3)}"
              f"  cut-respecting-2col:{cutok}/{chi2}  any-2dicol:{dicok}/{chi2}")
        for r in chi3[:5]:
            inh2 = H.is_in_H2(r['n'], r['arcs'])
            print(f"      *** H6-KILL: {r['label']} kFD={r['kFD']} lam={r['lam']} chi=3 "
                  f"is_2extremal={r['twoext']} inH2={inh2}")
            print(f"          arcs={r['arcs']}")
    return regime


def main():
    print("H6 CRITICALITY-BARRIER: digon-free-cut outputs must be chi_vec=2.")

    n7, W7 = directed_wheel(6)
    print(f"\nW7 baseline: 2ext={H.is_2extremal(n7, W7)} lam={H.lambda_D(n7, W7)} "
          f"chi={H.chi_vec(n7, W7)} k(F_D)={digon_components(n7, W7)[0]}")
    rows7 = run(n7, W7, hub=6, rim=range(6), max_add=4, do_k3=True)
    reg7 = report("W7 double-delete digon-free-cut (k=2 and k=3)", rows7)

    n9, W9 = directed_wheel(8)
    print(f"\nW9 baseline: 2ext={H.is_2extremal(n9, W9)} lam={H.lambda_D(n9, W9)} "
          f"chi={H.chi_vec(n9, W9)} k(F_D)={digon_components(n9, W9)[0]}")
    rows9 = run(n9, W9, hub=8, rim=range(8), max_add=4, do_k3=False)
    reg9 = report("W9 double-delete digon-free-cut (k=2 and k=3)", rows9)

    # ---- overall verdict
    from collections import Counter
    all_rows = rows7 + rows9
    regime = reg7 + reg9                       # 3-conn AND lambda=2 AND k>=2
    kills = [r for r in regime if r['chi'] == 3]
    chi2 = [r for r in regime if r['chi'] == 2]
    cut_fail = [r for r in chi2 if r['cutcol'] is None]
    print("\n================ VERDICT ================")
    n_cut = len(all_rows)
    n3 = sum(1 for r in all_rows if r['three'])
    print(f"Total genuine digon-free-cut outputs generated: {n_cut}")
    print(f"  of which 3-connected: {n3}")
    print("  joint (3conn,lambda) over ALL cut outputs:")
    for kk, c in sorted(Counter((r['three'], r['lam']) for r in all_rows).items()):
        print(f"    {kk}: {c}")
    print(f"  H6 regime (3-conn AND lambda=2 AND k>=2): {len(regime)}")
    print(f"    chi=2 (H6 holds): {len(chi2)}")
    print(f"    chi=3 (H6 KILLED, Step-1 counterexample): {len(kills)}")
    print(f"    chi=2 but NO cut-respecting 2-colouring: {len(cut_fail)}")
    print("----------------------------------------")
    if len(regime) == 0:
        print(">>> EMPIRICAL FINDING (CONTRA D3): NO 3-connected genuine digon-free-cut")
        print("    output reaches lambda_D=2 -- every 3-conn k>=2 output has lambda>=3.")
        print("    The D3 claim 'a 3-conn lambda=2 hub-bearing k(F_D)=2 M exists' is NOT")
        print("    reproduced by this generator. If robust, this REVIVES the CONNECTIVITY")
        print("    reading: a digon-free cut forces lambda>=3 (old H5 / lambda>=3 mechanism).")
    elif kills:
        print(">>> H6 REFUTED: a 3-conn lambda=2 k>=2 chi=3 output exists (== 2-extremal).")
        print("    Hand-verify is_in_H2 on the kill list above (oracle incompleteness).")
    else:
        print(">>> H6 SURVIVES in regime: every 3-conn lambda=2 k>=2 output is 2-dicolourable.")
        if not cut_fail:
            print(">>> SHARP FORM HOLDS: cut-respecting 2-colouring exists for all (cut IS the split).")
        else:
            print(f">>> SHARP FORM FAILS on {len(cut_fail)} outputs.")
    ks = sorted(set(r['kFD'] for r in all_rows))
    print(f"k(F_D) values reached among cut outputs: {ks}")
    return all_rows


if __name__ == "__main__":
    main()
