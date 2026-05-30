#!/usr/bin/env python3
"""
Experiment 1 for Aboulker-Aubian-Charbit Conjecture 9.2 (arXiv:2304.04690).

Goal: exhaustively enumerate, up to isomorphism, all 2-EXTREMAL digraphs on
n <= N vertices and report |L_n|, then (Phase 2/3) build an H_2 oracle and
check which enumerated 2-extremals lie in H_2.

Digraphs: loopless, no parallel arcs (digons allowed = both xy and yx).

2-extremal D:
  - biconnected (underlying simple graph 2-connected),
  - strongly connected,
  - lambda(D) = 2   (max over ordered pairs (x,y), x!=y, of local arc-connectivity),
  - chi_vec(D) = 3  (dichromatic number).

Constraints that ALL 2-extremal D satisfy (Lemma 4.1: Eulerian):
  - in-deg(v) == out-deg(v) for every v (Eulerian),
  - all degrees >= 2 (here every vertex has out-deg>=1 by strongness; we impose >=2),
  - strong, 2-connected.

We enumerate Eulerian strong 2-connected digraphs on labeled vertices and dedup
by a canonical form (brute force over permutations for small n -- fine for n<=7
restricted to the Eulerian/strong universe via orderly-ish generation with pruning).

Self-contained: no external deps.
"""

import sys
import itertools
from functools import lru_cache

# ---------- digraph representation ----------
# A digraph on n vertices is a frozenset of arcs (i,j), i!=j.

def vertices(n):
    return range(n)

def out_adj(arcs, n):
    a = [set() for _ in range(n)]
    for (i, j) in arcs:
        a[i].add(j)
    return a

def in_adj(arcs, n):
    a = [set() for _ in range(n)]
    for (i, j) in arcs:
        a[j].add(i)
    return a

# ---------- strong connectivity ----------
def is_strong(arcs, n):
    if n == 0:
        return False
    oadj = out_adj(arcs, n)
    iadj = in_adj(arcs, n)
    def reach(adj, s):
        seen = {s}
        stack = [s]
        while stack:
            u = stack.pop()
            for w in adj[u]:
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        return seen
    return len(reach(oadj, 0)) == n and len(reach(iadj, 0)) == n

# ---------- underlying graph 2-connectivity ----------
def underlying_adj(arcs, n):
    a = [set() for _ in range(n)]
    for (i, j) in arcs:
        a[i].add(j)
        a[j].add(i)
    return a

def is_2connected(arcs, n):
    if n < 3:
        # 2-connected requires >=3 vertices in standard convention; sym C? n>=3
        # For our purposes 2-extremal needs n>=3.
        return False
    adj = underlying_adj(arcs, n)
    # connected?
    def connected(removed):
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
    if not connected(None):
        return False
    # no cut vertex
    for v in range(n):
        if not connected(v):
            return False
    return True

# ---------- Eulerian + degree ----------
def is_eulerian_deg(arcs, n, min_deg=2):
    indeg = [0]*n
    outdeg = [0]*n
    for (i, j) in arcs:
        outdeg[i] += 1
        indeg[j] += 1
    for v in range(n):
        if indeg[v] != outdeg[v]:
            return False
        if outdeg[v] < min_deg:  # out=in, so total degree-in 2*outdeg
            return False
    return True

# ---------- lambda(D): local arc connectivity, max over ordered pairs ----------
def maxflow_unit(arcs, n, s, t):
    """Max arc-disjoint s->t dipaths = max-flow with unit capacities on arcs.
    Simple BFS augmenting (Edmonds-Karp) on the arc set."""
    # build capacity dict on directed arcs; residual handled via two-way map
    cap = {}
    adj = [[] for _ in range(n)]
    def add_edge(u, v, c):
        if (u, v) not in cap:
            cap[(u, v)] = 0
            adj[u].append(v)
        if (v, u) not in cap:
            cap[(v, u)] = 0
            adj[v].append(u)
        cap[(u, v)] += c
    for (i, j) in arcs:
        add_edge(i, j, 1)
    flow = 0
    while True:
        # BFS for augmenting path
        parent = {s: None}
        from collections import deque
        q = deque([s])
        found = False
        while q:
            u = q.popleft()
            if u == t:
                found = True
                break
            for v in adj[u]:
                if v not in parent and cap[(u, v)] > 0:
                    parent[v] = u
                    q.append(v)
        if not found:
            break
        # augment by 1 (unit caps -> bottleneck 1)
        v = t
        while parent[v] is not None:
            u = parent[v]
            cap[(u, v)] -= 1
            cap[(v, u)] += 1
            v = u
        flow += 1
    return flow

