"""
H7 INTERFACE-GLUING CENSUS (next_action, D4 frontier).

Goal: build a GENERIC census of 3-connected, lambda_D=2, Eulerian digraphs that
possess a DIGON-FREE 2-fwd/2-bwd cut (the H6 antecedent). For each such digraph
record:
  - the digon-free 2/2 cut (S, Sbar),
  - the 4 crossing-arc endpoints (2 fwd S->Sbar, 2 bwd Sbar->S),
  - the crossing-arc PAIRING pattern into cross-dicycles (nested vs linked),
  - chi_vec(D),
  - WHICH merge of the two side-2-dicolourings (phi_S, phi_Sbar) yields a
    globally proper 2-dicolouring (i.e. confirms chi_vec=2 via a local glue).

Discipline gates obeyed:
  - GENERIC class, NOT hub_cut_surgery / multibase_join_sweep (G13/G14 biased to lambda>=3).
  - We do NOT impose width / connectivity / THIN-THICK levers (G15/G16 dead).
  - A 3-connected lambda=2 Eulerian digraph with a digon-free 2/2 cut AND
    chi_vec=3 would be a STEP-1 / Conj-9.2 candidate counterexample (flag, hand-verify).

GENERATION (generic M-class):
  - choose a digon FOREST F on n vertices with >=2 components (digons = symmetric
    pairs); enumerate forests via random labelled-forest sampling + small exhaustive.
  - add a set of SINGLE arcs that is balanced (in=out at every vertex) so D is
    Eulerian, with min out/in degree >= 2, no parallel single matching a digon,
    such that D is strong. Single arcs decompose into closed trails -> sample
    closed-trail unions (random Eulerian single-arc circulations).
  - filter: strong, underlying-2-connected, node-connectivity>=3, lambda_D==2,
    Eulerian min-deg>=2, and F_D has >=2 components (digon-free cut exists).

This is a SAMPLING census (the full class is huge); we run a bounded budget per n.
"""
import sys, os, itertools, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h2_oracle as H

random.seed(12345)


def _undirected_adj(n, arcs):
    adj = [set() for _ in range(n)]
    for (u, v) in arcs:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def digon_components(n, arcs):
    """Return list of vertex-sets of connected components of the DIGON graph F_D
    (edges = symmetric pairs). Isolated vertices are their own components."""
    arcset = set(arcs)
    adj = [set() for _ in range(n)]
    for (u, v) in arcset:
        if (v, u) in arcset:
            adj[u].add(v)
            adj[v].add(u)
    seen = [False] * n
    comps = []
    for s in range(n):
        if seen[s]:
            continue
        stack = [s]
        seen[s] = True
        comp = set()
        while stack:
            x = stack.pop()
            comp.add(x)
            for y in adj[x]:
                if not seen[y]:
                    seen[y] = True
                    stack.append(y)
        comps.append(comp)
    return comps


def _und_connected(n, adj, removed):
    start = next((v for v in range(n) if v != removed), None)
    if start is None:
        return True
    seen = {start}
    stack = [start]
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if w != removed and w not in seen:
                seen.add(w)
                stack.append(w)
    return len(seen) == n - (1 if removed is not None else 0)


def node_connectivity(n, arcs):
    """Underlying-graph vertex connectivity (exact, small n) via min vertex cut.
    Returns kappa. We only need to know whether kappa>=3, but compute exactly."""
    adj = _undirected_adj(n, arcs)
    if not _und_connected(n, adj, None):
        return 0
    # complete graph special case
    deg_min = min(len(adj[v]) for v in range(n))
    if deg_min == n - 1:
        return n - 1
    # exact kappa = min over removed vertex-subsets that disconnect; brute small n
    # use Whitney-style: try increasing cut sizes
    verts = list(range(n))
    for ksize in range(1, n - 1):
        for cut in itertools.combinations(verts, ksize):
            cutset = set(cut)
            rem = [v for v in verts if v not in cutset]
            if not rem:
                continue
            # connectivity of adj restricted to rem
            start = rem[0]
            seen = {start}
            stack = [start]
            while stack:
                u = stack.pop()
                for w in adj[u]:
                    if w not in cutset and w not in seen:
                        seen.add(w)
                        stack.append(w)
            if len(seen) != len(rem):
                return ksize
    return n - 1


