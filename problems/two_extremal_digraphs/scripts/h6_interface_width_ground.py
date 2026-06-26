"""GROUND the INTERFACE-WIDTH refinement of H6.

Proposal core (asymptotic-argument lens):
  For Eulerian, lambda_D=2 digraphs, consider a DIGON-FREE minimal cut (S,S-bar)
  crossing with exactly 2 fwd + 2 bwd single arcs (type (0,4) underlying).
  CLAIM (refined): if the digraph is 3-CONNECTED (equivalently the digon-free
  cut is NOT a vertex 2-cut, equivalently interface-width >=3 per side), then
  the side-2-dicolourings merge to a global 2-dicolouring => chi_vec=2
  (NOT 2-extremal).
  PREDICTION CONFIRM: every Eulerian lambda=2 3-connected digraph with a
    digon-free (2 fwd + 2 bwd) cut has chi_vec=2.
  PREDICTION KILL: a 3-connected such digraph with chi_vec=3.
  REFINEMENT (the lever pin): chi=3 with a digon-free 2/2 cut occurs ONLY at
    node-connectivity exactly 2 with interface-width 2 on a side.

This script runs STEP A on:
  (1) the truth set L_6 ∪ L_7 (chi=3, in-H2 members),
  (2) hub-cut surgery outputs at n=7 (the k=2 near-miss generator),
and reports, for every member possessing >=1 digon-free 2-fwd/2-bwd cut:
    (chi_vec, is_3connected, node_connectivity, per-side interface widths).
"""
import sys, itertools, json
sys.path.insert(0, 'scripts')
import h2_oracle as H
import hub_cut_surgery as Sg


def digon_free_22_cuts(n, arcs):
    """Enumerate all bipartitions (S, S-bar) (both nonempty) of the vertex set
    such that the crossing arcs are ALL single (no digon crosses) and there are
    exactly 2 forward (S->S-bar) and 2 backward (S-bar->S) single arcs.
    Returns list of dicts: S (frozenset), fwd arcs, bwd arcs, width_S, width_Sbar.
    We deduplicate by taking S as the side containing vertex 0 OR by frozenset
    canonicalization (S, S-bar) symmetric."""
    arcset = set(arcs)
    verts = list(range(n))
    seen = set()
    out = []
    # iterate over subsets S with 0 in S to halve symmetry; require both sides nonempty
    rest = verts[1:]
    for sz in range(0, len(rest) + 1):
        for combo in itertools.combinations(rest, sz):
            S = frozenset((0,) + combo)
            Sbar = frozenset(v for v in verts if v not in S)
            if not Sbar:
                continue
            key = frozenset([S, Sbar])
            if key in seen:
                continue
            seen.add(key)
            fwd = []   # S -> Sbar
            bwd = []    # Sbar -> S
            digon_cross = False
            for (u, v) in arcs:
                if u in S and v in Sbar:
                    if (v, u) in arcset:
                        digon_cross = True
                        break
                    fwd.append((u, v))
                elif u in Sbar and v in S:
                    if (v, u) in arcset:
                        digon_cross = True
                        break
                    bwd.append((u, v))
            if digon_cross:
                continue
            if len(fwd) == 2 and len(bwd) == 2:
                # interface width per side = #distinct endpoints of the 4 crossing arcs on that side
                cross = fwd + bwd
                touch_S = set()
                touch_Sbar = set()
                for (u, v) in cross:
                    if u in S:
                        touch_S.add(u); touch_Sbar.add(v)
                    else:
                        touch_Sbar.add(u); touch_S.add(v)
                out.append(dict(S=S, Sbar=Sbar, fwd=fwd, bwd=bwd,
                                width_S=len(touch_S), width_Sbar=len(touch_Sbar)))
    return out


def node_connectivity(n, arcs):
    """underlying-graph vertex connectivity (min # vertices whose removal
    disconnects or leaves <=1 vertex). small n brute force."""
    adj = [set() for _ in range(n)]
    for (u, v) in arcs:
        adj[u].add(v); adj[v].add(u)

    def connected(removed):
        rem = set(removed)
        start = None
        for x in range(n):
            if x not in rem:
                start = x; break
        if start is None:
            return True
        seen = {start}; stack = [start]
        while stack:
            u = stack.pop()
            for w in adj[u]:
                if w not in rem and w not in seen:
                    seen.add(w); stack.append(w)
        return len(seen) == n - len(rem)

    # complete-ish graph special case
    for k in range(0, n):
        # is there a k-subset whose removal disconnects (and >=2 remain)?
        for rem in itertools.combinations(range(n), k):
            if n - k >= 2 and not connected(rem):
                return k
    return n - 1


def census(members, source):
    """members: list of (n, arcs). For each member that has >=1 digon-free 2/2
    cut, record invariants. Returns rows + summary tallies."""
    rows = []
    for (n, arcs) in members:
        cuts = digon_free_22_cuts(n, arcs)
        if not cuts:
            continue
        # cheap eulerian / lambda / chi gates
        indeg = [0]*n; outdeg = [0]*n
        for (u, v) in arcs:
            outdeg[u]+=1; indeg[v]+=1
        eul = all(indeg[v]==outdeg[v] and outdeg[v]>=2 for v in range(n))
        if not (eul and H.is_strong(n, arcs)):
            continue
        lam = H.lambda_D(n, arcs)
        chi = H.chi_vec(n, arcs)
        kappa = node_connectivity(n, arcs)
        three = (kappa >= 3)
        for c in cuts:
            rows.append(dict(source=source, n=n, lam=lam, chi=chi,
                             kappa=kappa, three=three,
                             width_S=c['width_S'], width_Sbar=c['width_Sbar'],
                             minwidth=min(c['width_S'], c['width_Sbar']),
                             arcs=sorted(arcs)))
    return rows