def lambda_D(arcs, n):
    best = 0
    for s in range(n):
        for t in range(n):
            if s == t:
                continue
            f = maxflow_unit(arcs, n, s, t)
            if f > best:
                best = f
    return best

def lambda_at_most(arcs, n, k):
    """Return True iff lambda(D) <= k (early-exit)."""
    for s in range(n):
        for t in range(n):
            if s == t:
                continue
            if maxflow_unit(arcs, n, s, t) > k:
                return False
    return True

# ---------- chi_vec(D): dichromatic number ----------
def has_directed_cycle_in_subset(oadj, subset):
    """subset: set of vertices; does induced subdigraph contain a directed cycle?"""
    color = {}  # 0=visiting,1=done
    def dfs(u):
        color[u] = 0
        for w in oadj[u]:
            if w not in subset:
                continue
            c = color.get(w)
            if c == 0:
                return True
            if c is None:
                if dfs(w):
                    return True
        color[u] = 1
        return False
    for v in subset:
        if v not in color:
            if dfs(v):
                return True
    return False

def is_acyclic_class(oadj, classlist):
    return not has_directed_cycle_in_subset(oadj, set(classlist))

def can_dicolor_k(arcs, n, k):
    """True iff chi_vec(D) <= k via backtracking partition into k acyclic classes."""
    oadj = out_adj(arcs, n)
    assign = [-1]*n
    classes = [[] for _ in range(k)]

    def ok_to_add(v, c):
        # adding v to class c: check induced subdigraph on classes[c]+[v] acyclic.
        sub = set(classes[c])
        sub.add(v)
        return not has_directed_cycle_in_subset(oadj, sub)

    def bt(v, used):
        if v == n:
            return True
        # symmetry break: only allow up to (used+1) classes, in order
        limit = min(k, used + 1)
        for c in range(limit):
            if ok_to_add(v, c):
                classes[c].append(v)
                assign[v] = c
                if bt(v + 1, max(used, c + 1)):
                    return True
                classes[c].pop()
                assign[v] = -1
        return False
    return bt(0, 0)

def chi_vec(arcs, n):
    k = 1
    while True:
        if can_dicolor_k(arcs, n, k):
            return k
        k += 1
        if k > n:
            return n  # safety

# ---------- canonical form (brute force over permutations) ----------
def canonical(arcs, n):
    best = None
    arclist = list(arcs)
    for perm in itertools.permutations(range(n)):
        key = tuple(sorted((perm[i], perm[j]) for (i, j) in arclist))
        if best is None or key < best:
            best = key
    return best

def cheap_invariant(arcs, n):
    """Fast isomorphism invariant: per-vertex (digon_deg, single_out, single_in),
    sorted; plus multiset of digon-adjacencies. Used only to BUCKET before the
    expensive full canonical, so two non-isomorphic graphs may share a bucket
    (then full canonical separates them) but isomorphic ones always collide."""
    digon = [0]*n
    so = [0]*n
    si = [0]*n
    arcset = set(arcs)
    for (i, j) in arcs:
        if (j, i) in arcset:
            digon[i] += 1
        else:
            so[i] += 1
            si[j] += 1
    sig = tuple(sorted((digon[v], so[v], si[v]) for v in range(n)))
    return sig

