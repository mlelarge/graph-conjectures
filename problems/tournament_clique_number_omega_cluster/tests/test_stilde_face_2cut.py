import itertools
import json
import os
import sys


SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from decide_layer_labeling import decide_caps_labeling  # noqa: E402
from stilde_face_2cut import (  # noqa: E402
    parent_heights_2cut, parent_state_2cut, order_2cut,
    parent_heights_3piece, order_3piece, portfolio_cut_certificates,
)
from stilde_profile_closure import (  # noqa: E402
    closure_heights, lattice_path, module_orders, step_profile,
)


def _path_2cut(s, m):
    st = [(0, 0, 0)]
    for j in range(1, s + 1):
        st.append((0, 0, j))
    for i in range(1, m + 1):
        st.append((i, 0, s))
    for j in range(1, m + 1):
        st.append((m, j, s))
    for j in range(s + 1, m + 1):
        st.append((m, m, j))
    return tuple(st)


def _path_3piece(s, t, m):
    st = [(0, 0, 0)]
    for j in range(1, s + 1):
        st.append((0, 0, j))
    for i in range(1, m + 1):
        st.append((i, 0, s))
    for j in range(s + 1, t + 1):
        st.append((m, 0, j))
    for j in range(1, m + 1):
        st.append((m, j, t))
    for j in range(t + 1, m + 1):
        st.append((m, m, j))
    return tuple(st)


def test_2cut_formulas_match_closure_heights():
    # the reduced (Q1,Q2) formulas are exact for the 2-cut, over all s
    w = decide_caps_labeling(4, (1, 3, 5))["witness_order"]
    P = [step_profile(list(module_orders(w, 4)[b]), 3) for b in range(3)]
    m = 27
    for s in range(m + 1):
        h, _ = closure_heights(P, _path_2cut(s, m))
        q1, q2 = parent_heights_2cut(P[0], P[1], P[2], s)
        assert (h[1], h[2]) == (q1, q2), (s, (h[1], h[2]), (q1, q2))
        assert h[0] == 1  # q_0 stays 1 for every s (face-language theorem)


def test_3piece_formulas_match_closure_heights_on_face():
    # Exhaustive small validation of the two-cut extension on q0=1 face children.
    profiles = [
        step_profile(list(order), 1)
        for order in itertools.permutations(range(3))
    ]
    profiles = [profile for profile in profiles if profile.heights[0] == 1]
    m = 3
    for m0 in profiles:
        for m1 in profiles:
            for m2 in profiles:
                for s in range(m + 1):
                    for t in range(s, m + 1):
                        h, _ = closure_heights([m0, m1, m2], _path_3piece(s, t, m))
                        assert h[0] == 1
                        assert (h[1], h[2]) == parent_heights_3piece(m0, m1, m2, s, t)


def test_3piece_order_matches_formula_on_F4_modules():
    w = decide_caps_labeling(4, (1, 3, 5))["witness_order"]
    P = [step_profile(list(module_orders(w, 4)[b]), 3) for b in range(3)]
    for s, t in [(0, 8), (8, 11), (11, 27)]:
        order = order_3piece(P[0], P[1], P[2], s, t)
        parent = step_profile(order, 4)
        q1, q2 = parent_heights_3piece(P[0], P[1], P[2], s, t)
        assert parent.heights == (1, q1, q2)


def test_2cut_reconstructed_order_realizes_F4():
    # a clean 2-cut of the optimal modules realises F_4 = 15 (shape (1,3,5))
    w = decide_caps_labeling(4, (1, 3, 5))["witness_order"]
    P = [step_profile(list(module_orders(w, 4)[b]), 3) for b in range(3)]
    best = min(
        parent_heights_2cut(P[0], P[1], P[2], s)[0]
        * parent_heights_2cut(P[0], P[1], P[2], s)[1]
        for s in range(28)
    )
    assert best == 15


def test_2cut_state_formulas_match_step_profile_at_b1_to_b2():
    # Exhaustive small validation: the reduced (pre_1,suf_2) state is closed under
    # the 2-cut, not just the terminal height pair.
    profiles = [step_profile(order, 1) for order in itertools.permutations(range(3))]
    for m0 in profiles:
        for m1 in profiles:
            for m2 in profiles:
                for s in range(4):
                    order = order_2cut(m0, m1, m2, s)
                    parent = step_profile(order, 2)
                    pre1, suf2 = parent_state_2cut(m0, m1, m2, s)
                    assert pre1 == parent.prefix[1]
                    assert suf2 == parent.suffix[2]


def test_2cut_state_formulas_match_F4_witness_modules():
    w = decide_caps_labeling(4, (1, 3, 5))["witness_order"]
    P = [step_profile(list(module_orders(w, 4)[b]), 3) for b in range(3)]
    for s in range(28):
        order = order_2cut(P[0], P[1], P[2], s)
        parent = step_profile(order, 4)
        pre1, suf2 = parent_state_2cut(P[0], P[1], P[2], s)
        assert pre1 == parent.prefix[1]
        assert suf2 == parent.suffix[2]


def test_portfolio_cut_certificate_matches_F4_witness_modules():
    w = decide_caps_labeling(4, (1, 3, 5))["witness_order"]
    P = [step_profile(list(module_orders(w, 4)[b]), 3) for b in range(3)]

    certs = portfolio_cut_certificates(P[0], P[1], P[2])

    assert [p.heights for p in P] == [(1, 3, 3), (1, 2, 5), (1, 3, 5)]
    assert [cert.cut for cert in certs] == [8, 9, 10, 11]
    assert {(cert.need_pre1, cert.need_suf2) for cert in certs} == {(1, 2)}
    assert {(cert.pre1_at_cut, cert.suf2_after_cut) for cert in certs} == {(1, 2)}
    assert {(cert.parent_q1, cert.parent_q2) for cert in certs} == {(3, 5)}


def test_portfolio_cut_certificate_matches_cached_F5_witness_modules():
    data_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "L5_refutation.json",
    )
    with open(data_path, encoding="utf-8") as handle:
        order = json.load(handle)["witnesses"]["(1, 5, 5)"]["order"]
    P = [step_profile(list(module_orders(order, 5)[b]), 4) for b in range(3)]

    certs = portfolio_cut_certificates(P[0], P[1], P[2])

    assert [p.heights for p in P] == [(1, 5, 3), (1, 4, 5), (1, 5, 5)]
    assert [cert.cut for cert in certs] == [24, 25, 26, 27]
    assert {(cert.need_pre1, cert.need_suf2) for cert in certs} == {(1, 2)}
    assert {(cert.pre1_at_cut, cert.suf2_after_cut) for cert in certs} == {(1, 2)}
    assert {(cert.parent_q1, cert.parent_q2) for cert in certs} == {(5, 5)}
