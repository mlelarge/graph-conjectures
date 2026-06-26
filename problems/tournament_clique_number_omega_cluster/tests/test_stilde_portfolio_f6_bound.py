import os
import sys

SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from stilde_portfolio_f6_bound import diagnose, structured_build  # noqa: E402


def test_regeneration_obstruction_is_M2_structure_not_companions():
    facts = diagnose()
    # (1) the three (5,7)-portfolio companions all EXIST at depth 5 -> not the issue
    assert tuple(facts["companions_57_exist"]["(1, 5, 7)"]) == (1, 5, 7)
    assert tuple(facts["companions_57_exist"]["(1, 5, 5)"]) == (1, 5, 5)
    assert tuple(facts["companions_57_exist"]["(1, 4, 7)"]) == (1, 4, 7)
    # (2) an arbitrary (1,5,7) witness gives a blown-up 2-cut: q2 stacks to 12,
    #     product 60 >> target 35 (no single cut suppresses pre1 and suf2 together)
    assert facts["arbitrary_M2_best_2cut"]["product"] >= 36
    assert facts["arbitrary_M2_best_2cut"]["heights"][2] >= 8
    # (3) the structured depth-5 optimum (1,5,5) has NO simultaneous small cut, so
    #     it cannot serve as M2 to grow a depth-6 parent
    cuts = facts["structured_1_5_5_simultaneous_cuts"]
    assert cuts["(1,2)"] == 0
    assert cuts["(2,2)"] == 0


def test_self_similar_recursion_breaks():
    # the naive fixed-shape self-similar M2 chain does not survive to depth 5
    assert structured_build(5, 7, 4) is not None
    assert structured_build(5, 7, 5) is None