# ---------- 2-extremal test ----------
def is_2extremal(arcs, n):
    if not is_eulerian_deg(arcs, n, min_deg=2):
        return False
    if not is_strong(arcs, n):
        return False
    if not is_2connected(arcs, n):
        return False
    if not lambda_at_most(arcs, n, 2):
        return False
    if lambda_D(arcs, n) != 2:
        return False
    if chi_vec(arcs, n) != 3:
        return False
    return True

# ---------- symmetric odd cycle (base of H_2) ----------
def sym_cycle(n):
    arcs = set()
    for i in range(n):
        j = (i + 1) % n
        arcs.add((i, j))
        arcs.add((j, i))
    return frozenset(arcs)

# ---------- enumeration of candidate Eulerian digraphs ----------
def enumerate_eulerian_strong_2conn(n):
    """
    Enumerate digraphs satisfying Eulerian + min out-deg>=2 + strong + 2-connected,
    deduped by canonical form. We generate by choosing the underlying arc set.

    To keep it tractable we iterate over subsets of the n*(n-1) possible arcs only
    after pruning by an Eulerian-feasible construction: too large for n>=6 if naive
    (2^(n(n-1))). Instead we enumerate over UNDERLYING simple graphs that are
    2-connected, then orient each non-digon edge in all ways consistent with...
    Actually the clean approach: an Eulerian digraph's arc set, restricted to each
    pair {i,j}, is one of: none, i->j, j->i, digon. We need in=out at each vertex.

    For small n we just enumerate all arc-subsets but with heavy pruning:
    we go pair by pair; this is 4^(n choose 2) states which is large.
    n=3: 4^3=64; n=4: 4^6=4096; n=5: 4^10 ~1e6; n=6: 4^15 ~1e9 (too big naive).

    So we do a DFS over pairs assigning a state, pruning with the running degree
    balance feasibility. We only keep canonical reps.
    """
    pairs = list(itertools.combinations(range(n), 2))
    npairs = len(pairs)
    # state per pair: 0 none, 1 i->j, 2 j->i, 3 digon
    # track outdeg-indeg difference per vertex (net = out - in)
    buckets = {}  # cheap_invariant -> list of canonical keys; results stored per bucket
    results = []

    # max remaining contribution to |net| reduction per vertex: each remaining
    # incident pair can change net by at most 1 (i->j adds +1 to i, -1 to j; etc.)
    # We'll just do simple pruning: |net[v]| <= number of remaining pairs incident to v.
    incident = [[] for _ in range(n)]
    for idx, (i, j) in enumerate(pairs):
        incident[i].append(idx)
        incident[j].append(idx)

    net = [0]*n  # out - in

    def remaining_incident(idx, v):
        return sum(1 for k in incident[v] if k > idx)

    chosen = [0]*npairs

    def feasible(idx):
        # after deciding pairs 0..idx, can remaining still zero out all nets?
        for v in range(n):
            rem = remaining_incident(idx, v)
            if abs(net[v]) > rem:
                return False
        return True

    def build_arcs():
        arcs = set()
        for k, (i, j) in enumerate(pairs):
            s = chosen[k]
            if s == 1:
                arcs.add((i, j))
            elif s == 2:
                arcs.add((j, i))
            elif s == 3:
                arcs.add((i, j)); arcs.add((j, i))
        return frozenset(arcs)

    def dfs(idx):
        if idx == npairs:
            if all(x == 0 for x in net):
                arcs = build_arcs()
                # quick degree>=2 (in=out>=2) check before expensive tests
                indeg = [0]*n
                for (a, b) in arcs:
                    indeg[b] += 1
                if any(d < 2 for d in indeg):
                    return
                if not is_strong(arcs, n):
                    return
                if not is_2connected(arcs, n):
                    return
                sig = cheap_invariant(arcs, n)
                bucket = buckets.setdefault(sig, [])
                can = canonical(arcs, n)
                if can in bucket:
                    return
                bucket.append(can)
                results.append(arcs)
            return
        (i, j) = pairs[idx]
        for s in (0, 1, 2, 3):
            chosen[idx] = s
            if s == 1:
                net[i] += 1; net[j] -= 1
            elif s == 2:
                net[i] -= 1; net[j] += 1
            # s==0 and s==3 leave net unchanged
            if feasible(idx):
                dfs(idx + 1)
            # undo
            if s == 1:
                net[i] -= 1; net[j] += 1
            elif s == 2:
                net[i] += 1; net[j] -= 1
        chosen[idx] = 0

    dfs(0)
    return results

