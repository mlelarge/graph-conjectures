"""Build the 2-pole gadget trace-set lattice.

This is the first computational substrate for Lemma 2 in
docs/minimal_counterexample.md.  It enumerates connected simple subcubic
2-poles with two degree-2 ports and all other vertices degree 3, computes the
full 2-pole trace set (including the tree-connectivity partition pi), groups
gadgets by identical trace set, and computes the Hasse diagram for trace-set
inclusion.

The order of the two ports matters: a side of a 2-edge-cut has an ordered
boundary (e1, e2).  By default both port orders are included as oriented
gadgets.
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

from decomposition import compute_trace_set_2pole  # noqa: E402


TraceKey = tuple[tuple[str, str], tuple[tuple[int, ...], ...]]
TraceSetKey = frozenset[TraceKey]


def pi_key(pi: frozenset) -> tuple[tuple[int, ...], ...]:
    """Stable, hashable representation of a pi partition."""
    return tuple(sorted(tuple(sorted(block)) for block in pi))


def trace_key(trace: tuple[tuple[str, str], frozenset]) -> TraceKey:
    chi, pi = trace
    return (tuple(chi), pi_key(pi))


def trace_set_key(traces: set[tuple[tuple[str, str], frozenset]]) -> TraceSetKey:
    return frozenset(trace_key(t) for t in traces)


def trace_json(key: TraceKey) -> dict[str, Any]:
    chi, pi = key
    return {"chi": list(chi), "pi": [list(block) for block in pi]}


def trace_set_json(key: TraceSetKey) -> list[dict[str, Any]]:
    return [trace_json(t) for t in sorted(key)]


def trace_key_from_json(t: dict[str, Any]) -> TraceKey:
    chi = (t["chi"][0], t["chi"][1])
    pi = tuple(sorted(tuple(sorted(block)) for block in t["pi"]))
    return (chi, pi)


def trace_set_key_from_json(rows: list[dict[str, Any]]) -> TraceSetKey:
    return frozenset(trace_key_from_json(t) for t in rows)


def graph6_string(G: nx.Graph) -> str:
    return nx.to_graph6_bytes(G, header=False).decode().strip()


def stable_record_key(n: int, graph_index: int, ports: list[int]) -> str:
    return f"{n}:{graph_index}:{','.join(str(p) for p in ports)}"


def record_to_checkpoint_json(record: dict) -> dict[str, Any]:
    return {
        "id": record["id"],
        "key": record["_record_key"],
        "n": record["n"],
        "graph_index": record["graph_index"],
        "graph6": record["graph6"],
        "ports": record["ports"],
        "trace_count": record["trace_count"],
        "traces": trace_set_json(record["_trace_key"]),
    }


def record_from_checkpoint_json(row: dict[str, Any]) -> dict:
    key = trace_set_key_from_json(row["traces"])
    return {
        "id": row["id"],
        "_record_key": row["key"],
        "n": row["n"],
        "graph_index": row["graph_index"],
        "graph6": row["graph6"],
        "ports": row["ports"],
        "trace_count": row["trace_count"],
        "_trace_key": key,
    }


def load_checkpoint(path: Path, n_min: int, n_max: int) -> list[dict]:
    if not path.exists():
        return []
    records: dict[str, dict] = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        record = record_from_checkpoint_json(row)
        if n_min <= record["n"] <= n_max:
            records[record["_record_key"]] = record
    return sorted(records.values(), key=lambda r: int(r["id"][1:]))


def append_checkpoint(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(json.dumps(record_to_checkpoint_json(record), sort_keys=True) + "\n")
        fh.flush()


def enumerate_2pole_graphs(n: int) -> list[nx.Graph]:
    """Enumerate connected 2-pole subcubic graphs on n vertices via nauty."""
    if n % 2 == 1 or n < 4:
        return []
    if shutil.which("geng") is None:
        raise RuntimeError("geng not found on PATH")

    # Degree sequence: two degree-2 vertices and n-2 degree-3 vertices.
    # Sum degrees = 2*2 + 3*(n-2) = 3n - 2.
    m = (3 * n - 2) // 2
    proc = subprocess.run(
        ["geng", "-q", "-c", "-d2", "-D3", str(n), f"{m}:{m}"],
        check=True,
        capture_output=True,
    )
    graphs: list[nx.Graph] = []
    for line in proc.stdout.splitlines():
        if not line:
            continue
        G = nx.from_graph6_bytes(line)
        degs = sorted(d for _, d in G.degree())
        if degs == [2, 2] + [3] * (n - 2):
            graphs.append(G)
    return graphs


def oriented_ports(G: nx.Graph, mode: str) -> list[list[int]]:
    ports = sorted(v for v, d in G.degree() if d == 2)
    if len(ports) != 2:
        raise ValueError(f"expected exactly two ports, got {ports}")
    if mode == "canonical":
        return [ports]
    if mode == "both":
        return [ports, [ports[1], ports[0]]]
    raise ValueError(f"bad orientation mode {mode!r}")


def compute_records(
    n_min: int,
    n_max: int,
    orientations: str,
    limit_per_order: int | None,
    progress_every: int = 0,
    checkpoint: Path | None = None,
) -> list[dict]:
    records = load_checkpoint(checkpoint, n_min, n_max) if checkpoint else []
    seen = {record["_record_key"] for record in records}
    next_id = 0
    if records:
        next_id = max(int(record["id"][1:]) for record in records) + 1
        if progress_every:
            print(f"loaded {len(records)} checkpointed oriented gadgets", file=sys.stderr)

    start = n_min if n_min % 2 == 0 else n_min + 1
    for n in range(max(4, start), n_max + 1, 2):
        graphs = enumerate_2pole_graphs(n)
        if limit_per_order is not None:
            graphs = graphs[:limit_per_order]
        if progress_every:
            print(f"n={n}: {len(graphs)} unoriented gadgets", file=sys.stderr)
        for graph_index, G in enumerate(graphs):
            g6 = graph6_string(G)
            for ports in oriented_ports(G, orientations):
                rec_key = stable_record_key(n, graph_index, ports)
                if rec_key in seen:
                    continue
                traces = compute_trace_set_2pole(G, ports)
                key = trace_set_key(traces)
                record = {
                    "id": f"g{next_id}",
                    "_record_key": rec_key,
                    "n": n,
                    "graph_index": graph_index,
                    "graph6": g6,
                    "ports": ports,
                    "trace_count": len(key),
                    "_trace_key": key,
                }
                records.append(record)
                seen.add(rec_key)
                if checkpoint is not None:
                    append_checkpoint(checkpoint, record)
                next_id += 1
                if progress_every and next_id % progress_every == 0:
                    print(f"  computed {next_id} oriented gadgets", file=sys.stderr)
    return records


def build_classes(records: list[dict]) -> tuple[list[dict], dict[TraceSetKey, str]]:
    grouped: dict[TraceSetKey, list[dict]] = defaultdict(list)
    for record in records:
        grouped[record["_trace_key"]].append(record)

    classes: list[dict] = []
    key_to_class: dict[TraceSetKey, str] = {}
    for i, (key, members) in enumerate(
        sorted(grouped.items(), key=lambda kv: (len(kv[0]), min(m["n"] for m in kv[1]), len(kv[1])))
    ):
        class_id = f"C{i}"
        key_to_class[key] = class_id
        member_ids = [m["id"] for m in members]
        classes.append({
            "id": class_id,
            "trace_count": len(key),
            "member_count": len(members),
            "min_order": min(m["n"] for m in members),
            "members": member_ids,
            "traces": trace_set_json(key),
            "_trace_key": key,
        })
    return classes, key_to_class


def cover_edges(classes: list[dict]) -> list[dict[str, str]]:
    """Return Hasse edges A -> B where Trace(A) is a proper subset of Trace(B)."""
    keys = {c["id"]: c["_trace_key"] for c in classes}
    proper: list[tuple[str, str]] = []
    for a_id, a_key in keys.items():
        for b_id, b_key in keys.items():
            if a_id == b_id:
                continue
            if a_key < b_key:
                proper.append((a_id, b_id))

    covers: list[dict[str, str]] = []
    for a_id, b_id in proper:
        a_key = keys[a_id]
        b_key = keys[b_id]
        has_intermediate = any(
            c_id not in (a_id, b_id) and a_key < c_key < b_key
            for c_id, c_key in keys.items()
        )
        if not has_intermediate:
            covers.append({"subset": a_id, "superset": b_id})
    return sorted(covers, key=lambda e: (e["subset"], e["superset"]))


def strip_internal_keys(payload: dict) -> dict:
    for record in payload["gadgets"]:
        record.pop("_trace_key", None)
        record.pop("_record_key", None)
        record["trace_class"] = payload["_record_class"][record["id"]]
    for cls in payload["classes"]:
        cls.pop("_trace_key", None)
    payload.pop("_record_class", None)
    return payload


def build_payload(
    n_max: int,
    orientations: str,
    limit_per_order: int | None = None,
    progress_every: int = 0,
    n_min: int = 4,
    checkpoint: Path | None = None,
) -> dict:
    records = compute_records(
        n_min,
        n_max,
        orientations,
        limit_per_order,
        progress_every,
        checkpoint,
    )
    classes, key_to_class = build_classes(records)
    record_class = {r["id"]: key_to_class[r["_trace_key"]] for r in records}
    covers = cover_edges(classes)
    maximal = sorted(
        c["id"] for c in classes
        if not any(edge["subset"] == c["id"] for edge in covers)
    )
    minimal = sorted(
        c["id"] for c in classes
        if not any(edge["superset"] == c["id"] for edge in covers)
    )
    counts_by_order: dict[str, int] = defaultdict(int)
    for record in records:
        counts_by_order[str(record["n"])] += 1

    payload = {
        "meta": {
            "n_max": n_max,
            "n_min": n_min,
            "orientations": orientations,
            "limit_per_order": limit_per_order,
            "checkpoint": str(checkpoint) if checkpoint else None,
            "gadget_count": len(records),
            "trace_class_count": len(classes),
            "counts_by_order": dict(sorted(counts_by_order.items(), key=lambda kv: int(kv[0]))),
            "order_convention": "ports are ordered; trace pi uses port indices 0 and 1",
            "inclusion_convention": "cover edge A->B means Trace(A) is a proper subset of Trace(B)",
        },
        "gadgets": records,
        "classes": classes,
        "cover_edges": covers,
        "minimal_classes": minimal,
        "maximal_classes": maximal,
        "_record_class": record_class,
    }
    return strip_internal_keys(payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=4)
    parser.add_argument("--n-max", type=int, default=10)
    parser.add_argument("--orientations", choices=("both", "canonical"), default="both")
    parser.add_argument("--limit-per-order", type=int, default=None)
    parser.add_argument("--progress-every", type=int, default=25)
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="JSONL checkpoint of computed oriented gadget trace sets",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="JSON output path; default data/gadget_lattice_2pole_n{n}.json",
    )
    args = parser.parse_args()

    output = args.output
    if output is None:
        suffix = "both" if args.orientations == "both" else "canonical"
        output = ROOT / "data" / f"gadget_lattice_2pole_n{args.n_max}_{suffix}.json"

    payload = build_payload(
        args.n_max,
        args.orientations,
        args.limit_per_order,
        args.progress_every,
        args.n_min,
        args.checkpoint,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    meta = payload["meta"]
    print(f"wrote {output}")
    print(
        f"gadgets={meta['gadget_count']} trace_classes={meta['trace_class_count']} "
        f"cover_edges={len(payload['cover_edges'])}"
    )
    print(f"counts_by_order={meta['counts_by_order']}")
    print(f"minimal_classes={payload['minimal_classes']}")
    print(f"maximal_classes={payload['maximal_classes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
