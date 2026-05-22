"""Path-rigid block search for the Path-FAS hardness route.

AAL's forest-FAS reduction uses an 8-vertex tournament with a unique
forest-ordering, but the forced backedge tree has maximum degree 4. That
block cannot appear in a linear-forest ordering. This script records a
replacement candidate: an 8-vertex tournament whose unique forest-ordering
has a Hamiltonian-path backedge graph.
"""
from __future__ import annotations

import argparse
import random
from itertools import permutations
from typing import Iterable, Sequence


Matrix = list[list[int]]
Edge = tuple[int, int]


# Tournament obtained from the identity order by reversing exactly the
# unordered edges below. The unique forest-ordering is (0, 1, ..., 7).
# This is path-rigid, but vertex 0 has forced backdegree 2, so it is not
# suitable as the AAL anchor l_x once a false-state edge x-l_x is added.
PATH_RIGID_BACKEDGE_PAIRS: tuple[Edge, ...] = (
    (0, 5),
    (0, 6),
    (1, 4),
    (1, 6),
    (2, 5),
    (3, 7),
    (4, 7),
)

PATH_RIGID_TOURNAMENT: Matrix = [
    [0, 1, 1, 1, 1, 0, 0, 1],
    [0, 0, 1, 1, 0, 1, 0, 1],
    [0, 0, 0, 1, 1, 0, 1, 1],
    [0, 0, 0, 0, 1, 1, 1, 0],
    [0, 1, 0, 0, 0, 1, 1, 0],
    [1, 0, 1, 0, 0, 0, 1, 1],
    [1, 1, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 1, 1, 0, 0, 0],
]

PATH_RIGID_ORDER: tuple[int, ...] = tuple(range(8))


# Stronger replacement: the unique forest-ordering is (0, 1, ..., 8), its
# forced backedge graph is a Hamiltonian path, and the leftmost/anchor
# vertex 0 is an endpoint. Thus adding one extra false-state backedge at
# vertex 0 can still leave maximum degree at most 2.
ANCHOR_SAFE_BACKEDGE_PAIRS: tuple[Edge, ...] = (
    (0, 5),
    (1, 4),
    (1, 7),
    (2, 5),
    (2, 8),
    (3, 6),
    (3, 7),
    (4, 8),
)

ANCHOR_SAFE_PATH_RIGID_TOURNAMENT: Matrix = [
    [0, 1, 1, 1, 1, 0, 1, 1, 1],
    [0, 0, 1, 1, 0, 1, 1, 0, 1],
    [0, 0, 0, 1, 1, 0, 1, 1, 0],
    [0, 0, 0, 0, 1, 1, 0, 0, 1],
    [0, 1, 0, 0, 0, 1, 1, 1, 0],
    [1, 0, 1, 0, 0, 0, 1, 1, 1],
    [0, 0, 0, 1, 0, 0, 0, 1, 1],
    [0, 1, 0, 1, 0, 0, 0, 0, 1],
    [0, 0, 1, 0, 1, 0, 0, 0, 0],
]

ANCHOR_SAFE_ORDER: tuple[int, ...] = tuple(range(9))


AAL_FIGURE1_TOURNAMENT: Matrix = [
    [0, 1, 1, 0, 0, 0, 1, 0],
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 1, 0, 1, 1],
    [1, 0, 0, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 1, 1],
    [1, 0, 1, 0, 0, 0, 1, 1],
    [0, 1, 0, 0, 0, 0, 0, 1],
    [1, 1, 0, 0, 0, 0, 0, 0],
]


def tournament_from_identity_backedges(n: int, pairs: Iterable[Edge]) -> Matrix:
    """Build the tournament whose identity-order backedges are `pairs`."""
    back = {tuple(sorted(e)) for e in pairs}
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) in back:
                T[j][i] = 1
            else:
                T[i][j] = 1
    return T


def _find(parent: list[int], x: int) -> int:
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def backedge_summary(T: Sequence[Sequence[int]], order: Sequence[int]) -> dict:
    """Return backedge graph data for one order."""
    n = len(T)
    pos = [0] * n
    for i, v in enumerate(order):
        pos[v] = i

    arcs: list[Edge] = []
    deg = [0] * n
    for u in range(n):
        for v in range(n):
            if T[u][v] and pos[v] < pos[u]:
                arcs.append((u, v))
                deg[u] += 1
                deg[v] += 1

    parent = list(range(n))
    is_forest = True
    for u, v in arcs:
        ru = _find(parent, u)
        rv = _find(parent, v)
        if ru == rv:
            is_forest = False
            break
        parent[ru] = rv

    max_degree = max(deg) if deg else 0
    touched = {v for e in arcs for v in e}
    is_path = (
        is_forest
        and len(arcs) > 0
        and max_degree <= 2
        and len(arcs) == len(touched) - 1
        and sum(1 for v in touched if deg[v] == 1) == 2
    )
    return {
        "order": tuple(order),
        "arcs": arcs,
        "degree": deg,
        "count": len(arcs),
        "max_degree": max_degree,
        "is_forest": is_forest,
        "is_linear_forest": is_forest and max_degree <= 2,
        "is_path": is_path,
    }


