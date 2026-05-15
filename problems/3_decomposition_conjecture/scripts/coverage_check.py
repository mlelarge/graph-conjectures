"""Coverage and replacement checks against the 2-pole gadget lattice.

Given an arbitrary 2-pole side (H, ports), compute Trace(H, ports) and ask:

  (1) Envelope direction: is there a lattice class C with
      Trace(H, ports) subseteq Trace(C)?  This asks whether the side lives
      inside the trace universe already realised by the lattice.  It is useful
      diagnostic information, but it is not the Lemma-2 replacement direction.

  (2) Which traces of (H, ports) are not in *any* lattice class's trace
      set? These are the "uncovered" traces -- combinations of (chi, pi)
      that no gadget on <= n_max vertices in the lattice realises.

  (3) Replacement direction: is there a strictly smaller lattice class C with
      Trace(C) subseteq Trace(H, ports)?  This is the direction needed for
      Lemma 2, exposed by find_replacement_gadget().

Outputs JSON to stdout (or --output) so it can be archived alongside
data/gadget_lattice_2pole_n10_both.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from decomposition import compute_trace_set_2pole  # noqa: E402
from gadget_lattice import pi_key, trace_key, trace_set_key  # noqa: E402


def trace_key_from_json(t: dict[str, Any]) -> tuple[tuple[str, str], tuple[tuple[int, ...], ...]]:
    chi = (t["chi"][0], t["chi"][1])
    pi = tuple(sorted(tuple(sorted(block)) for block in t["pi"]))
    return (chi, pi)


def trace_set_from_class(cls: dict[str, Any]) -> frozenset:
    return frozenset(trace_key_from_json(t) for t in cls["traces"])


def load_lattice(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def find_replacement_gadget(
    H: nx.Graph,
    ports: list[int],
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Find a candidate Lemma-2 replacement for the 2-pole side (H, ports).

    The Lemma-2 trace-containment reduction requires:
      Trace(A') subseteq Trace(H)   AND   |V(A')| < |V(H)|.

    Returns a dict:
      - side_trace_count            (|Trace(H, ports)|)
      - candidate_class_ids         (classes C with Trace(C) subseteq Trace(H))
      - smallest_candidate          (best replacement: smallest |V(A')| among
                                     candidates, then largest |Trace(A')|)
      - replaceable                 (True iff a strictly-smaller candidate exists)
      - traces_only_in_side         (Trace(H) - Trace(smallest_candidate);
                                     these traces would be "lost" by the
                                     replacement — fine for the reduction
                                     since the inclusion goes the other way)

    Direction note: this function tests the CORRECT inclusion direction
    for Lemma 2, opposite to the older `check_coverage` (which tests
    Trace(H) subseteq Trace(C), useful for a different question).
    """
    side_traces = compute_trace_set_2pole(H, ports)
    side_key = trace_set_key(side_traces)
    side_size = H.number_of_nodes()

    candidates: list[dict[str, Any]] = []
    for cls in payload["classes"]:
        cls_traces = trace_set_from_class(cls)
        if cls_traces <= side_key:
            candidates.append(cls)

    strict_candidates = [c for c in candidates if c["min_order"] < side_size]

    best = None
    if strict_candidates:
        best = min(
            strict_candidates,
            key=lambda c: (c["min_order"], -c["trace_count"]),
        )

    extra_in_side: frozenset = side_key
    if best is not None:
        best_traces = trace_set_from_class(best)
        extra_in_side = side_key - best_traces

    return {
        "side_trace_count": len(side_key),
        "side_size": side_size,
        "candidate_class_ids": [c["id"] for c in candidates],
        "strict_candidate_class_ids": [c["id"] for c in strict_candidates],
        "smallest_candidate": (
            {
                "id": best["id"],
                "min_order": best["min_order"],
                "trace_count": best["trace_count"],
            }
            if best else None
        ),
        "replaceable": bool(strict_candidates),
        "traces_only_in_side": [
            {"chi": list(chi), "pi": [list(b) for b in pi]}
            for chi, pi in sorted(extra_in_side)
        ],
    }




def union_of_all_traces(payload: dict[str, Any]) -> frozenset:
    out: set = set()
    for cls in payload["classes"]:
        out |= trace_set_from_class(cls)
    return frozenset(out)


