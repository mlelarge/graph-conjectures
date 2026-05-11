"""JSON certificate schema for unit-vector-flow witness/infeasibility runs.

A certificate captures everything an independent verifier needs to
re-check a single oracle decision: the graph (graph6 + edge ordering),
the solver and parameters, and either the witness vectors or the
infeasibility evidence.

Schema version 1. Schema is forward-compatible: verifiers must ignore
unknown top-level keys.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import platform
from typing import Any

import networkx as nx

from graphs import to_graph6
from witness import WitnessResult, orient, verify_witness

SCHEMA_VERSION = 1


def _provenance() -> dict[str, Any]:
    return {
        "host": platform.node(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "timestamp_utc": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
    }


def witness_certificate(
    name: str,
    G: nx.Graph,
    result: WitnessResult,
    *,
    solver: str,
    solver_params: dict[str, Any],
    seed: int | None,
) -> dict[str, Any]:
    """Build a certificate for a numerical witness (or non-converged) run."""
    edges, _sign = orient(G)
    cert: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": "numerical_witness",
        "name": name,
        "graph": {
            "n": G.number_of_nodes(),
            "m": G.number_of_edges(),
            "graph6": to_graph6(G),
            "edges": [list(e) for e in edges],
            "orientation": "lex: edge (u,v) with u<v points u -> v",
        },
        "result": {
            "status": result.status,
            "best_residual_squared": result.best_residual_squared,
            "best_max_abs_residual": result.best_max_abs_residual,
            "n_restarts": result.n_restarts,
            "converged_restart": result.converged_restart,
        },
        "solver": {
            "name": solver,
            "params": solver_params,
            "seed": seed,
        },
        "provenance": _provenance(),
    }
    if result.status == "witness":
        cert["witness"] = {
            "vectors": result.vectors,
            "verification": verify_witness(G, edges, result.vectors, tol=1e-7),
        }
    return cert


def infeasibility_certificate(
    name: str,
    G: nx.Graph,
    *,
    method: str,
    method_params: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """Stub for an exact / SOS infeasibility certificate.

    ``evidence`` should be a dict whose contents an independent verifier
    can use, e.g. a Gröbner basis containing ``1``, an SOS certificate,
    or RAG output. The exact backend fills this in; the schema imposes
    no further structure for now.
    """
    edges, _sign = orient(G)
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "infeasibility",
        "name": name,
        "graph": {
            "n": G.number_of_nodes(),
            "m": G.number_of_edges(),
            "graph6": to_graph6(G),
            "edges": [list(e) for e in edges],
            "orientation": "lex: edge (u,v) with u<v points u -> v",
        },
        "method": {"name": method, "params": method_params},
        "evidence": evidence,
        "provenance": _provenance(),
    }


def write_certificate(cert: dict[str, Any], path: str | os.PathLike) -> pathlib.Path:
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(cert, indent=2, sort_keys=False))
    return p


def load_certificate(path: str | os.PathLike) -> dict[str, Any]:
    return json.loads(pathlib.Path(path).read_text())
