"""Ingest Flocco-Pulaj-Yerger (FPY) Lemke-square certificates into our format.

Stub for the Phase 2b reproduction step in
``PEBBLING_PHASE_2B_STATUS.md``. Reads per-root FPY weight CSVs and tree
edges CSVs from the public repo (locally mirrored or fetched via HTTP)
and emits a list of ``Strategy`` records compatible with
``check_pebbling_weight_certificate.py``.

This module *does not* yet decide the dual multipliers ``alpha_i`` for
each strategy. The FPY repository does not store them next to the
strategies; the paper says that for the hardest root ``(v_1, v_1)`` the
bound uses 10 symmetric tree strategies (and 6 for other roots), but the
combining coefficients have to be reconstructed (most likely uniform
``alpha_i = 1/k`` for the ``averaging`` form). The ingestion adapter
therefore produces a *partial* certificate that the user can either:

- supply ``dual_multipliers`` by hand (fastest route to a checkable cert
  if the averaging interpretation is correct);
- post-process by solving an LP that, given fixed strategies, picks
  optimal ``alpha_i`` to minimise ``sum_i alpha_i b_i`` subject to dual
  feasibility (this is itself a small LP, separate from the original
  MILP that *generated* the strategies).

Float-to-rational conversion. The published CSVs store weights as
floats (e.g., ``31.56``). We convert them via ``Fraction(Decimal(str(x)))``
which preserves any value with a finite decimal expansion. For values
that are exact dyadic rationals (powers of two, ``1.75 = 7/4``, etc.)
this is exact. For values that are LP solutions rounded to two decimal
places (e.g., ``31.56``) the resulting rational is exact for the rounded
value but may differ from the underlying LP optimum; we surface this in
``ingest_warnings``.

This is intentionally a stub. It implements the parsing pieces so the
path to a Phase 2b reproduction is concrete; it does not by itself
reproduce the FPY 96 bound.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from pebbling_graphs import Graph, cartesian_product, load_named_graph, pair_to_index


@dataclass
class IngestedStrategy:
    """One strategy ingested from FPY repo CSV files (no alpha yet)."""

    name: str
    root_pair: tuple[int, int]
    tree_edges: list[tuple[int, int]]
    weights: dict[int, Fraction]
    ingest_warnings: list[str] = field(default_factory=list)

    def to_dict(self, basic: bool = False) -> dict:
        return {
            "name": self.name,
            "tree_edges": [list(e) for e in self.tree_edges],
            "weights": {str(v): str(w) for v, w in self.weights.items()},
            "basic": basic,
        }


def _decimal_to_fraction(s: str) -> Fraction:
    """Parse a CSV cell as an exact Fraction.

    Treats the value as a finite-precision decimal: ``"31.56"`` becomes
    ``Fraction(789, 25)``, ``"1.75"`` becomes ``Fraction(7, 4)``,
    ``"0.0"`` becomes ``Fraction(0)``. Refuses scientific notation
    silently expanding to a non-decimal (we do not see it in the FPY
    CSVs).
    """
    s = s.strip()
    if s == "":
        return Fraction(0)
    return Fraction(Decimal(s))


def parse_weight_csv(text: str, h_n: int) -> tuple[dict[int, Fraction], list[str]]:
    """Parse an FPY weight matrix CSV into ``(weights, warnings)``.

    The CSV has a header row of column indices and a leading column of
    row indices. Cell ``(i, j)`` is the weight at vertex ``(i, j)`` of
    ``L box L`` (assuming the first factor labels rows and the second
    labels columns); we encode it as the flat index ``i * h_n + j``.

    Cells containing ``0`` or ``0.0`` are dropped from the returned
    dict (weights default to ``0`` outside the support).
    """
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        return {}, ["empty CSV"]
    header = rows[0]
    # FPY format: first cell is empty, then column indices 0..7
    if header[0] != "" or len(header) < 2:
        return {}, [f"unexpected header row {header!r}"]
    try:
        col_indices = [int(c) for c in header[1:]]
    except ValueError as exc:
        return {}, [f"non-integer column index: {exc}"]
    weights: dict[int, Fraction] = {}
    warnings: list[str] = []
    for r_idx, row in enumerate(rows[1:], start=1):
        if len(row) != len(header):
            warnings.append(
                f"row {r_idx} has {len(row)} cells, expected {len(header)}"
            )
            continue
        try:
            row_index = int(row[0])
        except ValueError:
            warnings.append(f"non-integer row index at row {r_idx}: {row[0]!r}")
            continue
        for c, cell in zip(col_indices, row[1:]):
            try:
                w = _decimal_to_fraction(cell)
            except (ValueError, ArithmeticError) as exc:
                warnings.append(f"weight cell ({row_index},{c})={cell!r}: {exc}")
                continue
            if w == 0:
                continue
            v = pair_to_index(row_index, c, h_n)
            weights[v] = w
            # Flag values that look like rounded LP solutions
            if w.denominator not in (1, 2, 4, 8, 16, 32, 64, 128, 256):
                warnings.append(
                    f"weight at ({row_index},{c}) = {w} has non-dyadic denominator "
                    f"({w.denominator}); likely a rounded LP value"
                )
    return weights, warnings


def parse_edges_csv(text: str, h_n: int) -> tuple[list[tuple[int, int]], list[str]]:
    """Parse an FPY tree-edges CSV into a list of (parent_idx, child_idx) flat pairs.

    The CSV has a header ``,0,1`` and rows of the form
    ``i,"(p1, p2)","(c1, c2)"`` where columns 0 and 1 are the parent and
    child as ``(u, v)`` pairs in V(L) x V(L). Returned edges are
    unordered ``(min, max)`` flat-index pairs to match the project's
    Cartesian-product encoding.
    """
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        return [], ["empty CSV"]
    header = rows[0]
    if len(header) < 3 or header[0] != "" or header[1] != "0" or header[2] != "1":
        return [], [f"unexpected header row {header!r}"]
    edges: list[tuple[int, int]] = []
    warnings: list[str] = []
    for r_idx, row in enumerate(rows[1:], start=1):
        if len(row) < 3:
            warnings.append(f"row {r_idx} has only {len(row)} cells")
            continue
        parent_str, child_str = row[1], row[2]
        try:
            p = _parse_pair(parent_str)
            c = _parse_pair(child_str)
        except ValueError as exc:
            warnings.append(f"row {r_idx}: {exc}")
            continue
        u = pair_to_index(p[0], p[1], h_n)
        v = pair_to_index(c[0], c[1], h_n)
        if u == v:
            warnings.append(f"row {r_idx} self-loop ({p}, {c})")
            continue
        if u > v:
            u, v = v, u
        edges.append((u, v))
    return edges, warnings


def _parse_pair(s: str) -> tuple[int, int]:
    """Accept ``(u, v)`` or the live FPY-runtime form ``('u', 'v')``.

    The FPY pipeline calls ``str()`` on tuples whose entries are themselves
    strings (NetworkX cartesian-product nodes), so the on-disk form is
    e.g. ``('0', '1')`` with inner single quotes around each digit.
    """
    s = s.strip()
    if not s.startswith("(") or not s.endswith(")"):
        raise ValueError(f"expected '(u, v)', got {s!r}")
    inside = s[1:-1]
    parts = inside.split(",")
    if len(parts) != 2:
        raise ValueError(f"expected '(u, v)', got {s!r}")

    def _strip_quotes(p: str) -> str:
        p = p.strip()
        if len(p) >= 2 and p[0] == p[-1] and p[0] in ("'", '"'):
            p = p[1:-1]
        return p

    return int(_strip_quotes(parts[0])), int(_strip_quotes(parts[1]))


def ingest_strategy(
    weight_csv_text: str,
    edges_csv_text: str,
    *,
    name: str,
    root_pair: tuple[int, int],
    h_n: int,
) -> IngestedStrategy:
    """Ingest one (weight matrix, tree edges) pair into a strategy."""
    weights, w_warn = parse_weight_csv(weight_csv_text, h_n)
    edges, e_warn = parse_edges_csv(edges_csv_text, h_n)
    return IngestedStrategy(
        name=name,
        root_pair=root_pair,
        tree_edges=edges,
        weights=weights,
        ingest_warnings=w_warn + e_warn,
    )


def emit_partial_certificate(
    *,
    strategies: Iterable[IngestedStrategy],
    root_pair: tuple[int, int],
    factor_graph_name: str,
    factor_n: int,
    claimed_bound: int,
    dual_multipliers: list[str] | None = None,
) -> dict:
    """Build a partial certificate JSON dictionary.

    If ``dual_multipliers`` is ``None``, the field is left empty and the
    user is expected to fill it in (e.g., uniform ``["1/k"] * k`` or by
    solving an aggregation LP).
    """
    strats = list(strategies)
    factor = load_named_graph(factor_graph_name)
    if factor.n != factor_n:
        raise ValueError(
            f"factor graph {factor_graph_name} has n={factor.n}, expected {factor_n}"
        )
    product = cartesian_product(factor, factor, name=f"{factor_graph_name}_box_{factor_graph_name}")
    root_idx = pair_to_index(root_pair[0], root_pair[1], factor.n)
    return {
        "graph": {
            "n": product.n,
            "edges": [list(e) for e in product.edges],
            "name": product.name,
        },
        "root": root_idx,
        "claimed_bound": claimed_bound,
        "strategies": [s.to_dict(basic=False) for s in strats],
        "dual_multipliers": dual_multipliers if dual_multipliers is not None else [],
        "notes": (
            "Ingested from Flocco-Pulaj-Yerger 2024 repo "
            "(https://github.com/dominicflocco/Graph_Pebbling). "
            "Float weights converted to exact Fractions via "
            "Fraction(Decimal(str(x))). dual_multipliers must be filled "
            "in before the certificate can be checked."
        ),
        "ingest_warnings": [w for s in strats for w in s.ingest_warnings],
    }


# --- CLI -------------------------------------------------------------------


def _cli() -> None:
    import argparse
    import json

    ap = argparse.ArgumentParser(
        description=(
            "Ingest one Flocco-Pulaj-Yerger weight matrix + edges CSV "
            "into a partial certificate JSON. dual_multipliers must be "
            "supplied by the user before the result can be checked."
        )
    )
    ap.add_argument("weight_csv", help="path to ls_sym_cert<i>-v(r1, r2).csv")
    ap.add_argument("edges_csv", help="path to ls_sym_edges<i>-v(r1, r2).csv")
    ap.add_argument("--root-pair", type=str, required=True, help="e.g. '0,1'")
    ap.add_argument("--factor-graph", default="L", help="factor graph name (default L)")
    ap.add_argument("--factor-n", type=int, default=8)
    ap.add_argument("--claimed-bound", type=int, default=96)
    args = ap.parse_args()

    rp = tuple(int(x) for x in args.root_pair.split(","))
    if len(rp) != 2:
        raise SystemExit("--root-pair must be of the form 'r1,r2'")
    weight_text = Path(args.weight_csv).read_text()
    edges_text = Path(args.edges_csv).read_text()
    strat = ingest_strategy(
        weight_text,
        edges_text,
        name=Path(args.weight_csv).stem,
        root_pair=rp,
        h_n=args.factor_n,
    )
    payload = emit_partial_certificate(
        strategies=[strat],
        root_pair=rp,
        factor_graph_name=args.factor_graph,
        factor_n=args.factor_n,
        claimed_bound=args.claimed_bound,
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    _cli()
