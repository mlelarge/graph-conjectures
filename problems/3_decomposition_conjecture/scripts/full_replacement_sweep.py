"""Reproducible full replacement sweep at a given n against a fixed lattice.

For each oriented 2-pole subcubic graph at order n, archive:
  - graph6, ports
  - structural class (bridge | articulation_no_bridge | non_port_2cut | essentially_3conn)
  - trace count
  - is_trace_contained (boolean) and the absorbing lattice class id (smallest
    by min_order, then trace count) if contained
  - is_compatibility_universal (boolean)
  - status: "trace_contained" | "compat_universal_not_contained" | "neither"

Plus an absorption histogram (which lattice class absorbed each side).

Resumable: writes a JSONL checkpoint after each side; on restart, skips already-processed (graph6, ports) entries.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from coverage_check import load_lattice, trace_set_from_class, union_of_all_traces  # noqa: E402
from decomposition import (  # noqa: E402
    BOUNDARY_COLOUR,
    are_2pole_traces_compatible,
    compute_trace_set_2pole,
    realises_target_traces,
)


# C0 trace set: the K_4-minus-edge gadget. C0 is the smallest class in the
# n<=12 lattice (min_order=4, trace_count=3). C0's traces are symmetric under
# port swap (port 0 <-> port 1), so a single early-termination check on one
# orientation suffices for both. If C0 absorbs, it IS the smallest absorbing
# class (no class in the lattice has smaller min_order or trace count).
C0_TRACES: frozenset = frozenset({
    (("T_CC", "T_T"), frozenset({frozenset({0}), frozenset({1})})),
    (("T_T", "T_CC"), frozenset({frozenset({0}), frozenset({1})})),
    (("T_TM", "T_TM"), frozenset({frozenset({0, 1})})),
})
from gadget_lattice import (  # noqa: E402
    enumerate_2pole_graphs,
    graph6_string,
    oriented_ports,
    trace_set_key,
)


def has_non_port_trivial_2cut(G: nx.Graph, ports: list) -> bool:
    pt = {frozenset(G.neighbors(p)) for p in ports}
    for u, v in combinations(G.nodes(), 2):
        cut = frozenset({u, v})
        if cut in pt:
            continue
        H2 = G.copy()
        H2.remove_nodes_from([u, v])
        if not nx.is_connected(H2):
            return True
    return False


def structural_class(G: nx.Graph, ports: list) -> str:
    if list(nx.bridges(G)):
        return "bridge"
    if list(nx.articulation_points(G)):
        return "articulation_no_bridge"
    if has_non_port_trivial_2cut(G, ports):
        return "non_port_2cut"
    return "essentially_3conn"


def is_compatibility_universal(traces_set, universe) -> bool:
    for tau in universe:
        tau_full = (tau[0], frozenset(frozenset(b) for b in tau[1]))
        if not any(
            are_2pole_traces_compatible(
                (sigma[0], frozenset(frozenset(b) for b in sigma[1])),
                tau_full,
            )
            for sigma in traces_set
        ):
            return False
    return True


def absorbing_class(side_key, classes):
    """Return the smallest absorbing class (by (min_order, trace_count))
    whose trace set is a subset of side_key, or None."""
    contained = [c for c in classes if trace_set_from_class(c) <= side_key]
    if not contained:
        return None
    return min(contained, key=lambda c: (c["min_order"], c["trace_count"]))


def reverse_trace(trace):
    """Reverse a 2-pole trace from ports (p0, p1) to ports (p1, p0)."""
    chi, pi = trace
    rev_chi = (chi[1], chi[0])
    rev_blocks = []
    for block in pi:
        rev_blocks.append(frozenset(1 - i for i in block))
    return rev_chi, frozenset(rev_blocks)


def reverse_trace_set(traces):
    return {reverse_trace(t) for t in traces}


def classify_trace_set(traces, universe, classes) -> dict[str, Any]:
    side_key = trace_set_key(traces)
    absorber = absorbing_class(side_key, classes)
    is_contained = absorber is not None
    is_univ = is_compatibility_universal(traces, universe)

    if is_contained:
        status = "trace_contained"
    elif is_univ:
        status = "compat_universal_not_contained"
    else:
        status = "neither"

    return {
        "trace_count": len(side_key),
        "is_trace_contained": is_contained,
        "absorbing_class_id": absorber["id"] if absorber else None,
        "absorbing_class_min_order": absorber["min_order"] if absorber else None,
        "absorbing_class_trace_count": absorber["trace_count"] if absorber else None,
        "is_compatibility_universal": is_univ,
        "status": status,
    }


def load_seen(checkpoint: Path) -> set:
    if not checkpoint.exists():
        return set()
    seen = set()
    with checkpoint.open() as f:
        for line in f:
            r = json.loads(line)
            seen.add((r["graph6"], tuple(r["ports"])))
    return seen


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument(
        "--lattice",
        type=Path,
        default=ROOT / "data" / "gadget_lattice_2pole_n12_both.json",
    )
    parser.add_argument(
        "--filter",
        choices=("all", "essentially_3conn", "non_port_2cut", "no_bridge"),
        default="all",
    )
    parser.add_argument(
        "--checkpoint", type=Path, required=True,
        help="JSONL file: one record per oriented side"
    )
    parser.add_argument(
        "--summary-output", type=Path, default=None,
        help="JSON aggregate written at end; defaults to checkpoint with .summary.json"
    )
    parser.add_argument("--progress-every", type=int, default=50)
    parser.add_argument("--limit", type=int, default=None, help="Cap on unoriented count (after filter)")
    parser.add_argument(
        "--shard-mod", type=int, default=1,
        help="Total number of parallel shards (default 1: no sharding)"
    )
    parser.add_argument(
        "--shard-index", type=int, default=0,
        help="This worker's shard index in [0, shard-mod); graphs with idx %% shard-mod == shard-index are processed"
    )
    parser.add_argument(
        "--read-checkpoint", type=Path, action="append", default=[],
        help="Read-only checkpoint(s) to add to seen-set (repeatable). Useful for resuming sharded sweeps where another worker wrote some data."
    )
    args = parser.parse_args()
    if not (0 <= args.shard_index < args.shard_mod):
        parser.error(
            f"--shard-index must be in [0, --shard-mod); got {args.shard_index} of {args.shard_mod}"
        )

    payload = load_lattice(args.lattice)
    universe = union_of_all_traces(payload)
    classes = payload["classes"]
    print(
        f"Lattice: {len(classes)} classes, universe |U|={len(universe)}", file=sys.stderr
    )

    graphs = enumerate_2pole_graphs(args.n)
    print(f"n={args.n}: {len(graphs)} unoriented 2-pole graphs", file=sys.stderr)

    seen = load_seen(args.checkpoint)
    for extra_cp in args.read_checkpoint:
        extra_seen = load_seen(extra_cp)
        new_size = len(extra_seen - seen)
        seen |= extra_seen
        print(
            f"Loaded read-only checkpoint {extra_cp}: {len(extra_seen)} records ({new_size} new)",
            file=sys.stderr,
        )
    print(f"Total already-processed oriented sides: {len(seen)}", file=sys.stderr)
    if args.shard_mod > 1:
        print(
            f"Sharding: this worker handles graph indices where idx %% {args.shard_mod} == {args.shard_index}",
            file=sys.stderr,
        )

    args.checkpoint.parent.mkdir(parents=True, exist_ok=True)

    filtered_count = 0
    written = 0
    skipped = 0
    start = time.time()

    with args.checkpoint.open("a") as fout:
        for idx, G in enumerate(graphs):
            if args.shard_mod > 1 and idx % args.shard_mod != args.shard_index:
                continue
            g6 = graph6_string(G)
            ports_canon = sorted(v for v, d in G.degree() if d == 2)
            sc = structural_class(G, ports_canon)

            if args.filter == "essentially_3conn" and sc != "essentially_3conn":
                continue
            if args.filter == "non_port_2cut" and sc != "non_port_2cut":
                continue
            if args.filter == "no_bridge" and sc == "bridge":
                continue
            filtered_count += 1
            if args.limit is not None and filtered_count > args.limit:
                break

            orientations = oriented_ports(G, "both")
            missing = [ports for ports in orientations if (g6, tuple(ports)) not in seen]
            skipped += len(orientations) - len(missing)
            if not missing:
                continue

            base_ports = orientations[0]

            # Fast path: try C0 early-termination first. C0's trace set is
            # symmetric under port swap, so a single check covers both
            # orientations.
            if realises_target_traces(G, base_ports, C0_TRACES):
                quick_record = {
                    "trace_count": None,
                    "is_trace_contained": True,
                    "absorbing_class_id": "C0",
                    "absorbing_class_min_order": 4,
                    "absorbing_class_trace_count": 3,
                    "is_compatibility_universal": None,
                    "status": "trace_contained",
                }
                for ports in missing:
                    record = {
                        "graph6": g6,
                        "ports": list(ports),
                        "structural_class": sc,
                        **quick_record,
                    }
                    fout.write(json.dumps(record, sort_keys=True) + "\n")
                    fout.flush()
                    seen.add((g6, tuple(ports)))
                    written += 1
                if args.progress_every and (idx + 1) % args.progress_every == 0:
                    el = time.time() - start
                    print(
                        f"  [{idx+1}/{len(graphs)}] elapsed={el:.0f}s "
                        f"written={written} skipped={skipped} (fast-path C0)",
                        file=sys.stderr,
                    )
                continue

            # Slow path: C0 doesn't absorb, compute full trace set and
            # classify properly. Derive both orientations from one trace
            # computation.
            base_traces = compute_trace_set_2pole(G, base_ports)
            trace_sets_by_ports = {tuple(base_ports): base_traces}
            if len(orientations) == 2:
                trace_sets_by_ports[tuple(orientations[1])] = reverse_trace_set(base_traces)

            for ports in missing:
                traces = trace_sets_by_ports.get(tuple(ports))
                if traces is None:
                    traces = compute_trace_set_2pole(G, ports)
                record = {
                    "graph6": g6,
                    "ports": list(ports),
                    "structural_class": sc,
                    **classify_trace_set(traces, universe, classes),
                }
                fout.write(json.dumps(record, sort_keys=True) + "\n")
                fout.flush()
                seen.add((g6, tuple(ports)))
                written += 1

            if args.progress_every and (idx + 1) % args.progress_every == 0:
                el = time.time() - start
                print(
                    f"  [{idx+1}/{len(graphs)}] elapsed={el:.0f}s "
                    f"written={written} skipped={skipped}",
                    file=sys.stderr,
                )

    # Build summary from checkpoint
    summary_path = args.summary_output or args.checkpoint.with_suffix(".summary.json")
    status_counts: Counter = Counter()
    structural_counts: Counter = Counter()
    absorber_counts: Counter = Counter()
    neither: list = []
    universal_not_contained: list = []
    with args.checkpoint.open() as fin:
        for line in fin:
            r = json.loads(line)
            status_counts[r["status"]] += 1
            structural_counts[r["structural_class"]] += 1
            if r["absorbing_class_id"]:
                absorber_counts[r["absorbing_class_id"]] += 1
            if r["status"] == "neither":
                neither.append(r)
            elif r["status"] == "compat_universal_not_contained":
                universal_not_contained.append(r)

    summary = {
        "n": args.n,
        "lattice_meta": payload["meta"],
        "filter": args.filter,
        "limit": args.limit,
        "total_oriented_sides_processed": sum(status_counts.values()),
        "status_counts": dict(status_counts),
        "structural_counts": dict(structural_counts),
        "top_absorbing_classes": absorber_counts.most_common(20),
        "neither_count": len(neither),
        "neither_records": neither,
        "compat_universal_not_contained_count": len(universal_not_contained),
        "compat_universal_not_contained_records": universal_not_contained,
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"wrote {summary_path}", file=sys.stderr)
    print(json.dumps(summary["status_counts"]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
