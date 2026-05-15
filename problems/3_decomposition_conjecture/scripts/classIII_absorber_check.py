#!/usr/bin/env python3
"""Verify the Class-III compatibility replacement.

The residual n=12 side H = K?AB?qQT@WWG with ports (2,4) is not
trace-contained by a smaller 2-pole gadget.  It is nevertheless
compatibility-universal: every trace in the 16-trace universe can be glued
to at least one trace realised by H.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import networkx as nx

from decomposition import are_2pole_traces_compatible, compute_trace_set_2pole
from gadget_lattice import trace_json, trace_key, trace_key_from_json


RESIDUAL_GRAPH6 = "K?AB?qQT@WWG"
RESIDUAL_PORTS = (2, 4)
UNIVERSAL_GADGET = {"graph6": "I?B@t`gs?", "ports": [4, 5], "class": "C58"}


def load_universe(lattice_path: Path) -> set:
    payload = json.loads(lattice_path.read_text())
    universe = set()
    for cls in payload["classes"]:
        for trace in cls["traces"]:
            universe.add(trace_key_from_json(trace))
    return universe


def witness_payload(lattice_path: Path) -> dict[str, Any]:
    universe = load_universe(lattice_path)
    H = nx.from_graph6_bytes(RESIDUAL_GRAPH6.encode())
    residual_traces = {trace_key(t) for t in compute_trace_set_2pole(H, list(RESIDUAL_PORTS))}

    witnesses = []
    uncovered = []
    for opposite_trace in sorted(universe):
        compatible = [
            h_trace
            for h_trace in sorted(residual_traces)
            if are_2pole_traces_compatible(
                (h_trace[0], frozenset(frozenset(block) for block in h_trace[1])),
                (
                    opposite_trace[0],
                    frozenset(frozenset(block) for block in opposite_trace[1]),
                ),
            )
        ]
        if not compatible:
            uncovered.append(opposite_trace)
            continue
        witnesses.append(
            {
                "opposite_trace": trace_json(opposite_trace),
                "witness_trace_on_residual": trace_json(compatible[0]),
                "compatible_witness_count": len(compatible),
            }
        )

    return {
        "residual": {"graph6": RESIDUAL_GRAPH6, "ports": list(RESIDUAL_PORTS)},
        "universal_gadget": UNIVERSAL_GADGET,
        "lattice": str(lattice_path),
        "universe_trace_count": len(universe),
        "residual_trace_count": len(residual_traces),
        "uncovered_opposite_traces": [trace_json(t) for t in sorted(uncovered)],
        "is_compatibility_universal": not uncovered,
        "witnesses": witnesses,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--lattice",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "data"
        / "gadget_lattice_2pole_n10_both.json",
    )
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    payload = witness_payload(args.lattice)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
