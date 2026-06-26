import itertools
import os
import random
import sys


SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from stilde_interval_profiles import (  # noqa: E402
    interval_closure_profile,
    interval_profile,
    prefix_suffix_from_interval,
)
from stilde_profile_closure import step_profile  # noqa: E402


def test_interval_profile_contains_prefix_suffix_staircases():
    order = (8, 6, 2, 0, 1, 3, 4, 5, 7)
    interval = interval_profile(order, depth=2)
    prefix, suffix = prefix_suffix_from_interval(interval)
    step = step_profile(order, depth=2)
    assert prefix == step.prefix
    assert suffix == step.suffix
    assert interval.heights == step.heights


def test_interval_closure_matches_direct_depth1_exhaustive():
    for order in itertools.permutations(range(3)):
        direct = interval_profile(order, depth=1)
        closed = interval_closure_profile(order, depth=1)
        assert closed.interval == direct.interval
        assert closed.heights == direct.heights


def test_interval_closure_matches_direct_depth2_sampled():
    rng = random.Random(0)
    for _ in range(20):
        order = list(range(9))
        rng.shuffle(order)
        direct = interval_profile(order, depth=2)
        closed = interval_closure_profile(order, depth=2)
        assert closed.interval == direct.interval
        assert closed.heights == direct.heights
