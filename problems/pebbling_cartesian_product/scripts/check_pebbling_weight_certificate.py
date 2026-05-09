"""Rational checker for Hurlbert-style pebbling weight-function certificates.

Implements the Phase 2a deliverable from
``PEBBLING_CARTESIAN_PRODUCT_COUNTEREXAMPLE_PLAN.md``. The checker verifies
an upper bound ``pi(G, r) <= N`` from a *certificate* consisting of one or
more *strategies* (Hurlbert 2017, "The weight function lemma for graph
pebbling") together with non-negative *dual multipliers*. Every arithmetic
step uses ``fractions.Fraction``; no floating point is used in any
acceptance decision.

## Strategy and weight-function lemma (Hurlbert 2017)

Let ``G`` be a graph and ``r`` a root. A *strategy* of ``G`` rooted at ``r``
is a subtree ``T`` of ``G`` (V(T) subset V(G), E(T) subset E(G), |V(T)| >= 2,
T connected and acyclic), rooted at ``r``, together with a non-negative
weight function ``w: V(G) -> Q_{>=0}`` such that:

1. ``w(r) = 0``;
2. for every ``v in V(T) \\ {r}`` whose parent ``v^+`` in ``T`` is **not**
   the root, ``w(v^+) = 2 w(v)`` (basic) or ``w(v^+) >= 2 w(v)`` (nonbasic);
3. ``w(v) = 0`` for every ``v not in V(T)``.

Define ``b_T = sum_{v in V(T) \\ {r}} w(v)`` ("the weight of the strategy
configuration"). The Weight Function Lemma states: every ``r``-unsolvable
configuration ``C`` with ``C(r) = 0`` satisfies ``sum_v w(v) C(v) <= b_T``.

## Dual certificate of an upper bound

Given strategies ``T_1,...,T_k`` with weight functions ``w_1,...,w_k`` and
strategy-weights ``b_1,...,b_k``, plus non-negative multipliers
``alpha_1,...,alpha_k``, suppose

    for every v in V(G) \\ {r},  sum_i alpha_i w_i(v)  >=  1.    (D)

Then for every ``r``-unsolvable configuration ``C`` with ``C(r) = 0``,

    |C| = sum_v C(v)
        = sum_v 1 * C(v)
        <= sum_v (sum_i alpha_i w_i(v)) C(v)            (by (D))
        =  sum_i alpha_i (sum_v w_i(v) C(v))
        <= sum_i alpha_i b_i                            (Weight Function Lemma).

Therefore ``pi(G, r) <= floor(sum_i alpha_i b_i) + 1``.

Condition (D) is the dual feasibility of the LP relaxation; the floor
allows the certificate to be tight when the primal LP optimum is integer.

## Certificate format

A certificate is a JSON object with the following shape (all rationals are
strings, parsed via ``Fraction``):

```
{
  "graph": "<name loadable from data/pebbling_product/graphs>"
            | {"n": int, "edges": [[u, v], ...], "name": str},
  "root": int,
  "claimed_bound": int,
  "strategies": [
    {
      "name": str (optional),
      "tree_edges": [[u, v], ...],   # subset of E(G), unordered pairs
      "weights": {"<vertex>": "<rational>", ...},  # full or partial; missing -> 0
      "basic": bool                   # whether parent-doubling is exact
    },
    ...
  ],
  "dual_multipliers": ["<rational>", ...]   # length == len(strategies)
}
```

The checker:

1. Loads the graph independently of the certificate.
2. Validates each strategy's tree (subset of ``E(G)``, connected, acyclic,
   contains the root).
3. Validates each weight function (``w(r) = 0``; basic / nonbasic
   parent-doubling along the rooted tree; ``w(v) = 0`` for ``v not in
   V(T)``).
4. Validates dual multipliers are non-negative.
5. Checks dual feasibility: ``sum_i alpha_i w_i(v) >= 1`` for every
   ``v != r``.
6. Computes ``b_i`` from the strategy and the weight function.
7. Computes ``derived_bound = floor(sum_i alpha_i b_i) + 1`` and compares
   it to ``claimed_bound``.

The checker rejects on the **first** failure and reports its location.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from pebbling_graphs import Graph, GRAPH_DIR, make_graph, load_named_graph


def _to_fraction(x) -> Fraction:
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x, 1)
    if isinstance(x, float):
        raise TypeError(
            "rational arithmetic only: refusing float input "
            f"({x!r}); pass rationals as strings"
        )
    if isinstance(x, str):
        return Fraction(x)
    raise TypeError(f"cannot convert {x!r} to Fraction")


@dataclass
class Strategy:
    """A Hurlbert strategy: a subtree of G rooted at r plus a weight function."""

    tree_edges: list[tuple[int, int]]
    weights: dict[int, Fraction]
    basic: bool = True
    name: str = ""


@dataclass
class WeightCertificate:
    graph_name: str
    root: int
    claimed_bound: int
    strategies: list[Strategy]
    dual_multipliers: list[Fraction]


@dataclass
class CertCheckResult:
    accepted: bool
    derived_bound: int | None
    claimed_bound: int
    sum_alpha_b: str  # rational, as string
    failure: dict | None = None
    message: str = ""
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "accepted": self.accepted,
            "derived_bound": self.derived_bound,
            "claimed_bound": self.claimed_bound,
            "sum_alpha_b": self.sum_alpha_b,
            "failure": self.failure,
            "message": self.message,
            "extra": self.extra,
        }


# --- loading ---------------------------------------------------------------


def _parse_strategy(payload: dict) -> Strategy:
    raw_edges = payload["tree_edges"]
    tree_edges: list[tuple[int, int]] = []
    for e in raw_edges:
        if len(e) != 2:
            raise ValueError(f"strategy edge {e!r} is not a pair")
        u, v = int(e[0]), int(e[1])
        if u == v:
            raise ValueError(f"strategy edge ({u},{v}) is a self-loop")
        if u > v:
            u, v = v, u
        tree_edges.append((u, v))
    weights_raw = payload.get("weights", {})
    weights: dict[int, Fraction] = {}
    for k, v in weights_raw.items():
        weights[int(k)] = _to_fraction(v)
    basic = bool(payload.get("basic", True))
    name = str(payload.get("name", ""))
    return Strategy(tree_edges=tree_edges, weights=weights, basic=basic, name=name)


def parse_certificate(payload: dict) -> WeightCertificate:
    graph_field = payload["graph"]
    if isinstance(graph_field, str):
        graph_name = graph_field
    else:
        graph_name = str(graph_field.get("name", "<inline>"))
    root = int(payload["root"])
    claimed_bound = int(payload["claimed_bound"])
    strategies = [_parse_strategy(s) for s in payload["strategies"]]
    duals = [_to_fraction(x) for x in payload["dual_multipliers"]]
    if len(duals) != len(strategies):
        raise ValueError(
            "len(dual_multipliers) "
            f"({len(duals)}) != len(strategies) ({len(strategies)})"
        )
    return WeightCertificate(
        graph_name=graph_name,
        root=root,
        claimed_bound=claimed_bound,
        strategies=strategies,
        dual_multipliers=duals,
    )


def load_certificate_file(path: str | Path) -> tuple[WeightCertificate, Graph]:
    """Load a certificate JSON file and resolve its graph independently."""
    p = Path(path)
    with p.open() as fp:
        payload = json.load(fp)
    cert = parse_certificate(payload)
    graph_field = payload["graph"]
    if isinstance(graph_field, str):
        g = load_named_graph(graph_field)
    else:
        g = make_graph(
            int(graph_field["n"]),
            graph_field["edges"],
            name=str(graph_field.get("name", "<inline>")),
        )
    return cert, g


# --- tree / strategy validation -------------------------------------------


def _build_rooted_tree(
    n: int,
    edges: Iterable[tuple[int, int]],
    root: int,
) -> tuple[set[int], dict[int, int], dict[int, int]]:
    """Return (V(T), parent_map, depth_map) or raise ValueError.

    Validates that ``edges`` form a connected acyclic subgraph that
    contains ``root``. ``parent_map[v]`` is the unique neighbour of ``v`` on
    the path to ``root``; ``depth_map[v]`` is the distance to ``root`` in
    the tree.
    """
    edges = list(edges)
    incident: dict[int, list[int]] = {}
    edge_set: set[tuple[int, int]] = set()
    vset: set[int] = set()
    for u, v in edges:
        if u == v:
            raise ValueError(f"tree edge ({u},{v}) is a self-loop")
        if (u, v) in edge_set:
            raise ValueError(f"duplicate tree edge ({u},{v})")
        edge_set.add((u, v))
        incident.setdefault(u, []).append(v)
        incident.setdefault(v, []).append(u)
        vset.add(u)
        vset.add(v)
    for v in vset:
        if not (0 <= v < n):
            raise ValueError(f"tree vertex {v} out of range [0,{n})")
    if root not in vset:
        # Allow a degenerate strategy with V(T) = {} only when |edges| = 0
        # and the strategy is to be interpreted as identically zero. In
        # practice this is useless, so we reject.
        raise ValueError(f"root {root} not in tree vertex set")
    # BFS from root: must reach every vertex of vset, exactly once each
    parent: dict[int, int] = {root: -1}
    depth: dict[int, int] = {root: 0}
    queue = [root]
    while queue:
        u = queue.pop(0)
        for w in incident.get(u, []):
            if w in parent:
                continue
            parent[w] = u
            depth[w] = depth[u] + 1
            queue.append(w)
    reached = set(parent)
    if reached != vset:
        unreachable = vset - reached
        raise ValueError(
            f"tree vertices {sorted(unreachable)} not reachable from root {root}; "
            "subgraph is disconnected"
        )
    if len(edge_set) != len(vset) - 1:
        raise ValueError(
            f"tree has {len(edge_set)} edges but {len(vset)} vertices; "
            "expected exactly |V|-1 edges in a tree"
        )
    return vset, parent, depth


def _validate_strategy(
    g: Graph,
    root: int,
    strategy: Strategy,
    *,
    strategy_idx: int,
) -> tuple[set[int], dict[int, int], Fraction] | dict:
    """Validate one strategy. On success returns (V(T), parent_map, b_T).
    On failure returns a failure dict."""
    g_edge_set: set[tuple[int, int]] = set(g.edges)
    for u, v in strategy.tree_edges:
        a, b = (u, v) if u < v else (v, u)
        if (a, b) not in g_edge_set:
            return {
                "stage": "strategy_tree_edges",
                "strategy_index": strategy_idx,
                "edge": [a, b],
                "reason": (
                    f"tree edge ({a},{b}) is not an edge of graph {g.name or '<unnamed>'}"
                ),
            }
    try:
        vset, parent, _ = _build_rooted_tree(g.n, strategy.tree_edges, root)
    except ValueError as exc:
        return {
            "stage": "strategy_tree_structure",
            "strategy_index": strategy_idx,
            "reason": str(exc),
        }

    # Validate weights:
    #   w(r) = 0
    #   w(v) = 0 for v not in V(T)
    #   for v in V(T) \ {r} with parent != r: basic -> w(v^+) = 2 w(v),
    #                                         nonbasic -> w(v^+) >= 2 w(v)
    weights = strategy.weights
    if weights.get(root, Fraction(0)) != 0:
        return {
            "stage": "strategy_weight_root",
            "strategy_index": strategy_idx,
            "reason": (
                f"w(root={root}) must be 0, got {weights[root]}"
            ),
        }
    for v, w in weights.items():
        if w < 0:
            return {
                "stage": "strategy_weight_nonneg",
                "strategy_index": strategy_idx,
                "vertex": v,
                "reason": f"w({v}) = {w} < 0",
            }
        if v not in vset and w != 0:
            return {
                "stage": "strategy_weight_outside_tree",
                "strategy_index": strategy_idx,
                "vertex": v,
                "reason": (
                    f"w({v}) = {w} but {v} is not in V(T); "
                    "weights outside the tree must be 0"
                ),
            }

    # Doubling inequalities along the rooted tree, except for vertices
    # whose parent is the root.
    for v in vset:
        if v == root:
            continue
        p = parent[v]
        if p == root:
            # Free weight on neighbors of r
            continue
        wv = weights.get(v, Fraction(0))
        wp = weights.get(p, Fraction(0))
        if strategy.basic:
            if wp != 2 * wv:
                return {
                    "stage": "strategy_basic_doubling",
                    "strategy_index": strategy_idx,
                    "vertex": v,
                    "parent": p,
                    "w_v": str(wv),
                    "w_parent": str(wp),
                    "reason": (
                        f"basic strategy requires w({p}) = 2 w({v}); "
                        f"got w({p}) = {wp}, 2 w({v}) = {2 * wv}"
                    ),
                }
        else:
            if wp < 2 * wv:
                return {
                    "stage": "strategy_nonbasic_doubling",
                    "strategy_index": strategy_idx,
                    "vertex": v,
                    "parent": p,
                    "w_v": str(wv),
                    "w_parent": str(wp),
                    "reason": (
                        f"nonbasic strategy requires w({p}) >= 2 w({v}); "
                        f"got w({p}) = {wp}, 2 w({v}) = {2 * wv}"
                    ),
                }

    # Strategy weight b_T = sum over non-root tree vertices of w(v)
    b_T = sum(
        (weights.get(v, Fraction(0)) for v in vset if v != root),
        start=Fraction(0),
    )
    return vset, parent, b_T


# --- main check -----------------------------------------------------------


def check_certificate(cert: WeightCertificate, graph: Graph) -> CertCheckResult:
    """Verify a Hurlbert-style weight-function certificate."""
    n = graph.n
    if not 0 <= cert.root < n:
        return CertCheckResult(
            accepted=False,
            derived_bound=None,
            claimed_bound=cert.claimed_bound,
            sum_alpha_b="0",
            failure={"stage": "root", "reason": f"root {cert.root} out of range [0,{n})"},
            message="invalid root",
        )

    if not cert.strategies:
        return CertCheckResult(
            accepted=False,
            derived_bound=None,
            claimed_bound=cert.claimed_bound,
            sum_alpha_b="0",
            failure={"stage": "strategies", "reason": "no strategies provided"},
            message="empty strategy list",
        )

    # Validate dual multipliers
    for i, alpha in enumerate(cert.dual_multipliers):
        if alpha < 0:
            return CertCheckResult(
                accepted=False,
                derived_bound=None,
                claimed_bound=cert.claimed_bound,
                sum_alpha_b="0",
                failure={
                    "stage": "dual_multipliers",
                    "strategy_index": i,
                    "reason": f"alpha[{i}] = {alpha} < 0",
                },
                message="negative dual multiplier",
            )

    # Validate each strategy and accumulate b_T
    strategy_data: list[tuple[set[int], dict[int, int], Fraction]] = []
    for idx, strat in enumerate(cert.strategies):
        result = _validate_strategy(graph, cert.root, strat, strategy_idx=idx)
        if isinstance(result, dict):
            return CertCheckResult(
                accepted=False,
                derived_bound=None,
                claimed_bound=cert.claimed_bound,
                sum_alpha_b="0",
                failure=result,
                message=result.get("reason", "strategy validation failed"),
            )
        strategy_data.append(result)

    # Dual feasibility: for each v != root, sum_i alpha_i w_i(v) >= 1
    for v in range(n):
        if v == cert.root:
            continue
        total = Fraction(0)
        for alpha, strat in zip(cert.dual_multipliers, cert.strategies):
            total += alpha * strat.weights.get(v, Fraction(0))
        if total < 1:
            return CertCheckResult(
                accepted=False,
                derived_bound=None,
                claimed_bound=cert.claimed_bound,
                sum_alpha_b="0",
                failure={
                    "stage": "dual_feasibility",
                    "vertex": v,
                    "sum_alpha_w": str(total),
                    "reason": (
                        f"sum_i alpha_i w_i({v}) = {total} < 1"
                    ),
                },
                message=(
                    f"dual feasibility fails at vertex {v}: "
                    f"weighted-sum = {total} < 1"
                ),
            )

    # Compute sum_i alpha_i b_i and the derived bound
    total_ab = Fraction(0)
    per_strategy: list[dict] = []
    for alpha, strat, (_vset, _parent, b_T) in zip(
        cert.dual_multipliers, cert.strategies, strategy_data
    ):
        contrib = alpha * b_T
        total_ab += contrib
        per_strategy.append(
            {
                "name": strat.name,
                "alpha": str(alpha),
                "b_T": str(b_T),
                "alpha_b": str(contrib),
            }
        )

    derived_bound = (total_ab.numerator // total_ab.denominator) + 1
    if total_ab.numerator < 0:
        # negative b? impossible given non-negativity, but be defensive
        derived_bound = 0

    if cert.claimed_bound < derived_bound:
        return CertCheckResult(
            accepted=False,
            derived_bound=derived_bound,
            claimed_bound=cert.claimed_bound,
            sum_alpha_b=str(total_ab),
            failure={
                "stage": "claim_too_strong",
                "reason": (
                    f"claimed_bound {cert.claimed_bound} < derived_bound "
                    f"{derived_bound} = floor({total_ab}) + 1"
                ),
            },
            message=(
                f"claim too strong: dual multipliers only certify "
                f"pi(G,r) <= {derived_bound}, not {cert.claimed_bound}"
            ),
            extra={"per_strategy": per_strategy},
        )

    return CertCheckResult(
        accepted=True,
        derived_bound=derived_bound,
        claimed_bound=cert.claimed_bound,
        sum_alpha_b=str(total_ab),
        failure=None,
        message=(
            f"accepted: pi(G, r={cert.root}) <= {derived_bound} "
            f"(<= claimed {cert.claimed_bound})"
        ),
        extra={"per_strategy": per_strategy},
    )


# --- helper for generating certificates for trees -------------------------


def make_path_certificate(n: int, root: int = 0) -> dict:
    """Generate a certificate for ``pi(P_n, r=root) <= 2**(n-1)``.

    Uses a single basic strategy on the entire path with weights
    ``w(v) = 2**(dist(v, root) - 1)`` for ``v != root`` (free weight on the
    unique neighbor of the root, halving thereafter), and dual multiplier
    ``alpha = 1``. The dual feasibility constraint
    ``alpha * w(v) >= 1`` becomes ``w(v) >= 1`` for all ``v != root``,
    which holds with equality at the leaf farthest from the root.
    """
    if n < 2:
        raise ValueError(f"path certificate requires n >= 2, got {n}")
    if not 0 <= root < n:
        raise ValueError(f"root {root} out of range")
    if root != 0 and root != n - 1:
        raise NotImplementedError(
            "make_path_certificate currently supports root at an endpoint only"
        )
    edges = [[i, i + 1] for i in range(n - 1)]
    weights = {str(root): "0"}
    # Distance is i-root for root=0, root-i for root=n-1
    far_dist = n - 1
    for v in range(n):
        if v == root:
            continue
        d = abs(v - root)
        # w(v) = 2^(far_dist - d); the leaf has weight 1 = 2^0; far end > 1
        weights[str(v)] = str(2 ** (far_dist - d))
    return {
        "graph": {"n": n, "edges": edges, "name": f"P{n}"},
        "root": root,
        "claimed_bound": 2 ** (n - 1),
        "strategies": [
            {
                "name": f"P{n} full path",
                "tree_edges": edges,
                "weights": weights,
                "basic": True,
            }
        ],
        "dual_multipliers": ["1"],
    }


def make_star_certificate(k: int, root: int = 0) -> dict:
    """Generate a certificate for ``pi(K_{1,k}, r=center) <= k+1``.

    The center is vertex 0 by convention; leaves are 1..k. Strategy: the
    full star, with weight 1 on each leaf, and dual multiplier 1. The
    weight function is trivially basic since every non-root vertex is a
    neighbour of the root (no doubling inequalities apply).
    """
    if k < 1:
        raise ValueError(f"star K_{{1,k}} requires k >= 1")
    if root != 0:
        raise NotImplementedError("make_star_certificate fixes root at 0")
    edges = [[0, i] for i in range(1, k + 1)]
    weights = {"0": "0"}
    for i in range(1, k + 1):
        weights[str(i)] = "1"
    return {
        "graph": {"n": k + 1, "edges": edges, "name": f"K_1_{k}"},
        "root": 0,
        "claimed_bound": k + 1,
        "strategies": [
            {
                "name": f"K_1_{k} full star",
                "tree_edges": edges,
                "weights": weights,
                "basic": True,
            }
        ],
        "dual_multipliers": ["1"],
    }


# --- CLI -------------------------------------------------------------------


def _cli() -> None:
    import argparse

    ap = argparse.ArgumentParser(
        description="Check a Hurlbert-style pebbling weight-function certificate."
    )
    ap.add_argument("certificate", help="path to the certificate JSON file")
    ap.add_argument("--json", action="store_true", help="emit full result JSON")
    args = ap.parse_args()

    cert, g = load_certificate_file(args.certificate)
    result = check_certificate(cert, g)
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        verdict = "ACCEPTED" if result.accepted else "REJECTED"
        print(f"{verdict}")
        print(f"graph: {cert.graph_name} (n={g.n})")
        print(f"root: {cert.root}")
        print(f"claimed bound: {result.claimed_bound}")
        print(f"derived bound: {result.derived_bound}")
        print(f"sum_i alpha_i b_i = {result.sum_alpha_b}")
        if result.failure is not None:
            print("failure:")
            for k, v in result.failure.items():
                print(f"  {k}: {v}")
        if result.message:
            print(f"message: {result.message}")


if __name__ == "__main__":
    _cli()
