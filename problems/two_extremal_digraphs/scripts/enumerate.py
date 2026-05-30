#!/usr/bin/env python3
"""
FAST enumerator for the truth set L_n of 2-extremal digraphs (Aboulker-Aubian-Charbit
Conjecture 9.2, arXiv:2304.04690 Section 9).

Strategy (generate-smart, not brute force):
  1. Generate all 2-connected (biconnected) simple graphs G on n vertices with min
     degree >= 2 using nauty's `geng -C -d2`.  (A 2-extremal digraph is Eulerian with
     in=out>=2 at every vertex, so its underlying simple graph is 2-connected with
     every vertex of simple-degree >= 2.)
  2. For each underlying G with edge set E, decide for every edge whether it is a
     DIGON (both arcs) or a SINGLE arc (one direction).  The digon edges contribute 0
     to the Eulerian net balance (out-in) at both endpoints; the single edges form a
     subgraph H = (V, S).  An Eulerian orientation of H (every vertex in=out among
     single arcs) exists iff every vertex has EVEN degree in H.  We enumerate all such
     (digon-subset, Eulerian-orientation) combinations.
  3. Each resulting digraph is tested for 2-extremality (lambda==2, chi_vec==3, strong,
     2-connected) using the validated primitives from the recon seed, and deduped by a
     pynauty directed canonical certificate (networkx VF2 fallback if pynauty missing).

Output: data/L_<n>.json as a JSON list of {"n", "arcs": [[u,v],...], "canon": "<hex>"}.

Correctness gate: |L_3|=1, |L_4|=1, |L_5|=3 must reproduce.
"""

import sys, os, json, time, subprocess, itertools
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

# Orbit reduction is OFF by default (pure-Python orbit keys are a net loss for the
# high-symmetry graphs that dominate); set ORBIT=1 to enable it experimentally.
_USE_ORBIT = os.environ.get("ORBIT", "0") == "1"

# ---- import validated primitives from the recon seed (same directory) ----
sys.path.insert(0, HERE)
from enumerate_2extremal_v0_recon import (  # noqa: E402
    is_strong, is_2connected, is_eulerian_deg, lambda_at_most, lambda_D, chi_vec,
    sym_cycle, is_2extremal, maxflow_unit,
)

# ---------- canonical form: pynauty directed certificate, VF2 fallback ----------
_HAVE_PYNAUTY = False
try:
    import pynauty  # type: ignore
    _HAVE_PYNAUTY = True
except Exception:
    import networkx as nx  # type: ignore


def canon(arcs, n):
    """Return a canonical string for the digraph (n, arcs).  Isomorphic digraphs
    (allowing digons; arc direction respected) get identical strings."""
    if _HAVE_PYNAUTY:
        g = pynauty.Graph(n, directed=True)
        adj = {v: [] for v in range(n)}
        for (u, v) in arcs:
            adj[u].append(v)
        for v in range(n):
            if adj[v]:
                g.connect_vertex(v, adj[v])
        return pynauty.certificate(g).hex()
    # networkx VF2 fallback: bucket by an invariant then a hashable witness.
    # We canonicalise by brute force over the automorphism-reduced label set is
    # expensive; instead use nx.weisfeiler_lehman_graph_hash on the digraph plus
    # a VF2 equivalence-class merge at the call site.  Here we just return a
    # strong invariant; the dedup loop below uses VF2 to confirm.
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    G.add_edges_from((u, v) for (u, v) in arcs)
    return "wl:" + nx.weisfeiler_lehman_graph_hash(G, iterations=4)


def _vf2_isomorphic(a1, a2, n):
    import networkx as nx
    G1 = nx.DiGraph(); G1.add_nodes_from(range(n)); G1.add_edges_from(a1)
    G2 = nx.DiGraph(); G2.add_nodes_from(range(n)); G2.add_edges_from(a2)
    return nx.is_isomorphic(G1, G2)


# ---------- geng: 2-connected simple graphs ----------
def geng_path():
    for cand in ("geng", "nauty-geng"):
        from shutil import which
        p = which(cand)
        if p:
            return p
    raise RuntimeError("nauty geng not found on PATH")


