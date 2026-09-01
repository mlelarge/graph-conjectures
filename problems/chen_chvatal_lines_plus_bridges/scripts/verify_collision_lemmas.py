"""Rigorously test candidate STRUCTURAL lemmas about distance-2 line collisions
on 3-connected diam>=4 graphs.  A single failing graph REFUTES a lemma.

Lemmas under test (for a collision = a line L shared by distance-2 pairs):
  L1 (STAR=>geodesic-4): if two colliding distance-2 pairs share a vertex a,
     say (a,b),(a,c) with b!=c, then d(b,c)=4 and a is metrically between b,c
     ([b a c]).  (Predicts STAR collisions are "straight 4-segments".)
  L2 (no STAR mult>=3): no vertex a is the shared vertex of 3 mutually
     line-equal distance-2 pairs (a,b),(a,c),(a,d).  Equivalent: each STAR
     collided line has multiplicity exactly 2.
  L3 (same common-nbr set never): colliding pairs never share the same
     N(.)cap N(.) interior set.
  L4 (mult<=3): no distance-2 line is shared by >=4 pairs.
  L5 (diffuse=>diameter): if two colliding pairs are endpoint-disjoint
     (a,b),(c,d), then the 4 endpoints have pairwise some distance-4 (the
     collision is long-range / antipodal), i.e. max over the 4 endpoints of
     pairwise distance == 4 (== diam when diam==4).
"""
from __future__ import annotations
import argparse, itertools, random, subprocess, sys
from collections import defaultdict
import networkx as nx
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core


def is_three_connected_brute(n, edges):
    if n < 4:
        return False
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    if any(len(adj[v]) < 3 for v in range(n)):
        return False
    for a, b in itertools.combinations(range(n), 2):
        rem = {a, b}
        start = next((x for x in range(n) if x not in rem), None)
        if start is None:
            continue
        seen = {start}; stack = [start]
        while stack:
            u = stack.pop()
            for w in adj[u]:
                if w not in rem and w not in seen:
                    seen.add(w); stack.append(w)
        if len(seen) != n - 2:
            return False
    return True


def check(n, edges):
    dist = core.all_pairs_distances(n, edges)
    diam = max(dist[i][j] for i in range(n) for j in range(n))
    if diam < 4:
        return None
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    line_of = {}
    for a, b in itertools.combinations(range(n), 2):
        if dist[a][b] == 2:
            line_of[(a, b)] = core.line_of_pair(dist, n, a, b)
    by_line = defaultdict(list)
    for p, L in line_of.items():
        by_line[L].append(p)
    fails = []
    for L, ps in by_line.items():
        if len(ps) <= 1:
            continue
        m = len(ps)
        # L4
        if m >= 4:
            fails.append(("L4_mult>=4", ps))
        # L3
        cnsets = {frozenset(adj[a] & adj[b]) for (a, b) in ps}
        if len(cnsets) == 1:
            fails.append(("L3_same_cn", ps))
        # pairwise structure
        star_partners = defaultdict(list)  # shared vertex -> partners
        for (p, q) in itertools.combinations(ps, 2):
            sp, sq = set(p), set(q)
            sh = sp & sq
            if len(sh) == 1:
                a = next(iter(sh))
                b = next(iter(sp - sh)); c = next(iter(sq - sh))
                # L1
                between = (dist[b][a] + dist[a][c] == dist[b][c])
                if not (dist[b][c] == 4 and between):
                    fails.append(("L1_star_not_geodesic4", (a, b, c, dist[b][c], between)))
                star_partners[a].append(b); star_partners[a].append(c)
            elif len(sh) == 0:
                # L5 diffuse
                verts = list(p) + list(q)
                mx = max(dist[x][y] for x in verts for y in verts)
                if mx != 4:
                    fails.append(("L5_diffuse_not4", (p, q, mx)))
        # L2 no STAR mult>=3 through one vertex
        for a, parts in star_partners.items():
            if len(set(parts)) >= 3:
                fails.append(("L2_star_mult>=3", (a, sorted(set(parts)))))
    return {"diam": diam, "fails": fails,
            "n_collided": sum(1 for v in by_line.values() if len(v) > 1)}


def gen_geng(n, band):
    cmd = ["geng", "-C", "-d3", "-q", str(n)]
    if band:
        cmd.append(band)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1 << 20)
    for line in proc.stdout:
        g6 = line.strip()
        if not g6:
            continue
        nn, edges = core.graph6_to_edges(g6)
        if is_three_connected_brute(nn, edges):
            yield g6, nn, edges
    returncode = proc.wait()
    if returncode != 0:
        raise subprocess.CalledProcessError(returncode, cmd)


def gen_gnp(n, p, want, seed):
    rng = random.Random(seed)
    found = 0; tries = 0
    while found < want and tries < 300000:
        tries += 1
        g = nx.gnp_random_graph(n, p, seed=rng.randint(0, 1 << 30))
        edges = list(g.edges())
        if not core.is_connected(n, edges):
            continue
        if not is_three_connected_brute(n, edges):
            continue
        dist = core.all_pairs_distances(n, edges)
        if max(dist[i][j] for i in range(n) for j in range(n)) < 4:
            continue
        found += 1
        yield f"gnp{found}", n, edges


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", choices=["geng", "gnp"], default="geng")
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--band", type=str, default=None)
    ap.add_argument("--p", type=float, default=0.30)
    ap.add_argument("--want", type=int, default=400)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    gen = (gen_geng(args.n, args.band) if args.src == "geng"
           else gen_gnp(args.n, args.p, args.want, args.seed))
    ngraphs = 0; ncoll = 0
    failbag = defaultdict(list)
    for g6, n, edges in gen:
        r = check(n, edges)
        if r is None:
            continue
        ngraphs += 1
        ncoll += r["n_collided"]
        for tag, info in r["fails"]:
            if len(failbag[tag]) < 5:
                failbag[tag].append((g6, info))
    print({"src": args.src, "n": args.n, "band": args.band,
           "graphs": ngraphs, "collided_lines": ncoll,
           "fail_tags": {k: len(v) for k, v in failbag.items()},
           "fail_examples": {k: v for k, v in failbag.items()}})


if __name__ == "__main__":
    main()
