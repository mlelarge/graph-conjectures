import os
import sys


SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from stilde_pod_profiles import arc_colour, pod_profile  # noqa: E402


def test_canonical_arc_colours_are_cyclic_first_difference():
    assert arc_colour(0, 1, 1) == 0
    assert arc_colour(1, 2, 1) == 1
    assert arc_colour(2, 0, 1) == 2

    # 01 -> 12 is decided by the first coordinate 0 -> 1.
    assert arc_colour(1, 5, 2) == 0
    # 12 -> 10 is decided by the second coordinate 2 -> 0.
    assert arc_colour(5, 3, 2) == 2


def test_directed_triangle_profile():
    profile = pod_profile([0, 1, 2], depth=1)
    assert profile["layer_heights"] == [1, 1, 2]
    assert profile["occupied_rank_triples"] == 2
    assert profile["largest_rank_fibre"] == 2
