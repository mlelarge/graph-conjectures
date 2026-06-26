import os
import sys


SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from stilde_2staircase_growth import (  # noqa: E402
    canonical_depth2_frontier,
    dominates,
    exact_depth3_candidates,
    exact_depth3_frontier,
    fixed_height_dominates_by_jumps,
    is_antichain,
    restricted_next_frontier,
    sample_cut_antichain,
    scalar_minimal_pair,
    scalar_pair,
    slice_pareto_frontier,
)


def test_jump_positions_encode_fixed_height_dominance():
    same_height = [
        state for state in exact_depth3_frontier()
        if state.heights[1:] == (3, 3)
    ][:30]
    for left in same_height:
        for right in same_height:
            assert dominates(left, right) == fixed_height_dominates_by_jumps(left, right)


def test_exact_closed_2staircase_frontier_is_larger_than_representative_frontier():
    depth2 = canonical_depth2_frontier()
    depth3 = exact_depth3_frontier()
    assert len(depth2) == 10
    assert len(depth3) == 488
    assert sum(state.heights[1:] == (3, 3) for state in depth3) == 124


def test_sample_cut_family_is_an_antichain_in_depth3_frontier():
    depth3_keys = {(state.pre1, state.suf2) for state in exact_depth3_frontier()}
    family = sample_cut_antichain()
    assert len(family) == 5
    assert all((state.pre1, state.suf2) in depth3_keys for state in family)
    assert is_antichain(family)


def test_depth3_sample_family_has_plateau_certificate():
    candidates = exact_depth3_candidates()
    family = sample_cut_antichain()
    pair = (3, 3)
    assert all(scalar_pair(state) == pair for state in family)
    assert scalar_minimal_pair(candidates, pair)

    slice_front = {
        (state.pre1, state.suf2)
        for state in slice_pareto_frontier(candidates, pair)
    }
    assert all((state.pre1, state.suf2) in slice_front for state in family)


def test_depth3_plateau_family_does_not_scalar_iterate():
    nxt = restricted_next_frontier(sample_cut_antichain())
    assert len(nxt) == 580
    assert sum(scalar_pair(state) == (5, 5) for state in nxt) == 485
    # The natural large next slice is not scalar-isolated in the full problem:
    # depth 4 has feasible lower boundary pairs such as (4,4), so a proof needs
    # a jump-separation argument, not scalar isolation alone.
    assert any(scalar_pair(state) == (4, 6) for state in nxt)
    assert any(scalar_pair(state) == (6, 4) for state in nxt)


def test_delayed_jump_barrier_is_false():
    # REFUTATION (docs sec.23): the (5,5) plateau-iteration family is dominated by
    # generated lower-scalar (4,5)/(5,4) states, so the delayed-jump barrier (sec.22)
    # is false.  We find one explicit lower-scalar dominator via a seeded search.
    import random
    from stilde_2staircase_growth import (
        canonical_depth2_frontier, exact_next_frontier, sample_cut_antichain,
        restricted_next_frontier, parent_state, dominates,
    )
    d3 = exact_next_frontier(canonical_depth2_frontier())
    a4 = [s for s in restricted_next_frontier(sample_cut_antichain())
          if s.heights[1:] == (5, 5)]
    rng = random.Random(0)
    m = 27
    for _ in range(200000):
        y = parent_state(rng.choice(d3), rng.choice(d3), rng.choice(d3),
                         rng.randint(0, m))
        if y.heights[1] <= 5 and y.heights[2] <= 5 and y.heights[1:] != (5, 5):
            if any(dominates(y, x) and y.heights != x.heights for x in a4):
                assert y.heights[1:] in ((4, 5), (5, 4))  # lower-scalar boundary
                return
    raise AssertionError("expected a lower-scalar dominator of the (5,5) family")