def crossing_arcs(n, arcs, S):
    """Single (non-digon) arcs crossing the cut (S, Sbar)."""
    arcset = set(arcs)
    Sb = set(range(n)) - set(S)
    fwd, bwd = [], []
    for (u, v) in arcset:
        digon = (v, u) in arcset
        if digon:
            continue
        if u in S and v in Sb:
            fwd.append((u, v))
        elif u in Sb and v in S:
            bwd.append((u, v))
    return fwd, bwd


def digon_free_cut(n, arcs, S):
    """True iff no DIGON crosses (S, Sbar)."""
    arcset = set(arcs)
    Sb = set(range(n)) - set(S)
    for (u, v) in arcset:
        if (v, u) in arcset:  # digon
            if (u in S and v in Sb) or (u in Sb and v in S):
                return False
    return True


def find_digon_free_22_cuts(n, arcs):
    """Return list of S (frozenset, |S|<=n/2 representative) giving a digon-free
    cut with exactly 2 fwd single arcs and 2 bwd single arcs, both sides
    nonempty, underlying-connected on each side not required (cut just needs the
    arc pattern). We restrict to cuts that align with a UNION of digon-components
    (a digon-free cut cannot split a digon component)."""
    comps = digon_components(n, arcs)
    if len(comps) < 2:
        return []
    cuts = []
    m = len(comps)
    # enumerate subsets of components (nonempty proper)
    for r in range(1, m):
        for combo in itertools.combinations(range(m), r):
            S = set()
            for ci in combo:
                S |= comps[ci]
            if not digon_free_cut(n, arcs, S):
                continue
            fwd, bwd = crossing_arcs(n, arcs, S)
            if len(fwd) == 2 and len(bwd) == 2:
                key = frozenset(S)
                # dedupe by smaller side
                rep = key if len(key) * 2 <= n else frozenset(set(range(n)) - key)
                cuts.append((rep, fwd, bwd))
    # dedupe
    seen = set()
    out = []
    for rep, fwd, bwd in cuts:
        if rep in seen:
            continue
        seen.add(rep)
        out.append((rep, fwd, bwd))
    return out


def pairing_pattern(S, fwd, bwd):
    """Classify how the 2 fwd + 2 bwd crossing single arcs pair into cross
    structures. fwd=[(a1,b1),(a2,b2)] with a in S, b in Sbar; bwd=[(c1,d1),(c2,d2)]
    with c in Sbar, d in S. We describe the bipartite-ish pairing by the
    multiset of (which-S-endpoint, which-Sbar-endpoint) adjacencies; 'nested' vs
    'linked' encoded by whether the fwd/bwd arcs share endpoints."""
    a = [u for (u, v) in fwd]       # S-side tails of fwd
    bf = [v for (u, v) in fwd]      # Sbar-side heads of fwd
    cb = [u for (u, v) in bwd]      # Sbar-side tails of bwd
    d = [v for (u, v) in bwd]       # S-side heads of bwd
    # endpoint reuse signature
    S_endpoints = a + d
    Sb_endpoints = bf + cb
    sig = (
        len(set(S_endpoints)),   # distinct S-side endpoints among the 4 arcs
        len(set(Sb_endpoints)),  # distinct Sbar-side endpoints
        len(set(a) & set(d)),    # S vertices that are both a fwd-tail and bwd-head
        len(set(bf) & set(cb)),  # Sbar vertices both fwd-head and bwd-tail
    )
    return sig


