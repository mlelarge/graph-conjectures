import itertools
import os
import random
import sys


SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from stilde_interval_quotients import (  # noqa: E402
    clip_full_closure,
    clipped_interval_closure_profile,
    clipped_interval_profile,
)
from stilde_pod_profiles import pod_profile  # noqa: E402


def test_clipped_interval_profile_detects_cap_excess():
    order = tuple(range(9))
    caps = (1, 1, 3)
    clipped = clipped_interval_profile(order, depth=2, caps=caps)
    heights = tuple(pod_profile(order, depth=2)["layer_heights"])
    assert clipped.heights == tuple(
        min(height, cap + 1) for height, cap in zip(heights, caps)
    )


def test_clipped_interval_closure_matches_clip_after_full_depth1():
    caps = (1, 1, 2)
    for order in itertools.permutations(range(3)):
        direct = clipped_interval_closure_profile(order, depth=1, caps=caps)
        reference = clip_full_closure(order, depth=1, caps=caps)
        assert direct.interval == reference.interval
        assert direct.heights == reference.heights


def test_clipped_interval_closure_matches_clip_after_full_depth2_sampled():
    rng = random.Random(0)
    for caps in ((2, 2, 2), (1, 3, 5), (2, 3, 4)):
        for _ in range(10):
            order = list(range(9))
            rng.shuffle(order)
            direct = clipped_interval_closure_profile(order, depth=2, caps=caps)
            reference = clip_full_closure(order, depth=2, caps=caps)
            assert direct.interval == reference.interval
            assert direct.heights == reference.heights
