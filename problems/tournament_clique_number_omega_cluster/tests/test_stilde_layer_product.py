import os
import sys


SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from decide_stilde_layer_product import (  # noqa: E402
    decide_below_lex_product,
    decide_joint_minimum,
)


def test_layer_product_exact_through_depth_two():
    for depth in (1, 2):
        results = decide_below_lex_product(depth)
        assert results
        assert not any(result["sat"] for result in results)


def test_joint_minimum_at_depth_one():
    results = decide_joint_minimum(depth=1, clique_cap=2)
    satisfiable = [result for result in results if result["sat"]]
    assert min(result["product"] for result in satisfiable) == 2


def test_depth_three_layer_and_joint_minimum():
    below_eight = decide_below_lex_product(depth=3)
    assert not any(result["sat"] for result in below_eight)

    joint = decide_joint_minimum(depth=3, clique_cap=4)
    satisfiable = [result for result in joint if result["sat"]]
    assert min(result["product"] for result in satisfiable) == 8
    assert {tuple(result["caps"]) for result in satisfiable} == {(2, 2, 2)}
