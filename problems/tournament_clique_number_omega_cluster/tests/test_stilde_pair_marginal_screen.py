import os
import sys

SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from decide_layer_labeling import decide_caps_labeling  # noqa: E402
from stilde_pair_marginal_screen import (  # noqa: E402
    exhaustive_min_product, pair_marginal_screen,
)


CASES = [(2, (1, 1, 4)), (3, (1, 2, 4)), (3, (2, 2, 2)), (4, (1, 3, 5))]


def test_screen_invariants_hold():
    # g_c >= 0, Shearer, transitive-cell lower bound, and the excess cap.
    for depth, caps in CASES:
        result = decide_caps_labeling(depth, caps)
        assert result["sat"], (depth, caps)
        screen = pair_marginal_screen(result["witness_order"], depth)
        assert screen["ok_gaps_nonneg"]
        assert screen["ok_shearer"]
        assert screen["ok_triple_lb"]
        assert screen["ok_excess_cap"]


def test_shearer_certificate_is_dominated_by_direct_computation():
    # Proposition (sec 25): lambda_lb(pi) <= Q(pi)^{1/d} for every order, so the
    # Shearer pair-rigidity bound never beats the trivial L_d^{1/d} estimate.
    for depth, caps in CASES:
        result = decide_caps_labeling(depth, caps)
        screen = pair_marginal_screen(result["witness_order"], depth)
        q_root = screen["product"] ** (1.0 / depth)
        assert screen["lambda_lb_from_this_witness"] <= q_root + 1e-9


def test_d2_max_over_minimizers_obeys_cap():
    # Even the worst of all 246 d=2 minimizers stays under the cap (no minimizer
    # evades the domination bound).
    res = exhaustive_min_product(2)
    assert res["L_k"] == 4
    assert res["max_sum_gaps_over_minimizers"] <= res["excess_cap"] + 1e-9
    assert res["worst_lambda_lb"] <= res["L_k_root"] + 1e-9
