"""HUB-PRESERVING DIGON-CUT SURGERY on the wheel W_n.

Attacks open_crux Step 1 via H5 (HUB-BARRIER) in the hub + k(F_D)>=2 regime.

Procedure (n=7 wheel, hub=6):
  baseline W7 (2-extremal, lambda=2, chi=3, k(F_D)=1, hub capdeg 12).
  For each rim r in 0..5:
    delete the hub-digon {(r,6),(6,r)} -> base. This splits F_D into k=2
    components {r} and the rest, while keeping the hub (capdeg 12 -> 10).
    Deleting the digon creates deficits: at r out-deg-1, in-deg-1;
    at 6 in-deg-1, out-deg-1. Restore Eulerian balance by adding single arcs:
      one arc r->x (x'!=... ) and x->6 wouldn't be balanced; do it properly:
      lost: out-arc r->6 and in-arc 6 from r ; and in-arc r<-6 and out-arc 6->r.
    Net deficits after removing both (r,6) and (6,r):
       r: out -1, in -1
       6: out -1, in -1
    Restore by adding TWO single arcs forming balanced compensation:
       add (r->a) and (b->r)  to fix r's out/in,
       add (c->6) and (6->d)  to fix 6's out/in,
    BUT that adds 4 arcs and over-balances a,b,c,d. Better: a single arc that
    serves r's out-deficit AND 6's in-deficit at once is (r->6) again (the digon).
    So we route through the existing structure: enumerate all pairs of single
    arcs {p->q, s->t} whose addition restores in=out at every vertex with
    in=out>=2 and no new digon. We do this by solving the balance directly.

We enumerate over ALL ordered single-arc completions (1 or 2 arcs) that
re-balance the digraph, reject loops/parallels/new-digons, and call the oracle.
Also a dual surgery: delete a rim single arc, add a hub-digon to a new vertex.
"""
import sys, itertools
sys.path.insert(0, 'scripts')
import h2_oracle as H


def digon_components(n, arcs):
    """Union-find on the digon graph F_D; return number of components among
    vertices that touch at least one digon, plus full partition counting
    isolated digon-free vertices each as their own comp? We count k(F_D)
    as #components of the digon graph restricted to vertices incident to a
    digon (standard F_D)."""
    arcset = set(arcs)
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        parent[find(a)] = find(b)
    touched = set()
    for (u, v) in arcs:
        if (v, u) in arcset and u < v:
            union(u, v)
            touched.add(u); touched.add(v)
    if not touched:
        return 0, touched
    roots = set(find(x) for x in touched)
    return len(roots), touched


def capdeg(n, arcs):
    """capacity-degree: each digon contributes 2 (one each dir doubled?),
    here we use out-capacity = #single-out + 2*#digon-out as in M-multigraph.
    Simpler: capdeg(v) = (#arcs incident counting digon edges doubled).
    We use the M-multigraph degree: digon -> 2 edges, single arc -> 1 edge."""
    arcset = set(arcs)
    cap = [0] * n
    seen = set()
    for (u, v) in arcs:
        if (v, u) in arcset:
            # digon -> contributes weight-2 edge between u,v (count once per ordered? )
            # M doubles digons: undirected edge of multiplicity 2.
            if (min(u, v), max(u, v)) not in seen:
                seen.add((min(u, v), max(u, v)))
                cap[u] += 2; cap[v] += 2
        else:
            cap[u] += 1; cap[v] += 1
    return cap


def is_3connected(n, arcs):
    """underlying-graph 3-connectivity by 2-vertex-removal test (DFS), n small."""
    adj = [set() for _ in range(n)]
    for (u, v) in arcs:
        adj[u].add(v); adj[v].add(u)
    def connected(removed):
        start = None
        for x in range(n):
            if x not in removed:
                start = x; break
        if start is None:
            return True
        seen = {start}
        stack = [start]
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


def balance(n, arcs):
    indeg = [0] * n; outdeg = [0] * n
    for (u, v) in arcs:
        outdeg[u] += 1; indeg[v] += 1
    return indeg, outdeg


def analyze(n, arcs, label):
    arcset = set(arcs)
    indeg, outdeg = balance(n, arcs)
    eul = all(indeg[v] == outdeg[v] and outdeg[v] >= 2 for v in range(n))
    strong = H.is_strong(n, arcs)
    two = False; lam = None; chi = None
    # only compute expensive invariants if cheap gates pass-ish (still compute lam/chi for data)
    if eul and strong and H.is_2connected(n, arcs):
        lam = H.lambda_D(n, arcs)
        chi = H.chi_vec(n, arcs)
        two = (lam == 2 and chi == 3)
    else:
        # still try to get lambda/chi for histogram if Eulerian (lambda_D needs strong-ish)
        if eul and strong:
            lam = H.lambda_D(n, arcs)
    k, touched = digon_components(n, arcs)
    cap = capdeg(n, arcs)
    hub = max(cap) if cap else 0
    return dict(label=label, eul=eul, strong=strong, lam=lam, chi=chi,
                two=two, kFD=k, hub=hub, n=n, arcs=sorted(arcs))