def forest_order_summaries(T: Sequence[Sequence[int]]) -> list[dict]:
    """Enumerate all forest-orderings of a small tournament."""
    out: list[dict] = []
    for order in permutations(range(len(T))):
        info = backedge_summary(T, order)
        if info["is_forest"]:
            out.append(info)
    return out


def verify_path_rigid_block() -> dict:
    """Exhaustively certify the recorded path-rigid block."""
    forest_orders = forest_order_summaries(PATH_RIGID_TOURNAMENT)
    lfo_orders = [x for x in forest_orders if x["is_linear_forest"]]
    path_orders = [x for x in forest_orders if x["is_path"]]
    unique = forest_orders[0] if len(forest_orders) == 1 else None
    return {
        "n": len(PATH_RIGID_TOURNAMENT),
        "forest_order_count": len(forest_orders),
        "lfo_order_count": len(lfo_orders),
        "path_order_count": len(path_orders),
        "unique_order": unique["order"] if unique else None,
        "unique_arcs": unique["arcs"] if unique else None,
        "unique_degree": unique["degree"] if unique else None,
        "unique_max_degree": unique["max_degree"] if unique else None,
        "unique_is_path": unique["is_path"] if unique else None,
    }


def verify_anchor_safe_block() -> dict:
    """Exhaustively certify the stronger anchor-safe path-rigid block."""
    forest_orders = forest_order_summaries(ANCHOR_SAFE_PATH_RIGID_TOURNAMENT)
    lfo_orders = [x for x in forest_orders if x["is_linear_forest"]]
    path_orders = [x for x in forest_orders if x["is_path"]]
    unique = forest_orders[0] if len(forest_orders) == 1 else None
    anchor_degree = unique["degree"][0] if unique else None
    return {
        "n": len(ANCHOR_SAFE_PATH_RIGID_TOURNAMENT),
        "forest_order_count": len(forest_orders),
        "lfo_order_count": len(lfo_orders),
        "path_order_count": len(path_orders),
        "unique_order": unique["order"] if unique else None,
        "unique_arcs": unique["arcs"] if unique else None,
        "unique_degree": unique["degree"] if unique else None,
        "unique_max_degree": unique["max_degree"] if unique else None,
        "unique_is_path": unique["is_path"] if unique else None,
        "anchor_degree": anchor_degree,
        "anchor_can_accept_one_more_edge": anchor_degree is not None and anchor_degree <= 1,
    }


def aal_figure1_summary() -> dict:
    """Summarize why the original AAL Figure 1 block is not path-safe."""
    info = backedge_summary(AAL_FIGURE1_TOURNAMENT, PATH_RIGID_ORDER)
    forest_orders = forest_order_summaries(AAL_FIGURE1_TOURNAMENT)
    return {
        "identity_arcs": info["arcs"],
        "identity_degree": info["degree"],
        "identity_max_degree": info["max_degree"],
        "forest_order_count": len(forest_orders),
    }


def random_hamilton_path_pairs(n: int, rng: random.Random) -> list[Edge]:
    path = list(range(n))
    rng.shuffle(path)
    return [tuple(sorted((path[i], path[i + 1]))) for i in range(n - 1)]


def search_path_rigid_blocks(n: int, trials: int, seed: int) -> dict | None:
    """Randomly search identity-Hamiltonian-path candidates."""
    rng = random.Random(seed)
    best: tuple[int, list[Edge]] | None = None
    for trial in range(trials):
        pairs = random_hamilton_path_pairs(n, rng)
        T = tournament_from_identity_backedges(n, pairs)
        forest_count = 0
        lfo_count = 0
        for order in permutations(range(n)):
            info = backedge_summary(T, order)
            if info["is_forest"]:
                forest_count += 1
                if info["is_linear_forest"]:
                    lfo_count += 1
                if forest_count >= 2:
                    break
        if forest_count == 1:
            return {
                "trial": trial,
                "n": n,
                "backedge_pairs": sorted(pairs),
                "tournament": T,
            }
        if best is None or forest_count < best[0]:
            best = (forest_count, sorted(pairs))
    return {
        "trial": None,
        "n": n,
        "best_forest_count_before_cutoff": best[0] if best else None,
        "best_backedge_pairs": best[1] if best else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--search", action="store_true")
    parser.add_argument("--n", type=int, default=8)
    parser.add_argument("--trials", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20260522)
    args = parser.parse_args()

    if args.search:
        print(search_path_rigid_blocks(args.n, args.trials, args.seed))
        return

    print("AAL Figure 1:", aal_figure1_summary())
    print("path-rigid block:", verify_path_rigid_block())
    print("anchor-safe path-rigid block:", verify_anchor_safe_block())


if __name__ == "__main__":
    main()