def side_2colourings(n, arcs, S):
    """All proper 2-dicolourings (functions S->{0,1}) of the induced subdigraph
    D[S], returned as list of dicts (vertex->colour). 2-dicolouring = both colour
    classes acyclic in D[S]."""
    S = sorted(S)
    arcset = set(arcs)
    induced = [(u, v) for (u, v) in arcset if u in S and v in S]
    idx = {v: i for i, v in enumerate(S)}
    k = len(S)
    oadj = {v: [] for v in S}
    for (u, v) in induced:
        oadj[u].append(v)

    def acyclic(colmap):
        for c in (0, 1):
            sub = {v for v in S if colmap[v] == c}
            if H._has_dicycle_in_subset({v: oadj[v] for v in S}, sub):
                return False
        return True
    out = []
    for bits in range(1 << k):
        colmap = {S[i]: (bits >> i) & 1 for i in range(k)}
        if acyclic(colmap):
            out.append(colmap)
    return out


def is_global_proper(n, arcs, colmap):
    """colmap: dict vertex->{0,1} on ALL vertices. Proper iff both colour classes
    acyclic in D."""
    oadj = H.out_adj(n, arcs)
    oadj = {v: oadj[v] for v in range(n)}
    for c in (0, 1):
        sub = {v for v in range(n) if colmap[v] == c}
        if H._has_dicycle_in_subset(oadj, sub):
            return False
    return True


def try_merges(n, arcs, S):
    """Take all side-2-colourings of D[S] and D[Sbar]; for each (phi_S, phi_Sbar)
    pair and each of the 2 colour-swaps on the Sbar side, test global properness.
    Return (n_valid_merges, n_pairs_tried, found_any)."""
    Sb = set(range(n)) - set(S)
    cs_S = side_2colourings(n, arcs, S)
    cs_Sb = side_2colourings(n, arcs, Sb)
    if not cs_S or not cs_Sb:
        return (0, 0, False)
    valid = 0
    tried = 0
    for ps in cs_S:
        for pb in cs_Sb:
            for swap in (0, 1):
                full = dict(ps)
                for v, c in pb.items():
                    full[v] = c ^ swap
                tried += 1
                if is_global_proper(n, arcs, full):
                    valid += 1
    return (valid, tried, valid > 0)


# ---------------------------------------------------------------------------
# GENERIC M-class generator: random digon-forest + random balanced single arcs
# ---------------------------------------------------------------------------

def random_forest_edges(n, n_components):
    """Random spanning forest on n vertices with exactly n_components trees
    (digon edges). Returns set of frozenset edges."""
    verts = list(range(n))
    random.shuffle(verts)
    # partition into n_components nonempty groups
    if n_components > n:
        return None
    cuts = sorted(random.sample(range(1, n), n_components - 1)) if n_components > 1 else []
    groups = []
    prev = 0
    for c in cuts + [n]:
        groups.append(verts[prev:c])
        prev = c
    edges = set()
    for g in groups:
        random.shuffle(g)
        for i in range(1, len(g)):
            j = random.randrange(i)
            edges.add(frozenset((g[i], g[j])))
    return edges


def random_balanced_singles(n, digon_edges, max_trail_arcs, attempts=40):
    """Build a balanced single-arc set (in=out at every vertex) as a union of
    random simple directed cycles, avoiding arcs that coincide with a digon
    edge direction. Returns set of (u,v) single arcs (no symmetric pair)."""
    digon_pairs = set()
    for e in digon_edges:
        a, b = tuple(e)
        digon_pairs.add((a, b))
        digon_pairs.add((b, a))
    singles = set()
    n_cycles = random.randint(2, 4)
    for _ in range(n_cycles):
        L = random.randint(3, min(n, 6))
        nodes = random.sample(range(n), L)
        cyc = list(nodes)
        ok = True
        new = []
        for i in range(L):
            u, v = cyc[i], cyc[(i + 1) % L]
            if (u, v) in digon_pairs or (u, v) in singles or (v, u) in singles:
                ok = False
                break
            new.append((u, v))
        if ok:
            singles.update(new)
    return singles


