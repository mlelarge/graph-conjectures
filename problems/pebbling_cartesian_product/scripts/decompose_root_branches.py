"""Decompose Hurlbert-style strategies into root-branch columns.

A Hurlbert strategy with root ``r`` and root-children ``u_1, ..., u_k``
(neighbours of ``r`` in the strategy's tree, all in ``V(T)``)
decomposes into a sum of ``k`` one-branch strategies, each with a single
root-child. Mathematical justification: the doubling rule
``w(parent) >= 2 w(child)`` only constrains parent-child pairs in the
tree, and the root contributes weight 0 to every branch's constraints.
So restricting the weight function to ``{r}`` plus the subtree at one
root-child yields a valid Hurlbert strategy on its own.

Decomposing a multi-branch strategy into single-branch strategies can
only **improve** the master LP optimum: each branch becomes an
independent column with its own multiplier, and the LP is free to
assign different alpha to different branches. If the original strategy
was already LP-optimal as one column, the LP will simply assign equal
alpha to all branches and recover the original objective.

Usage::

    python scripts/decompose_root_branches.py <input_certificate.json> <output_certificate.json>
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict, deque
from pathlib import Path


def decompose_strategy(strat: dict, root: int) -> list[dict]:
    """Decompose one strategy by root-branch.

    Returns a list of new strategy dicts, one per root-child of the
    strategy's tree. If the tree has only one root-child, returns a
    single-element list containing a copy of ``strat``.
    """
    edges = [tuple(e) for e in strat["tree_edges"]]
    weights_str = strat.get("weights", {})
    weights = {int(k): v for k, v in weights_str.items()}

    incident = defaultdict(list)
    for u, v in edges:
        incident[u].append(v)
        incident[v].append(u)

    # BFS from root to determine the parent map (defines branches uniquely).
    parent = {root: None}
    queue = deque([root])
    while queue:
        u = queue.popleft()
        for v in incident.get(u, []):
            if v not in parent:
                parent[v] = u
                queue.append(v)

    # Build children dict
    children: dict[int, list[int]] = defaultdict(list)
    for v, p in parent.items():
        if p is not None:
            children[p].append(v)

    root_children = sorted(children[root])
    if len(root_children) <= 1:
        out = dict(strat)
        out["name"] = strat.get("name", "") + " (one root-child)"
        return [out]

    branches: list[dict] = []
    for rc in root_children:
        # Collect subtree vertices reachable from rc without going through root
        subtree = {rc}
        q = deque([rc])
        while q:
            u = q.popleft()
            for c in children.get(u, []):
                if c not in subtree:
                    subtree.add(c)
                    q.append(c)
        # New weights = root (= 0) plus subtree weights
        b_weights = {str(root): "0"}
        for v in subtree:
            b_weights[str(v)] = weights.get(v, "0")
        # Tree edges: edges in the subtree plus the (root, rc) edge.
        b_edges = [[root, rc] if root < rc else [rc, root]]
        for v in subtree:
            for c in children.get(v, []):
                if c in subtree:
                    a, b = (v, c) if v < c else (c, v)
                    b_edges.append([a, b])
        # Deduplicate edges (defensive)
        b_edges_dedup = sorted({tuple(e) for e in b_edges})
        b_edges_clean = [list(e) for e in b_edges_dedup]
        branches.append(
            {
                "name": (
                    strat.get("name", "")
                    + f" (branch at root-child flat {rc})"
                ),
                "tree_edges": b_edges_clean,
                "weights": b_weights,
                "basic": strat.get("basic", False),
            }
        )
    return branches


def decompose_certificate(payload: dict) -> dict:
    """Decompose every strategy in the certificate by root-branch.

    Preserves dual feasibility by giving each branch the SAME multiplier
    as its parent strategy. So if the input had alpha_i for strategy
    T_i and T_i has k_i root-branches, the output has alpha_i replicated
    k_i times. Sum alpha_branch * b_branch matches the input
    sum alpha_i * b_i exactly.
    """
    new_strats: list[dict] = []
    new_multipliers: list[str] = []
    input_multipliers = list(payload.get("dual_multipliers", [])) or [
        f"1/{len(payload['strategies'])}"
    ] * len(payload["strategies"])
    for strat, alpha in zip(payload["strategies"], input_multipliers):
        branches = decompose_strategy(strat, int(payload["root"]))
        new_strats.extend(branches)
        new_multipliers.extend([alpha] * len(branches))
    out = dict(payload)
    out["strategies"] = new_strats
    out["dual_multipliers"] = new_multipliers
    out["claimed_bound"] = payload.get("claimed_bound", 0)
    note = payload.get("notes", "")
    out["notes"] = (
        (note + " ").strip()
        + " Decomposed via scripts/decompose_root_branches.py: each "
        "multi-branch root strategy is split into one strategy per "
        "root-child, with weights restricted to that root-child's "
        "subtree."
    )
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("input", help="path to input certificate JSON")
    ap.add_argument("output", help="path to write decomposed certificate JSON")
    args = ap.parse_args()
    with open(args.input) as fp:
        payload = json.load(fp)
    out = decompose_certificate(payload)
    with open(args.output, "w") as fp:
        json.dump(out, fp, indent=2)
    n_old = len(payload["strategies"])
    n_new = len(out["strategies"])
    print(f"decomposed {n_old} strategies -> {n_new} root-branch columns")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
