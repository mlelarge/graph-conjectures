"""Low-hit sigma-trace quotient probe for the J-pathwidth DP.

The D68 synthesis identifies the bag ordering sigma as the bottleneck:
the exact J-DP state is (sigma, degree, component partition), and the
factor |bag|! dominates the partition term.

This module tests the next candidate compression.  For a bag state and
a not-yet-introduced vertex x, inserting x at a cut of sigma only
matters if it would load at most two backedges: degree-2 makes all
larger-hit cuts immediately invalid.  The *low-hit trace* records, for
each future x, the low-hit insertion events but not the full bag
permutation.

Two variants are implemented.

* mode="sets": for each future x, record the set of feasible hit-sets
  {u} or {u,v} that can be loaded by some insertion cut.  Cut positions
  and the order of non-hit vertices are forgotten.
* mode="ordered": same, but the hit endpoints retain their sigma order.

For a quotient to be sound, every two full DP states at the same layer
with the same quotient must have the same winning status, where
"winning" is computed by an exact backward pass through the full J-DP
state graph.  A mixed winning/losing quotient class is a real
extension-equivalence collision.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Dict, Iterable, Sequence, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from J_pathwidth_dp import (  # noqa: E402
    J_graph,
    is_backedge_in_LFO,
    nice_path_decomposition,
    path_fas_state_signature,
)
from lfo_score_window import score_windows  # noqa: E402

Matrix = Sequence[Sequence[int]]


State = Tuple[Tuple[int, ...], Dict[int, int], Dict[int, int]]


@dataclass(frozen=True)
class LayerStats:
    layer: int
    bag_size: int
    full_states: int
    quotient_classes: int
    winning_states: int
    mixed_classes: int


def _must_precede(windows: Sequence[Tuple[int, int]], u: int, v: int) -> bool:
    return windows[u][1] < windows[v][0]


def _allowed_positions(
    sigma: Tuple[int, ...],
    v: int,
    windows: Sequence[Tuple[int, int]],
) -> list[int]:
    positions: list[int] = []
    for i in range(len(sigma) + 1):
        ok = True
        for j, u in enumerate(sigma):
            u_before_v = j < i
            if _must_precede(windows, v, u) and u_before_v:
                ok = False
                break
            if _must_precede(windows, u, v) and not u_before_v:
                ok = False
                break
        if ok:
            positions.append(i)
    return positions


def enumerate_full_dp_layers(
    T: Matrix,
    radius: int = 2,
) -> tuple[list[frozenset], list[dict[tuple, State]], list[dict[tuple, set[tuple]]], list[frozenset]]:
    """Enumerate the exact J-DP layers and transition graph.

    Returns (decomposition, layers, transitions, introduced_by_layer).
    `transitions[i][state_key]` is the set of successor keys at layer i+1.
    """
    n = len(T)
    windows = score_windows(T, radius)
    J, _, _, _ = J_graph(T, radius)
    decomposition, _ = nice_path_decomposition(J)
    if len(decomposition[0]) != 0:
        raise AssertionError("decomposition must start empty")

    initial_key = path_fas_state_signature((), (), {}, {})
    layers: list[dict[tuple, State]] = [{initial_key: ((), {}, {})}]
    transitions: list[dict[tuple, set[tuple]]] = []
    introduced_by_layer: list[frozenset] = [frozenset()]
    cur_bag = decomposition[0]
    introduced = set()

    for nxt_bag in decomposition[1:]:
        bag_states = layers[-1]
        new_states: dict[tuple, State] = {}
        edge_map: dict[tuple, set[tuple]] = defaultdict(set)
        diff_intro = nxt_bag - cur_bag
        diff_forget = cur_bag - nxt_bag
        if diff_intro and diff_forget:
            raise ValueError("transition is not nice")

        if diff_intro:
            v = next(iter(diff_intro))
            introduced.add(v)
            for key, (sigma, degree, comp) in bag_states.items():
                for pos in _allowed_positions(sigma, v, windows):
                    new_sigma = sigma[:pos] + (v,) + sigma[pos:]
                    new_degree = dict(degree)
                    new_degree[v] = 0
                    new_comp = dict(comp)
                    new_comp[v] = v

                    parent_local: dict[int, int] = {x: new_comp[x] for x in new_sigma}
                    for x in new_sigma:
                        r = new_comp[x]
                        parent_local.setdefault(r, r)

                    def find_local(x: int, _p=parent_local) -> int:
                        while _p[x] != x:
                            _p[x] = _p[_p[x]]
                            x = _p[x]
                        return x

                    def union_local(a: int, b: int, _p=parent_local) -> None:
                        ra = find_local(a)
                        rb = find_local(b)
                        if ra != rb:
                            _p[rb] = ra

                    feasible = True
                    sigma_pos = {x: i for i, x in enumerate(new_sigma)}
                    for u in sigma:
                        if not J.has_edge(v, u):
                            continue
                        if not is_backedge_in_LFO(T, v, u, sigma_pos):
                            continue
                        if new_degree[v] >= 2 or new_degree[u] >= 2:
                            feasible = False
                            break
                        if find_local(v) == find_local(u):
                            feasible = False
                            break
                        new_degree[v] += 1
                        new_degree[u] += 1
                        union_local(v, u)
                    if not feasible:
                        continue
                    final_comp = {x: find_local(x) for x in new_sigma}
                    sig_key = path_fas_state_signature(
                        new_sigma, new_sigma, new_degree, final_comp
                    )
                    if sig_key not in new_states:
                        new_states[sig_key] = (new_sigma, dict(new_degree), dict(final_comp))
                    edge_map[key].add(sig_key)

        elif diff_forget:
            v = next(iter(diff_forget))
            for key, (sigma, degree, comp) in bag_states.items():
                new_sigma = tuple(x for x in sigma if x != v)
                new_degree = {x: degree[x] for x in new_sigma}
                new_comp = {x: comp[x] for x in new_sigma}
                sig_key = path_fas_state_signature(
                    new_sigma, new_sigma, new_degree, new_comp
                )
                if sig_key not in new_states:
                    new_states[sig_key] = (new_sigma, new_degree, new_comp)
                edge_map[key].add(sig_key)
        else:
            new_states = dict(bag_states)
            for key in bag_states:
                edge_map[key].add(key)

        transitions.append(dict(edge_map))
        layers.append(new_states)
        cur_bag = nxt_bag
        introduced_by_layer.append(frozenset(introduced))
        if not new_states:
            # Keep the remaining decomposition shape irrelevant; the DP is dead.
            break

    return decomposition[: len(layers)], layers, transitions, introduced_by_layer


def winning_state_sets(
    layers: list[dict[tuple, State]],
    transitions: list[dict[tuple, set[tuple]]],
) -> list[set[tuple]]:
    """Backward winning-state pass through the exact state graph."""
    if not layers:
        return []
    wins: list[set[tuple]] = [set() for _ in layers]
    wins[-1] = set(layers[-1].keys())
    for i in range(len(layers) - 2, -1, -1):
        nxt_win = wins[i + 1]
        cur_win: set[tuple] = set()
        for key, succs in transitions[i].items():
            if any(s in nxt_win for s in succs):
                cur_win.add(key)
        wins[i] = cur_win
    return wins


def _bag_partition_signature(sigma: Tuple[int, ...], comp: Dict[int, int]) -> tuple:
    """Component partition of bag vertices, encoded in sorted-bag order."""
    bag = tuple(sorted(sigma))
    class_id: dict[int, int] = {}
    out: list[int] = []
    nxt = 0
    for v in bag:
        r = comp[v]
        if r not in class_id:
            class_id[r] = nxt
            nxt += 1
        out.append(class_id[r])
    return tuple(out)


def low_hit_trace_signature(
    T: Matrix,
    state: State,
    introduced: frozenset[int],
    mode: str = "sets",
    radius: int = 2,
) -> tuple:
    """Return the low-hit sigma quotient for a full DP state.

    The base records bag set, degrees, and bag component partition.  The
    trace records feasible low-hit insertion events for every vertex not
    yet introduced by the fixed path decomposition.
    """
    if mode not in {"sets", "ordered", "cuts"}:
        raise ValueError("mode must be one of: sets, ordered, cuts")
    sigma, degree, comp = state
    bag = tuple(sorted(sigma))
    windows = score_windows(T, radius)
    J, _, _, _ = J_graph(T, radius)
    n = len(T)

    base_degree = tuple((v, degree[v]) for v in bag)
    base_partition = _bag_partition_signature(sigma, comp)

    future_records: list[tuple] = []
    future_vertices = [v for v in range(n) if v not in introduced]
    for x in future_vertices:
        events: set[tuple] = set()
        for pos in _allowed_positions(sigma, x, windows):
            new_sigma = sigma[:pos] + (x,) + sigma[pos:]
            sigma_pos = {v: i for i, v in enumerate(new_sigma)}
            hit = []
            for u in sigma:
                if J.has_edge(x, u) and is_backedge_in_LFO(T, x, u, sigma_pos):
                    hit.append(u)
            if len(hit) > 2:
                continue
            if any(degree[u] >= 2 for u in hit):
                continue
            if len(hit) == 2 and comp[hit[0]] == comp[hit[1]]:
                continue
            if mode == "sets":
                event = tuple(sorted(hit))
            elif mode == "ordered":
                event = tuple(hit)
            else:
                left = sigma[pos - 1] if pos > 0 else None
                right = sigma[pos] if pos < len(sigma) else None
                event = (left, right, tuple(hit))
            events.add(event)
        future_records.append((x, tuple(sorted(events, key=repr))))

    return (bag, base_degree, base_partition, tuple(future_records))


def quotient_collision_report(
    T: Matrix,
    mode: str = "sets",
    radius: int = 2,
) -> dict:
    """Search for a mixed winning/losing low-hit quotient class."""
    decomposition, layers, transitions, introduced_by_layer = enumerate_full_dp_layers(T, radius)
    wins = winning_state_sets(layers, transitions)
    layer_stats: list[LayerStats] = []
    first_collision: dict | None = None

    for i, states in enumerate(layers):
        buckets: dict[tuple, list[tuple]] = defaultdict(list)
        for key, state in states.items():
            sig = low_hit_trace_signature(
                T, state, introduced_by_layer[i], mode=mode, radius=radius
            )
            buckets[sig].append(key)

        mixed = []
        for sig, keys in buckets.items():
            verdicts = {k in wins[i] for k in keys}
            if len(verdicts) > 1:
                mixed.append((sig, keys))

        layer_stats.append(
            LayerStats(
                layer=i,
                bag_size=len(decomposition[i]),
                full_states=len(states),
                quotient_classes=len(buckets),
                winning_states=len(wins[i]),
                mixed_classes=len(mixed),
            )
        )

        if mixed and first_collision is None:
            sig, keys = mixed[0]
            win_key = next(k for k in keys if k in wins[i])
            lose_key = next(k for k in keys if k not in wins[i])
            first_collision = {
                "layer": i,
                "bag": sorted(decomposition[i]),
                "mode": mode,
                "class_size": len(keys),
                "winning_state": _state_summary(layers[i][win_key]),
                "losing_state": _state_summary(layers[i][lose_key]),
            }

    return {
        "mode": mode,
        "n": len(T),
        "accepted": bool(wins and next(iter(layers[0])) in wins[0]),
        "layers": [asdict(s) for s in layer_stats],
        "has_collision": first_collision is not None,
        "first_collision": first_collision,
        "max_full_states": max((s.full_states for s in layer_stats), default=0),
        "max_quotient_classes": max((s.quotient_classes for s in layer_stats), default=0),
    }


def _state_summary(state: State) -> dict:
    sigma, degree, comp = state
    return {
        "sigma": sigma,
        "degree": tuple((v, degree[v]) for v in sigma),
        "partition": _bag_partition_signature(sigma, comp),
    }


def random_tournament(n: int, rng: random.Random) -> list[list[int]]:
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.getrandbits(1):
                T[i][j] = 1
            else:
                T[j][i] = 1
    return T


def random_probe(n: int, count: int, mode: str, seed: int = 20260527) -> dict:
    rng = random.Random(seed)
    checked = 0
    collisions = []
    for idx in range(count):
        T = random_tournament(n, rng)
        rep = quotient_collision_report(T, mode=mode)
        checked += 1
        if rep["has_collision"]:
            collisions.append({"idx": idx, "collision": rep["first_collision"]})
            break
    return {"n": n, "mode": mode, "checked": checked, "collisions": collisions}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--T", help="Tournament as JSON matrix")
    parser.add_argument("--mode", choices=["sets", "ordered", "cuts"], default="sets")
    parser.add_argument("--random", type=int, help="Run this many random tournaments.")
    parser.add_argument("--n", type=int, default=7)
    args = parser.parse_args()

    if args.T:
        print(json.dumps(quotient_collision_report(json.loads(args.T), args.mode), indent=2))
    elif args.random is not None:
        print(json.dumps(random_probe(args.n, args.random, args.mode), indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
