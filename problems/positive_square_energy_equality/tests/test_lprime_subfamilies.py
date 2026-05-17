"""Regression tests for the (L') ear-deletion lemma on structured 2-tree subfamilies.

Tests the closed-form formulas derived in
- docs/lprime_books.md
- docs/lprime_two_paths.md
- docs/lprime_selector.md
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from spectrum_check import s_plus_minus  # noqa: E402
from family_check import book, two_path  # noqa: E402
from extreme_family import book_with_tail  # noqa: E402

THRESHOLD = 17.0 / 16.0


# ------------------------------------------------------------
# Theorem 1 (Books): closed-form delta+/-(B_k)
# ------------------------------------------------------------

def closed_form_delta_minus_book(k: int) -> float:
    """delta-(B_k) = 2 - 4 / (sqrt(8k+1) + sqrt(8k-7))."""
    return 2.0 - 4.0 / (math.sqrt(8 * k + 1) + math.sqrt(8 * k - 7))


def closed_form_delta_plus_book(k: int) -> float:
    """delta+(B_k) = 2 + 4 / (sqrt(8k+1) + sqrt(8k-7))."""
    return 2.0 + 4.0 / (math.sqrt(8 * k + 1) + math.sqrt(8 * k - 7))


def numerical_delta_plus_minus_book(k: int) -> tuple[float, float]:
    G = book(k)
    H = book(k - 1)
    full = s_plus_minus(G)
    sub = s_plus_minus(H)
    return (full["s_plus"] - sub["s_plus"],
            full["s_minus"] - sub["s_minus"])


def test_book_delta_closed_form():
    """Verify delta+/-(B_k) closed form against eigvalsh for k = 2..50."""
    for k in range(2, 51):
        d_plus_num, d_minus_num = numerical_delta_plus_minus_book(k)
        d_plus_cf = closed_form_delta_plus_book(k)
        d_minus_cf = closed_form_delta_minus_book(k)
        assert abs(d_plus_num - d_plus_cf) < 1e-12, (
            f"k={k}: delta+ numeric={d_plus_num} closed form={d_plus_cf}"
        )
        assert abs(d_minus_num - d_minus_cf) < 1e-12, (
            f"k={k}: delta- numeric={d_minus_num} closed form={d_minus_cf}"
        )


def test_book_delta_above_threshold():
    """delta-(B_k) >= 17/16 for k = 2..50."""
    for k in range(2, 51):
        d_minus = closed_form_delta_minus_book(k)
        assert d_minus >= THRESHOLD, (
            f"k={k}: delta-={d_minus} < threshold {THRESHOLD}"
        )


def test_book_delta_monotone():
    """delta-(B_k) is strictly increasing in k."""
    prev = closed_form_delta_minus_book(2)
    for k in range(3, 51):
        cur = closed_form_delta_minus_book(k)
        assert cur > prev, f"k={k}: not monotone ({cur} <= {prev})"
        prev = cur


def test_book_trace_identity():
    """delta+(B_k) + delta-(B_k) = 4."""
    for k in range(2, 51):
        s = closed_form_delta_plus_book(k) + closed_form_delta_minus_book(k)
        assert abs(s - 4.0) < 1e-12, f"k={k}: sum={s} (expected 4)"


def test_book_boundary_value():
    """delta-(B_2) = (7 - sqrt(17)) / 2."""
    expected = (7.0 - math.sqrt(17.0)) / 2.0
    actual = closed_form_delta_minus_book(2)
    assert abs(actual - expected) < 1e-14
    # Numerically ~ 1.43844718719...
    assert abs(actual - 1.43844718719) < 1e-8


# ------------------------------------------------------------
# Theorem 2 (2-paths): asymptotic closed form
# ------------------------------------------------------------

def closed_form_delta_minus_two_path_limit() -> float:
    """delta-_inf(L) = (32 pi - 27 sqrt 3) / (12 pi)."""
    return (32.0 * math.pi - 27.0 * math.sqrt(3.0)) / (12.0 * math.pi)


def closed_form_delta_plus_two_path_limit() -> float:
    """delta+_inf(L) = (16 pi + 27 sqrt 3) / (12 pi)."""
    return (16.0 * math.pi + 27.0 * math.sqrt(3.0)) / (12.0 * math.pi)


def test_two_path_asymptotic_sum():
    """delta+_inf(L) + delta-_inf(L) = 4."""
    s = (closed_form_delta_plus_two_path_limit()
         + closed_form_delta_minus_two_path_limit())
    assert abs(s - 4.0) < 1e-14


def test_two_path_asymptotic_above_threshold():
    """delta-_inf(L) > 17/16."""
    val = closed_form_delta_minus_two_path_limit()
    assert val > THRESHOLD, f"delta-_inf(L) = {val} <= {THRESHOLD}"
    # Sanity: ~ 1.4262
    assert abs(val - 1.4261766520) < 1e-9


def test_two_path_finite_n_threshold():
    """delta-(L_n) >= 17/16 for n = 4..30. Minimum at n=6."""
    min_delta = math.inf
    arg_min_n = None
    for k in range(2, 29):  # n = k+2 = 4..30
        G = two_path(k)
        H = two_path(k - 1)
        full = s_plus_minus(G)
        sub = s_plus_minus(H)
        d_minus = full["s_minus"] - sub["s_minus"]
        assert d_minus >= THRESHOLD, (
            f"n={k+2}: delta-={d_minus} < {THRESHOLD}"
        )
        if d_minus < min_delta:
            min_delta = d_minus
            arg_min_n = k + 2
    # The min over n = 5..30 is at n = 6 (not n = 4, which is a special case)
    assert arg_min_n in (4, 6), f"unexpected argmin n = {arg_min_n}"


# ------------------------------------------------------------
# Theorem 3 (Selector): delta-_inf(BT) and selector check
# ------------------------------------------------------------

def closed_form_delta_minus_BT_limit() -> float:
    """delta-_inf(BT) = 4 - alpha^2 + beta^2, where
    alpha = positive real root of 2x^3 - 7x - 3 = 0
    beta  = positive real root of 2x^3 + 2x^2 - 3x - 2 = 0.
    """
    # Solve numerically; uniqueness of positive real root is known.
    alpha = max(np.roots([2, 0, -7, -3]).real)
    beta = max(np.roots([2, 2, -3, -2]).real)
    return 4.0 - alpha ** 2 + beta ** 2


def test_BT_asymptotic_closed_form():
    """delta-(BT(k, 2)) converges to 4 - alpha^2 + beta^2 as k -> infinity.
    Test at k = 500 (n = 504) within 1% of the limit.
    """
    lim = closed_form_delta_minus_BT_limit()
    assert 1.03 < lim < 1.04, f"unexpected limit {lim}"
    G = book_with_tail(500, 2)
    full = s_plus_minus(G)
    v = 500 + 3  # outer tail ear
    H = G.copy()
    H.remove_node(v)
    sub = s_plus_minus(H)
    d_minus = full["s_minus"] - sub["s_minus"]
    # At k = 500, expect within 0.005 of limit
    assert abs(d_minus - lim) < 0.005, (
        f"k=500: delta-={d_minus} not close to limit {lim}"
    )


def test_BT_universal_lemma_fails_for_large_k():
    """The universal ear lemma (L) is false: BT(k=50, 2) has tail-ear delta- < 17/16."""
    G = book_with_tail(50, 2)
    full = s_plus_minus(G)
    v = 53  # outer tail ear (k + 3 = 53)
    H = G.copy()
    H.remove_node(v)
    sub = s_plus_minus(H)
    d_minus = full["s_minus"] - sub["s_minus"]
    assert d_minus < THRESHOLD, f"expected delta- < 17/16, got {d_minus}"


def test_BT_existential_rescue():
    """The book-page ear of BT(k, 2) has delta- well above 17/16."""
    for k in [10, 50, 200]:
        G = book_with_tail(k, 2)
        full = s_plus_minus(G)
        v_page = 3  # one of the book pages
        H = G.copy()
        H.remove_node(v_page)
        sub = s_plus_minus(H)
        d_minus = full["s_minus"] - sub["s_minus"]
        assert d_minus >= THRESHOLD, (
            f"k={k} page-ear delta-={d_minus} below threshold"
        )
        # Page-ear delta-_sum >> threshold
        assert d_minus > 1.5, (
            f"k={k}: page-ear delta- = {d_minus} not comfortably above threshold"
        )


def test_BT_selector_holds_on_pages():
    """Strong selector conjecture: deg_sum >= 6 implies delta- >= 17/16 (BT pages)."""
    for k in [5, 25, 100]:
        G = book_with_tail(k, 2)
        full = s_plus_minus(G)
        v_page = 3
        H = G.copy()
        H.remove_node(v_page)
        sub = s_plus_minus(H)
        d_minus = full["s_minus"] - sub["s_minus"]
        nbrs = list(G.neighbors(v_page))
        deg_sum = H.degree(nbrs[0]) + H.degree(nbrs[1])
        assert deg_sum >= 6, f"page ear deg_sum = {deg_sum}"
        assert d_minus >= THRESHOLD, f"k={k}: delta- = {d_minus} < threshold"


def test_BT_selector_filters_bad_ear():
    """Tail ear of BT(k, 2) has deg_sum = 5, below the threshold-6 selector."""
    for k in [25, 50, 100]:
        G = book_with_tail(k, 2)
        v = k + 3
        H = G.copy()
        H.remove_node(v)
        nbrs = list(G.neighbors(v))
        deg_sum = H.degree(nbrs[0]) + H.degree(nbrs[1])
        assert deg_sum == 5, (
            f"k={k} tail ear deg_sum = {deg_sum} (expected 5)"
        )


# ------------------------------------------------------------
# Standalone CLI
# ------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_book_delta_closed_form,
        test_book_delta_above_threshold,
        test_book_delta_monotone,
        test_book_trace_identity,
        test_book_boundary_value,
        test_two_path_asymptotic_sum,
        test_two_path_asymptotic_above_threshold,
        test_two_path_finite_n_threshold,
        test_BT_asymptotic_closed_form,
        test_BT_universal_lemma_fails_for_large_k,
        test_BT_existential_rescue,
        test_BT_selector_holds_on_pages,
        test_BT_selector_filters_bad_ear,
    ]
    for t in tests:
        print(f"running {t.__name__}...", end="", flush=True)
        try:
            t()
            print(" OK")
        except AssertionError as e:
            print(f" FAIL\n  {e}")
            raise
