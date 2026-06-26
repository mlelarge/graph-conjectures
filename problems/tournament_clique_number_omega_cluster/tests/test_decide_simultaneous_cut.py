import os
import sys

SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from decide_simultaneous_cut import decide_simultaneous_cut  # noqa: E402
from decide_layer_labeling import decide_caps_labeling  # noqa: E402
from stilde_profile_closure import step_profile  # noqa: E402
from stilde_pod_profiles import pod_profile  # noqa: E402
from stilde_face_2cut import order_2cut  # noqa: E402


def test_encoding_validates_on_depth3():
    # depth-3 (1,3,5) is the M2 of the depth-4 optimum and HAS a (1,2) cut;
    # it does NOT have a (1,1) cut; (1,1,1) is impossible.
    sat = decide_simultaneous_cut(3, 3, 5, 1, 2)
    assert sat["sat"] and sat["verified"]
    assert sat["heights"] == (1, 3, 5)
    assert decide_simultaneous_cut(3, 3, 5, 1, 1)["sat"] is False
    assert decide_simultaneous_cut(3, 1, 1, 1, 1)["sat"] is False


def test_F6_candidate_product_35_has_no_simultaneous_cut():
    # headline: no depth-5 face module of heights <=(1,5,7) admits a simultaneous
    # (1,2) cut -> the clean slack-(1,2) portfolio mechanism (F_4, F_5) BREAKS at
    # depth 6; product 35 is unreachable by the portfolio route.
    assert decide_simultaneous_cut(5, 5, 7, 1, 2)["sat"] is False
    assert decide_simultaneous_cut(5, 6, 6, 1, 1)["sat"] is False


def test_portfolio_min_product_is_45_and_certifies_F6_bound():
    # the minimum portfolio-reachable product is 45 (slack grows to (2,4)).
    res = decide_simultaneous_cut(5, 5, 9, 2, 4)
    assert res["sat"] and res["verified"]
    m2 = step_profile(res["witness_order"], 5)
    p = res["cut_position"]
    # companions exist, so the construction certifies F_6 <= 45
    c0 = decide_caps_labeling(5, (1, 5, 5))
    c1 = decide_caps_labeling(5, (1, 3, 9))
    assert c0["sat"] and c1["sat"]
    m0 = step_profile(c0["witness_order"], 5)
    m1 = step_profile(c1["witness_order"], 5)
    prof = pod_profile(order_2cut(m0, m1, m2, p), 6)
    assert prof["layer_heights"][0] == 1
    assert prof["height_product"] <= 45
