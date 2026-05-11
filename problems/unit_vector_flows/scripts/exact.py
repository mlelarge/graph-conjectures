"""Exact-backend spike: build the polynomial S²-flow ideal of a cubic
graph and run sympy's Gröbner basis on it.

Status: experimental. Sympy is pure-Python and will not scale past very
small graphs. The point of this module is to (a) make the polynomial
system explicit and reproducible, (b) calibrate on the trivially
positive K_4, (c) measure where sympy gives up. Larger work moves to
Macaulay2 / Singular / a SOS pipeline.

Variables. After fixing the canonical lex orientation of edges, each
edge ``e`` carries three rationals ``x_{e,0}, x_{e,1}, x_{e,2}``.

Constraints.
* For every vertex v: ``sum_{e in incidence(v)} sigma(v,e) x_e == 0``
  (three scalar equations).
* For every edge e: ``x_{e,0}^2 + x_{e,1}^2 + x_{e,2}^2 - 1 == 0``.

Rotation pinning. We fix the three vectors at vertex 0 to a 120-degree
triple in the xy plane:

    sigma(0, e_0) x_{e_0} = (1, 0, 0)
    sigma(0, e_1) x_{e_1} = (-1/2,  sqrt(3)/2, 0)
    sigma(0, e_2) x_{e_2} = (-1/2, -sqrt(3)/2, 0)

This kills the global SO(3) symmetry. The polynomial system stays over
``QQ[sqrt(3)]`` because of the y-component; we keep ``sqrt(3)`` as a
formal symbol with the relation ``s^2 - 3 = 0``.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

import networkx as nx
import sympy as sp

from witness import orient


@dataclass
class IdealResult:
    name: str
    n_vars: int
    n_polys: int
    elapsed_seconds: float
    contains_one: Optional[bool]
    note: str


def build_ideal(G: nx.Graph, *, pin: bool = True, drop_redundant: bool = False):
    """Return ``(polys, vars, sqrt3_relation)`` for the S²-flow ideal of G.

    ``polys`` is a list of sympy polynomials whose common zero set in
    ``\\bar{\\mathbb{Q}}`` is the variety of S²-flows on G (modulo SO(3)
    if ``pin=True``). ``sqrt3_relation`` is ``s**2 - 3`` and must be added
    to the ideal whenever ``pin=True``.

    When ``drop_redundant=True``, the conservation equations at the
    *last* vertex are dropped to make the system square. This is sound
    because the sum of all vertex Kirchhoff equations is identically
    zero, so once vertex 0 is satisfied (via pinning) and all other
    vertices except v_last are imposed, v_last's equations follow.
    """
    edges, sign = orient(G)
    m = len(edges)

    s = sp.symbols("s")
    var_names = [f"x_{e}_{k}" for e in range(m) for k in range(3)]
    syms = sp.symbols(var_names)
    X = [sp.Matrix(3, 1, list(syms[3 * e : 3 * e + 3])) for e in range(m)]

    polys: list[sp.Expr] = []

    pinned_edges: set[int] = set()
    pinned_subs: dict[sp.Symbol, sp.Expr] = {}

    if pin:
        v0 = next(iter(sign))
        terms = sign[v0]
        if len(terms) != 3:
            raise ValueError("rotation pinning expects a cubic vertex")
        targets = [
            sp.Matrix([1, 0, 0]),
            sp.Matrix([sp.Rational(-1, 2), s / 2, 0]),
            sp.Matrix([sp.Rational(-1, 2), -s / 2, 0]),
        ]
        for (k, sigma), tgt in zip(terms, targets):
            sigma_i = sp.Integer(int(sigma))
            for j in range(3):
                pinned_subs[X[k][j]] = sigma_i * tgt[j]
            pinned_edges.add(k)

    skip_vertices = set()
    if pin:
        skip_vertices.add(next(iter(sign)))
    if drop_redundant:
        skip_vertices.add(list(sign.keys())[-1])

    for v, terms in sign.items():
        if v in skip_vertices:
            continue
        s_vec = sp.Matrix([0, 0, 0])
        for k, sigma in terms:
            s_vec = s_vec + sp.Integer(int(sigma)) * X[k]
        for j in range(3):
            polys.append(sp.expand(s_vec[j].subs(pinned_subs)))

    for e in range(m):
        if e in pinned_edges:
            continue
        norm_sq = sum(X[e][j] ** 2 for j in range(3))
        polys.append(sp.expand((norm_sq - 1).subs(pinned_subs)))

    free_vars = [v for v in syms if v not in pinned_subs]
    if pin:
        return polys, free_vars + [s], sp.Poly(s ** 2 - 3, s)
    return polys, list(syms), None


def has_one_in_groebner(G: nx.Graph, *, pin: bool = True, timeout_s: float = 60.0) -> IdealResult:
    """Run a Gröbner basis on the S²-flow ideal. If the basis is ``[1]``
    the ideal is the unit ideal -- no S²-flow exists. Otherwise the
    ideal is non-trivial; this gives no information about real solvability.

    No reliable timeout in pure sympy; we report wall time and let the
    caller kill the process.
    """
    polys, free_vars, sqrt3 = build_ideal(G, pin=pin)
    gens = list(free_vars)
    full = list(polys)
    if sqrt3 is not None:
        full.append(sp.Poly(sqrt3, gens).as_expr())
    name = G.graph.get("name", "<unnamed>")
    t0 = time.time()
    try:
        gb = sp.groebner(full, *gens, order="lex")
        elapsed = time.time() - t0
        gb_list = list(gb)
        contains_one = (len(gb_list) == 1) and (sp.simplify(gb_list[0] - 1) == 0)
        note = f"|GB|={len(gb_list)}"
    except Exception as exc:
        elapsed = time.time() - t0
        contains_one = None
        note = f"sympy raised {type(exc).__name__}: {exc}"
    return IdealResult(
        name=name,
        n_vars=len(gens),
        n_polys=len(full),
        elapsed_seconds=elapsed,
        contains_one=contains_one,
        note=note,
    )


if __name__ == "__main__":
    import argparse

    from graphs import k4, prism, petersen, blanusa_first

    targets = {
        "K_4": k4,
        "prism_3": lambda: prism(3),
        "Petersen": petersen,
        "Blanusa-1": blanusa_first,
    }
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--graphs",
        nargs="+",
        default=["K_4", "prism_3"],
        choices=list(targets),
    )
    args = ap.parse_args()

    for name in args.graphs:
        G = targets[name]()
        polys, free_vars, _ = build_ideal(G, pin=True)
        print(
            f"{name}: n={G.number_of_nodes()} m={G.number_of_edges()} "
            f"polys={len(polys)} free_vars={len(free_vars)}"
        )
        res = has_one_in_groebner(G, pin=True)
        print(
            f"   -> contains_one={res.contains_one} elapsed={res.elapsed_seconds:.2f}s "
            f"note={res.note}"
        )
