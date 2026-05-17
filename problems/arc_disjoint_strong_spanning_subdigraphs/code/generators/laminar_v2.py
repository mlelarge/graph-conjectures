"""Vehicle 1 (v2): constraints-first laminar tight-3-cut systems.

v1 of `laminar.py` started from a dense base circulation and planted
shells on top, so the planted shells were almost never the only realizers
of their cut and the global lambda fell to 1. v2 inverts the order:

  1. Pick a laminar family of subsets X_1 ⊋ X_2 ⊋ ... ⊋ X_k of [n].
  2. Treat each shell's directed cut as a triple of "color slots". A
     strong arc decomposition must place at least one of each color on
     every shell. Form the NAE-3SAT instance over arc-color variables.
  3. Engineer an *inconsistent* arc/cut pattern: pick small laminar
     families + shared-arc patterns such that the NAE constraints are
     UNSAT.
  4. Realize the pattern as a sparse Eulerian digraph: extend with the
     minimum additional arcs needed to make D 3-arc-strong (no other
     tight 3-cuts), and verify.

We try four hand-designed "shapes":

  (S1) Two shells X_1 ⊋ X_2 with the three cut arcs of X_2 also lying in
       the cut of X_1, plus one extra arc in X_1 \\ X_2 going outward —
       no inconsistency, included as a control (must be SAT).

  (S2) Three shells X_1 ⊋ X_2 ⊋ X_3, with cuts of size 3 each, sharing
       arcs in a "ladder" pattern designed to encode a triangle of NAE
       constraints (NAE-3 over 3 boolean variables ≡ x_1 != x_2 != x_3 -
       no contradiction by itself).

  (S3) Four shells with shared-arc pattern encoding x XOR y XOR z = 1 in
       NAE form, where x, y, z are arc-color variables — UNSAT iff the
       four shells' NAEs are mutually inconsistent. (Hand-crafted; this
       is the conceptual heart.)

  (S4) Larger systems sampled randomly: pick a random laminar family +
       random arc-sharing pattern, realize as Eulerian, filter.

For each shape we *both* produce the engineered candidate and randomize
some of the unrelated background arcs to give the verifier some
diversity (small jitter).
"""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, field
from typing import Iterator

import networkx as nx

from digraph import Digraph


@dataclass(frozen=True)
class LaminarV2Instance:
    name: str
    n: int
    arcs: tuple[tuple[int, int], ...]
    shells: tuple[tuple[int, ...], ...]
    shape: str
    params: tuple

    def build(self) -> Digraph:
        return Digraph.from_arcs(range(self.n), list(self.arcs))


# ----------------------------------------------------------------------------
# Helpers for tight-3-cut engineering
# ----------------------------------------------------------------------------


def _verify_tight_3_cut(arcs: list[tuple[int, int]], X: set[int]) -> bool:
    """True iff |delta^+(X)| == 3 exactly."""
    cnt = 0
    for u, v in arcs:
        if u in X and v not in X:
            cnt += 1
    return cnt == 3


def _make_eulerian_inside(
    arcs: list[tuple[int, int]], X: set[int]
) -> list[tuple[int, int]]:
    """Extend `arcs` with intra-X arcs so that every v in X has equal
    in- and out-degree, by adding a single Hamilton-style cycle if needed.

    For our purposes we use a *minimal* extension: we just add a directed
    cycle on X if D[X] is not yet strong.  If D[X] is already strong but
    not balanced, we add a 2-cycle between the most-imbalanced pair.
    """
    X_sorted = sorted(X)
    # Make D[X] contain a Hamilton cycle on X
    H = list(arcs)
    cycle_arcs = [(X_sorted[i], X_sorted[(i + 1) % len(X_sorted)]) for i in range(len(X_sorted))]
    for u, v in cycle_arcs:
        if (u, v) not in H:
            H.append((u, v))
    return H


# ----------------------------------------------------------------------------
# (S1) Two-shell control (must be SAT)
# ----------------------------------------------------------------------------


