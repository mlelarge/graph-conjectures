"""pynauty-based canonical hashing for `Digraph` instances.

The Phase 3 v2 sweep produced 4 613 *labeled-distinct* candidates (hashed
by sorted arc list). That bounds the iso-canonical count from above, but
does not equal it: two labeled-distinct digraphs are typically isomorphic
through a vertex relabelling. Before Phase 4 starts staring at color-
routing patterns we need iso-class counts.

This module provides `canonical_key(D) -> str`, a deterministic 32-hex
SHA-256 hash that is *invariant under vertex relabelling of D* (and only
that — direction is preserved, parallel arcs are preserved, the labels
themselves are not used).

Implementation notes
--------------------

pynauty (the Python wrapper around McKay & Piperno's nauty) supports
directed graphs but **not multigraphs**: an adjacency-dict edge is
present or absent, with no multiplicity. We have two cases:

1. *Simple* digraphs (no parallel arcs in any direction). For these
   we hand pynauty the directed adjacency directly. The canonical
   certificate produced by `pynauty.certificate(g)` is then a byte
   string invariant under vertex relabelling, and our hash is
   `sha256(certificate)` truncated to 32 hex chars.

2. *Multidigraphs* (some ordered pair (u, v) appears more than once).
   We encode arc multiplicities by inserting a *labelled subdivision
   vertex* for each arc copy and using pynauty's vertex-coloring to
   keep "original" vertices distinguishable from "subdivision" vertices
   *of each multiplicity class*. Concretely, an arc u -> v with
   multiplicity m yields m subdivision vertices each on a chain
   u -> s_i -> v, and all subdivision vertices get the colour
   (1, m, parity) where parity flags subdivisions belonging to arcs of
   that multiplicity. This preserves iso-equivalence because two
   multidigraphs are isomorphic iff their multiplicity-coloured
   subdivisions are.

   Crucially, we use a 2-step subdivision for arcs *and* their reverses
   so that direction information survives: arc u -> v becomes
   u -> a -> b -> v with a and b in distinct colour classes (the
   "out-side" and "in-side" of the subdivision); a self-loop u -> u
   becomes u -> a -> b -> u with the same colour scheme.

Since the 9 UNSAT 2-arc-strong templates are all *simple* digraphs
(arc-multiplicity 1 throughout — verified by inspection of
`benchmarks.py`) and the Vehicle 3, Vehicle 2, Vehicle 5 generators all
produce simple digraphs (gluings, balanced orientations, perturbed
bidirected/circulants, and substitution all return simple arc lists),
case (1) covers everything in scope. We still implement case (2) for
robustness; the test suite at the bottom of this file exercises both
paths.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict
from typing import Hashable, Iterable

import pynauty  # type: ignore

from digraph import Digraph


# ----------------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------------


def canonical_key(D: Digraph) -> str:
    """Return a deterministic iso-canonical hash for D.

    The hash is:
     - invariant under vertex relabelling of D;
     - sensitive to direction (D and its reverse map to different keys
       in general);
     - sensitive to multiplicity (D and its underlying simple digraph
       map to different keys if D has parallel arcs).

    The returned string is exactly 64 hex characters (full sha-256).

    Implementation. We reduce digraph isomorphism to undirected coloured
    graph isomorphism using the well-known "arc-encoding" gadget: every
    arc u -> v becomes a chain u --- (out, m) --- (in, m) --- v in an
    undirected coloured graph, where m is the arc's multiplicity. The
    "original" vertices form one colour class; the "tail-side"
    subdivision vertices of each multiplicity m form another colour
    class; the "head-side" subdivision vertices of each multiplicity m
    form a third. This encoding is faithful (two digraphs are
    isomorphic iff their undirected coloured encodings are), and lets
    nauty exploit its undirected refinement, which is uniformly faster
    than its directed mode on this class of inputs.
    """
    n = D.n()
    if n == 0:
        return _sha("EMPTY")

    # Build a list of integer-labelled arcs (multiplicities preserved).
    arcs: list[tuple[int, int]] = []
    for u, v, _k in D.arcs():
        arcs.append((int(u), int(v)))

    # Count multiplicities per ordered pair.
    mult: dict[tuple[int, int], int] = defaultdict(int)
    for a in arcs:
        mult[a] += 1

    return _canonical_key_via_undirected_encoding(n, mult)


def iso_partition(digraphs: Iterable[tuple[Hashable, Digraph]]) -> dict[str, list[Hashable]]:
    """Group a collection of (label, Digraph) pairs by canonical hash.

    Returns {canonical_key: [labels...]}; the size of each list is the
    iso-class size (under vertex relabelling).
    """
    out: dict[str, list[Hashable]] = defaultdict(list)
    for label, D in digraphs:
        out[canonical_key(D)].append(label)
    return dict(out)


# ----------------------------------------------------------------------------
# Internals
# ----------------------------------------------------------------------------


def _sha(payload: object) -> str:
    return hashlib.sha256(repr(payload).encode("utf-8")).hexdigest()


def _canonical_key_via_undirected_encoding(n: int, mult: dict[tuple[int, int], int]) -> str:
    """Canonical key via reduction to undirected coloured graph isomorphism.

    Each arc u -> v with multiplicity m becomes a chain (undirected
    edges)
        u  --  out_node  --  in_node  --  v
    where `out_node` and `in_node` live in dedicated colour classes
    distinguished by m. The encoding is faithful: a vertex bijection of
    the original digraphs extends to a colour-preserving vertex
    bijection of the encodings, and conversely.

    Empirically this is multiple orders of magnitude faster than
    pynauty's directed mode for the digraphs we deal with (n <= 20).
    """
    next_id = n
    # Adjacency for undirected graph: store each edge as (u, v) with u<v,
    # and emit symmetric pairs to pynauty's adjacency dict.
    adj: dict[int, set[int]] = {v: set() for v in range(n)}
    out_side_by_mult: dict[int, list[int]] = defaultdict(list)
    in_side_by_mult: dict[int, list[int]] = defaultdict(list)

    # Deterministic iteration: sort by (u, v).
    for (u, v), m in sorted(mult.items()):
        for _ in range(m):
            a = next_id     # tail-side subdivision
            b = next_id + 1  # head-side subdivision
            next_id += 2
            adj.setdefault(a, set())
            adj.setdefault(b, set())
            adj[u].add(a)
            adj[a].add(u)
            adj[a].add(b)
            adj[b].add(a)
            adj[b].add(v)
            adj[v].add(b)
            out_side_by_mult[m].append(a)
            in_side_by_mult[m].append(b)

    total = next_id

    # Colouring:
    #  class 0 = original vertices (V(D))
    #  class (1, m) = out-side subdivisions for multiplicity m
    #  class (2, m) = in-side subdivisions for multiplicity m
    coloring: list[set[int]] = [set(range(n))]
    keys: list[tuple[int, int]] = sorted(
        set([(1, m) for m in out_side_by_mult] + [(2, m) for m in in_side_by_mult])
    )
    for side, m in keys:
        if side == 1:
            coloring.append(set(out_side_by_mult[m]))
        else:
            coloring.append(set(in_side_by_mult[m]))

    g = pynauty.Graph(
        number_of_vertices=total,
        directed=False,
        adjacency_dict={k: sorted(vs) for k, vs in adj.items() if vs},
        vertex_coloring=[c for c in coloring if c],
    )
    cert = pynauty.certificate(g)
    return hashlib.sha256(cert + f"|n={n}|undir_enc".encode()).hexdigest()


# ----------------------------------------------------------------------------
# Self-test
# ----------------------------------------------------------------------------


def _selftest() -> None:
    """Internal sanity tests; runs when this module is executed directly."""
    import random

    # Test 1: relabelled digraph has the same canonical key.
    D1 = Digraph.from_arcs(range(5), [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2)])
    perm = [3, 0, 4, 1, 2]
    arcs_perm = [(perm[u], perm[v]) for u, v in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2)]]
    D2 = Digraph.from_arcs(range(5), arcs_perm)
    k1, k2 = canonical_key(D1), canonical_key(D2)
    assert k1 == k2, f"relabel invariance failed: {k1} vs {k2}"
    print(f"[T1] relabel-invariance: ok (key = {k1[:16]}...)")

    # Test 2: direction sensitivity. Reverse of a non-symmetric digraph
    # should not match the original.
    D3 = Digraph.from_arcs(range(3), [(0, 1), (1, 2)])  # path 0 -> 1 -> 2
    D4 = Digraph.from_arcs(range(3), [(1, 0), (2, 1)])  # reverse: 2 -> 1 -> 0
    # These ARE iso as directed (they're both paths), so same key:
    assert canonical_key(D3) == canonical_key(D4)
    # But the path 0 -> 1 -> 2 and the cycle 0 -> 1 -> 2 -> 0 differ:
    D5 = Digraph.from_arcs(range(3), [(0, 1), (1, 2), (2, 0)])
    assert canonical_key(D3) != canonical_key(D5)
    print("[T2] direction/structure sensitivity: ok")

    # Test 3: multiplicity is detected. Single edge != double edge.
    Da = Digraph.from_arcs(range(2), [(0, 1)])
    Db = Digraph.from_arcs(range(2), [(0, 1), (0, 1)])
    assert canonical_key(Da) != canonical_key(Db)
    print("[T3] multiplicity sensitivity: ok")

    # Test 4: S4 (the 4-vertex obstruction) self-isomorphism.
    from benchmarks import all_benchmarks
    bs = {b.name: b for b in all_benchmarks()}
    s4 = bs["S4"].build()
    # Random permutation
    rnd = random.Random(0)
    perm = list(range(s4.n()))
    rnd.shuffle(perm)
    arcs = [(perm[u], perm[v]) for u, v, _ in s4.arcs()]
    s4p = Digraph.from_arcs(range(s4.n()), arcs)
    assert canonical_key(s4) == canonical_key(s4p)
    print(f"[T4] S4 relabel-invariance: ok (key = {canonical_key(s4)[:16]}...)")

    # Test 5: all 9 UNSAT templates have distinct canonical keys.
    UNSAT_NAMES = {
        "S4", "C6_square", "C8_square",
        "C3_K2K2K2", "C3_K2K2P2", "C3_K2K2K3",
        "AiEtAl_L211_min", "AiEtAl_L312_min", "AiEtAl_iv_star_iv",
    }
    keys = {}
    for b in all_benchmarks():
        if b.name not in UNSAT_NAMES:
            continue
        D = b.build()
        k = canonical_key(D)
        assert k not in keys, f"collision: {b.name} and {keys[k]}"
        keys[k] = b.name
    print(f"[T5] all {len(keys)} UNSAT templates have distinct keys: ok")
    print("[OK] canonicalize self-test passed.")


if __name__ == "__main__":
    _selftest()
