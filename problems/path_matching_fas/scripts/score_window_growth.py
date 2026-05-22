"""Empirical growth summaries for the score-window LFO solver."""
from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
from collections import defaultdict
from typing import Iterable

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lfo_score_window import find_lfo_order_score_window  # noqa: E402
from sweep import all_tournaments, canonical_key  # noqa: E402
from tournament_canonical import string_to_matrix  # noqa: E402


def summarize(values: list[int]) -> dict:
    if not values:
        return {
            "count": 0,
            "max": None,
            "median": None,
            "mean": None,
            "p95": None,
        }
    xs = sorted(values)
    idx95 = min(len(xs) - 1, math.ceil(0.95 * len(xs)) - 1)
    return {
        "count": len(xs),
        "max": max(xs),
        "median": statistics.median(xs),
        "mean": round(statistics.mean(xs), 3),
        "p95": xs[idx95],
    }


def ols(xs: list[float], ys: list[float]) -> dict:
    if len(xs) != len(ys) or len(xs) < 2:
        raise ValueError("need at least two paired observations")
    mx = statistics.mean(xs)
    my = statistics.mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        raise ValueError("x values are constant")
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    intercept = my - slope * mx
    yhat = [intercept + slope * x for x in xs]
    ss_res = sum((y - yh) ** 2 for y, yh in zip(ys, yhat))
    ss_tot = sum((y - my) ** 2 for y in ys)
    r2 = 1.0 if ss_tot == 0 else 1 - ss_res / ss_tot
    return {
        "slope": round(slope, 6),
        "intercept": round(intercept, 6),
        "r2": round(r2, 6),
    }


def regress_growth(rows: list[dict], metric: str = "max") -> dict:
    clean = [
        row for row in rows
        if row.get(metric) not in (None, 0) and row["n"] > 1
    ]
    ns = [row["n"] for row in clean]
    vals = [row[metric] for row in clean]
    if len(clean) < 2:
        return {"metric": metric, "error": "not enough rows"}
    return {
        "metric": metric,
        "rows": len(clean),
        "log_nodes_vs_n": ols([float(n) for n in ns], [math.log(v) for v in vals]),
        "log_nodes_vs_log_n": ols([math.log(n) for n in ns], [math.log(v) for v in vals]),
    }


def nonisomorphic_score_window_nodes(n: int) -> list[int]:
    seen = set()
    out = []
    for T in all_tournaments(n):
        key = canonical_key(T)
        if key in seen:
            continue
        seen.add(key)
        out.append(find_lfo_order_score_window(T)["nodes"])
    return out


def _n7_records(data_dir: str) -> Iterable[dict]:
    data = json.load(open(os.path.join(data_dir, "lfo_full_n7.json")))
    for bucket in data["buckets"]:
        yield from bucket["records"]


def _n9_sample_records(data_dir: str, stride: int) -> Iterable[tuple[dict, dict]]:
    reps_path = os.path.join(data_dir, "lfo_reps_n9.jsonl")
    results_path = os.path.join(data_dir, "lfo_census_n9_results.jsonl")
    with open(reps_path) as frep, open(results_path) as fres:
        for idx, (lr, ls) in enumerate(zip(frep, fres)):
            if idx % stride == 0:
                yield json.loads(lr), json.loads(ls)


def collect_growth(data_dir: str, n9_stride: int = 500, include_exact_small: bool = True) -> dict:
    rows = []

    if include_exact_small:
        for n in range(3, 7):
            rows.append({
                "n": n,
                "source": "exact_all_noniso",
                **summarize(nonisomorphic_score_window_nodes(n)),
            })

    n7_nodes = [
        find_lfo_order_score_window(rec["T"])["nodes"]
        for rec in _n7_records(data_dir)
    ]
    rows.append({
        "n": 7,
        "source": "exact_all_noniso",
        **summarize(n7_nodes),
    })

    n8_data = json.load(open(os.path.join(data_dir, "lfo_extend_census_n8.json")))
    n8_nodes = [
        find_lfo_order_score_window(rec["T"])["nodes"]
        for rec in n8_data["no_records"]
    ]
    rows.append({
        "n": 8,
        "source": "exact_no_records_only",
        **summarize(n8_nodes),
    })

    n9_by_kind: dict[str, list[int]] = defaultdict(list)
    for rep, result in _n9_sample_records(data_dir, n9_stride):
        T = string_to_matrix(rep["key"])
        kind = "yes" if result["has_lfo"] else result["no_kind"]
        n9_by_kind[kind].append(find_lfo_order_score_window(T)["nodes"])

    all_n9 = [node for values in n9_by_kind.values() for node in values]
    rows.append({
        "n": 9,
        "source": f"sample_stride_{n9_stride}",
        **summarize(all_n9),
        "by_kind": {kind: summarize(values) for kind, values in sorted(n9_by_kind.items())},
    })

    return {
        "rows": rows,
        "regression_mixed_max": regress_growth(rows, "max"),
        "regression_mixed_p95": regress_growth(rows, "p95"),
        "caveat": (
            "n=8 is NO-records only and n=9 is a stride sample; "
            "these regressions are descriptive, not asymptotic evidence."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    default_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
    )
    parser.add_argument("--data-dir", default=default_dir)
    parser.add_argument("--n9-stride", type=int, default=500)
    args = parser.parse_args()
    print(json.dumps(collect_growth(args.data_dir, args.n9_stride), indent=2))


if __name__ == "__main__":
    main()