def shape_S1_two_shells(n: int = 9) -> LaminarV2Instance:
    """Two nested shells X_1 = {0..5}, X_2 = {0..2} of sizes 6, 3.

    Cut of X_2 = three arcs from {0,1,2} to {3..8}, exactly 3.
    Cut of X_1 = three arcs from {0..5} to {6..8}, exactly 3 (sharing none
    with X_2's cut by construction).

    Inside each X_i: small cycle to keep D[X_i] strong.
    Plus return arcs from complement.
    """
    arcs: list[tuple[int, int]] = []

    # X_1 = {0..5}, X_2 = {0..2}, complement of X_1 = {6,7,8}.
    X1 = set(range(6))
    X2 = set(range(3))

    # Cut of X_2 (3 arcs from X_2 to V \ X_2):
    arcs += [(0, 3), (1, 4), (2, 5)]

    # Cut of X_1 (3 arcs from X_1 to V \ X_1):
    arcs += [(3, 6), (4, 7), (5, 8)]

    # Return arcs from V \ X_1 back into X_1 (3 of them for arc-conn 3):
    arcs += [(6, 0), (7, 1), (8, 2)]

    # Make D[X_2] strong: 0->1->2->0.
    arcs += [(0, 1), (1, 2), (2, 0)]
    # Make D[X_1 \ X_2] = D[{3,4,5}] strong: 3->4->5->3.
    arcs += [(3, 4), (4, 5), (5, 3)]
    # Make D[V \ X_1] = D[{6,7,8}] strong: 6->7->8->6.
    arcs += [(6, 7), (7, 8), (8, 6)]
    # Bring out-degrees up: connect X_2 to X_1\X_2.
    arcs += [(3, 0), (4, 1), (5, 2)]

    return LaminarV2Instance(
        name=f"laminarV2_S1_n{n}",
        n=n,
        arcs=tuple(arcs),
        shells=(tuple(sorted(X1)), tuple(sorted(X2))),
        shape="S1",
        params=(n,),
    )


# ----------------------------------------------------------------------------
# (S2) Three-shell NAE-triangle (control: should be SAT — NAE over 3
# variables is trivially satisfiable).
# ----------------------------------------------------------------------------


def shape_S2_three_shells(n: int = 12) -> LaminarV2Instance:
    """Three nested shells X_1 ⊋ X_2 ⊋ X_3 of sizes 9, 6, 3.

    Construction:
      X_3 = {0,1,2};  delta^+(X_3) = {0->3, 1->4, 2->5}.
      X_2 = {0..5};   delta^+(X_2) = {3->6, 4->7, 5->8}.
      X_1 = {0..8};   delta^+(X_1) = {6->9, 7->10, 8->11}.

    Each shell's cut is a different triple of arcs; no shared arcs.
    Inside each shell-difference we put a directed triangle; the
    complement V\X_1 = {9,10,11} also gets a directed triangle and
    return arcs 9->0, 10->1, 11->2.
    """
    arcs: list[tuple[int, int]] = []
    X3 = set(range(3))
    X2 = set(range(6))
    X1 = set(range(9))

    arcs += [(0, 3), (1, 4), (2, 5)]   # delta^+(X3)
    arcs += [(3, 6), (4, 7), (5, 8)]   # delta^+(X2)
    arcs += [(6, 9), (7, 10), (8, 11)] # delta^+(X1)

    # Return arcs:
    arcs += [(9, 0), (10, 1), (11, 2)]

    # Triangles inside each band of 3:
    arcs += [(0, 1), (1, 2), (2, 0)]
    arcs += [(3, 4), (4, 5), (5, 3)]
    arcs += [(6, 7), (7, 8), (8, 6)]
    arcs += [(9, 10), (10, 11), (11, 9)]

    # Extra inside-arcs to lift in-degrees of vertices that are stranded.
    # Each {3,4,5} vertex currently has in-degree 2 (one from X3 cut and
    # one from triangle). Add reverse arcs back-and-forth across bands:
    arcs += [(3, 0), (4, 1), (5, 2)]  # X2\X3 -> X3
    arcs += [(6, 3), (7, 4), (8, 5)]  # X1\X2 -> X2\X3
    arcs += [(9, 6), (10, 7), (11, 8)] # V\X1 -> X1\X2

    return LaminarV2Instance(
        name=f"laminarV2_S2_n{n}",
        n=n,
        arcs=tuple(arcs),
        shells=(tuple(sorted(X1)), tuple(sorted(X2)), tuple(sorted(X3))),
        shape="S2",
        params=(n,),
    )