def graph6_to_edges(line, n):
    """Decode a graph6 string (no header) into an edge list and vertex count.
    Implements the standard graph6 format."""
    data = line.strip()
    b = data.encode("ascii")
    # first byte(s) encode n; for n<63 it's a single byte b[0]-63
    if b[0] == 126:
        raise NotImplementedError("n>=63 graph6 not needed here")
    nn = b[0] - 63
    bits = []
    for ch in b[1:]:
        v = ch - 63
        for k in range(5, -1, -1):
            bits.append((v >> k) & 1)
    edges = []
    idx = 0
    for j in range(1, nn):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                edges.append((i, j))
            idx += 1
    return nn, edges


def gen_biconnected_graphs(n):
    """Yield (n, edge_list) for every biconnected simple graph on n vertices with
    min degree >= 2, via geng -C -d2."""
    gp = geng_path()
    proc = subprocess.run([gp, "-C", "-d2", "-q", str(n)],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"geng failed: {proc.stderr}")
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        nn, edges = graph6_to_edges(line, n)
        yield nn, edges


# ---------- Eulerian orientation enumeration for a chosen single-edge set ----------
def eulerian_orientations(single_edges, n):
    """Yield every orientation of `single_edges` (list of {u,v}) such that every
    vertex has in-degree == out-degree among the single arcs.  Prerequisite (checked
    by caller): every vertex has EVEN degree in (V, single_edges).
    net[v] = out(v) - in(v); we orient edges one by one with feasibility pruning."""
    m = len(single_edges)
    incident = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(single_edges):
        incident[u].append(idx)
        incident[v].append(idx)
    # remaining incident edges with index > idx, per vertex
    net = [0] * n
    chosen = [0] * m  # 0 => u->v ; 1 => v->u

    def remaining_after(idx, v):
        return sum(1 for k in incident[v] if k > idx)

    out = []

    def rec(idx):
        if idx == m:
            if all(x == 0 for x in net):
                arcs = []
                for k, (u, v) in enumerate(single_edges):
                    arcs.append((u, v) if chosen[k] == 0 else (v, u))
                out.append(arcs)
            return
        u, v = single_edges[idx]
        for d in (0, 1):
            if d == 0:
                net[u] += 1; net[v] -= 1
            else:
                net[u] -= 1; net[v] += 1
            # feasibility: |net[w]| must be coverable by remaining incident edges
            ok = True
            for w in (u, v):
                if abs(net[w]) > remaining_after(idx, w):
                    ok = False; break
            if ok:
                chosen[idx] = d
                rec(idx + 1)
            if d == 0:
                net[u] -= 1; net[v] += 1
            else:
                net[u] += 1; net[v] -= 1

    rec(0)
    return out


def aut_group_perms(n, edges):
    """Return the FULL automorphism group of the simple graph (n, edges) as a list of
    permutations (tuples).  Uses pynauty generators expanded by BFS closure.  The
    group is small for the graphs we handle, so full expansion is fine.  Falls back to
    [identity] if pynauty is unavailable."""
    ident = tuple(range(n))
    if not _HAVE_PYNAUTY:
        return [ident]
    g = pynauty.Graph(n, directed=False)
    adj = {v: [] for v in range(n)}
    for (u, v) in edges:
        adj[u].append(v)  # undirected: connect_vertex adds both ways internally? no.
    # pynauty undirected: add each neighbour once per endpoint
    nb = {v: set() for v in range(n)}
    for (u, v) in edges:
        nb[u].add(v); nb[v].add(u)
    for v in range(n):
        if nb[v]:
            g.connect_vertex(v, sorted(nb[v]))
    gens, _, _, _, _ = pynauty.autgrp(g)
    gens = [tuple(p) for p in gens]
    group = {ident}
    frontier = [ident]
    while frontier:
        nf = []
        for p in frontier:
            for gpm in gens:
                q = tuple(gpm[p[i]] for i in range(n))
                if q not in group:
                    group.add(q); nf.append(q)
        frontier = nf
        if len(group) > 200000:  # safety cap; graphs here have tiny Aut
            break
    return list(group)