def check_coverage(
    H: nx.Graph,
    ports: list[int],
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Compute Trace(H, ports) and compare to the lattice.

    Returns a dict with:
      - side_trace_count
      - side_traces            (list of trace_json dicts)
      - covering_class_ids     (list of class IDs C with side ⊆ Trace(C))
      - smallest_covering_class (smallest by min_order among coverers, or None)
      - uncovered_traces       (side traces not in union of all class trace sets)
      - per_class_missing      (for each maximal class: which side traces are
                                missing from that class)
    """
    side_traces = compute_trace_set_2pole(H, ports)
    side_key = trace_set_key(side_traces)

    coverers: list[dict[str, Any]] = []
    for cls in payload["classes"]:
        cls_traces = trace_set_from_class(cls)
        if side_key <= cls_traces:
            coverers.append(cls)

    smallest = None
    if coverers:
        smallest = min(coverers, key=lambda c: (c["min_order"], c["trace_count"]))

    universe = union_of_all_traces(payload)
    uncovered = sorted(t for t in side_key if t not in universe)

    per_class_missing: dict[str, list] = {}
    for cls_id in payload["maximal_classes"]:
        cls = next(c for c in payload["classes"] if c["id"] == cls_id)
        cls_traces = trace_set_from_class(cls)
        missing = sorted(t for t in side_key if t not in cls_traces)
        per_class_missing[cls_id] = [
            {"chi": list(chi), "pi": [list(b) for b in pi]} for chi, pi in missing
        ]

    return {
        "side_trace_count": len(side_key),
        "side_traces": [
            {"chi": list(chi), "pi": [list(b) for b in pi]}
            for chi, pi in sorted(side_key)
        ],
        "covering_class_ids": [c["id"] for c in coverers],
        "smallest_covering_class": (
            {"id": smallest["id"], "min_order": smallest["min_order"], "trace_count": smallest["trace_count"]}
            if smallest else None
        ),
        "uncovered_traces": [
            {"chi": list(chi), "pi": [list(b) for b in pi]} for chi, pi in uncovered
        ],
        "per_maximal_missing": per_class_missing,
    }


def load_graph(graph6: str | None, edges: list[list[int]] | None) -> nx.Graph:
    if graph6 is not None:
        return nx.from_graph6_bytes(graph6.encode())
    if edges is not None:
        G = nx.Graph()
        G.add_edges_from(edges)
        return G
    raise ValueError("provide --graph6 or --edges")


def auto_ports(G: nx.Graph, order: list[int] | None) -> list[int]:
    if order is not None:
        return order
    ports = sorted(v for v, d in G.degree() if d == 2)
    if len(ports) != 2:
        raise ValueError(f"expected exactly 2 ports, found {ports}")
    return ports


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph6", type=str, default=None)
    parser.add_argument(
        "--edges",
        type=str,
        default=None,
        help='JSON list of [u, v] edges, e.g. "[[0,1],[1,2]]"',
    )
    parser.add_argument(
        "--ports",
        type=str,
        default=None,
        help='JSON list of two port-vertex labels, e.g. "[6, 7]"',
    )
    parser.add_argument(
        "--lattice",
        type=Path,
        default=ROOT / "data" / "gadget_lattice_2pole_n10_both.json",
    )
    parser.add_argument(
        "--mode",
        choices=("coverage", "replacement"),
        default="coverage",
        help="coverage tests Trace(H) subseteq Trace(C); replacement tests Trace(C) subseteq Trace(H)",
    )
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    edges = json.loads(args.edges) if args.edges else None
    ports = json.loads(args.ports) if args.ports else None
    G = load_graph(args.graph6, edges)
    ports = auto_ports(G, ports)

    payload = load_lattice(args.lattice)
    if args.mode == "coverage":
        result = check_coverage(G, ports, payload)
    else:
        result = find_replacement_gadget(G, ports, payload)
    out = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(out)
    else:
        sys.stdout.write(out)

    if args.mode == "coverage":
        summary = (
            f"side_trace_count={result['side_trace_count']} "
            f"covers={len(result['covering_class_ids'])} "
            f"uncovered={len(result['uncovered_traces'])}"
        )
        if result["smallest_covering_class"]:
            s = result["smallest_covering_class"]
            summary += f" smallest_covering={s['id']}(min_order={s['min_order']})"
    else:
        summary = (
            f"side_trace_count={result['side_trace_count']} "
            f"replaceable={result['replaceable']} "
            f"strict_candidates={len(result['strict_candidate_class_ids'])}"
        )
        if result["smallest_candidate"]:
            s = result["smallest_candidate"]
            summary += f" smallest_candidate={s['id']}(min_order={s['min_order']})"
    print(summary, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
