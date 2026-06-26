import math
import os
import sys


SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from stilde_rank_entropy import entropy_profile  # noqa: E402


def test_entropy_chain_rule_on_directed_triangle():
    profile = entropy_profile([0, 1, 2], depth=1)
    assert math.isclose(
        profile["rank_entropy_bits"] + profile["conditional_entropy_bits"],
        math.log2(3),
    )
    assert profile["conditional_entropy_bits"] <= 1