def orbit_canon_key(arclist, perms):
    """Canonical key of an arc set under a group of vertex permutations: the
    lexicographically smallest sorted arc-tuple over all perms.  Cheap pure-Python
    dedup that collapses Aut(G)-equivalent orientations before the global certificate.
    `arclist` is a list of (u,v) tuples (the digraph arcs)."""
    best = None
    for p in perms:
        key = tuple(sorted((p[u], p[v]) for (u, v) in arclist))
        if best is None or key < best:
            best = key
    return best


def orient_digraphs(n, edges):
    """Yield every Eulerian digraph arc-set (frozenset of (u,v)) whose underlying
    simple graph is exactly `edges`, with in=out>=2 at every vertex.
    Each edge is either a digon (both arcs) or a single oriented arc."""
    m = len(edges)
    # For an Eulerian orientation of the single-edge subgraph to exist, every vertex
    # must have even single-degree.  We enumerate single-edge subsets via a recursion
    # that tracks single-degree parity, pruning early.
    deg = [0] * n
    for (u, v) in edges:
        deg[u] += 1; deg[v] += 1

    # We pick subset S = single edges; complement = digons.  Constraint: every vertex
    # has even degree within S.  Then in-degree in the digraph = (single-in) + (#digons
    # incident) and similarly out; with an Eulerian orientation of S, in=out at every v.
    # Total in-degree = out-degree = (single_deg_v)/2 + digon_deg_v.  We need >=2.
    # Since underlying degree deg[v] = single_deg_v + digon_deg_v and single_deg_v even,
    # total arc in-degree = digon_deg_v + single_deg_v/2.  Require >=2 (always true if
    # deg[v]>=2 and ... we still check after orienting via is_eulerian_deg).

    incident = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        incident[u].append(idx)
        incident[v].append(idx)

    sdeg = [0] * n           # running single-degree parity-tracking
    is_single = [False] * m

    def remaining_after(idx, v):
        return sum(1 for k in incident[v] if k > idx)

    results = []

    def pick(idx):
        if idx == m:
            # all vertices must have EVEN single-degree
            if any(sdeg[v] & 1 for v in range(n)):
                return
            single = [edges[k] for k in range(m) if is_single[k]]
            digons = [edges[k] for k in range(m) if not is_single[k]]
            base = []
            for (u, v) in digons:
                base.append((u, v)); base.append((v, u))
            if not single:
                arcs = frozenset(base)
                results.append(arcs)
                return
            for orient in eulerian_orientations(single, n):
                arcs = frozenset(base + orient)
                results.append(arcs)
            return
        # parity pruning: if we make this edge a digon (not single), sdeg unchanged;
        # if single, sdeg of both endpoints flips.  A vertex whose remaining incident
        # edges (after idx) is 0 must already have even sdeg.
        for single in (False, True):
            u, v = edges[idx]
            is_single[idx] = single
            if single:
                sdeg[u] += 1; sdeg[v] += 1
            # prune: any vertex with no remaining incident edges must have even sdeg
            ok = True
            for w in (u, v):
                if remaining_after(idx, w) == 0 and (sdeg[w] & 1):
                    ok = False; break
            if ok:
                pick(idx + 1)
            if single:
                sdeg[u] -= 1; sdeg[v] -= 1

    pick(0)
    return results


def lambda_exactly_2(arcs, n):
    """True iff lambda(D) == 2.  Single pass: any pair flow>2 -> False; track max."""
    best = 0
    for s in range(n):
        for t in range(n):
            if s == t:
                continue
            f = maxflow_unit(arcs, n, s, t)
            if f > 2:
                return False
            if f > best:
                best = f
    return best == 2


