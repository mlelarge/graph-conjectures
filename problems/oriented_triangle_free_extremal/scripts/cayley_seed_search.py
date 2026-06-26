"""Explicit-construction proposal (t_vec side): structurally-orthogonal SEED hunt.

Every D25-derived family caps at chi_vec=3 (graveyard G1,G5,G6 + agent-verified
iterated-blowup, circulant-scaffold, shifted-backward, two-sided-Mycielskian).
The universal 3-colouring exploits the cyclic backward-MATCHING pack structure of
the backward-blowup.  This script hunts a 3-dicritical oriented triangle-free
seed that is NOT a backward-blowup -- an oriented Cayley digraph on a small
abelian group with a triangle-free connection set -- and reports any chi_vec>=4
witness directly (which would beat m(4)<=209 if n<=208).

EXHAUSTIVE over small connection sets (not random): for each group and each
half-system S (S, -S disjoint, 0 notin S) up to a size cap, build Cay(G,S),
keep oriented + triangle-free ones, compute chi_vec exactly.
"""
from __future__ import annotations
import sys, os, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core


def cayley_abelian(mods, S):
    elts = list(itertools.product(*[range(m) for m in mods]))
    idx = {g: i for i, g in enumerate(elts)}
    def add(g, s): return tuple((a + b) % m for a, b, m in zip(g, s, mods))
    arcs = [(idx[g], idx[add(g, s)]) for g in elts for s in S]
    return len(elts), arcs


def neg(s, mods):
    return tuple((-a) % m for a, m in zip(s, mods))


def half_systems(mods, smax):
    """Yield connection sets S with |S|<=smax, 0 notin S, S cap -S = empty,
    choosing at most one of each {s,-s} pair."""
    elts = [g for g in itertools.product(*[range(m) for m in mods]) if any(g)]
    pairs, seen = [], set()
    for g in elts:
        if g in seen:
            continue
        ng = neg(g, mods)
        seen.add(g); seen.add(ng)
        pairs.append((g, ng) if g != ng else None)  # g==ng impossible if no 2-torsion in that coord combo
    pairs = [p for p in pairs if p is not None]
    # choose a nonempty subset of pairs, and for each pick a direction
    for r in range(1, min(smax, len(pairs)) + 1):
        for combo in itertools.combinations(pairs, r):
            for dirs in itertools.product(*[(0, 1)] * r):
                S = [combo[i][dirs[i]] for i in range(r)]
                yield S


def run(groups, smax=4, report_every=2000):
    best = {}
    for mods in groups:
        cnt = 0
        for S in half_systems(mods, smax):
            cnt += 1
            n, arcs = cayley_abelian(mods, S)
            if not core.is_oriented(arcs):
                continue
            if not core.is_triangle_free(n, arcs):
                continue
            chi = core.dichromatic_number(n, arcs, ub=5)
            key = mods
            if key not in best or chi > best[key][0]:
                best[key] = (chi, tuple(S), n, len(arcs))
                print(f"Z{mods}: new best chi={chi} |S|={len(S)} S={S} n={n} arcs={len(arcs)}", flush=True)
            if chi >= 4:
                print(f"!!!! CHI>=4 WITNESS  Z{mods} S={S} n={n} chi={chi} arcs={len(arcs)}", flush=True)
        print(f"Z{mods}: scanned {cnt} half-systems, best={best.get(mods)}", flush=True)
    return best


if __name__ == "__main__":
    # Small enough for exact chi_vec; triangle-free oriented Cayley digraphs.
    GROUPS = [(3, 3), (3, 5), (5, 3), (3, 7), (7, 3),
              (3, 3, 3), (9, 3), (5, 5)]
    smax = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    run(GROUPS, smax=smax)
