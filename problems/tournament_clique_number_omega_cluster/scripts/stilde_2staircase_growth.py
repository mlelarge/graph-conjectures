"""Growth probes for the closed two-staircase 2-cut algebra.

The clean 2-cut state is (q1, q2, pre_1, suf_2).  This module treats that as an
abstract algebraic object, using the exact closure formulas from
``stilde_face_2cut.parent_state_2cut`` rather than reconstructing full orders.

The main diagnostic is that the full algebraic Pareto frontier is already much
larger than the sampled representative frontier recorded in sec. 18:

    depth 2: 10 states
    one exact 2-cut closure step: 488 Pareto states at depth 3

Moreover, 124 of the depth-3 states have the same terminal height pair (3,3).
So the residual complexity is not endpoint diversity; it is the antichain of
jump positions of the two staircases.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from functools import lru_cache

from stilde_face_2cut import parent_heights_2cut, parent_state_2cut
from stilde_profile_closure import step_profile


@dataclass(frozen=True)
class TwoStaircaseState:
    depth: int
    heights: tuple[int, int, int]
    pre1: tuple[int, ...]
    suf2: tuple[int, ...]
    label: int | None = None
    witness: tuple | None = None

    @property
    def prefix(self):
        return ((), self.pre1, ())

    @property
    def suffix(self):
        return ((), (), self.suf2)


def state_from_profile(profile, label=None):
    return TwoStaircaseState(
        depth=profile.depth,
        heights=profile.heights,
        pre1=profile.prefix[1],
        suf2=profile.suffix[2],
        label=label,
    )


def state_key(state):
    return state.pre1, state.suf2


def dominates(left, right):
    """Pointwise dominance for the reduced state."""

    return (
        all(x <= y for x, y in zip(left.pre1, right.pre1))
        and all(x <= y for x, y in zip(left.suf2, right.suf2))
    )


def pareto_frontier(states):
    """Deduplicate by reduced state and keep pointwise Pareto-minimal states."""

    by_key = {}
    for state in states:
        by_key.setdefault(state_key(state), state)
    items = list(by_key.values())
    keep = []
    for i, state in enumerate(items):
        if not any(i != j and dominates(other, state) for j, other in enumerate(items)):
            keep.append(state)
    return keep


def same_reduced_state(left, right):
    return state_key(left) == state_key(right)


def is_antichain(states):
    states = tuple(states)
    for i, left in enumerate(states):
        for j, right in enumerate(states):
            if i != j and dominates(left, right):
                return False
    return True


def scalar_pair(state):
    return state.heights[1], state.heights[2]


def scalar_minimal_pair(candidates, pair):
    """No generated candidate has both endpoint heights <= pair, except pair."""

    a, b = pair
    return not any(
        scalar_pair(state) != pair
        and state.heights[1] <= a
        and state.heights[2] <= b
        for state in candidates
    )


def slice_pareto_frontier(candidates, pair):
    """Pareto frontier inside one terminal height-pair slice."""

    return pareto_frontier(
        state for state in candidates
        if scalar_pair(state) == pair
    )


def jump_positions(staircase):
    """First positions where a monotone staircase reaches levels 1..height."""

    height = staircase[-1]
    positions = []
    level = 1
    for index, value in enumerate(staircase):
        while level <= height and value >= level:
            positions.append(index)
            level += 1
    if len(positions) != height:
        raise ValueError("staircase does not reach each integer level")
    return tuple(positions)


def fixed_height_dominates_by_jumps(left, right):
    """Dominance in jump-vector coordinates, for equal terminal heights.

    For a monotone staircase, smaller pointwise values mean every level is reached
    no earlier.  Thus P <= P' is equivalent to jump(P) >= jump(P').
    """

    if left.heights != right.heights:
        raise ValueError("jump dominance here is only for equal height triples")
    return (
        all(x >= y for x, y in zip(jump_positions(left.pre1), jump_positions(right.pre1)))
        and all(x >= y for x, y in zip(jump_positions(left.suf2), jump_positions(right.suf2)))
    )


@lru_cache(maxsize=1)
def canonical_depth2_frontier():
    """Exact reduced Pareto frontier of all q0=1 B_2 orders."""

    profiles = [
        step_profile(order, 2)
        for order in itertools.permutations(range(9))
    ]
    front = pareto_frontier(
        state_from_profile(profile)
        for profile in profiles
        if profile.heights[0] == 1
    )
    front.sort(key=lambda state: (state.heights[1:], state.pre1, state.suf2))
    return tuple(
        TwoStaircaseState(
            state.depth,
            state.heights,
            state.pre1,
            state.suf2,
            label=index,
        )
        for index, state in enumerate(front)
    )


def parent_state(left, middle, floating, cut, label=None):
    """Exact parent state under M_2[:cut] | M_0 | M_1 | M_2[cut:]."""

    q1, q2 = parent_heights_2cut(left, middle, floating, cut)
    pre1, suf2 = parent_state_2cut(left, middle, floating, cut)
    return TwoStaircaseState(
        depth=floating.depth + 1,
        heights=(1, q1, q2),
        pre1=pre1,
        suf2=suf2,
        label=label,
        witness=(left.label, middle.label, floating.label, cut),
    )


def exact_next_frontier(frontier):
    """One exact 2-cut closure step from a reduced frontier."""

    child_size = 3 ** frontier[0].depth
    states = []
    label = 0
    for left, middle, floating in itertools.product(frontier, repeat=3):
        for cut in range(child_size + 1):
            states.append(parent_state(left, middle, floating, cut, label=label))
            label += 1
    return pareto_frontier(states)


def exact_next_candidates(frontier):
    """All one-step generated states before Pareto pruning."""

    child_size = 3 ** frontier[0].depth
    states = []
    label = 0
    for left, middle, floating in itertools.product(frontier, repeat=3):
        for cut in range(child_size + 1):
            states.append(parent_state(left, middle, floating, cut, label=label))
            label += 1
    return tuple(states)


@lru_cache(maxsize=1)
def exact_depth3_frontier():
    return tuple(exact_next_frontier(canonical_depth2_frontier()))


@lru_cache(maxsize=1)
def exact_depth3_candidates():
    return exact_next_candidates(canonical_depth2_frontier())


def depth3_fixed_height_antichain():
    """The (3,3)-height slice of the exact depth-3 frontier."""

    return [
        state for state in exact_depth3_frontier()
        if state.heights[1:] == (3, 3)
    ]


def sample_cut_antichain():
    """A small explicit antichain from one child triple and several cuts.

    With the canonical depth-2 labels, states 1 and 5 have shapes (2,2) and
    (2,3).  The five cuts 4..8 form a visible tradeoff: pre_1 jumps later while
    suf_2 jumps earlier.  These five states survive in the exact depth-3 frontier.
    """

    front = canonical_depth2_frontier()
    left = front[1]
    middle = front[1]
    floating = front[5]
    return [
        parent_state(left, middle, floating, cut)
        for cut in range(4, 9)
    ]


def restricted_next_frontier(family):
    """One exact 2-cut closure step using only states in ``family``."""

    family = tuple(family)
    child_size = 3 ** family[0].depth
    states = []
    for left, middle, floating in itertools.product(family, repeat=3):
        for cut in range(child_size + 1):
            states.append(parent_state(left, middle, floating, cut))
    return pareto_frontier(states)


if __name__ == "__main__":
    depth2 = canonical_depth2_frontier()
    depth3 = exact_next_frontier(depth2)
    same_height = [state for state in depth3 if state.heights[1:] == (3, 3)]
    print({
        "depth2_frontier": len(depth2),
        "depth3_exact_frontier": len(depth3),
        "depth3_height_3_3": len(same_height),
    })
