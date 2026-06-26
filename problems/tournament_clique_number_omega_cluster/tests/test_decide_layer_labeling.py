"""Cross-checks for the level-labeling SAT encodings (eager + lazy CEGAR)."""
import itertools
import os
import sys


SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from decide_layer_labeling import decide_caps_labeling  # noqa: E402
from decide_layer_lazy import decide_caps_lazy  # noqa: E402
from decide_layer_positional import decide_caps_positional  # noqa: E402
from decide_stilde_layer_product import decide_caps  # noqa: E402


def test_labeling_matches_chain_encoding_depths_2_3():
    for depth in (2, 3):
        for caps in itertools.product(range(1, 4), repeat=3):
            ref = decide_caps(depth, caps)["sat"]
            got = decide_caps_labeling(depth, caps)["sat"]
            assert got == ref, (depth, caps, got, ref)


def test_lazy_matches_eager_depths_2_3():
    for depth in (2, 3):
        for caps in [(1, 1, 2), (1, 2, 2), (2, 2, 2), (1, 1, 4), (2, 2, 3)]:
            eager = decide_caps_labeling(depth, caps)["sat"]
            lazy = decide_caps_lazy(depth, caps)["sat"]
            assert lazy == eager, (depth, caps, lazy, eager)


def test_positional_matches_eager_depths_2_3():
    for depth in (2, 3):
        for caps in itertools.product(range(1, 4), repeat=3):
            eager = decide_caps_labeling(depth, caps)["sat"]
            positional = decide_caps_positional(depth, caps)["sat"]
            assert positional == eager, (depth, caps, positional, eager)


def test_positional_rank_domain_constraints_match_eager():
    for depth, caps_list in (
        (2, [(1, 1, 2), (1, 2, 2), (2, 2, 2)]),
        (3, [(1, 2, 2), (2, 2, 2), (2, 2, 3)]),
    ):
        for caps in caps_list:
            eager = decide_caps_labeling(depth, caps)["sat"]
            constrained = decide_caps_positional(
                depth,
                caps,
                range_keys=True,
                distinct_keys=True,
            )["sat"]
            assert constrained == eager, (depth, caps, constrained, eager)


def test_depth4_L4_boundary():
    # L_4 = 15: (1,3,5) SAT, every smaller-or-equal skew below 15 UNSAT
    assert decide_caps_labeling(4, (1, 3, 5))["sat"] is True
    assert decide_caps_positional(4, (1, 3, 5))["sat"] is True
    assert decide_caps_labeling(4, (2, 2, 3))["sat"] is False   # product 12
    assert decide_caps_positional(4, (2, 2, 3))["sat"] is False
    assert decide_caps_labeling(4, (1, 1, 14))["sat"] is False  # product 14


def test_depth5_L5_is_24_boundary():
    # L_5 = 24: (2,3,4) SAT; representative product-<24 triples UNSAT.
    assert decide_caps_labeling(5, (2, 3, 4))["sat"] is True
    assert decide_caps_labeling(5, (1, 3, 5))["sat"] is False   # product 15
    assert decide_caps_labeling(5, (2, 3, 3))["sat"] is False   # product 18
