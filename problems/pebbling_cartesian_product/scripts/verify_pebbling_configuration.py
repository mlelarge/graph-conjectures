"""Exact pebbling reachability verifier (forward BFS with identity dedup).

Implements the Phase 1 deliverable from
``PEBBLING_CARTESIAN_PRODUCT_COUNTEREXAMPLE_PLAN.md``.

A configuration ``C`` is a tuple of nonnegative integers indexed by vertex.
A pebbling move at ``v`` along edge ``v-w`` removes 2 pebbles from ``v``
and adds 1 to ``w`` (requires ``C[v] >= 2``). The configuration is
``r``-solvable iff a finite sequence of moves leads to a state with at
least one pebble on the root ``r``.

The verifier exposes four outcomes:

- ``solvable``: a state with ``C'[r] >= target_pebbles`` is reachable; an
  explicit move sequence is returned.
- ``unsolvable``: the forward search exhausted the entire reachable set
  without ever placing the required number of pebbles on ``r``.
- ``inconclusive_within_budget``: the configured time/state limit was hit
  before either condition fired.
- ``invalid_input``: graph, root, or configuration validation failed.

## Search architecture

The search is plain forward BFS with **identity-based deduplication**: each
distinct configuration is enumerated at most once. There is currently no
dominance pruning beyond identity. The full coordinatewise-dominance prune
("if any explored state ``s`` satisfies ``s >= v`` elementwise then prune
``v``") is sound by the monotonicity argument below, but its naive
implementation is ``O(|seen|^2 * n)`` per call, which makes the small
acceptance tests dramatically slower without changing their answers. It
is left as a documented future optimization.

Soundness for ``unsolvable`` rests on the monotonicity of pebbling moves:
if ``C <= C'`` componentwise, every move legal from ``C`` is legal from
``C'`` and yields a coordinatewise-larger result. So enumerating every
reachable state from ``C`` and finding none on the root is a complete
unsolvability proof regardless of whether dominance pruning is used.

## Distance-weight pre-filter

A weight-based pre-filter additionally certifies unsolvability whenever
the distance weight ``W(C, r) = sum_v C[v] / 2^{dist(v, r)}`` is strictly
less than ``target_pebbles``. Distance weight is non-increasing under
pebbling moves (triangle inequality), so ``W(C, r) < target`` immediately
rules out delivering ``target`` pebbles to ``r``. This pre-filter is
exact (uses ``Fraction``) and emits ``explored_states = 0`` to make it
clear no BFS was run.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections import deque
from dataclasses import asdict, dataclass, field
from fractions import Fraction
from pathlib import Path

from pebbling_graphs import Graph, bfs_distances


VERIFIER_VERSION = "verify_pebbling_configuration/v1"


@dataclass
class ResourceLimits:
    """Hard resource ceilings for a single verification call."""

    max_states: int = 5_000_000
    max_seconds: float = 600.0
    max_total_pebbles: int = 10_000


@dataclass
class VerifierResult:
    """Structured outcome of a single verification call."""

    outcome: str
    graph_name: str
    n: int
    root: int
    configuration: tuple[int, ...]
    initial_size: int
    explored_states: int
    elapsed_seconds: float
    state_set_hash: str
    verifier_version: str
    resource_limits: dict
    move_sequence: list[tuple[int, int]] | None = None
    weight_pre_filter: dict | None = None
    message: str = ""
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["configuration"] = list(self.configuration)
        return d


# --- input validation ------------------------------------------------------


def _validate_inputs(g: Graph, root: int, configuration) -> tuple[tuple[int, ...], str | None]:
    if not 0 <= root < g.n:
        return tuple(), f"root {root} out of range [0, {g.n})"
    if len(configuration) != g.n:
        return tuple(), (
            f"configuration length {len(configuration)} != n={g.n}"
        )
    cfg: list[int] = []
    for i, x in enumerate(configuration):
        try:
            v = int(x)
        except (TypeError, ValueError):
            return tuple(), f"configuration[{i}]={x!r} is not an integer"
        if v < 0:
            return tuple(), f"configuration[{i}]={v} is negative"
        cfg.append(v)
    return tuple(cfg), None


# --- weight pre-filter -----------------------------------------------------


def distance_weight(g: Graph, root: int, configuration) -> Fraction:
    """``sum_v C[v] / 2**dist(v, r)`` as an exact ``Fraction``.

    Rests on a graph being connected; otherwise ``bfs_distances`` returns
    ``-1`` for unreachable vertices and we treat their weight as zero (the
    initial configuration on an isolated component cannot reach ``r``
    anyway, but we exit gracefully rather than crash).
    """
    dist = bfs_distances(g, root)
    total = Fraction(0)
    for v, c in enumerate(configuration):
        if c == 0:
            continue
        d = dist[v]
        if d < 0:
            continue
        total += Fraction(c, 1 << d)
    return total


# --- core search -----------------------------------------------------------


def _state_set_hash(states: list[tuple[int, ...]]) -> str:
    """Deterministic hash of the explored state set, for reproducibility."""
    h = hashlib.sha256()
    for s in sorted(states):
        h.update(repr(s).encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def _reconstruct_path(
    parents: dict[tuple[int, ...], tuple[tuple[int, ...], int, int] | None],
    end: tuple[int, ...],
) -> list[tuple[int, int]]:
    moves: list[tuple[int, int]] = []
    cur: tuple[int, ...] | None = end
    while cur is not None:
        info = parents[cur]
        if info is None:
            break
        prev, src, dst = info
        moves.append((src, dst))
        cur = prev
    moves.reverse()
    return moves


def verify_configuration(
    g: Graph,
    root: int,
    configuration,
    *,
    target_pebbles: int = 1,
    limits: ResourceLimits | None = None,
) -> VerifierResult:
    """Decide whether ``target_pebbles`` pebbles can be moved to ``root``.

    The default ``target_pebbles=1`` corresponds to standard pebbling
    (`r`-solvability). Setting ``target_pebbles=2`` answers the question
    underlying the 2-pebbling property: can two pebbles be placed on the
    root? Setting it to a larger ``t`` tests ``t``-pebbling.

    Returns a structured result with one of four outcomes
    (``solvable``, ``unsolvable``, ``inconclusive_within_budget``,
    ``invalid_input``).
    """
    if target_pebbles < 1:
        raise ValueError(f"target_pebbles must be >= 1, got {target_pebbles}")
    limits = limits or ResourceLimits()
    cfg, err = _validate_inputs(g, root, configuration)
    if err:
        try:
            invalid_size = int(sum(int(x) for x in configuration)) if configuration else 0
        except (TypeError, ValueError):
            invalid_size = 0
        return VerifierResult(
            outcome="invalid_input",
            graph_name=g.name,
            n=g.n,
            root=root,
            configuration=tuple(configuration),
            initial_size=invalid_size,
            explored_states=0,
            elapsed_seconds=0.0,
            state_set_hash="",
            verifier_version=VERIFIER_VERSION,
            resource_limits=asdict(limits),
            message=err,
        )

    initial_size = sum(cfg)
    if initial_size > limits.max_total_pebbles:
        return VerifierResult(
            outcome="invalid_input",
            graph_name=g.name,
            n=g.n,
            root=root,
            configuration=cfg,
            initial_size=initial_size,
            explored_states=0,
            elapsed_seconds=0.0,
            state_set_hash="",
            verifier_version=VERIFIER_VERSION,
            resource_limits=asdict(limits),
            message=(
                f"initial size {initial_size} exceeds max_total_pebbles "
                f"{limits.max_total_pebbles}"
            ),
        )

    # If the root already has the target number of pebbles, solvable in 0 moves.
    if cfg[root] >= target_pebbles:
        return VerifierResult(
            outcome="solvable",
            graph_name=g.name,
            n=g.n,
            root=root,
            configuration=cfg,
            initial_size=initial_size,
            explored_states=1,
            elapsed_seconds=0.0,
            state_set_hash=_state_set_hash([cfg]),
            verifier_version=VERIFIER_VERSION,
            resource_limits=asdict(limits),
            move_sequence=[],
            weight_pre_filter={"weight": str(distance_weight(g, root, cfg))},
            message="root already pebbled",
        )

    weight = distance_weight(g, root, cfg)
    pre_filter = {
        "weight": str(weight),
        "weight_numerator": weight.numerator,
        "weight_denominator": weight.denominator,
        "target_pebbles": target_pebbles,
        "rules_out_solvability": weight < target_pebbles,
    }

    if weight < target_pebbles:
        return VerifierResult(
            outcome="unsolvable",
            graph_name=g.name,
            n=g.n,
            root=root,
            configuration=cfg,
            initial_size=initial_size,
            explored_states=0,
            elapsed_seconds=0.0,
            state_set_hash="",
            verifier_version=VERIFIER_VERSION,
            resource_limits=asdict(limits),
            weight_pre_filter=pre_filter,
            message=(
                "unsolvable by distance-weight certificate: "
                f"sum_v C[v]/2^{{dist(v,r)}} = {weight} < target {target_pebbles}"
            ),
        )

    adj = g.adjacency()
    start = time.monotonic()

    # Forward BFS with identity-based deduplication (each distinct
    # configuration is visited at most once). Dominance pruning is a
    # sound but expensive future optimization; see module docstring.
    seen: set[tuple[int, ...]] = {cfg}
    parents: dict[tuple[int, ...], tuple[tuple[int, ...], int, int] | None] = {cfg: None}
    queue: deque[tuple[int, ...]] = deque([cfg])
    explored = 0
    found: tuple[int, ...] | None = None

    while queue:
        state = queue.popleft()
        explored += 1

        if explored % 4096 == 0:
            if time.monotonic() - start > limits.max_seconds:
                return VerifierResult(
                    outcome="inconclusive_within_budget",
                    graph_name=g.name,
                    n=g.n,
                    root=root,
                    configuration=cfg,
                    initial_size=initial_size,
                    explored_states=explored,
                    elapsed_seconds=time.monotonic() - start,
                    state_set_hash=_state_set_hash(list(seen)),
                    verifier_version=VERIFIER_VERSION,
                    resource_limits=asdict(limits),
                    weight_pre_filter=pre_filter,
                    message=f"exceeded max_seconds={limits.max_seconds}",
                )

        if len(seen) > limits.max_states:
            return VerifierResult(
                outcome="inconclusive_within_budget",
                graph_name=g.name,
                n=g.n,
                root=root,
                configuration=cfg,
                initial_size=initial_size,
                explored_states=explored,
                elapsed_seconds=time.monotonic() - start,
                state_set_hash=_state_set_hash(list(seen)),
                verifier_version=VERIFIER_VERSION,
                resource_limits=asdict(limits),
                weight_pre_filter=pre_filter,
                message=f"exceeded max_states={limits.max_states}",
            )

        # Generate successors by every legal move.
        for src in range(g.n):
            if state[src] < 2:
                continue
            for dst in adj[src]:
                # Apply move src -> dst.
                lst = list(state)
                lst[src] -= 2
                lst[dst] += 1
                succ = tuple(lst)
                if succ in seen:
                    continue
                seen.add(succ)
                parents[succ] = (state, src, dst)
                if succ[root] >= target_pebbles:
                    found = succ
                    queue.clear()
                    break
                queue.append(succ)
            if found is not None:
                break
        if found is not None:
            break

    elapsed = time.monotonic() - start

    if found is not None:
        return VerifierResult(
            outcome="solvable",
            graph_name=g.name,
            n=g.n,
            root=root,
            configuration=cfg,
            initial_size=initial_size,
            explored_states=explored,
            elapsed_seconds=elapsed,
            state_set_hash=_state_set_hash(list(seen)),
            verifier_version=VERIFIER_VERSION,
            resource_limits=asdict(limits),
            move_sequence=_reconstruct_path(parents, found),
            weight_pre_filter=pre_filter,
            message="reachable via forward BFS",
        )

    return VerifierResult(
        outcome="unsolvable",
        graph_name=g.name,
        n=g.n,
        root=root,
        configuration=cfg,
        initial_size=initial_size,
        explored_states=explored,
        elapsed_seconds=elapsed,
        state_set_hash=_state_set_hash(list(seen)),
        verifier_version=VERIFIER_VERSION,
        resource_limits=asdict(limits),
        weight_pre_filter=pre_filter,
        message="exhausted reachable state set without placing a pebble on root",
    )


# --- pebbling-number computation ------------------------------------------


@dataclass
class SizeSweepResult:
    """Outcome of brute-force sweeping every ``size``-pebble configuration.

    - ``status == "all_solvable"``: every weak composition was solvable;
      ``witness`` is empty.
    - ``status == "unsolvable_witness"``: ``witness`` is an unsolvable
      configuration of size ``size``.
    - ``status == "inconclusive"``: the verifier returned
      ``inconclusive_within_budget`` on at least one configuration;
      ``witness`` is the first such configuration. The caller cannot
      decide solvability of the full size from this result.
    """

    status: str
    witness: list[int]


def is_r_solvable_for_size(
    g: Graph,
    root: int,
    size: int,
    *,
    limits: ResourceLimits | None = None,
) -> SizeSweepResult:
    """Brute-force check that EVERY ``size``-pebble configuration is ``r``-solvable.

    Iterates over all weak compositions of ``size`` into ``g.n`` parts.
    Use only for small graphs and small sizes; the count of compositions
    is ``C(size + n - 1, n - 1)``.

    Returns a tri-state :class:`SizeSweepResult`. In particular the result
    distinguishes "found unsolvable witness" from "verifier ran out of
    budget"; the caller must not collapse the two.
    """
    n = g.n
    state: dict = {"unsolvable": None, "inconclusive": None}

    def gen(rem: int, idx: int, current: list[int]) -> bool:
        if state["unsolvable"] is not None:
            return True
        if idx == n - 1:
            current.append(rem)
            cfg = tuple(current)
            res = verify_configuration(g, root, cfg, limits=limits)
            current.pop()
            if res.outcome == "unsolvable":
                state["unsolvable"] = list(cfg)
                return True
            if res.outcome == "inconclusive_within_budget":
                if state["inconclusive"] is None:
                    state["inconclusive"] = list(cfg)
                return False
            if res.outcome == "invalid_input":
                raise RuntimeError(
                    f"verifier rejected internal configuration {list(cfg)}: "
                    f"{res.message}"
                )
            # outcome == "solvable" -> continue
            return False
        for k in range(rem + 1):
            current.append(k)
            stop = gen(rem - k, idx + 1, current)
            current.pop()
            if stop:
                return True
        return False

    gen(size, 0, [])
    if state["unsolvable"] is not None:
        return SizeSweepResult(status="unsolvable_witness", witness=state["unsolvable"])
    if state["inconclusive"] is not None:
        return SizeSweepResult(status="inconclusive", witness=state["inconclusive"])
    return SizeSweepResult(status="all_solvable", witness=[])


class PebblingNumberInconclusive(RuntimeError):
    """Raised when ``pebbling_number`` cannot decide a size due to verifier budget."""

    def __init__(self, size: int, root: int, witness: list[int], message: str = ""):
        super().__init__(
            message
            or (
                f"verifier returned inconclusive_within_budget at size={size}, "
                f"root={root}, configuration={witness}; raise resource limits "
                "or refuse to claim a pebbling number"
            )
        )
        self.size = size
        self.root = root
        self.witness = witness


def pebbling_number(
    g: Graph,
    *,
    lower: int | None = None,
    upper: int | None = None,
    limits: ResourceLimits | None = None,
    verbose: bool = False,
) -> int:
    """Compute ``pi(G)`` by brute-force enumeration.

    Increments ``s`` from ``max(lower, |V|)`` until every weak composition
    of ``s`` into ``|V|`` parts is ``r``-solvable for every root ``r``,
    and returns that ``s``. Use only for small graphs (``|V|`` up to ~8
    and ``s`` modest).

    Raises :class:`PebblingNumberInconclusive` if the verifier hits its
    resource budget on any configuration. The function never collapses
    inconclusive into "unsolvable witness" — that would silently inflate
    the reported pebbling number.
    """
    n = g.n
    s = max(lower or 0, n)
    cap = upper if upper is not None else max(2 * n, 32)
    while s <= cap:
        any_unsolvable = False
        for r in range(n):
            res = is_r_solvable_for_size(g, r, s, limits=limits)
            if res.status == "inconclusive":
                raise PebblingNumberInconclusive(
                    size=s, root=r, witness=res.witness
                )
            if res.status == "unsolvable_witness":
                any_unsolvable = True
                if verbose:
                    print(
                        f"  size {s}, root {r}: unsolvable witness "
                        f"{res.witness}; bumping s"
                    )
                break
        if not any_unsolvable:
            if verbose:
                print(f"  size {s}: every (root, config) is solvable -> pi(G) = {s}")
            return s
        s += 1
    raise RuntimeError(
        f"pebbling_number: did not converge by upper={cap}; raise the cap"
    )


# --- CLI -------------------------------------------------------------------


def _load_graph_arg(arg: str) -> Graph:
    """Resolve ``arg`` to a Graph: either a name in ``data/pebbling_product/graphs``
    or a JSON file path."""
    from pebbling_graphs import load_named_graph, GRAPH_DIR

    p = Path(arg)
    if p.exists() and p.suffix == ".json":
        with p.open() as fp:
            payload = json.load(fp)
        from pebbling_graphs import make_graph

        return make_graph(int(payload["n"]), payload["edges"], name=payload.get("name", p.stem))
    # else look in graph dir
    return load_named_graph(arg)


def _cli() -> None:
    import argparse

    ap = argparse.ArgumentParser(description="Verify a pebbling configuration.")
    ap.add_argument("graph", help="graph name (in data/pebbling_product/graphs) or JSON path")
    ap.add_argument("--root", type=int, required=True)
    ap.add_argument("--config", type=str, required=True, help="comma-separated configuration")
    ap.add_argument(
        "--target-pebbles",
        type=int,
        default=1,
        help="number of pebbles required on the root for solvability "
        "(default 1; set 2 to test the 2-pebbling property)",
    )
    ap.add_argument("--max-states", type=int, default=5_000_000)
    ap.add_argument("--max-seconds", type=float, default=600.0)
    ap.add_argument("--json", action="store_true", help="print full result JSON")
    args = ap.parse_args()

    g = _load_graph_arg(args.graph)
    cfg = [int(x) for x in args.config.split(",")]
    limits = ResourceLimits(max_states=args.max_states, max_seconds=args.max_seconds)
    result = verify_configuration(
        g, args.root, cfg, target_pebbles=args.target_pebbles, limits=limits
    )
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"outcome: {result.outcome}")
        print(f"graph: {result.graph_name} (n={result.n})")
        print(f"root: {result.root}")
        print(f"target pebbles: {args.target_pebbles}")
        print(f"configuration: {list(result.configuration)}")
        print(f"initial size: {result.initial_size}")
        if result.weight_pre_filter:
            print(
                "distance weight: "
                f"{result.weight_pre_filter['weight']} "
                f"(rules_out_solvability="
                f"{result.weight_pre_filter['rules_out_solvability']})"
            )
        print(f"explored states: {result.explored_states}")
        print(f"elapsed: {result.elapsed_seconds:.3f}s")
        if result.outcome == "solvable" and result.move_sequence is not None:
            print(f"move sequence ({len(result.move_sequence)} moves):")
            for src, dst in result.move_sequence:
                print(f"  {src} -> {dst}")
        if result.message:
            print(f"message: {result.message}")


if __name__ == "__main__":
    _cli()