def load_truth():
    mem = []
    for n in (6, 7):
        d = json.load(open(f'data/L_{n}.json'))
        for rec in d:
            mem.append((rec['n'], [tuple(a) for a in rec['arcs']]))
    return mem


def surgery_outputs(n_wheel):
    """Run hub_cut_surgery generator and collect all candidate digraphs."""
    if n_wheel == 7:
        W = [(0,3),(0,6),(1,5),(1,6),(2,4),(2,6),(3,1),(3,6),(4,0),(4,6),
             (5,2),(5,6),(6,0),(6,1),(6,2),(6,3),(6,4),(6,5)]
        rows, ref = Sg.run_wheel(7, W, hub=6, rim=range(6),
                                 tag="W7 surgery (interface census)", max_add=3)
    else:
        return []
    out = []
    for r in rows:
        out.append((r['n'], [tuple(a) for a in r['arcs']]))
    return out


def main():
    print("="*70)
    print("STEP A: cut census + width split")
    print("="*70)

    truth = load_truth()
    rows_t = census(truth, 'truth_L6L7')
    print(f"\n[TRUTH L6∪L7] members with >=1 digon-free 2/2 cut: "
          f"{len(set(tuple(r['arcs']) for r in rows_t))} digraphs, "
          f"{len(rows_t)} (member,cut) rows")
    # tally
    def tally(rows):
        from collections import Counter
        c = Counter()
        for r in rows:
            c[(r['chi'], r['three'], r['kappa'], r['minwidth'])] += 1
        return c
    print("  (chi, 3conn, kappa, min-interface-width): count")
    for k, v in sorted(tally(rows_t).items()):
        print(f"    {k}: {v}")

    # KEY PREDICTION CHECKS on truth set
    # Refinement: chi=3 digon-free-cut members are all node-conn EXACTLY 2.
    chi3 = [r for r in rows_t if r['chi'] == 3]
    print(f"\n  chi=3 digon-free-2/2-cut rows: {len(chi3)}")
    if chi3:
        kappas = sorted(set(r['kappa'] for r in chi3))
        threes = sorted(set(r['three'] for r in chi3))
        minw = sorted(set(r['minwidth'] for r in chi3))
        print(f"    node-connectivity values among chi=3: {kappas}")
        print(f"    is_3connected among chi=3: {threes}")
        print(f"    min-interface-width among chi=3: {minw}")
    # MAIN PREDICTION: any 3-connected digon-free-2/2-cut row with chi=3?  => KILL
    kill_truth = [r for r in rows_t if r['three'] and r['chi'] == 3]
    print(f"\n  *** MAIN-PREDICTION KILL rows in truth (3conn + digon-free 2/2 cut + chi=3): {len(kill_truth)}")
    for r in kill_truth:
        print(f"    n={r['n']} kappa={r['kappa']} width=({r['width_S']},{r['width_Sbar']}) arcs={r['arcs']}")

    # SECONDARY KILL of refinement: node-conn-2 (NOT 3conn) member with minwidth>=3 yet chi=3
    sec_kill = [r for r in rows_t if (not r['three']) and r['minwidth'] >= 3 and r['chi'] == 3]
    print(f"\n  SECONDARY-KILL rows (kappa<3 but minwidth>=3 and chi=3): {len(sec_kill)}")
    for r in sec_kill:
        print(f"    n={r['n']} kappa={r['kappa']} width=({r['width_S']},{r['width_Sbar']}) arcs={r['arcs']}")

    print("\n" + "="*70)
    print("STEP A on hub-cut surgery outputs (n=7 near-miss generator)")
    print("="*70)
    surg = surgery_outputs(7)
    # dedup
    seen = set(); surg_u = []
    for (n, arcs) in surg:
        key = (n, tuple(sorted(arcs)))
        if key in seen:
            continue
        seen.add(key); surg_u.append((n, arcs))
    print(f"distinct surgery candidates: {len(surg_u)}")
    rows_s = census(surg_u, 'surgery_W7')
    print(f"surgery members with >=1 digon-free 2/2 cut: "
          f"{len(set(tuple(r['arcs']) for r in rows_s))} digraphs, {len(rows_s)} rows")
    print("  (chi, 3conn, kappa, min-interface-width): count")
    for k, v in sorted(tally(rows_s).items()):
        print(f"    {k}: {v}")
    kill_surg = [r for r in rows_s if r['three'] and r['chi'] == 3]
    print(f"\n  *** KILL rows in surgery (3conn + digon-free 2/2 cut + chi=3): {len(kill_surg)}")
    for r in kill_surg:
        print(f"    n={r['n']} kappa={r['kappa']} width=({r['width_S']},{r['width_Sbar']}) lam={r['lam']} arcs={r['arcs']}")

    # any 3-conn surgery row at all with a digon-free 2/2 cut, and what chi?
    three_surg = [r for r in rows_s if r['three']]
    print(f"\n  3-connected surgery rows with digon-free 2/2 cut: {len(three_surg)}; "
          f"chi values: {sorted(set(r['chi'] for r in three_surg))}")

    # OVERALL VERDICT INPUTS
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    all_kill = kill_truth + kill_surg
    print(f"TOTAL MAIN-PREDICTION KILL candidates (3conn + digon-free 2/2 cut + chi=3): {len(all_kill)}")
    print(f"TOTAL SECONDARY-KILL (kappa<3, minwidth>=3, chi=3): {len(sec_kill)}")
    return dict(rows_t=rows_t, rows_s=rows_s, kill_truth=kill_truth,
                kill_surg=kill_surg, sec_kill=sec_kill)


if __name__ == "__main__":
    main()
