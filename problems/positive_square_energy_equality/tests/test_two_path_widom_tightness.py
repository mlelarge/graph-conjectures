"""Regression harness for the finite-$n$ proof of $\\delta^-(L_n) \\ge 17/16$
on 2-paths $L_n = P_n^2$.

Companion to ``docs/lprime_two_paths_finite.md`` (plan v8 step 5c). Asserts:

1. **Direct verification** for $n\\in[4,200]$: $\\delta^-(L_n) \\ge 17/16$.
2. **Convergence to Szegő limit**: $|\\delta^-(L_{200})-\\delta^-_\\infty|<10^{-3}$.
3. **Worst-case localization**: $\\min_{n\\in[4,200]}\\delta^-(L_n)$ is attained at $n=6$.
4. **Empirical $O(1/n)$ tail constant**: $n\\cdot|\\delta^-(L_n)-\\delta^-_\\infty|\\le 1$ for $n\\in[4,200]$
   (loose verification of the BBG-style finite-$n$ asymptotic used in the conditional tail argument).

Side effect: writes ``data/two_path_widom_gaps.json`` with one record per $n$.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from spectrum_check import s_plus_minus  # noqa: E402
from family_check import two_path  # noqa: E402

THRESHOLD = 17.0 / 16.0
DELTA_INF = (32.0 * math.pi - 27.0 * math.sqrt(3.0)) / (12.0 * math.pi)
SZEGO_SLACK = DELTA_INF - THRESHOLD  # ~ 0.3637

DATA_DIR = ROOT / "data"
GAPS_JSON = DATA_DIR / "two_path_widom_gaps.json"

N_MAX = 200  # match the range of data/two_path_ear_gains.json


def _delta_minus(n: int) -> float:
    """Compute $\\delta^-(L_n) = s^-(L_n) - s^-(L_{n-1})$ via eigvalsh.

    `two_path(k)` builds $L_{k+2}$, so $L_n$ corresponds to `two_path(n-2)`.
    """
    G = two_path(n - 2)
    H = two_path(n - 3)
    full = s_plus_minus(G)
    sub = s_plus_minus(H)
    return float(full["s_minus"] - sub["s_minus"])


def _compute_records() -> list[dict]:
    records: list[dict] = []
    for n in range(4, N_MAX + 1):
        d = _delta_minus(n)
        records.append(
            {
                "n": n,
                "delta_minus": d,
                "gap_to_szego": d - DELTA_INF,
            }
        )
    return records


def _ensure_records() -> list[dict]:
    """Compute records once, cache to disk, and reuse across tests."""
    if GAPS_JSON.exists():
        try:
            with open(GAPS_JSON) as f:
                cached = json.load(f)
            if isinstance(cached, list) and len(cached) == N_MAX - 3:
                ns = [rec["n"] for rec in cached]
                if ns == list(range(4, N_MAX + 1)):
                    return cached
        except (json.JSONDecodeError, KeyError):
            pass
    records = _compute_records()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(GAPS_JSON, "w") as f:
        json.dump(records, f, indent=2)
    return records


def test_delta_minus_above_threshold():
    """delta-(L_n) >= 17/16 for every n in [4, 200]. The core 5c claim."""
    records = _ensure_records()
    for rec in records:
        n = rec["n"]
        d = rec["delta_minus"]
        assert d >= THRESHOLD, (
            f"FAIL at n={n}: delta-={d:.6f} < 17/16={THRESHOLD:.6f}"
        )


def test_convergence_to_szego_limit():
    """|delta-(L_{200}) - delta-_inf| < 1e-3 (rate verification)."""
    records = _ensure_records()
    d_200 = next(rec["delta_minus"] for rec in records if rec["n"] == N_MAX)
    err = abs(d_200 - DELTA_INF)
    assert err < 1e-3, (
        f"|delta-(L_{N_MAX}) - delta-_inf| = {err:.6e} not < 1e-3"
    )


def test_worst_case_at_n6():
    """Tabulate gap delta-(L_n)-delta-_inf; argmin of delta-(L_n) is n=6."""
    records = _ensure_records()
    worst = min(records, key=lambda r: r["delta_minus"])
    assert worst["n"] == 6, (
        f"argmin n = {worst['n']}, expected 6. min delta- = {worst['delta_minus']:.6f}"
    )
    # The minimum is approx 1.31901 (asserted with slack)
    assert abs(worst["delta_minus"] - 1.319007) < 1e-4, (
        f"min delta- at n=6 = {worst['delta_minus']:.6f}, expected ~1.31901"
    )


def test_empirical_O_one_over_n_tail():
    """Loose verification of BBG-style O(1/n) tail: n * |delta-(L_n)-delta-_inf| <= 1.

    The constant $K_*$ for which $|\\delta^-(L_n)-\\delta^-_\\infty|\\le K_*/n$ holds
    uniformly in $n\\in[4,200]$ is empirically $\\le 0.65$ (attained at $n=6$).
    We test $K_*\\le 1$, leaving slack for floating-point noise.
    """
    records = _ensure_records()
    worst_K = 0.0
    worst_n = None
    for rec in records:
        n = rec["n"]
        K = n * abs(rec["gap_to_szego"])
        if K > worst_K:
            worst_K = K
            worst_n = n
    assert worst_K <= 1.0, (
        f"O(1/n) tail constant n*|gap| reached {worst_K:.4f} at n={worst_n}, expected <=1"
    )


def test_szego_slack_strict():
    """Sanity: delta-_inf - 17/16 > 0.36 (independent of finite-$n$ check)."""
    assert SZEGO_SLACK > 0.36, (
        f"Szegő limit slack {SZEGO_SLACK:.6f} <= 0.36 -- 5b precondition broken"
    )


def test_data_file_written_and_consistent():
    """Round-trip the JSON cache and check schema."""
    records = _ensure_records()
    assert GAPS_JSON.exists(), f"missing {GAPS_JSON}"
    with open(GAPS_JSON) as f:
        cached = json.load(f)
    assert isinstance(cached, list)
    assert len(cached) == N_MAX - 3, (
        f"record count {len(cached)} != {N_MAX - 3}"
    )
    for rec in cached:
        assert set(rec.keys()) >= {"n", "delta_minus", "gap_to_szego"}
        assert 4 <= rec["n"] <= N_MAX
        assert isinstance(rec["delta_minus"], float)
        assert isinstance(rec["gap_to_szego"], float)
    assert cached == records


def test_trace_identity_at_each_n():
    """delta+(L_n) + delta-(L_n) = 4 to numerical precision.

    Trace identity: tr A(L_n)^2 - tr A(L_{n-1})^2 = 2*(2n-3) - 2*(2(n-1)-3) = 4.
    """
    for n in range(4, 51):
        G = two_path(n - 2)
        H = two_path(n - 3)
        full = s_plus_minus(G)
        sub = s_plus_minus(H)
        d_plus = full["s_plus"] - sub["s_plus"]
        d_minus = full["s_minus"] - sub["s_minus"]
        assert abs(d_plus + d_minus - 4.0) < 1e-10, (
            f"n={n}: delta+ + delta- = {d_plus + d_minus:.10f} != 4"
        )


if __name__ == "__main__":
    # Manual driver for quick local check.
    tests = [
        test_delta_minus_above_threshold,
        test_convergence_to_szego_limit,
        test_worst_case_at_n6,
        test_empirical_O_one_over_n_tail,
        test_szego_slack_strict,
        test_data_file_written_and_consistent,
        test_trace_identity_at_each_n,
    ]
    for t in tests:
        t()
        print(f"OK  {t.__name__}")
    print(f"\nAll {len(tests)} tests passed.")
    print(f"Data written to: {GAPS_JSON}")
