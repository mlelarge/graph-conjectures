#!/usr/bin/env python3
"""Layout the conjecture relation graph (data/relations.json) for the site.

Pure-python, dependency-free and deterministic (no randomness): a
Fruchterman–Reingold force layout per connected component, components then
packed left-to-right / top-to-bottom by decreasing size.

Used by build.py to render site/relations/; can also be run standalone to
dump the positioned graph as JSON:

    python scraper/relations_layout.py > /tmp/relations_graph.json
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

# Golden-angle initial placement makes the layout deterministic yet spread out.
GOLDEN_ANGLE = math.pi * (3.0 - math.sqrt(5.0))

ITERATIONS = 400


def _components(node_ids: list[str], edges: list[dict]) -> list[list[str]]:
    adj: dict[str, set[str]] = defaultdict(set)
    for e in edges:
        adj[e["source"]].add(e["target"])
        adj[e["target"]].add(e["source"])
    seen: set[str] = set()
    comps: list[list[str]] = []
    for nid in node_ids:
        if nid in seen:
            continue
        comp, stack = [], [nid]
        seen.add(nid)
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        comps.append(sorted(comp))
    comps.sort(key=lambda c: (-len(c), c[0]))
    return comps


def _layout_component(comp: list[str], edges: list[dict]) -> dict[str, tuple[float, float]]:
    """Fruchterman–Reingold on one component, in a unit-area square."""
    n = len(comp)
    if n == 1:
        return {comp[0]: (0.0, 0.0)}
    idx = {nid: i for i, nid in enumerate(comp)}
    in_comp = set(comp)
    links = [(idx[e["source"]], idx[e["target"]]) for e in edges
             if e["source"] in in_comp and e["target"] in in_comp]

    size = math.sqrt(n) * 120.0          # side of the drawing square
    k = size / math.sqrt(n)              # ideal edge length
    # deterministic sunflower-spiral initial positions
    pos = []
    for i in range(n):
        r = size * 0.45 * math.sqrt((i + 0.5) / n)
        a = i * GOLDEN_ANGLE
        pos.append([r * math.cos(a), r * math.sin(a)])

    temp = size * 0.12
    cool = temp / (ITERATIONS + 1)
    for _ in range(ITERATIONS):
        disp = [[0.0, 0.0] for _ in range(n)]
        # repulsion (O(n^2); n ≤ a few hundred, fine)
        for i in range(n):
            xi, yi = pos[i]
            for j in range(i + 1, n):
                dx, dy = xi - pos[j][0], yi - pos[j][1]
                d2 = dx * dx + dy * dy or 1e-6
                f = k * k / d2
                disp[i][0] += dx * f; disp[i][1] += dy * f
                disp[j][0] -= dx * f; disp[j][1] -= dy * f
        # attraction along edges
        for i, j in links:
            dx = pos[i][0] - pos[j][0]
            dy = pos[i][1] - pos[j][1]
            d = math.sqrt(dx * dx + dy * dy) or 1e-3
            f = d / k
            fx, fy = dx * f, dy * f
            disp[i][0] -= fx; disp[i][1] -= fy
            disp[j][0] += fx; disp[j][1] += fy
        # bounded displacement + light centering pull
        for i in range(n):
            dx, dy = disp[i]
            dx -= pos[i][0] * 0.02
            dy -= pos[i][1] * 0.02
            d = math.sqrt(dx * dx + dy * dy) or 1e-9
            step = min(d, temp)
            pos[i][0] += dx / d * step
            pos[i][1] += dy / d * step
        temp = max(temp - cool, size * 0.005)

    return {nid: (pos[idx[nid]][0], pos[idx[nid]][1]) for nid in comp}


def _pack(placed: list[dict[str, tuple[float, float]]]) -> dict[str, tuple[float, float]]:
    """Pack per-component layouts into rows, biggest first."""
    boxes = []
    for compos in placed:
        xs = [p[0] for p in compos.values()]
        ys = [p[1] for p in compos.values()]
        pad = 90.0
        boxes.append((min(xs) - pad, min(ys) - pad,
                      max(xs) + pad, max(ys) + pad, compos))
    row_width = max(1600.0, math.sqrt(sum((b[2]-b[0]) * (b[3]-b[1]) for b in boxes)) * 1.6)
    out: dict[str, tuple[float, float]] = {}
    cx = cy = 0.0
    row_h = 0.0
    for (x0, y0, x1, y1, compos) in boxes:
        w, h = x1 - x0, y1 - y0
        if cx > 0 and cx + w > row_width:
            cx = 0.0
            cy += row_h
            row_h = 0.0
        for nid, (x, y) in compos.items():
            out[nid] = (round(x - x0 + cx, 1), round(y - y0 + cy, 1))
        cx += w
        row_h = max(row_h, h)
    return out


def build_relations_graph(relations: dict, node_meta: dict[str, dict]) -> dict | None:
    """Positioned node/edge lists for the relations page.

    relations: parsed data/relations.json
    node_meta: id -> {name, status, url, source, kind} for every id that may
               appear in an edge (missing ids are dropped with their edges).
    """
    rels = [r for r in relations.get("relations", [])
            if r["source"] in node_meta and r["target"] in node_meta]
    if not rels:
        return None

    node_ids = sorted({r["source"] for r in rels} | {r["target"] for r in rels})
    comps = _components(node_ids, rels)
    positions = _pack([_layout_component(c, rels) for c in comps])

    nodes = []
    for nid in node_ids:
        m = node_meta[nid]
        x, y = positions[nid]
        nodes.append({
            "id": nid, "x": x, "y": y,
            "name": m["name"], "status": m.get("status") or "unclear",
            "url": m["url"], "source": m["source"], "kind": m.get("kind", ""),
        })
    edges = []
    for r in rels:
        edges.append({
            "source": r["source"], "target": r["target"],
            "relation": r["relation"], "verdict": r["verdict"],
            "confidence": r["confidence"], "argument": r["argument"],
            "citations": r.get("citations", []),
        })
    return {
        "nodes": nodes,
        "edges": edges,
        "n_components": len(comps),
        "semantics": relations.get("semantics", {}),
        "verification_note": relations.get("verification_note", ""),
    }


def relations_by_node(relations: dict, node_meta: dict[str, dict]) -> dict[str, list[dict]]:
    """Per-node relation lists for the problem pages.

    Directed relations produce an 'implies' entry on the source page and an
    'implied by' entry on the target page; symmetric relations appear on both.
    """
    out: dict[str, list[dict]] = defaultdict(list)
    for r in relations.get("relations", []):
        s, t = r["source"], r["target"]
        if s not in node_meta or t not in node_meta:
            continue
        base = {"relation": r["relation"], "verdict": r["verdict"],
                "confidence": r["confidence"], "argument": r["argument"]}
        if r["relation"] == "implies":
            out[s].append({**base, "role": "implies", "other": node_meta[t], "other_id": t})
            out[t].append({**base, "role": "implied by", "other": node_meta[s], "other_id": s})
        else:
            label = {"equivalent_to": "equivalent to",
                     "same_conjecture": "same conjecture as",
                     "related_only": "related to"}.get(r["relation"], r["relation"])
            out[s].append({**base, "role": label, "other": node_meta[t], "other_id": t})
            out[t].append({**base, "role": label, "other": node_meta[s], "other_id": s})
    role_order = {"equivalent_to": 0, "same_conjecture": 1, "implies": 2, "related_only": 3}
    for lst in out.values():
        lst.sort(key=lambda e: (role_order.get(e["relation"], 9), e["other"]["name"].lower()))
    return dict(out)


if __name__ == "__main__":
    project = Path(__file__).resolve().parent.parent
    relations = json.loads((project / "data" / "relations.json").read_text(encoding="utf-8"))
    # Standalone mode: minimal node meta straight from the id namespace.
    meta = {}
    for r in relations["relations"]:
        for nid in (r["source"], r["target"]):
            kind, _, rest = nid.partition(":")
            meta.setdefault(nid, {
                "name": rest, "status": "unclear", "source": kind,
                "url": (f"op/{rest}/" if kind == "opg" else f"arxiv/{rest}/"),
            })
    print(json.dumps(build_relations_graph(relations, meta), indent=1))