def gen_completions(n, base_arcs, max_add=4, allow_digon=False):
    """Enumerate sets of <=max_add SINGLE arcs to add to base so the result is
    Eulerian (in=out, >=2) with no new digon (unless allow_digon), no loop,
    no parallel. The base (after a hub-digon deletion) typically has one rim
    vertex r at in=out=1 (deficit +1/+1) and the hub at in=out=5. A balanced
    single-arc completion must restore in=out>=2 everywhere WITHOUT recreating
    the deleted digon. Brute-force over candidate single arcs, pick subsets
    that re-balance."""
    base = set(base_arcs)
    indeg, outdeg = balance(n, base_arcs)
    cands = []
    for u in range(n):
        for v in range(n):
            if u == v:
                continue
            if (u, v) in base:
                continue
            if (not allow_digon) and (v, u) in base:  # would create digon
                continue
            cands.append((u, v))
    results = []
    seen_sets = set()
    for sz in range(1, max_add + 1):
        for combo in itertools.combinations(cands, sz):
            cs = set(combo)
            # no internal digon among added (unless allowed)
            ok = True
            if not allow_digon:
                for (u, v) in combo:
                    if (v, u) in cs:
                        ok = False; break
            if not ok:
                continue
            ind = indeg[:]; outd = outdeg[:]
            for (u, v) in combo:
                outd[u] += 1; ind[v] += 1
            if all(ind[v] == outd[v] and outd[v] >= 2 for v in range(n)):
                key = frozenset(combo)
                if key in seen_sets:
                    continue
                seen_sets.add(key)
                results.append(list(base_arcs) + list(combo))
    return results


def run_wheel(n, arcs, hub, rim, tag, max_add=4):
    print(f"\n===== {tag} (n={n}, hub={hub}) =====")
    base_ok = H.is_2extremal(n, arcs)
    print(f"baseline 2extremal={base_ok} lambda={H.lambda_D(n,arcs)} chi={H.chi_vec(n,arcs)} k(F_D)={digon_components(n,arcs)[0]} hubcap={max(capdeg(n,arcs))}")
    rows = []
    refutes = []
    rimlist = list(rim)
    for r in rimlist:
        # ---- surgery A: delete hub-digon (r,hub),(hub,r); rebalance via single arcs
        base = [a for a in arcs if a not in {(r, hub), (hub, r)}]
        comps = gen_completions(n, base, max_add=max_add)
        for cand in comps:
            res = analyze(n, cand, f"A r={r}")
            res['cut_rim'] = r; res['surgery'] = 'A-singles'
            res['added'] = sorted(set(cand) - set(base))
            rows.append(res)
            if res['two'] and res['kFD'] >= 2:
                refutes.append(res)
        # ---- surgery B: delete hub-digon (r,hub),(hub,r) AND add a rim digon
        # (r,s) for each other rim s, to keep r in F_D as a SEPARATE component;
        # then rebalance the residual deficits (at s and hub) with single arcs.
        for s in rimlist:
            if s == r:
                continue
            if (r, s) in set(arcs) or (s, r) in set(arcs):
                continue  # already adjacent
            base2 = base + [(r, s), (s, r)]  # new rim digon -> r,s each +1 in/+1 out
            comps2 = gen_completions(n, base2, max_add=max_add)
            for cand in comps2:
                res = analyze(n, cand, f"B r={r} s={s}")
                res['cut_rim'] = r; res['surgery'] = f'B-digon({r},{s})'
                res['added'] = sorted(set(cand) - set(arcs))
                rows.append(res)
                if res['two'] and res['kFD'] >= 2:
                    refutes.append(res)
    return rows, refutes


def histogram(rows):
    """For every False (not 2-extremal) candidate, record which gate fails,
    split by whether the new k=2 cut is digon-free (kFD>=2)."""
    hist = {}
    for r in rows:
        if r['two']:
            continue
        # determine failure mode
        if not r['eul']:
            mode = 'eulerian'
        elif not r['strong']:
            mode = 'strong'
        elif r['lam'] is not None and r['lam'] != 2:
            mode = f"lambda={r['lam']}"
        elif r['chi'] is not None and r['chi'] != 3:
            mode = f"chi={r['chi']}"
        else:
            mode = 'other/2conn'
        split = 'kFD>=2' if r['kFD'] >= 2 else 'kFD<2'
        hist[(mode, split)] = hist.get((mode, split), 0) + 1
    return hist


def main():
    W7 = [(0,3),(0,6),(1,5),(1,6),(2,4),(2,6),(3,1),(3,6),(4,0),(4,6),
          (5,2),(5,6),(6,0),(6,1),(6,2),(6,3),(6,4),(6,5)]
    all_rows = []
    all_ref = []
    rows, ref = run_wheel(7, W7, hub=6, rim=range(6), tag="W7 hub-digon-cut surgery", max_add=3)
    all_rows += rows; all_ref += ref
    print(f"candidates generated: {len(rows)}")
    h = histogram(rows)
    print("FAILURE-MODE HISTOGRAM (mode, kFD-split): count")
    for k in sorted(h, key=lambda x: (-h[x], str(x))):
        print(f"  {k}: {h[k]}")
    n2 = sum(1 for r in rows if r['two'])
    print(f"2-extremal outputs: {n2}")
    k2 = sum(1 for r in rows if r['kFD'] >= 2)
    print(f"outputs with kFD>=2: {k2}")
    # report 2-extremal ones regardless of kFD
    for r in rows:
        if r['two']:
            print(f"  2EXTREMAL output: cut_rim={r['cut_rim']} added={r['added']} kFD={r['kFD']} hubcap={r['hub']} lam={r['lam']} chi={r['chi']}")

    if all_ref:
        print("\n*** REFUTES-H5 candidates (2-extremal AND kFD>=2): ***")
        for r in all_ref:
            three = is_3connected(r['n'], r['arcs'])
            inh2 = H.is_in_H2(r['n'], r['arcs'])
            print(f"  cut_rim={r['cut_rim']} added={r['added']} kFD={r['kFD']} hubcap={r['hub']} 3conn={three} inH2={inh2}")
            print(f"    arcs={r['arcs']}")
    else:
        print("\nNo REFUTES-H5 candidate at n=7 (no 2-extremal output with kFD>=2).")

    return all_rows, all_ref


if __name__ == "__main__":
    main()
