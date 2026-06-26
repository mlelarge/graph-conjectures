#!/usr/bin/env python3
"""
Eulerian-pruned search for 2-extremal orientations of a fixed underlying graph,
plus the experiments cited in `docs/planarity_of_2extremal.md` and
`docs/conjecture_p_proof_attempt.md`:

  * K5 / K3,3 admit no 2-extremal orientation (disproof of "small non-planar");
  * which 3-connected graphs admit a 2-extremal orientation, and whether every
    such orientation is a GENERALISED WHEEL (NOT necessarily a classical wheel --
    non-star empty-A generalised wheels are 3-connected too, e.g. the n=10
    3-regular example);
  * sparse non-planar graphs admit none (the 2-extremal => planar disproof sweep).

Why Eulerian pruning.  A 2-extremal digraph is Eulerian, so for a fixed underlying
graph G an orientation is feasible only if the single-arc part is an Eulerian
orientation of G minus the digon edges.  Naive 3^|E| enumeration wastes almost all
its time on non-Eulerian assignments and was only able to CAP (not certify) dense
cases.  Here we enumerate exactly:
    Dig  (digon edge set)  ranges over  { D : deg_D(v) == deg_G(v) (mod 2) }
        = a coset of the cycle space (fundamental cycles of a spanning tree),
    then the single edges  G - Dig  (all even degrees) get every Eulerian
    orientation (backtracking on out-degree budgets).
This is exact and far smaller, so it CERTIFIES the previously-capped cases.

Requires networkx (root .venv) for planarity / connectivity:
    PYTHONPATH=problems/two_extremal_digraphs/scripts \
      .venv/bin/python problems/two_extremal_digraphs/scripts/planarity_search.py
"""

import argparse
import itertools
import os
import sys
from shutil import which

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import h2_oracle as H  # noqa: E402

try:
    import networkx as nx
except Exception:  # pragma: no cover
    nx = None


def geng_path():
    for cand in ("geng", "nauty-geng"):
        p = which(cand)
        if p:
            return p
    raise RuntimeError("nauty geng not found on PATH (install nauty)")


# --------------------------------------------------------------------------
# Eulerian-pruned enumeration of 2-extremal orientations of a graph G.
# G is given as (n, list of undirected edges (u,v), u<v).
# --------------------------------------------------------------------------

def _digon_cosets(n, edges):
    """Yield every edge-subset `Dig` (as a frozenset of edge indices) with
    deg_Dig(v) == deg_G(v) (mod 2) for all v.  These are exactly the digon
    edge-sets that leave G-Dig with all-even degrees."""
    m = len(edges)
    inc = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        inc[u].append(i)
        inc[v].append(i)
    deg = [len(inc[v]) for v in range(n)]
    # spanning forest
    parent_edge = [-1] * n
    parent = [-1] * n
    seen = [False] * n
    order = []
    tree_edges = set()
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        stack = [s]
        while stack:
            x = stack.pop()
            order.append(x)
            for (y, ei) in adj[x]:
                if not seen[y]:
                    seen[y] = True
                    parent[y] = x
                    parent_edge[y] = ei
                    tree_edges.add(ei)
                    stack.append(y)
    non_tree = [i for i in range(m) if i not in tree_edges]
    # base T-join Dig0: make G-Dig0 even.  Process vertices leaf-up: a vertex
    # whose current parity (deg + incident Dig0) is odd pushes its parent edge.
    target = [deg[v] % 2 for v in range(n)]  # want deg_{G-Dig}(v) even -> deg_Dig(v) == deg[v] (mod2)
    in_dig0 = [False] * m
    cur_par = [0] * n
    for x in reversed(order):
        if parent[x] == -1:
            continue
        need = (target[x] + cur_par[x]) % 2  # deg_Dig0(x) must == target[x] mod 2
        if need:
            ei = parent_edge[x]
            in_dig0[ei] = True
            cur_par[x] ^= 1
            cur_par[parent[x]] ^= 1
    dig0 = frozenset(i for i in range(m) if in_dig0[i])
    # fundamental cycles for non-tree edges -> even-subgraph basis
    cycles = []
    for nt in non_tree:
        u, v = edges[nt]
        # path u..v in tree
        pu = set()
        x = u
        anc = {u: None}
        while parent[x] != -1:
            anc[parent[x]] = parent_edge[x]
            x = parent[x]
        # walk v up until meeting an ancestor of u
        path_edges = {nt}
        x = v
        seen_v = {}
        y = v
        chain = []
        while y != -1:
            chain.append(y)
            y = parent[y]
        chainset = set(chain)
        # LCA: first vertex on u's upward path that is in chainset
        x = u
        up_u = []
        while x not in chainset and parent[x] != -1:
            up_u.append(parent_edge[x])
            x = parent[x]
        lca = x
        for e in up_u:
            path_edges.add(e)
        y = v
        while y != lca:
            path_edges.add(parent_edge[y])
            y = parent[y]
        cycles.append(frozenset(path_edges))
    k = len(cycles)
    for bits in itertools.product((0, 1), repeat=k):
        dig = set(dig0)
        for b, cyc in zip(bits, cycles):
            if b:
                dig ^= cyc
        yield frozenset(dig)


