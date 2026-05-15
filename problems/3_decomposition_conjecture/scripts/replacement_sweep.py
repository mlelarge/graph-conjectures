"""Sweep 2-pole sides for Lemma-2 replacement candidates.

This is the reduction-direction companion to coverage_sweep.py.  For each
2-pole side (H, R), it checks whether the n<=10 lattice contains a strictly
smaller trace class C with

    Trace(C) subseteq Trace(H, R).

That is the direction needed to replace H by a smaller gadget in the
minimal-counterexample argument.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from coverage_check import find_replacement_gadget, load_lattice  # noqa: E402
from gadget_lattice import enumerate_2pole_graphs, graph6_string, oriented_ports  # noqa: E402


def sweep_replacements(
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

    per_side: list[dict[str, Any]] = []
    replaceable_count = 0
    not_replaceable_count = 0
    smallest_counter: Counter[str] = Counter()
    candidate_counter: Counter[str] = Counter()
    trace_set_failures: dict[str, dict[str, Any]] = {}

    for idx, G in enumerate(graphs):
        g6 = graph6_string(G)
        for ports in oriented_ports(G, orientations):
            result = find_replacement_gadget(G, ports, payload)
            if result["replaceable"]:
                replaceable_count += 1
                cid = result["smallest_candidate"]["id"]
                smallest_counter[cid] += 1
            else:
                not_replaceable_count += 1
                key = json.dumps(result["traces_only_in_side"], sort_keys=True)
                trace_set_failures.setdefault(key, {
                    "first_graph6": g6,
                    "first_ports": ports,
                    "side_trace_count": result["side_trace_count"],
                    "side_size": result["side_size"],
                    "traces": result["traces_only_in_side"],
                    "occurrences": 0,
                })
                trace_set_failures[key]["occurrences"] += 1
            for cid in result["strict_candidate_class_ids"]:
                candidate_counter[cid] += 1
            per_side.append({
                "n": n,
                "graph6": g6,
                "ports": ports,
                "side_size": result["side_size"],
                "side_trace_count": result["side_trace_count"],
                "replaceable": result["replaceable"],
                "smallest_candidate": result["smallest_candidate"],
                "strict_candidate_class_ids": result["strict_candidate_class_ids"],
            })

        if progress_every and (idx + 1) % progress_every == 0:
            print(
                f"  {idx + 1}/{len(graphs)} replaceable={replaceable_count} "
                f"not_replaceable={not_replaceable_count}",
                file=sys.stderr,
            )

    summary = {
        "n": n,
        "graph_count": len(graphs),
        "oriented_side_count": len(per_side),
        "replaceable_count": replaceable_count,
        "not_replaceable_count": not_replaceable_count,
        "smallest_candidate_histogram": dict(sorted(smallest_counter.items())),
        "strict_candidate_histogram": dict(sorted(candidate_counter.items())),
        "failure_trace_set_count": len(trace_set_failures),
        "failure_trace_sets": sorted(
            trace_set_failures.values(),
            key=lambda row: (row["side_trace_count"], row["first_graph6"], row["first_ports"]),
        ),
        "lattice_meta": payload["meta"],
    }
    return {"summary": summary, "per_oriented_side": per_side}


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
    result = sweep_replacements(
        args.n,
        payload,
        args.orientations,
        args.limit,
        args.progress_every,
    )
    summary = result["summary"]
    print(
        f"n={summary['n']} sides={summary['oriented_side_count']} "
        f"replaceable={summary['replaceable_count']} "
        f"not_replaceable={summary['not_replaceable_count']} "
        f"failure_trace_sets={summary['failure_trace_set_count']}",
        file=sys.stderr,
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(f"wrote {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
