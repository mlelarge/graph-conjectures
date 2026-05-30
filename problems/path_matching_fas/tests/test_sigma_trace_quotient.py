"""Regression tests for the low-hit sigma-trace quotient probe."""

from __future__ import annotations

import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from sigma_trace_quotient_probe import (  # noqa: E402
    quotient_collision_report,
    random_tournament,
)
from sleeping_block_skew_sweep import SKEW_TEMPLATES  # noqa: E402


def test_sigma_trace_has_no_collision_on_skew_templates() -> None:
    """The low-hit trace survives the three n=12 skew templates."""
    expected = {
        "one_block": (180, 178),
        "skew_induction": (110, 98),
        "wake1_failure": (967, 816),
    }
    for name, T in SKEW_TEMPLATES.items():
        rep = quotient_collision_report(T, mode="sets")
        assert not rep["has_collision"], (name, rep["first_collision"])
        assert (rep["max_full_states"], rep["max_quotient_classes"]) == expected[name]


def test_sigma_trace_has_no_collision_on_n7_minimal_no_catalogue() -> None:
    path = os.path.join(ROOT, "data", "minimal_no_obstruction_catalogue_n7.json")
    with open(path) as f:
        data = json.load(f)
    for record in data["records"]:
        rep = quotient_collision_report(record["T"], mode="sets")
        assert not rep["has_collision"], (record["name"], rep["first_collision"])
        assert rep["accepted"] is False


def test_sigma_trace_has_no_collision_on_random_n7_sample() -> None:
    rng = random.Random(20260528)
    for _ in range(30):
        T = random_tournament(7, rng)
        rep = quotient_collision_report(T, mode="sets")
        assert not rep["has_collision"], rep["first_collision"]


def test_sigma_trace_stronger_modes_agree_on_one_block() -> None:
    T = SKEW_TEMPLATES["one_block"]
    baseline = None
    for mode in ("sets", "ordered", "cuts"):
        rep = quotient_collision_report(T, mode=mode)
        assert not rep["has_collision"], rep["first_collision"]
        pair = (rep["max_full_states"], rep["max_quotient_classes"])
        if baseline is None:
            baseline = pair
        assert pair == baseline