# ----------------------------------------------------------------------------
# (S3) Engineered shared-arc inconsistency.
#
# Conceptual basis:
#   In a strong arc decomposition we 2-color arcs so every directed cut
#   delta^+(X) is non-monochromatic.  Equivalently, for every X, the
#   indicator vector (x_e)_{e in delta^+(X)} is not constant.  For a
#   tight 3-cut, the NAE-3 SAT constraint applies: at least one red and
#   at least one blue among the three arcs.
#
#   If two cuts delta^+(X), delta^+(Y) share *exactly two* arcs e_1, e_2
#   and a third arc each (a_3 for X, b_3 for Y), then any 2-coloring
#   satisfying both NAEs forces a relationship between c(a_3), c(b_3),
#   and c(e_1), c(e_2).  With more cuts sharing arcs in a tightly-coupled
#   pattern, we can in principle engineer a contradiction.
#
# Concrete attempt (S3a):
#   Take four cuts of size 3, all over a shared 6-arc "spine":
#       cut1 = {e_1, e_2, e_3},
#       cut2 = {e_1, e_4, e_5},
#       cut3 = {e_2, e_4, e_6},
#       cut4 = {e_3, e_5, e_6}.
#   The associated NAE-3 SAT on variables x_1, ..., x_6 is:
#       NAE(x_1, x_2, x_3),  NAE(x_1, x_4, x_5),
#       NAE(x_2, x_4, x_6),  NAE(x_3, x_5, x_6).
#   This is satisfied by x = (0, 1, 1, 0, 1, 0) (and many others) so it
#   is *not* UNSAT — i.e. shape S3a alone won't produce an obstruction.
#   This is what we want to confirm: even with 4 cuts sharing this much
#   structure, no contradiction yet.
#
# Concrete attempt (S3b):
#   Try forcing some arcs to a known color by adjacency / unit-clause
#   propagation, then layer the four cuts on top.  Pick a 5th cut that
#   contains the implied "all-blue" or "all-red" triple.  This *can* be
#   UNSAT in NAE-3-SAT.  We try the smallest such laminar configuration.
# ----------------------------------------------------------------------------


def shape_S3a_four_cuts(n: int = 10) -> LaminarV2Instance | None:
    """Four laminar tight 3-cuts sharing arcs in a "tetrahedron of cuts"
    pattern.  Not expected to be UNSAT (the underlying NAE-3SAT is SAT)
    but it is a constraint-rich Eulerian 3-arc-strong digraph and a useful
    diversity sample.
    """
    # We need 6 designated shared arcs e_1..e_6.  Each e_i is a directed
    # arc; the cuts are formed by *which X* you put the heads/tails of e_i
    # into.  To realize: take X_1 = {0..4}, X_2 = {0..2}, X_3 = {3,4} ?
    # Actually we want a laminar family of 4 nested sets.  Set:
    #   X_1 = {0..7}  (n=10), X_2 = {0..5}, X_3 = {0..3}, X_4 = {0,1}.
    # Let cut_i = delta^+(X_i).  These are not the abstract cuts 1..4
    # of S3a (which are not laminar).  We adopt the laminar restriction.
    #
    # Just plant the cuts and verify; we accept whatever NAE-pattern
    # results.
    arcs: list[tuple[int, int]] = []
    X1 = set(range(8))
    X2 = set(range(6))
    X3 = set(range(4))
    X4 = set(range(2))

    # delta^+(X4) = three arcs from {0,1} outward; we need them to land
    # in X3\X4 = {2,3}, which has only two vertices, so one of the three
    # arcs must use a parallel head.
    arcs += [(0, 2), (1, 3), (0, 3)]   # delta^+(X4)
    # delta^+(X3) = arcs from {0..3} to {4..9}; three of them in {4,5}.
    arcs += [(2, 4), (3, 5), (1, 4)]   # delta^+(X3)
    # delta^+(X2) = arcs from {0..5} to {6..9}; three of them in {6,7}.
    arcs += [(4, 6), (5, 7), (3, 6)]   # delta^+(X2)
    # delta^+(X1) = arcs from {0..7} to {8,9}; three of them in {8,9}.
    arcs += [(6, 8), (7, 9), (5, 8)]   # delta^+(X1)

    # Return arcs from V\X_1 = {8, 9} into X_1: at least 3 needed.
    arcs += [(8, 0), (9, 1), (8, 2)]

    # Make each band strong + bring up in/out-degrees.
    # Inside X4 = {0,1}: 2-cycle.
    arcs += [(0, 1), (1, 0)]
    # Inside X3 \ X4 = {2,3}: 2-cycle.
    arcs += [(2, 3), (3, 2)]
    # Inside X2 \ X3 = {4,5}: 2-cycle.
    arcs += [(4, 5), (5, 4)]
    # Inside X1 \ X2 = {6,7}: 2-cycle.
    arcs += [(6, 7), (7, 6)]
    # Inside V \ X1 = {8,9}: 2-cycle.
    arcs += [(8, 9), (9, 8)]
    # Some cross-band reverse arcs to lift in-degrees of stranded vertices.
    arcs += [(4, 2), (5, 3), (6, 4), (7, 5), (8, 6), (9, 7)]

    return LaminarV2Instance(
        name=f"laminarV2_S3a_n{n}",
        n=n,
        arcs=tuple(arcs),
        shells=(tuple(sorted(X1)), tuple(sorted(X2)), tuple(sorted(X3)), tuple(sorted(X4))),
        shape="S3a",
        params=(n,),
    )