def L_n(n):
    """All 2-extremal digraphs on n vertices, deduped by canonical form."""
    cands = enumerate_eulerian_strong_2conn(n)
    out = []
    for arcs in cands:
        # cands already strong+2conn+deg>=2+eulerian. Now lambda and chi_vec.
        if not lambda_at_most(arcs, n, 2):
            continue
        if lambda_D(arcs, n) != 2:
            continue
        if chi_vec(arcs, n) != 3:
            continue
        out.append(arcs)
    return out

# ================= H_2 oracle =================
# Directed Hajos join and 2-Hajos tree join are complex. For Phase 1/3 at small n
# we implement: base = symmetric odd cycles; closure under DIRECTED HAJOS JOIN.
# (2-Hajos tree join with empty A = generalised wheels; we add directed wheels
#  as an additional base family to catch those at small n -- documented below.)
# This gives a SOUND-but-possibly-INCOMPLETE H_2 recognizer: anything it accepts
# is genuinely in H_2 (we only apply real H_2 constructors). If an enumerated
# 2-extremal is REJECTED, it is only a *candidate* counterexample pending the full
# 2-Hajos-tree-join check.

def relabel(arcs, mapping):
    return frozenset((mapping[i], mapping[j]) for (i, j) in arcs)

def directed_hajos_join(D1, n1, D2, n2):
    """Yield all directed Hajos joins of D1 (n1 verts) and D2 (n2 verts).
    Def 1.5: pick arc u->v1 in D1, arc v2->w in D2. Remove uv1 from D1, v2w from D2,
    take disjoint union, identify v1 and v2 into v, add arc u->w.
    Returns list of (arcs, total_n) canonical-deduped."""
    res = set()
    for (u, v1) in D1:
        for (v2, w) in D2:
            # disjoint union: D2 vertices shifted by n1
            # identify v1 (in D1) and v2+n1 (in D2) -> call it v1
            # relabel D2: v2 maps to v1; others to fresh ids
            # build vertex mapping for D2
            shift = n1
            map2 = {}
            nxt = n1
            for x in range(n2):
                if x == v2:
                    map2[x] = v1
                else:
                    map2[x] = nxt
                    nxt += 1
            total = nxt
            a1 = set(D1)
            a1.discard((u, v1))
            a2 = set()
            for (a, b) in D2:
                if (a, b) == (v2, w):
                    continue
                a2.add((map2[a], map2[b]))
            joined = a1 | a2
            joined.add((u, map2[w]))
            # remove accidental loops / keep simple (no parallel by set)
            joined = {(a, b) for (a, b) in joined if a != b}
            res.add((canonical(frozenset(joined), total), total))
    return res

ODD = lambda n: n % 2 == 1

def directed_wheel(m):
    """Generalised wheel = 2-Hajos tree join with A empty:
    hub vertex m, rim vertices 0..m-1 forming a directed cycle 0->1->...->m-1->0,
    and a digon [hub, r] for every rim vertex r.
    (This is a generalised wheel; the star tree T has all edges in B; every
    leaf-to-leaf path uses 2 B-edges = even, so the parity condition holds.)"""
    arcs = set()
    hub = m
    for i in range(m):
        arcs.add((i, (i + 1) % m))      # peripheral directed cycle
        arcs.add((hub, i)); arcs.add((i, hub))  # digon hub<->rim
    return frozenset(arcs), m + 1

