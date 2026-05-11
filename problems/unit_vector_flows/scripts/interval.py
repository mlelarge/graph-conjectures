"""Interval-Krawczyk existence/uniqueness certification for S²-flow witnesses.

A *replayable* certificate at schema version 2 stores enough metadata that
an independent verifier can reconstruct the polynomial system from the
graph6 string and pinning information, parse the center from decimal
strings at the stored precision, and recompute the Krawczyk operator on
the same box -- without trusting the stored ``K_box`` values.

Math. Square pinned system :math:`F : \\mathbb{R}^N \\to \\mathbb{R}^N`
with one orientation pinned vertex (auto-satisfying its Kirchhoff +
norm equations) and one redundant vertex dropped (the global Kirchhoff
sum is identically zero, so its conservation eqs follow from the rest).
The auxiliary symbol :math:`s` carries the relation :math:`s^2 = 3`.

For a candidate center :math:`c \\in \\mathbb{Q}^N` and a box
:math:`I = [c-r, c+r]`,

.. math::
    K(I) = c - Y F(c) + (E - Y J(I)) (I - c),  \\quad Y = J(c)^{-1}.

If :math:`K(I) \\subset \\mathrm{int}(I)` componentwise, then F has a
unique real zero in I (Krawczyk's theorem). Y is computed in extended
mpmath precision; all arithmetic in the inclusion test runs in
``mpmath.iv`` interval arithmetic.

Reproducibility. The certificate stores: the graph6 string of the
canonicalised graph; the canonical edge order; the pinning vertex,
edge ordering, signs, and target labels; the dropped redundant
vertex; the free-variable list; a SHA-256 of the polynomial system;
the SHA-256 of the source numerical witness; the radius and the
center as decimal strings at ``dps`` digits; and per-component
positive containment margins. ``replay_krawczyk(cert)`` reconstructs
all of this and re-runs the inclusion test from scratch.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import pathlib
import platform
import time
from dataclasses import dataclass, asdict
from typing import Any

import mpmath
import networkx as nx
import numpy as np
import sympy as sp
from mpmath import iv

from exact import build_ideal
from graphs import from_graph6, to_graph6
from witness import orient, rotate_into_pinning_gauge


SCHEMA_VERSION = 2

TARGET_LABELS = ("(1,0,0)", "(-1/2, s/2, 0)", "(-1/2, -s/2, 0)")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _provenance() -> dict[str, Any]:
    return {
        "host": platform.node(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "mpmath": mpmath.__version__,
        "sympy": sp.__version__,
        "numpy": np.__version__,
        "schema_version": SCHEMA_VERSION,
    }


def _poly_system_hash(polys: list[sp.Expr], free_vars: list[sp.Symbol]) -> str:
    """SHA-256 of a canonicalised string form of the polynomial system.

    Canonicalisation: each polynomial is re-expanded and serialised as
    ``sympy.srepr``; the variable list is serialised similarly. This is
    sympy-version-sensitive and so should be treated as informational
    (a hash mismatch suggests the verifier built a structurally different
    system or runs on a different sympy version, not a bug per se).
    """
    h = hashlib.sha256()
    h.update(b"vars:")
    for v in free_vars:
        h.update(sp.srepr(v).encode("ascii"))
        h.update(b";")
    h.update(b"polys:")
    for p in polys:
        h.update(sp.srepr(sp.expand(p)).encode("ascii"))
        h.update(b";")
    return h.hexdigest()


def _file_sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _mpf_str(x: mpmath.mpf, dps: int) -> str:
    return mpmath.nstr(x, dps, strip_zeros=False)


def _build_square_system(G: nx.Graph):
    polys, free_vars, sqrt3 = build_ideal(G, pin=True, drop_redundant=True)
    polys = polys + [sqrt3.as_expr()]
    return polys, list(free_vars)


def _candidate_from_witness(
    G: nx.Graph, X_witness: np.ndarray, free_vars: list
) -> list[float]:
    Xr, _ = rotate_into_pinning_gauge(G, X_witness)
    edges, sign = orient(G)
    v0 = next(iter(sign))
    pinned_edges = {k for k, _ in sign[v0]}
    by_name: dict[str, float] = {}
    for e in range(len(edges)):
        if e in pinned_edges:
            continue
        for j in range(3):
            by_name[f"x_{e}_{j}"] = float(Xr[e, j])
    by_name["s"] = float(np.sqrt(3.0))
    return [by_name[str(v)] for v in free_vars]


# ---------------------------------------------------------------------------
# Krawczyk inclusion test (the core kernel)
# ---------------------------------------------------------------------------


def _Fmax(F_func, c_vals) -> mpmath.mpf:
    F_list = F_func(*c_vals)
    return max(abs(mpmath.mpf(v)) for v in F_list)


def _newton_refine(F_func, J_func, c, *, n: int, dps: int, max_iters: int) -> tuple[list, mpmath.mpf]:
    prev_F = _Fmax(F_func, c)
    for _ in range(max_iters):
        F_c_list = F_func(*c)
        F_c_vec = mpmath.matrix(n, 1)
        for i, v in enumerate(F_c_list):
            F_c_vec[i, 0] = mpmath.mpf(v)
        J_c_list = J_func(*c)
        J_c = mpmath.matrix(n)
        for i in range(n):
            for j in range(n):
                J_c[i, j] = mpmath.mpf(J_c_list[i][j])
        try:
            delta = mpmath.lu_solve(J_c, F_c_vec)
        except (ZeroDivisionError, TypeError, mpmath.libmp.libhyper.NoConvergence):
            break
        c_new = [c[i] - delta[i, 0] for i in range(n)]
        new_F = _Fmax(F_func, c_new)
        if new_F > prev_F:
            break  # diverging; revert
        c = c_new
        prev_F = new_F
        if prev_F < mpmath.mpf(f"1e-{2 * dps - 5}"):
            break
    return c, prev_F


def _krawczyk_inclusion(
    F_func, J_func, c: list, radius: float | mpmath.mpf, dps: int, n: int
) -> dict:
    """Core Krawczyk inclusion check.

    Inputs are the lambdified F, J, the center c (as mpmath.mpf scalars),
    the radius (as float or mpf), and the system size n. Returns a dict
    with the inclusion verdict, per-component intervals/margins, F(c),
    and Y norm-info — everything a cert needs.
    """
    F_at_c_list = F_func(*c)
    F_at_c = mpmath.matrix(n, 1)
    for i, v in enumerate(F_at_c_list):
        F_at_c[i, 0] = mpmath.mpf(v)
    F_residual = max(abs(F_at_c[i, 0]) for i in range(n))

    J_c_list = J_func(*c)
    J_c = mpmath.matrix(n)
    for i in range(n):
        for j in range(n):
            J_c[i, j] = mpmath.mpf(J_c_list[i][j])
    try:
        Y = J_c ** (-1)
    except (ZeroDivisionError, TypeError, mpmath.libmp.libhyper.NoConvergence) as exc:
        return {
            "ok": False,
            "reason": f"J(c) inversion failed: {type(exc).__name__}: {exc}",
            "F_residual": F_residual,
        }

    radius_mp = mpmath.mpf(str(radius))
    box = [iv.mpf((c[i] - radius_mp, c[i] + radius_mp)) for i in range(n)]
    box_minus_c = [iv.mpf((-radius_mp, radius_mp)) for _ in range(n)]
    F_c_iv = [iv.mpf(F_at_c[i, 0]) for i in range(n)]
    J_box = J_func(*box)
    Y_iv = [[iv.mpf(Y[i, j]) for j in range(n)] for i in range(n)]

    margins_lo: list[mpmath.mpf] = []
    margins_hi: list[mpmath.mpf] = []
    K_a: list[mpmath.mpf] = []
    K_b: list[mpmath.mpf] = []
    for i in range(n):
        # K_i = c_i - sum_j Y_ij F(c)_j + sum_j (delta_ij - sum_k Y_ik J_box[k][j]) * (box_j - c_j)
        A = Y_iv[i][0] * F_c_iv[0]
        for j in range(1, n):
            A = A + Y_iv[i][j] * F_c_iv[j]
        B = iv.mpf(0)
        for j in range(n):
            inner = Y_iv[i][0] * J_box[0][j]
            for k in range(1, n):
                inner = inner + Y_iv[i][k] * J_box[k][j]
            coef = (iv.mpf(1) - inner) if i == j else (-inner)
            B = B + coef * box_minus_c[j]
        K_i = iv.mpf(c[i]) - A + B
        K_a.append(mpmath.mpf(K_i.a))
        K_b.append(mpmath.mpf(K_i.b))
        # positive margin = how far K[i] sits inside box[i] (positive => good)
        gap_lo = mpmath.mpf(K_i.a) - (c[i] - radius_mp)  # > 0: K_i.a above box low
        gap_hi = (c[i] + radius_mp) - mpmath.mpf(K_i.b)  # > 0: K_i.b below box high
        margins_lo.append(gap_lo)
        margins_hi.append(gap_hi)

    min_margin = min(min(margins_lo), min(margins_hi))
    return {
        "ok": min_margin > 0,
        "F_residual": F_residual,
        "K_a": K_a,
        "K_b": K_b,
        "margins_lo": margins_lo,
        "margins_hi": margins_hi,
        "min_margin": min_margin,
    }


# ---------------------------------------------------------------------------
# High-level certify and replay
# ---------------------------------------------------------------------------


@dataclass
class KrawczykResult:
    certified: bool
    name: str
    n: int
    m: int
    radius: float
    dps: int
    F_residual_at_center: float
    min_containment_margin: float
    elapsed_seconds: float
    notes: str


def krawczyk_certify(
    G: nx.Graph,
    X_witness: np.ndarray | list[list[float]],
    *,
    radius: float = 1e-5,
    dps: int = 50,
    name: str = "<unnamed>",
    refine_newton: int = 5,
    source_certificate_path: pathlib.Path | None = None,
) -> tuple[KrawczykResult, dict[str, Any]]:
    t0 = time.time()
    mpmath.mp.dps = dps
    iv.dps = dps

    polys, free_vars = _build_square_system(G)
    n = len(free_vars)
    candidate = _candidate_from_witness(
        G, np.asarray(X_witness, dtype=np.float64), free_vars
    )

    J_sym = sp.Matrix([[sp.diff(p, v) for v in free_vars] for p in polys])
    F_func = sp.lambdify(free_vars, polys, modules=None)
    J_func = sp.lambdify(free_vars, J_sym.tolist(), modules=None)

    c = [mpmath.mpf(x) for x in candidate]
    c, _ = _newton_refine(F_func, J_func, c, n=n, dps=dps, max_iters=refine_newton)

    inclusion = _krawczyk_inclusion(F_func, J_func, c, radius, dps, n)

    edges, sign = orient(G)
    v0 = next(iter(sign))
    last_v = list(sign.keys())[-1]
    pinned = sign[v0]

    cert: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": "interval_witness",
        "name": name,
        "graph": {
            "n": G.number_of_nodes(),
            "m": G.number_of_edges(),
            "graph6": to_graph6(G),
            "edges": [list(e) for e in edges],
            "orientation": "lex (u,v) with u<v points u->v",
        },
        "pinning": {
            "pinned_vertex": int(v0),
            "pinned_edge_indices": [int(k) for k, _ in pinned],
            "pinned_signs": [int(s) for _, s in pinned],
            "target_labels": list(TARGET_LABELS),
            "dropped_redundant_vertex": int(last_v),
        },
        "system": {
            "free_vars": [str(v) for v in free_vars],
            "n_free_vars": n,
            "n_polynomials": len(polys),
            "polynomial_hash_sha256": _poly_system_hash(polys, free_vars),
            "polynomial_hash_canonicalization": "sympy.expand then sympy.srepr per poly, joined",
        },
        "krawczyk": {
            "radius_decimal": str(radius),
            "dps": dps,
            "center_decimal": [_mpf_str(x, dps) for x in c],
            "F_residual_at_center_decimal": _mpf_str(inclusion["F_residual"], 30),
            "containment_margins_lo_decimal": [_mpf_str(g, 30) for g in inclusion.get("margins_lo", [])],
            "containment_margins_hi_decimal": [_mpf_str(g, 30) for g in inclusion.get("margins_hi", [])],
            "min_margin_decimal": (
                _mpf_str(inclusion["min_margin"], 30) if "min_margin" in inclusion else None
            ),
            "K_box_decimal": (
                [[_mpf_str(a, 30), _mpf_str(b, 30)] for a, b in zip(inclusion["K_a"], inclusion["K_b"])]
                if "K_a" in inclusion
                else None
            ),
        },
        "verdict": {
            "certified": bool(inclusion["ok"]),
            "method": "Krawczyk operator on square pinned system; mpmath.iv interval arithmetic",
            "criterion": "K(I) strictly inside int(I) componentwise",
            "reason": inclusion.get("reason", ""),
        },
        "witness_source": {
            "numerical_certificate_path": (
                str(source_certificate_path) if source_certificate_path else None
            ),
            "numerical_certificate_sha256": (
                _file_sha256(source_certificate_path) if source_certificate_path else None
            ),
        },
        "provenance": {
            **_provenance(),
            "elapsed_seconds": time.time() - t0,
            "timestamp_utc": _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        },
    }

    result = KrawczykResult(
        certified=bool(inclusion["ok"]),
        name=name,
        n=G.number_of_nodes(),
        m=G.number_of_edges(),
        radius=float(radius),
        dps=dps,
        F_residual_at_center=float(inclusion["F_residual"]),
        min_containment_margin=float(inclusion["min_margin"]) if "min_margin" in inclusion else float("nan"),
        elapsed_seconds=time.time() - t0,
        notes=inclusion.get("reason", "") or ("certified" if inclusion["ok"] else "K not strictly inside box"),
    )
    return result, cert


def replay_krawczyk(cert: dict[str, Any]) -> dict[str, Any]:
    """Independently re-verify an interval_witness certificate.

    Reconstructs the graph, polynomial system, and center from the cert,
    then re-runs the Krawczyk inclusion test using its own arithmetic.
    Returns a dict with ``ok`` (the verifier's verdict), the computed
    ``min_margin``, and consistency notes (e.g., polynomial-hash match).
    """
    if cert.get("schema_version") != SCHEMA_VERSION:
        return {
            "ok": False,
            "reason": f"unsupported schema_version {cert.get('schema_version')}; verifier expects {SCHEMA_VERSION}",
        }
    if cert.get("kind") != "interval_witness":
        return {"ok": False, "reason": f"not an interval_witness cert (kind={cert.get('kind')})"}

    dps = int(cert["krawczyk"]["dps"])
    mpmath.mp.dps = dps
    iv.dps = dps

    G = from_graph6(cert["graph"]["graph6"])

    # Verify edge ordering and pinning vertex match this codebase's canonical
    # construction so that the polynomial system is the one being re-checked.
    edges, sign = orient(G)
    if [list(e) for e in edges] != cert["graph"]["edges"]:
        return {"ok": False, "reason": "canonical edge order disagrees with cert"}
    expected_v0 = next(iter(sign))
    if int(expected_v0) != cert["pinning"]["pinned_vertex"]:
        return {"ok": False, "reason": "pinned vertex disagrees with cert"}
    expected_drop = list(sign.keys())[-1]
    if int(expected_drop) != cert["pinning"]["dropped_redundant_vertex"]:
        return {"ok": False, "reason": "dropped redundant vertex disagrees with cert"}

    polys, free_vars = _build_square_system(G)
    if [str(v) for v in free_vars] != cert["system"]["free_vars"]:
        return {"ok": False, "reason": "free-variable list disagrees with cert"}

    poly_hash = _poly_system_hash(polys, free_vars)
    poly_hash_match = poly_hash == cert["system"]["polynomial_hash_sha256"]

    J_sym = sp.Matrix([[sp.diff(p, v) for v in free_vars] for p in polys])
    F_func = sp.lambdify(free_vars, polys, modules=None)
    J_func = sp.lambdify(free_vars, J_sym.tolist(), modules=None)

    c = [mpmath.mpf(s) for s in cert["krawczyk"]["center_decimal"]]
    radius = mpmath.mpf(cert["krawczyk"]["radius_decimal"])
    n = len(c)

    inclusion = _krawczyk_inclusion(F_func, J_func, c, radius, dps, n)
    ok = bool(inclusion["ok"])

    return {
        "ok": ok,
        "min_margin": _mpf_str(inclusion["min_margin"], 30) if "min_margin" in inclusion else None,
        "F_residual_at_center": _mpf_str(inclusion["F_residual"], 30),
        "polynomial_hash_match": poly_hash_match,
        "polynomial_hash_recomputed": poly_hash,
        "verdict_matches_cert": ok == bool(cert["verdict"]["certified"]),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cert_path", type=pathlib.Path, nargs="+")
    ap.add_argument("--radius", type=float, default=1e-5)
    ap.add_argument("--dps", type=int, default=50)
    ap.add_argument(
        "--out",
        type=pathlib.Path,
        default=None,
        help="if set, write detailed JSON certificate(s) to this directory",
    )
    args = ap.parse_args()

    if args.out is not None:
        args.out.mkdir(parents=True, exist_ok=True)

    from witness import find_witness as _find_witness

    retry_seeds = [42, 1000, 7, 31337, 17, 99, 9999, 12345]

    for p in args.cert_path:
        if p.name == "summary.json":
            continue
        cert = json.loads(p.read_text())
        if not isinstance(cert, dict) or cert.get("kind") != "numerical_witness" or cert.get("result", {}).get("status") != "witness":
            print(f"{p}: not a numerical witness, skipping")
            continue
        G = from_graph6(cert["graph"]["graph6"])
        X = cert["witness"]["vectors"]
        result, detail = krawczyk_certify(
            G, X, radius=args.radius, dps=args.dps, name=cert["name"],
            source_certificate_path=p,
        )
        if not result.certified:
            for s in retry_seeds:
                r2 = _find_witness(G, restarts=50, seed=s, residual_threshold=1e-15)
                if r2.status != "witness":
                    continue
                result, detail = krawczyk_certify(
                    G, r2.vectors, radius=args.radius, dps=args.dps, name=cert["name"],
                    source_certificate_path=p,
                )
                if result.certified:
                    detail["retry_seed"] = s
                    break
        flag = "CERTIFIED" if result.certified else "FAILED"
        print(
            f"[{flag}] {result.name:14s} n={result.n:3d} m={result.m:3d}  "
            f"|F(c)|={result.F_residual_at_center:.2e}  "
            f"min_margin={result.min_containment_margin:.2e}  "
            f"radius={result.radius:.0e} dps={result.dps}  "
            f"elapsed={result.elapsed_seconds:.2f}s"
        )
        if args.out is not None:
            (args.out / f"{result.name}.interval.json").write_text(
                json.dumps(detail, indent=2)
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