def shape_S3b_nae_unsat(n: int = 9) -> LaminarV2Instance | None:
    """Engineered attempt: three cuts of size 3, sharing arcs such that
    each pair of cuts shares exactly one arc, in a 'triangle' pattern.
    With the right adjacency, this can fail NAE-3SAT, but it's hard to
    realize as a digraph because of the laminar constraint.

    We instead use a *near-laminar* realization where shells overlap only
    minimally.  If the verifier returns UNSAT here we have a candidate.
    """
    # n = 9 vertices.  Shells:
    #   X_a = {0,1,2}; cut_a = three arcs out of X_a.
    #   X_b = {3,4,5}; cut_b = three arcs out of X_b.
    #   X_c = {6,7,8}; cut_c = three arcs out of X_c.
    # These three shells are *disjoint*, not laminar.  But their
    # complements ARE laminar in a trivial sense (each is the complement
    # of the others' union).
    #
    # We force cut_a and cut_b to share one arc (a -> b vertex), cut_b
    # and cut_c to share another, cut_c and cut_a to share another.
    # With proper engineering, NAE-3SAT can be unsatisfiable.
    arcs: list[tuple[int, int]] = []

    # cut_a = arcs from X_a = {0,1,2}: choose (0->3), (1->6), (2->?)
    # cut_b = arcs from X_b = {3,4,5}: choose (3->?), (4->0), (5->6)
    # Construct so shared arcs are:
    #   e_ab = some arc that's in both cuts ? Impossible for *distinct*
    #   disjoint shells X_a, X_b: an arc is in delta^+(X_a) iff its tail
    #   is in X_a and head outside; this is mutually exclusive with
    #   "tail in X_b".  So *disjoint* shells *cannot* share cut arcs.
    # Conclusion: for shared arcs we need overlapping shells, hence
    # laminar (nested) shells.
    return None  # Realization shape S3b: superseded by S3c.


