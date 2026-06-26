import itertools
import os
import random
import sys


SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from stilde_profile_dp import (  # noqa: E402
    combine_bruteforce,
    combine_dp,
    compressed_labelsets,
    min_product_compressed,
)


def test_generation_dp_matches_bruteforce_b1_to_b2():
    rng = random.Random(0)
    perms = list(itertools.permutations(range(3)))
    for _ in range(10):
        triple = [list(rng.choice(perms)) for _ in range(3)]
        bf = {(p.prefix, p.suffix) for p in combine_bruteforce(triple, 1)}
        dp = {(p.prefix, p.suffix) for p in combine_dp(triple, 1)}
        assert bf == dp


def test_decision_compresses_to_16_and_reproduces_L3():
    # per-label Pareto frontier of B_2 profiles is 16 (uniform by cyclic sigma)
    labelsets = compressed_labelsets(2)
    assert [len(s) for s in labelsets] == [16, 16, 16]
    # the compressed decision reproduces L_3 = 8 without SAT
    product, _caps, sizes = min_product_compressed(2, max_cap=8)
    assert product == 8
    assert sizes == [16, 16, 16]