def build_H2_up_to(maxn):
    """Bottom-up generate H_2 members (via sym odd cycles + directed Hajos join)
    up to maxn vertices. Returns dict n -> set of canonical forms.
    NOTE: omits 2-Hajos tree joins with non-empty A beyond what directed Hajos
    join produces; this is the documented incompleteness."""
    # store canonical -> n
    members = {}  # canonical_key -> n
    by_n = {n: set() for n in range(3, maxn + 1)}
    # bases: symmetric odd cycles of size 3,5,7,... up to maxn
    frontier = []
    for c in range(3, maxn + 1, 2):
        arcs = sym_cycle(c)
        key = canonical(arcs, c)
        members[key] = c
        by_n[c].add(key)
        frontier.append((arcs, c, key))
    # generalised wheels (2-Hajos tree join, A empty): hub + rim cycle of size m,
    # total m+1 vertices. Only keep those that are actually 2-extremal.
    for m in range(3, maxn):
        arcs, tot = directed_wheel(m)
        if tot > maxn:
            continue
        if not is_2extremal(arcs, tot):
            continue
        key = canonical(arcs, tot)
        if key not in members:
            members[key] = tot
            by_n.setdefault(tot, set()).add(key)
            frontier.append((arcs, tot, key))
    # closure under directed Hajos join: join sizes a + b - 1 (identify 2->1 vertex)
    # total vertices = a + b - 1. Iterate to fixpoint up to maxn.
    changed = True
    # keep a list of (arcs, n) for all known members
    known = []
    for key, n in list(members.items()):
        # reconstruct arcs from key (key is sorted tuple of arcs already canonical)
        known.append((frozenset(key), n))
    while changed:
        changed = False
        new_known = []
        for (D1, n1) in known:
            for (D2, n2) in known:
                tot = n1 + n2 - 1
                if tot > maxn:
                    continue
                for (key, total) in directed_hajos_join(D1, n1, D2, n2):
                    if key not in members:
                        members[key] = total
                        by_n.setdefault(total, set()).add(key)
                        new_known.append((frozenset(key), total))
                        changed = True
        known.extend(new_known)
    return by_n

# ================= main =================
def main():
    maxn = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    print(f"# 2-extremal enumeration, n up to {maxn}")
    # sanity: sym C3, C5, C7 must be 2-extremal
    for c in (3, 5, 7):
        a = sym_cycle(c)
        ext = is_2extremal(a, c)
        print(f"sanity sym C{c}: lambda={lambda_D(a,c)} chi_vec={chi_vec(a,c)} 2extremal={ext}")
    # sym C4 (even) should NOT be 2-extremal (chi_vec=2)
    a4 = sym_cycle(4)
    print(f"sanity sym C4: lambda={lambda_D(a4,4)} chi_vec={chi_vec(a4,4)} 2extremal={is_2extremal(a4,4)}")

    # Build H_2 oracle bottom-up
    print("# building H_2 (sym odd cycles + directed Hajos join) ...")
    h2 = build_H2_up_to(maxn)
    for n in range(3, maxn + 1):
        print(f"  |H2_{n}| (this generator) = {len(h2.get(n, set()))}")

    Lsizes = {}
    not_in_h2 = {}
    import time
    for n in range(3, maxn + 1):
        t0 = time.time()
        Ln = L_n(n)
        Lsizes[n] = len(Ln)
        # check membership in generated H_2
        missing = []
        h2n = h2.get(n, set())
        for arcs in Ln:
            key = canonical(arcs, n)
            if key not in h2n:
                missing.append(arcs)
        not_in_h2[n] = missing
        print(f"|L_{n}| (2-extremal) = {len(Ln)} ; not in generated-H2: {len(missing)} ; ({time.time()-t0:.1f}s)", flush=True)
        if missing:
            for arcs in missing[:10]:
                print(f"    candidate-not-in-genH2 n={n}: {sorted(arcs)}", flush=True)
    print("# SUMMARY", flush=True)
    print("Lsizes:", Lsizes, flush=True)
    print("not_in_generatedH2 counts:", {n: len(v) for n, v in not_in_h2.items()}, flush=True)

if __name__ == "__main__":
    main()