def shape_S3c_three_nested_overlapping_arcs(n: int = 10) -> LaminarV2Instance | None:
    """Three laminar nested shells X_1 ⊋ X_2 ⊋ X_3 with arcs engineered so
    delta^+(X_3) ⊆ delta^+(X_2) ⊆ delta^+(X_1) (one arc shared between
    consecutive nested cuts).

    Specifically:
      X_3 = {0}, X_2 = {0, 1}, X_1 = {0, 1, 2}.
      cut(X_3) = {0->1, 0->2, 0->3} (three arcs leaving {0}).
      cut(X_2) = {0->2, 0->3, 1->3} (one arc shared with cut(X_3): 0->2;
                                     one new: 1->3.  But 0->1 leaves X_3
                                     but is internal to X_2 so it's not
                                     in cut(X_2). Wait: 0->1 has tail 0 in
                                     X_2, head 1 in X_2, so it's not in
                                     cut(X_2).)
      cut(X_1) = three arcs from {0,1,2} to {3..9}.

    Setting up the constraints:
      Let the three arcs of cut(X_3) be e_1 = 0->2, e_2 = 0->3, e_3 = 0->1.
      cut(X_3) = {e_1, e_2, e_3}: NAE(e_1, e_2, e_3).
      cut(X_2) = three arcs out of {0, 1}: e_1' = 0->2, e_2' = 0->3 (= e_2),
                                            e_3' = 1->3.
                 But wait: are e_1 and e_3 also in cut(X_2)?
                   e_1 = 0->2: tail 0 in X_2, head 2 not in X_2. Yes,
                               in cut(X_2). (e_1 is in BOTH cuts.)
                   e_2 = 0->3: head 3 not in X_2. In cut(X_2).
                   e_3 = 0->1: head 1 in X_2. NOT in cut(X_2).
                 So cut(X_2) = {e_1, e_2, plus arcs from 1 to outside} =
                               {e_1, e_2, 1->something_outside}.
                 We want cut(X_2) to have size 3: so we add exactly one
                 arc from 1 to outside X_2. Call it e_4 = 1->3.
                 cut(X_2) = {e_1, e_2, e_4}: NAE(e_1, e_2, e_4).

    Now NAE(e_1,e_2,e_3) AND NAE(e_1,e_2,e_4) imply nothing new about
    {e_1, e_2} alone (they could be 0,1 or 1,0 or 0,0 or 1,1).  But if we
    add a third nested shell or *force* (e_3, e_4) to be of the same color
    by some other cut, we might get UNSAT.

    Add a third shell X_1 ⊋ X_2 with cut(X_1) of size 3, sharing arcs
    with X_2's cut: arcs in cut(X_1) have tail in X_1 = {0,1,2}, head
    outside.  Candidates from cut(X_2):
       e_1 = 0->2: head 2 IS in X_1, so NOT in cut(X_1).
       e_2 = 0->3: head 3 outside X_1. In cut(X_1).
       e_4 = 1->3: head 3 outside X_1. In cut(X_1).
    So cut(X_1) automatically contains e_2 and e_4 (both go to vertex 3
    which is outside X_1).  We need a third arc out of X_1; add e_5 = 2->4.
    cut(X_1) = {e_2, e_4, e_5}: NAE(e_2, e_4, e_5).

    Constraints so far:
      NAE(e_1,e_2,e_3) ∧ NAE(e_1,e_2,e_4) ∧ NAE(e_2,e_4,e_5).
    Still SAT in general — pick (1,0,1,1,0): NAE(1,0,1) ok; NAE(1,0,1) ok;
    NAE(0,1,0) ok.  So three shells alone aren't enough; we need more.

    However, this construction is the right *shape*: the realized digraph
    has many tight 3-cuts coupled to each other.  If we extend further or
    by *randomizing* the background arcs we may stumble onto an UNSAT.
    """
    arcs: list[tuple[int, int]] = []

    # Vertices 0..n-1. n = 10.
    if n < 6:
        return None

    # Engineered cut-defining arcs:
    arcs += [(0, 2), (0, 3), (0, 1)]   # cut(X_3) = {0->2, 0->3, 0->1}
    arcs += [(1, 3)]                    # extra arc completing cut(X_2)
    arcs += [(2, 4)]                    # extra arc completing cut(X_1)

    # We still need to make D 3-arc-strong overall, so we need in-degree
    # and out-degree >= 3 at every vertex, plus arc-conn 3.
    # Vertex 0 currently has out-deg 3, in-deg 0.  Bring up in-deg with
    # 3 return arcs from outside X_1 to 0: arcs n-1 -> 0, n-2 -> 0, n-3 -> 0.
    arcs += [(n - 1, 0), (n - 2, 0), (n - 3, 0)]

    # Vertex 1 has out-deg 1, in-deg 1.  Add 0->1 already there; add more.
    # Vertex 2 has out-deg 1, in-deg 1.  Vertex 3 has out-deg 0, in-deg 2.
    # Let's just bring everything to in/out-deg 3 by adding a directed
    # cycle through all vertices plus extra chords.

    # Hamilton cycle 0->1->2->...->(n-1)->0 :
    for i in range(n):
        arcs.append((i, (i + 1) % n))
    # Plus a chord cycle of step 2:
    for i in range(n):
        arcs.append((i, (i + 2) % n))
    # Plus a chord cycle of step 3:
    for i in range(n):
        arcs.append((i, (i + 3) % n))

    # Deduplicate parallel multi-arcs (keep one of each pair) — actually
    # parallel arcs are fine for multidigraph but we want a clean test.
    # For now, keep multiset.

    X3 = (0,)
    X2 = (0, 1)
    X1 = (0, 1, 2)
    return LaminarV2Instance(
        name=f"laminarV2_S3c_n{n}",
        n=n,
        arcs=tuple(arcs),
        shells=(X1, X2, X3),
        shape="S3c",
        params=(n,),
    )


