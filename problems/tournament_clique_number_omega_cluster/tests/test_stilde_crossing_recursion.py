import itertools
import os
import random
import sys


SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from stilde_crossing_recursion import check_order, direct_q  # noqa: E402


def test_recursion_matches_direct_depth1_exhaustive():
    for perm in itertools.permutations(range(3)):
        assert check_order(list(perm), 1)


def test_recursion_matches_direct_sampled_depth2_and_3():
    rng = random.Random(0)
    for depth, trials in ((2, 200), (3, 50)):
        n = 3**depth
        for _ in range(trials):
            perm = list(range(n))
            rng.shuffle(perm)
            assert check_order(perm, depth), (depth, perm)


def test_killed_crossings_optimum_depth2_lex():
    # lexicographic order: two colours backward-free, one full chain 2^depth.
    order = list(range(9))
    heights = sorted(direct_q(order, 2, c) for c in range(3))
    assert heights == [1, 1, 4]
