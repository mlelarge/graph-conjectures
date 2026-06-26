import itertools
import os
import sys


SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from stilde_crossing_recursion import direct_q  # noqa: E402
from stilde_face_language import (  # noqa: E402
    is_q0_face,
    path_has_m0_before_m1,
    q0_face_recursive_condition,
)
from stilde_profile_closure import (  # noqa: E402
    closure_heights,
    reconstruct_order,
    step_profile,
)


def _paths(m, valid):
    out = []

    def rec(state, path):
        if state == (m, m, m):
            out.append(tuple(path))
            return
        for module in range(3):
            if state[module] >= m:
                continue
            if valid and module == 1 and state[0] < m:
                continue
            nxt = list(state)
            nxt[module] += 1
            rec(tuple(nxt), path + [tuple(nxt)])

    rec((0, 0, 0), [(0, 0, 0)])
    return out


def test_depth2_face_language_equivalence_exhaustive():
    count = 0
    face_count = 0
    for order in itertools.permutations(range(9)):
        direct = is_q0_face(order, 2)
        assert direct == q0_face_recursive_condition(order, 2)
        count += 1
        face_count += int(direct)
    assert count == 362880
    assert face_count == 2268


def test_m2_floating_does_not_break_q0_face():
    face_children = [
        step_profile(order, 1)
        for order in itertools.permutations(range(3))
        if direct_q(order, 1, 0) == 1
    ]
    valid_paths = _paths(3, valid=True)
    assert len(valid_paths) == 84
    for children in itertools.product(face_children, repeat=3):
        for path in valid_paths:
            heights, _ = closure_heights(children, path)
            assert heights[0] == 1
            order = reconstruct_order([child.order for child in children], path)
            assert is_q0_face(order, 2)


def test_invalid_face_path_creates_q0_backedge():
    child = step_profile((0, 1, 2), 1)
    invalid_path = (
        (0, 0, 0),
        (0, 1, 0),
        (1, 1, 0),
        (2, 1, 0),
        (3, 1, 0),
        (3, 2, 0),
        (3, 3, 0),
        (3, 3, 1),
        (3, 3, 2),
        (3, 3, 3),
    )
    assert not path_has_m0_before_m1(invalid_path)
    heights, _ = closure_heights([child, child, child], invalid_path)
    order = reconstruct_order([child.order] * 3, invalid_path)
    assert heights[0] == 2
    assert not is_q0_face(order, 2)