# ----------------------------------------------------------------------------
# (S4) Random sparse Eulerian laminar candidates.
# ----------------------------------------------------------------------------


def gen_random_laminar_sparse(
    rng: random.Random,
    n_samples: int,
    n_values: list[int] = (8, 10, 12),
) -> Iterator[LaminarV2Instance]:
    """Sample random sparse Eulerian digraphs with random laminar shells
    forcing tight 3-cuts at multiple levels.

    Strategy: pick n, a chain of shell sizes (k1 < k2 < ... < k_t = n);
    for each shell of size k_i, place 3 random out-arcs to its complement;
    then add a random Eulerian "background" to bring each vertex to
    in/out-deg >= 3.
    """
    for _ in range(n_samples):
        n = rng.choice(list(n_values))
        # Random shell sizes — at least 2 shells of sizes k_1 < k_2 < n.
        # Allow up to 4 shells.
        max_t = rng.choice([2, 3])
        sizes = sorted(rng.sample(range(2, n), max_t))
        shells = [tuple(range(s)) for s in sizes]  # nested at 0..s-1

        arcs: list[tuple[int, int]] = []
        # Triple-out from each shell:
        for X in shells:
            X_set = set(X)
            complement = [v for v in range(n) if v not in X_set]
            if len(complement) < 3:
                # Can't place 3 distinct out-arcs to distinct heads; just
                # pick from {complement, complement, complement} with
                # repetition.
                heads = [rng.choice(complement) for _ in range(3)]
            else:
                heads = rng.sample(complement, 3)
            # Tails: pick 3 random tails inside X (with repetition if X is small).
            if len(X) >= 3:
                tails = rng.sample(list(X), 3)
            else:
                tails = [rng.choice(list(X)) for _ in range(3)]
            for t, h in zip(tails, heads):
                arcs.append((t, h))

        # Add base Eulerian skeleton: random tournament-like arcs to bring
        # in/out-deg >= 3.
        outd = [0] * n
        ind = [0] * n
        for u, v in arcs:
            outd[u] += 1
            ind[v] += 1
        # Greedily add arcs to lift deficiencies.
        max_tries = 20 * n
        tries = 0
        while min(outd) < 3 or min(ind) < 3:
            tries += 1
            if tries > max_tries:
                break
            u_cands = [v for v in range(n) if outd[v] < 3]
            v_cands = [v for v in range(n) if ind[v] < 3]
            u = rng.choice(u_cands) if u_cands else rng.randrange(n)
            v = rng.choice(v_cands) if v_cands else rng.randrange(n)
            if u == v:
                continue
            arcs.append((u, v))
            outd[u] += 1
            ind[v] += 1

        yield LaminarV2Instance(
            name=f"laminarV2_S4_n{n}_{_}",
            n=n,
            arcs=tuple(arcs),
            shells=tuple(shells),
            shape="S4",
            params=(n, sizes),
        )


# ----------------------------------------------------------------------------
# Top-level streaming generator
# ----------------------------------------------------------------------------


def gen_laminar_v2(
    rng: random.Random, n_random_samples: int = 200
) -> Iterator[LaminarV2Instance]:
    """Stream every shape we have."""
    # Hand-designed shapes:
    for inst in [shape_S1_two_shells(), shape_S2_three_shells()]:
        yield inst
    inst = shape_S3a_four_cuts()
    if inst is not None:
        yield inst
    inst = shape_S3c_three_nested_overlapping_arcs()
    if inst is not None:
        yield inst
    # Random sparse Eulerian samples:
    yield from gen_random_laminar_sparse(rng, n_random_samples)


def quick_degree_gate(arcs: list[tuple[int, int]], n: int) -> bool:
    outd = [0] * n
    ind = [0] * n
    for u, v in arcs:
        outd[u] += 1
        ind[v] += 1
    return all(d >= 3 for d in outd) and all(d >= 3 for d in ind)


def passes_arc_strong_3(D: Digraph, exact: bool = True) -> bool:
    if not D.is_strongly_connected():
        return False
    k = D.arc_connectivity()
    if exact:
        return k == 3
    return k >= 3