def gen_candidates(n, budget):
    """Yield (n, arcs) candidates from the generic M-class."""
    for _ in range(budget):
        ncomp = random.randint(2, max(2, n // 2))
        de = random_forest_edges(n, ncomp)
        if de is None:
            continue
        digon_arcs = set()
        for e in de:
            a, b = tuple(e)
            digon_arcs.add((a, b))
            digon_arcs.add((b, a))
        singles = random_balanced_singles(n, de, n)
        arcs = digon_arcs | singles
        # enforce balance/min-deg by oracle filter later
        yield (n, frozenset(arcs))


def census(n, budget):
    found = []        # H6-antecedent members
    flags = []        # chi_vec==3 (would be counterexample candidates)
    seen_canon = set()
    n_anteced = 0
    for (nn, arcs) in gen_candidates(n, budget):
        if not H.is_eulerian_deg(nn, arcs, min_deg=2):
            continue
        if not H.is_strong(nn, arcs):
            continue
        if not H.is_2connected(nn, arcs):
            continue
        comps = digon_components(nn, arcs)
        if len(comps) < 2:
            continue
        if node_connectivity(nn, arcs) < 3:
            continue
        if not H.lambda_at_most(nn, arcs, 2):
            continue
        if H.lambda_D(nn, arcs) != 2:
            continue
        cuts = find_digon_free_22_cuts(nn, arcs)
        if not cuts:
            continue
        c = H.canon(nn, arcs)
        if c in seen_canon:
            continue
        seen_canon.add(c)
        n_anteced += 1
        cv = H.chi_vec(nn, arcs)
        rec = {"n": nn, "arcs": sorted(arcs), "chi_vec": cv,
               "k_components": len(comps), "n_cuts": len(cuts), "cuts": []}
        for (S, fwd, bwd) in cuts:
            sig = pairing_pattern(S, fwd, bwd)
            merge = try_merges(nn, arcs, S)
            rec["cuts"].append({
                "S": sorted(S), "fwd": fwd, "bwd": bwd,
                "pairing_sig": sig,
                "merge_valid_count": merge[0], "merge_tried": merge[1],
                "glue_exists": merge[2],
            })
        if cv == 3:
            flags.append(rec)
        else:
            found.append(rec)
    return found, flags, n_anteced


if __name__ == "__main__":
    import json
    budgets = {6: 60000, 7: 60000, 8: 40000, 9: 20000}
    allfound = []
    allflags = []
    for n in (6, 7, 8, 9):
        f, fl, na = census(n, budgets[n])
        print(f"n={n}: antecedent_members={na}  chi3_FLAGS={len(fl)}  distinct_recorded={len(f)}")
        allfound.extend(f)
        allflags.extend(fl)
    print("=" * 60)
    print(f"TOTAL distinct H6-antecedent (chi=2) members: {len(allfound)}")
    print(f"TOTAL chi_vec=3 FLAGS (candidate counterexamples): {len(allflags)}")
    # H7 invariant mining
    print("-" * 60)
    print("H7: does a valid GLUE merge exist on every cut of every chi=2 member?")
    no_glue = []
    glue_all = True
    pairing_to_glue = {}
    for rec in allfound:
        for cut in rec["cuts"]:
            sig = cut["pairing_sig"]
            ge = cut["glue_exists"]
            pairing_to_glue.setdefault(sig, []).append(ge)
            if not ge:
                glue_all = False
                no_glue.append((rec["n"], rec["arcs"], cut["S"], sig))
    print(f"glue_exists on EVERY cut of EVERY chi=2 member: {glue_all}")
    if no_glue:
        print(f"  NON-LOCAL GLUE FAILURES (chi=2 but no local merge): {len(no_glue)}")
        for x in no_glue[:5]:
            print("   ", x)
    print("-" * 60)
    print("pairing_sig -> glue_exists distribution:")
    for sig, vals in sorted(pairing_to_glue.items()):
        print(f"  sig={sig}: glue_true={sum(vals)}/{len(vals)}")
    if allflags:
        print("=" * 60)
        print("!!! chi_vec=3 FLAGS (HAND-VERIFY is_in_H2 -- candidate Step-1 counterexamples) !!!")
        for rec in allflags:
            print(json.dumps(rec))
    # dump
    out = {"found": allfound, "flags": allflags}
    with open(os.path.join(os.path.dirname(__file__), "..", "data", "h7_census.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print("written data/h7_census.json")