def _eulerian_orientations(n, single_edges):
    """Yield every orientation of `single_edges` (list of (u,v)) with
    out-degree == in-degree at each vertex.  Backtracking on out budgets."""
    inc = [[] for _ in range(n)]
    for i, (u, v) in enumerate(single_edges):
        inc[u].append(i)
        inc[v].append(i)
    deg = [len(inc[v]) for v in range(n)]
    if any(d % 2 for d in deg):
        return
    budget = [d // 2 for d in deg]  # required out-degree at each vertex
    m = len(single_edges)
    orient = [None] * m
    # remaining incident undecided edges per vertex
    rem = [deg[v] for v in range(n)]

    def bt(i):
        if i == m:
            yield tuple(orient)
            return
        u, v = single_edges[i]
        for tail in (u, v):
            head = v if tail == u else u
            if budget[tail] <= 0:
                continue
            budget[tail] -= 1
            rem[u] -= 1
            rem[v] -= 1
            # feasibility: each endpoint still able to meet its out budget
            ok = budget[tail] <= rem[tail] and budget[head] <= rem[head]
            if ok:
                orient[i] = (tail, head)
                yield from bt(i + 1)
            budget[tail] += 1
            rem[u] += 1
            rem[v] += 1

    yield from bt(0)


def two_extremal_orientations(n, edges, limit=None):
    """Yield arc-sets of all 2-extremal orientations of G=(n,edges). Exact."""
    count = 0
    for dig in _digon_cosets(n, edges):
        digon_edges = [edges[i] for i in dig]
        single_idx = [i for i in range(len(edges)) if i not in dig]
        singles = [edges[i] for i in single_idx]
        # min-degree-2 quick prune: in=out=deg_Dig(v)+deg_singles(v)/2 >= 2
        degdig = [0] * n
        for (u, v) in digon_edges:
            degdig[u] += 1
            degdig[v] += 1
        degsin = [0] * n
        for (u, v) in singles:
            degsin[u] += 1
            degsin[v] += 1
        if any(degdig[v] + degsin[v] // 2 < 2 for v in range(n)):
            continue
        base = set()
        for (u, v) in digon_edges:
            base.add((u, v))
            base.add((v, u))
        for orient in _eulerian_orientations(n, singles):
            arcs = set(base)
            arcs.update(orient)
            arcs = frozenset(arcs)
            if H.is_2extremal(n, arcs):
                count += 1
                yield arcs
                if limit and count >= limit:
                    return


def _edges_of(G):
    return [tuple(sorted(e)) for e in G.edges()]


# --------------------------------------------------------------------------
# Experiments
# --------------------------------------------------------------------------

def exp_k5_k33():
    print("# K5 / K3,3 : 2-extremal orientations (Eulerian-pruned, exact)")
    for name, G in [("K5", nx.complete_graph(5)),
                    ("K33", nx.complete_bipartite_graph(3, 3))]:
        n = G.number_of_nodes()
        c = sum(1 for _ in two_extremal_orientations(n, _edges_of(G)))
        print(f"  {name}: 2-extremal orientations = {c}  "
              f"(planar={nx.check_planarity(G)[0]})", flush=True)


def exp_three_connected(nmax=7):
    import subprocess
    GENG = geng_path()
    print("# 3-connected graphs: which admit a 2-extremal orientation, and is "
          "EVERY such orientation a generalised wheel?  (Eulerian-pruned, exact)")
    for n in range(5, nmax + 1):
        out = subprocess.run([GENG, "-C", str(n)], capture_output=True,
                             text=True).stdout
        tot = admit = nongw = 0
        nongw_examples = []
        for line in out.splitlines():
            G = nx.from_graph6_bytes(line.strip().encode())
            if nx.node_connectivity(G) < 3:
                continue
            tot += 1
            ori = list(two_extremal_orientations(n, _edges_of(G)))
            if not ori:
                continue
            admit += 1
            # every 2-extremal orientation of this graph a generalised wheel?
            if not all(H._is_generalised_wheel(n, a) for a in ori):
                nongw += 1
                nongw_examples.append(line.strip())
        flag = "" if nongw == 0 else "   <-- NON-generalised-wheel admitting!"
        print(f"  n={n}: 3-connected={tot}  admit-2extremal={admit}  "
              f"admit-but-not-all-gen-wheel={nongw}{flag}", flush=True)
        for g6 in nongw_examples[:3]:
            print(f"      {g6}", flush=True)


def exp_sparse_nonplanar(nmax=8):
    import subprocess
    GENG = geng_path()
    print("# non-planar 2-connected graphs: any 2-extremal orientation? "
          "(would disprove Conj 9.2)  (Eulerian-pruned, exact)")
    for n in range(7, nmax + 1):
        emax = 2 * n + 2
        out = subprocess.run([GENG, "-C", "-d2", str(n), f"9:{emax}"],
                             capture_output=True, text=True).stdout
        npc = found = 0
        for line in out.splitlines():
            G = nx.from_graph6_bytes(line.strip().encode())
            if nx.check_planarity(G)[0]:
                continue
            npc += 1
            for a in two_extremal_orientations(n, _edges_of(G), limit=1):
                found += 1
                print(f"  !!! COUNTEREXAMPLE n={n}: {sorted(a)}")
        print(f"  n={n} |E|<= {emax}: non-planar={npc}  2-extremal found={found}",
              flush=True)


def _naive_two_extremal_count(n, edges):
    """Reference enumerator: all 3^|E| digon/forward/backward assignments."""
    c = 0
    for assign in itertools.product((0, 1, 2), repeat=len(edges)):
        arcs = set()
        for (u, v), t in zip(edges, assign):
            if t == 0:
                arcs.add((u, v))
                arcs.add((v, u))
            elif t == 1:
                arcs.add((u, v))
            else:
                arcs.add((v, u))
        if H.is_2extremal(n, frozenset(arcs)):
            c += 1
    return c


def exp_validate():
    """Compare the Eulerian-pruned enumerator against the naive 3^|E| reference
    on small named graphs; exactness of the pruned search is load-bearing."""
    print("# VALIDATE: Eulerian-pruned vs naive 3^|E| 2-extremal count")
    tests = [
        ("C5", nx.cycle_graph(5)), ("W4", nx.wheel_graph(4)),
        ("W5", nx.wheel_graph(5)), ("W6", nx.wheel_graph(6)),
        ("K4", nx.complete_graph(4)), ("K33", nx.complete_bipartite_graph(3, 3)),
        ("K5", nx.complete_graph(5)), ("prism", nx.circular_ladder_graph(3)),
        ("octahedron", nx.octahedral_graph()),
    ]
    all_ok = True
    for name, G in tests:
        n = G.number_of_nodes()
        E = _edges_of(G)
        naive = _naive_two_extremal_count(n, E)
        pruned = sum(1 for _ in two_extremal_orientations(n, E))
        ok = naive == pruned
        all_ok &= ok
        print(f"  {name:11s}: naive={naive:4d}  pruned={pruned:4d}  "
              f"{'OK' if ok else 'MISMATCH!!'}", flush=True)
    print(f"  ALL MATCH: {all_ok}", flush=True)
    return all_ok


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--validate", action="store_true",
                    help="compare pruned vs naive enumerator on small graphs")
    ap.add_argument("--quick", action="store_true",
                    help="K5/K3,3 and 3-connected n<=6 only (fast)")
    ap.add_argument("--three-nmax", type=int, default=7,
                    help="max n for the 3-connected sweep")
    ap.add_argument("--sparse-nmax", type=int, default=8,
                    help="max n for the non-planar disproof sweep (0=skip)")
    args = ap.parse_args(argv)
    if nx is None:
        print("networkx required (run with the root .venv)")
        return 1
    if args.validate:
        return 0 if exp_validate() else 1
    exp_k5_k33()
    exp_three_connected(nmax=6 if args.quick else args.three_nmax)
    if not args.quick and args.sparse_nmax >= 7:
        exp_sparse_nonplanar(nmax=args.sparse_nmax)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
