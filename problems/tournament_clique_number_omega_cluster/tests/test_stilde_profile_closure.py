import itertools
import os
import random
import sys


SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from stilde_profile_closure import (  # noqa: E402
    closure_details,
    decide_caps_by_profile_closure,
    minimum_product_by_profile_closure,
    reconstruct_order,
    step_profile,
)


def test_step_profile_on_singleton_has_empty_zero_and_singleton_one():
    profile = step_profile([0], depth=0)
    assert profile.heights == (1, 1, 1)
    assert profile.prefix == ((0, 1), (0, 1), (0, 1))
    assert profile.suffix == ((0, 1), (0, 1), (0, 1))


def test_profile_closure_matches_direct_q_on_small_orders():
    for order in itertools.permutations(range(3)):
        details = closure_details(order, depth=1)
        assert details["heights"] == details["direct_heights"]

    rng = random.Random(0)
    for _ in range(50):
        order = list(range(9))
        rng.shuffle(order)
        details = closure_details(order, depth=2)
        assert details["heights"] == details["direct_heights"]


def test_profile_closure_decides_directed_triangle_caps():
    assert not decide_caps_by_profile_closure(0, (1, 1, 1))["sat"]

    result = decide_caps_by_profile_closure(0, (1, 1, 2))
    assert result["sat"]
    assert result["layer_heights"] == (1, 1, 2)

    order = reconstruct_order(result["module_orders"], result["path"])
    assert order == result["witness_order"]


def test_profile_closure_recovers_L1_and_L2():
    depth1 = minimum_product_by_profile_closure(inner_depth=0, max_cap=2)
    assert depth1["sat"]
    assert depth1["product"] == 2

    depth2 = minimum_product_by_profile_closure(inner_depth=1, max_cap=4)
    assert depth2["sat"]
    assert depth2["product"] == 4
