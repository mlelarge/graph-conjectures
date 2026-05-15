"""Sweep all 2-pole subcubic graphs on n vertices through coverage_check.

For each graph (in both port orientations), compute Trace(H, R), and check
whether it is contained in some lattice class's trace set. This is the
ENVELOPE direction Trace(H) subseteq Trace(C). If not, the side exposes traces
beyond the lattice -- a "lattice expansion" candidate.

This is not the Lemma-2 replacement direction. Use replacement_sweep.py for
the Antichain Coverage / reducibility test Trace(C) subseteq Trace(H).

Output is a JSON manifest with per-graph results plus a global summary:
  - how many graphs are covered (side ⊆ some class)
  - how many have uncovered traces
  - the set of all uncovered traces aggregated across the sweep
  - the minimum |V| at which a new trace appears (if any)

Usage:
  python scripts/coverage_sweep.py --n 12 \
      --lattice data/gadget_lattice_2pole_n10_both.json \
      --output  data/coverage_sweep_n12.json
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from coverage_check import (  # noqa: E402
    check_coverage,
    load_lattice,
    union_of_all_traces,
)
from gadget_lattice import enumerate_2pole_graphs, graph6_string, oriented_ports  # noqa: E402


def sweep(
    n: int,
    payload: dict[str, Any],
    orientations: str,
    limit: int | None,
    progress_every: int,
) -> dict[str, Any]:
    graphs = enumerate_2pole_graphs(n)
    if limit is not None:
        graphs = graphs[:limit]
    print(f"n={n}: {len(graphs)} 2-pole graphs", file=sys.stderr)

    universe = union_of_all_traces(payload)

    per_graph: list[dict[str, Any]] = []
    covered = 0
    not_covered_by_single_class = 0
    sides_with_traces_outside_universe = 0
    union_uncovered_traces: set = set()
    smallest_uncovered_n: int | None = None

    for idx, G in enumerate(graphs):
        g6 = graph6_string(G)
        for ports in oriented_ports(G, orientations):
            result = check_coverage(G, ports, payload)
            covers = bool(result["covering_class_ids"])
            uncov_count = len(result["uncovered_traces"])
            if covers:
                covered += 1
            else:
                not_covered_by_single_class += 1
            if uncov_count:
                sides_with_traces_outside_universe += 1
            for t in result["uncovered_traces"]:
                chi = tuple(t["chi"])
                pi = tuple(sorted(tuple(sorted(b)) for b in t["pi"]))
                union_uncovered_traces.add((chi, pi))
                if smallest_uncovered_n is None or n < smallest_uncovered_n:
                    smallest_uncovered_n = n
            per_graph.append({
                "n": n,
                "graph6": g6,
                "ports": ports,
                "side_trace_count": result["side_trace_count"],
                "covered": covers,
                "uncovered_count": uncov_count,
                "smallest_covering_class": result["smallest_covering_class"],
            })

        if progress_every and (idx + 1) % progress_every == 0:
            print(
                f"  {idx + 1}/{len(graphs)} covered={covered} "
                f"not_single_covered={not_covered_by_single_class} "
                f"outside_universe_sides={sides_with_traces_outside_universe}",
                file=sys.stderr,
            )

    summary = {
        "n": n,
        "graph_count": len(graphs),
        "oriented_side_count": len(per_graph),
        "covered_count": covered,
        "not_covered_by_single_class_count": not_covered_by_single_class,
        "sides_with_traces_outside_universe_count": sides_with_traces_outside_universe,
        "union_uncovered_trace_count": len(union_uncovered_traces),
        "smallest_uncovered_n": smallest_uncovered_n,
        "union_uncovered_traces": [
            {"chi": list(chi), "pi": [list(b) for b in pi]}
            for chi, pi in sorted(union_uncovered_traces)
        ],
        "lattice_meta": payload["meta"],
        "lattice_universe_size": len(universe),
    }
    return {"summary": summary, "per_oriented_side": per_graph}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument(
        "--lattice",
        type=Path,
        default=ROOT / "data" / "gadget_lattice_2pole_n10_both.json",
    )
    parser.add_argument("--orientations", choices=("both", "canonical"), default="both")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--progress-every", type=int, default=25)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    payload = load_lattice(args.lattice)
    result = sweep(args.n, payload, args.orientations, args.limit, args.progress_every)

    summary = result["summary"]
    print(
        f"n={summary['n']} sides={summary['oriented_side_count']} "
        f"covered={summary['covered_count']} "
        f"not_single_covered={summary['not_covered_by_single_class_count']} "
        f"outside_universe_sides={summary['sides_with_traces_outside_universe_count']} "
        f"new_uncovered_traces={summary['union_uncovered_trace_count']}",
        file=sys.stderr,
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(f"wrote {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
