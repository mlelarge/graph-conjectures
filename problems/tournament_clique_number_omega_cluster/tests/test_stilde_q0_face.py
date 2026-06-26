import os
import sys


SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from stilde_q0_face import face_min_product, face_pareto_frontier  # noqa: E402


def test_face_minima_F1_to_F4():
    # F_k = min{q1 q2 : q0=1} = 2, 4, 8, 15 (equal to L_k through depth 4)
    assert face_min_product(1)[0] == 2
    assert face_min_product(2)[0] == 4
    assert face_min_product(3)[0] == 8
    assert face_min_product(4)[0] == 15
    # the depth-4 face optimum is the balanced (1,3,5), not two-free
    assert face_min_product(4)[1] == (1, 3, 5)


def test_face_pareto_frontier_b2_is_small():
    # the 2-objective face frontier is small at B_2 (53), unlike the full problem
    front = face_pareto_frontier(2)
    assert front["pareto_minimal"] == 53
    assert front["height_pairs"] == [(1, 4), (2, 2), (2, 3), (3, 2), (3, 3), (4, 1)]
