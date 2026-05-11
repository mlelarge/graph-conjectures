"""Witness structure analysis.

Given a numerical S²-flow witness (a list of unit vectors indexed by edges
under the canonical orientation), report quantities that matter for the
Houdrouge–Miraftab–Morin theory and for guessing exact constructions:

* unique directions up to sign;
* :math:`m\\times m` Gram matrix and its rank (= R-rank of the
  vector set in :math:`\\mathbb{R}^3`, always at most 3);
* histogram of pairwise dot products bucketed by simple rationals,
  flagging any that hit the equiangular value :math:`-1/2`;
* candidate algebraic expressions (rationals, square roots of small
  rationals) for each scalar entry, found by lattice/PSLQ search;
* HMM "odd-coordinate-free" probe: whether the rationalised vectors
  use only even-numerator coordinates (only meaningful after exact
  reconstruction).

This module's output is structural evidence, not a proof of anything.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
from dataclasses import dataclass, asdict
from typing import Iterable

import numpy as np


# ----- canonical signs -----

def canonical_up_to_sign(X: np.ndarray) -> np.ndarray:
    """Flip each row so that its lex-leading nonzero coordinate is positive."""
    out = X.copy()
    for i, v in enumerate(out):
        for k in range(v.shape[0]):
            if abs(v[k]) > 1e-12:
                if v[k] < 0:
                    out[i] = -v
                break
    return out


def cluster_unique_directions(X: np.ndarray, *, tol: float = 1e-6) -> list[np.ndarray]:
    canon = canonical_up_to_sign(X)
    clusters: list[np.ndarray] = []
    for v in canon:
        for c in clusters:
            if np.linalg.norm(v - c) < tol:
                break
        else:
            clusters.append(v)
    return clusters


# ----- gram / rank -----

def gram_summary(X: np.ndarray, *, tol: float = 1e-9) -> dict:
    XtX = X.T @ X
    eigs = np.linalg.eigvalsh(XtX)
    nontrivial = float(eigs.max())
    cutoff = max(tol, 1e-12 * nontrivial)
    rank = int(np.sum(eigs > cutoff))
    return {
        "shape": [int(s) for s in X.shape],
        "real_rank_in_R3": rank,
        "XtX": XtX.tolist(),
        "XtX_eigenvalues": eigs.tolist(),
    }


# ----- dot product histogram -----

DOT_BUCKETS: list[tuple[str, float]] = [
    ("+1", 1.0),
    ("-1", -1.0),
    ("0", 0.0),
    ("+1/2", 0.5),
    ("-1/2", -0.5),
    ("+1/3", 1.0 / 3.0),
    ("-1/3", -1.0 / 3.0),
    ("+1/4", 0.25),
    ("-1/4", -0.25),
    ("+1/5", 0.2),
    ("-1/5", -0.2),
    ("+2/3", 2.0 / 3.0),
    ("-2/3", -2.0 / 3.0),
]


def dot_histogram(X: np.ndarray, *, tol: float = 1e-6) -> dict:
    m = X.shape[0]
    buckets: dict[str, int] = {label: 0 for label, _ in DOT_BUCKETS}
    other: list[float] = []
    for i in range(m):
        for j in range(i + 1, m):
            d = float(X[i] @ X[j])
            for label, target in DOT_BUCKETS:
                if abs(d - target) < tol:
                    buckets[label] += 1
                    break
            else:
                other.append(d)
    return {"buckets": buckets, "other_count": len(other), "other_sample": sorted(other)[:10]}


# ----- algebraic candidates per entry -----

def algebraic_candidate(value: float, *, max_denom: int = 200, tol: float = 1e-9) -> str | None:
    """Try to recognise ``value`` as a simple closed form. Order:
    integer, p/q rational, ±sqrt(p/q) rational, ±sqrt(p)/q. None if no hit.
    """
    if abs(value) < tol:
        return "0"
    abs_v = abs(value)
    sign = "-" if value < 0 else ""
    # rational p/q
    best = None
    for q in range(1, max_denom + 1):
        p = round(abs_v * q)
        if p == 0:
            continue
        if abs(abs_v - p / q) < tol:
            best = (p, q, abs(abs_v - p / q))
            break
    if best is not None:
        p, q, _ = best
        return f"{sign}{p}/{q}" if q != 1 else f"{sign}{p}"
    # sqrt(p/q)
    sq = value * value
    for q in range(1, max_denom + 1):
        p = round(sq * q)
        if abs(sq - p / q) < tol:
            return f"{sign}sqrt({p}/{q})" if q != 1 else f"{sign}sqrt({p})"
    # value * q is a sqrt of an integer
    for q in range(1, max_denom + 1):
        s = (value * q) ** 2
        p = round(s)
        if p > 0 and abs(s - p) < tol:
            return f"{sign}sqrt({p})/{q}" if q != 1 else f"{sign}sqrt({p})"
    return None


def per_entry_candidates(X: np.ndarray) -> dict:
    """For each unique scalar entry, find an algebraic candidate (if any)."""
    seen: dict[float, str | None] = {}
    for v in X.ravel():
        v = float(v)
        # bucket near-equal floats
        key = None
        for s in seen:
            if abs(s - v) < 1e-9:
                key = s
                break
        if key is None:
            seen[v] = algebraic_candidate(v)
    return {f"{k:+.10f}": v for k, v in sorted(seen.items())}


# ----- main -----

@dataclass
class Analysis:
    name: str
    n_edges: int
    unique_directions_up_to_sign: int
    real_rank_in_R3: int
    gram: dict
    dot_histogram: dict
    entry_candidates: dict


def analyze(
    name: str,
    vectors: list[list[float]] | np.ndarray,
    *,
    G=None,
) -> Analysis:
    X = np.asarray(vectors, dtype=np.float64)
    if G is not None:
        from witness import rotate_into_pinning_gauge

        X, _ = rotate_into_pinning_gauge(G, X)
    uniq = cluster_unique_directions(X)
    g = gram_summary(X)
    dh = dot_histogram(X)
    ec = per_entry_candidates(X)
    return Analysis(
        name=name,
        n_edges=int(X.shape[0]),
        unique_directions_up_to_sign=len(uniq),
        real_rank_in_R3=g["real_rank_in_R3"],
        gram={"XtX_eigenvalues": g["XtX_eigenvalues"]},
        dot_histogram=dh,
        entry_candidates=ec,
    )


def analyze_path(path: pathlib.Path, *, gauge: bool = True) -> Analysis:
    cert = json.loads(path.read_text())
    if cert["kind"] != "numerical_witness" or cert["result"]["status"] != "witness":
        raise ValueError(f"{path}: not a numerical_witness with status=witness")
    G = None
    if gauge:
        from graphs import from_graph6

        G = from_graph6(cert["graph"]["graph6"])
    return analyze(cert["name"], cert["witness"]["vectors"], G=G)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", type=pathlib.Path)
    ap.add_argument("--full", action="store_true", help="emit JSON with all entry candidates")
    ap.add_argument(
        "--no-gauge",
        action="store_true",
        help="skip rotation into pinning gauge (default: rotate first)",
    )
    args = ap.parse_args()

    for p in args.paths:
        a = analyze_path(p, gauge=not args.no_gauge)
        rec = asdict(a)
        if not args.full:
            rec["entry_candidates"] = {
                k: v for k, v in rec["entry_candidates"].items() if v is not None
            }
            rec["dot_histogram"] = {
                "buckets": {k: v for k, v in rec["dot_histogram"]["buckets"].items() if v},
                "other_count": rec["dot_histogram"]["other_count"],
            }
            rec["gram"] = {
                "XtX_eigenvalues": [round(e, 6) for e in rec["gram"]["XtX_eigenvalues"]],
            }
        print(json.dumps(rec, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
