"""Pin the mixed-2-cut seam invariant and rule for Sub-lemma A-prime."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import seam_invariant as SI  # noqa: E402


def test_rule_predicts_all_non_base_L6_L7():
    n_ok, n_total, mismatches, rows = SI.verify_L6_L7()
    assert n_total == 40, n_total
    assert mismatches == [], mismatches
    assert n_ok == 40, (n_ok, n_total)


def test_three_tree_join_members_have_MC_zero():
    _, _, _, rows = SI.verify_L6_L7()
    tree = [r for r in rows if r["actual"] == "tree-join"]
    assert {(r["n"], r["index"]) for r in tree} == {(7, 7), (7, 14), (7, 36)}
    assert all(r["MC"] == 0 for r in tree)


def test_all_hajos_members_have_MC_positive():
    _, _, _, rows = SI.verify_L6_L7()
    hajos = [r for r in rows if r["actual"] == "hajos"]
    assert len(hajos) == 37
    assert all(r["MC"] >= 1 for r in hajos)


def test_small_consistency_L3_L5():
    rows = SI.verify_small_consistency()
    assert all(r["MC_matches_hajos"] for r in rows), rows


def test_proved_necessity_no_violation():
    # Hajos merge vertex => MC=1 is a theorem; data must never contradict it.
    assert SI.verify_necessity_direction() == []