# ---------- main enumeration ----------
def enumerate_Ln(n, verbose=True):
    """Streaming, memory-bounded enumeration.

    For each biconnected underlying graph we enumerate Eulerian orientations and apply
    the 2-extremality tests INLINE, cheapest-and-most-selective first, so the vast
    majority of orientations are rejected before any canonicalisation:

        eulerian-deg>=2  ->  strong  ->  lambda==2 (early-exit maxflow)  ->  canon-dedup
                                                                          ->  2conn  ->  chi_vec==3

    `lambda==2` is the dominant filter (almost every dense orientation has some pair with
    >2 arc-disjoint paths and is rejected after the first such pair).  Only the tiny set
    of strong, lambda-2 orientations is canon-deduped and chi_vec-tested, so memory stays
    bounded by |survivors|, not by the full orientation universe.
    """
    t0 = time.time()
    seen = {}           # canon -> sorted arcs (the L_n members)
    survivor_canon = set()   # canon of strong lambda-2 reps already chi_vec-tested
    bucket_arcs = {}    # VF2 fallback
    n_graphs = 0
    n_cands = 0
    n_strong = 0
    n_lam2 = 0
    for (nn, edges) in gen_biconnected_graphs(n):
        n_graphs += 1
        # Optional per-graph orbit reduction under Aut(G) (env ORBIT=1).  It collapses
        # orientations equivalent by a graph automorphism before the per-orientation
        # tests, but in pure Python the lex-min orbit key over large symmetric groups
        # costs more than the maxflow it saves on the dense graphs, so it is OFF by
        # default.  Left in place for experimentation / a future C-accelerated key.
        if _USE_ORBIT:
            perms = aut_group_perms(n, edges)
            if len(perms) > 1:
                local = {}
                for arcs in orient_digraphs(n, edges):
                    k = orbit_canon_key(tuple(arcs), perms)
                    if k not in local:
                        local[k] = arcs
                graph_orients = local.values()
            else:
                graph_orients = orient_digraphs(n, edges)
        else:
            graph_orients = orient_digraphs(n, edges)
        for arcs in graph_orients:
            n_cands += 1
            if not is_eulerian_deg(arcs, n, min_deg=2):
                continue
            if not is_strong(arcs, n):
                continue
            n_strong += 1
            if not lambda_exactly_2(arcs, n):
                continue
            n_lam2 += 1
            # canon-dedup only the (rare) strong lambda-2 reps
            c = canon(arcs, n)
            if _HAVE_PYNAUTY:
                if c in survivor_canon:
                    continue
                survivor_canon.add(c)
            else:
                lst = bucket_arcs.setdefault(c, [])
                if any(_vf2_isomorphic(arcs, a2, n) for a2 in lst):
                    continue
                lst.append(arcs)
                c = c + ":" + str(len(lst))
            if not is_2connected(arcs, n):
                continue
            if chi_vec(arcs, n) != 3:
                continue
            seen[c] = sorted(arcs)
    elapsed = time.time() - t0
    Ln = sorted(seen.items())  # deterministic order by canon
    if verbose:
        print(f"  n={n}: {n_graphs} biconn graphs -> {n_cands} orientations "
              f"-> {n_strong} strong -> {n_lam2} lambda2 "
              f"-> {len(survivor_canon)} unique-survivors -> |L_{n}|={len(Ln)}"
              f"  ({elapsed:.1f}s)", flush=True)
    return Ln  # list of (canon, sorted_arcs)


def dump_Ln(n, Ln):
    os.makedirs(DATA, exist_ok=True)
    objs = []
    for (c, arcs) in Ln:
        objs.append({"n": n, "arcs": [list(a) for a in arcs], "canon": c})
    path = os.path.join(DATA, f"L_{n}.json")
    with open(path, "w") as f:
        json.dump(objs, f, indent=0)
    return path


def main():
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    print(f"# FAST 2-extremal enumerator  (pynauty={_HAVE_PYNAUTY})")
    # sanity: sym C3/C5/C7 are 2-extremal; sym C4 is not
    for c in (3, 5, 7):
        a = sym_cycle(c)
        assert is_2extremal(a, c), f"sym C{c} should be 2-extremal"
    assert not is_2extremal(sym_cycle(4), 4), "sym C4 should NOT be 2-extremal"
    print("# primitive sanity OK (sym C3/C5/C7 extremal, sym C4 not)")

    sizes = {}
    for n in range(lo, hi + 1):
        Ln = enumerate_Ln(n)
        sizes[n] = len(Ln)
        path = dump_Ln(n, Ln)
        print(f"  dumped {path}", flush=True)
    print("# SIZES:", sizes, flush=True)
    # correctness gate
    gate = {3: 1, 4: 1, 5: 3}
    for k, v in gate.items():
        if k in sizes:
            status = "OK" if sizes[k] == v else f"MISMATCH expected {v}"
            print(f"  gate |L_{k}|={sizes[k]} ({status})", flush=True)


if __name__ == "__main__":
    main()
