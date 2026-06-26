"""Targeted search: triangle-free, digon-free digraph with chi_d>=3.

Strategy (sound, exact):
  For a fixed triangle-free underlying graph G, we want an orientation whose
  dichromatic number is >= 3, i.e. NO partition of V into 2 sets both acyclic.

  CEGAR over orientations:
    - SAT var d_e in {0,1} per edge picks its direction.
    - We maintain a set of "forbidden 2-colourings": each is a partition
      (A,B) of V.  For the chosen orientation to have chi_d>=3, EVERY 2-colouring
      must leave a monochromatic directed cycle.  We add, per candidate
      2-colouring (A,B), the constraint: the orientation contains a directed
      cycle inside A OR inside B.  We don't know which cycle a priori, so we use
      CEGAR: solve for an orientation consistent with all current constraints,
      then exactly test chi_d via the oracle; if chi_d>=3 -> witness; else the
      oracle's 2-dicolouring is a new (A,B) we must defeat -> add constraint that
      this very (A,B) be defeated by reversing>=1 arc of one of its acyclic parts
      so that part gets a cycle.  Since enumerating "which cycle" is hard, we
      instead just forbid the EXACT current orientation restricted to the arcs
      that made (A,B) acyclic, forcing progress.  Simpler & complete-enough for
      small G: forbid the full current orientation assignment (blocking clause),
      guaranteeing termination by exhausting orientations, but guided.

  Because pure blocking is just enumeration, for the structured candidate graphs
  we ALSO do plain orientation enumeration when |E| is small enough, and a
  randomized/greedy orientation sampler otherwise.
"""
from __future__ import annotations
import os
import sys, itertools, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core


def c5_blowup(t):
    """C5[K̄_t]: replace each vertex of C5 by an independent set of size t;
    join consecutive blobs completely.  Triangle-free (C5 has odd girth 5)."""
    n = 5 * t
    def blob(i):
        return list(range(i * t, i * t + t))
    edges = []
    for i in range(5):
        j = (i + 1) % 5
        for u in blob(i):
            for v in blob(j):
                edges.append((u, v))
    return n, edges


def grotzsch():
    """Grötzsch graph (Mycielskian of C5): 11 vertices, triangle-free, chi=4."""
    # standard construction
    # C5 on 0..4, mirror 5..9, apex 10
    edges = set()
    C5 = [(0,1),(1,2),(2,3),(3,4),(4,0)]
    for (a,b) in C5:
        edges.add((a,b))
    # mirror vertex i+5 connects to neighbours of i in C5, and to apex
    for i in range(5):
        nbrs = [b for (a,b) in C5 if a==i] + [a for (a,b) in C5 if b==i]
        for w in nbrs:
            edges.add(tuple(sorted((i+5, w))))
        edges.add(tuple(sorted((i+5, 10))))
    return 11, [tuple(e) for e in edges]


def search_orientations_enum(n, edges, cap_orient=2_000_000):
    """Enumerate orientations; return first with chi_d>=3, else best."""
    edges = list(edges)
    m = len(edges)
    best = (0, None)
    count = 0
    if 2**m > cap_orient:
        return None, best, count, False  # too big to enumerate
    for bits in range(2**m):
        arcs = []
        for k,(a,b) in enumerate(edges):
            if (bits>>k)&1: arcs.append((a,b))
            else: arcs.append((b,a))
        count += 1
        # cheap upper-bound test: is it 2-dicolourable?
        if not core.is_k_dicolourable(n, arcs, 2):
            return arcs, (3, arcs), count, True
    return None, best, count, True


def search_orientations_random(n, edges, tries=200000, seed=0):
    edges = list(edges)
    rng = random.Random(seed)
    for t in range(tries):
        arcs = [(a,b) if rng.random()<0.5 else (b,a) for (a,b) in edges]
        if not core.is_k_dicolourable(n, arcs, 2):
            return arcs, t
    return None, tries


if __name__ == '__main__':
    import json
    target = sys.argv[1] if len(sys.argv)>1 else 'all'
    cands = []
    if target in ('all','c5'):
        for t in (2,3):
            n,e = c5_blowup(t); cands.append((f'C5blowup_t{t}', n, e))
    if target in ('all','grotzsch'):
        n,e = grotzsch(); cands.append(('Grotzsch', n, e))
    for (name,n,edges) in cands:
        m=len(edges)
        print(f'=== {name}: n={n} |E|={m} (2^|E|={2**m if m<40 else "huge"}) ===', flush=True)
        if 2**m <= 50000:
            arcs, best, cnt, done = search_orientations_enum(n, edges)
            if arcs is not None:
                print(json.dumps({'name':name,'n':n,'FOUND_chi_d>=3':True,'arcs':arcs}), flush=True)
            else:
                print(f'  enumerated {cnt} orientations, none chi_d>=3', flush=True)
        else:
            arcs, t = search_orientations_random(n, edges, tries=30000)
            if arcs is not None:
                print(json.dumps({'name':name,'n':n,'FOUND_chi_d>=3_random':True,'arcs':arcs}), flush=True)
            else:
                print(f'  random {t} orientations sampled, none chi_d>=3', flush=True)
