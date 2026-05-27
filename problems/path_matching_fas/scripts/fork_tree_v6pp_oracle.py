"""Polynomial separation oracle for V6''-positive fork-tree cores.

The negative-Horn representation has one clause for each minimal fatal
support.  Listing those clauses is unnecessary for deciding a given
toggle assignment eps: by monotonicity, eps is fatal iff it contains a
V6''-positive cyclic-ladder core.  This module detects such a contained
core by searching for alternating cycles in the image graph.

Image graph model
=================

For a fork-tree pairing pi, each even toggle block E_p={2p,2p+1}
induces a fixed matching edge between the two B-images
{pi(2p), pi(2p+1)}.  The B-chain contributes path edges {a,a+1}.

A cyclic-ladder core is exactly an alternating cycle between:

  * block-matching edges from fully selected toggle blocks; and
  * B-chain path edges used as image intervals.

The directed transition graph encodes one path edge followed by one
block-matching edge:

    w --path-- v --block-mate-- beta(v).

Directed cycles in this transition graph are alternating ladder cores.
The V6'' triggers then become ordinary graph restrictions:

  * P3: an alternating cycle avoiding the maximum image k-1;
  * P4: an alternating cycle of length at least 2 using only natural
    odd-start path edges {1,2}, {3,4}, ...;
  * P3' on size-2 cores is covered by direct V6'' testing of each
    single block.  For multi-interval natural cycles, P4 already fires.

This is a separation oracle, not a clause enumerator: it returns one
contained V6''-positive core if one exists.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rectangle_detachability_probe import even_adjacent_blocks  # noqa: E402
from v6pp_completion_constructor import is_cyclic_ladder_core  # noqa: E402
from v6pp_predictor import predict_v6pp  # noqa: E402


@dataclass(frozen=True)
class ImageData:
    image_to_index: dict[int, int]
    image_to_block: dict[int, int]
    image_to_mate: dict[int, int]
    block_images: list[tuple[int, int]]


@dataclass(frozen=True)
class Arc:
    src: int
    via_path_neighbor: int
    dst: int
    path_start: int


def _validate(k: int, pi: Sequence[int], eps: Sequence[int] | None = None) -> None:
    if len(pi) != k or sorted(pi) != list(range(k)):
        raise ValueError("pi must be a permutation of range(k)")
    if eps is not None and len(eps) != k:
        raise ValueError("eps must have length k")


def image_data(k: int, pi: Sequence[int]) -> ImageData:
    """Return image ownership and block-mate maps."""
    _validate(k, pi)
    image_to_index = {pi[i]: i for i in range(k)}
    image_to_block: dict[int, int] = {}
    image_to_mate: dict[int, int] = {}
    block_images: list[tuple[int, int]] = []
    for block_id, (a, b) in enumerate(even_adjacent_blocks(k)):
        x, y = pi[a], pi[b]
        block_images.append((x, y))
        image_to_block[x] = block_id
        image_to_block[y] = block_id
        image_to_mate[x] = y
        image_to_mate[y] = x
    return ImageData(
        image_to_index=image_to_index,
        image_to_block=image_to_block,
        image_to_mate=image_to_mate,
        block_images=block_images,
    )


def fully_selected_blocks(k: int, eps: Sequence[int]) -> set[int]:
    """Even-block ids p such that both toggle indices of E_p are 1."""
    blocks = even_adjacent_blocks(k)
    return {
        block_id
        for block_id, (a, b) in enumerate(blocks)
        if int(eps[a]) == 1 and int(eps[b]) == 1
    }


def support_from_images(
    k: int,
    pi: Sequence[int],
    images: Sequence[int],
) -> tuple[int, ...]:
    data = image_data(k, pi)
    return tuple(sorted(data.image_to_index[x] for x in set(images)))


def _allowed_images(
    data: ImageData,
    active_blocks: set[int],
    excluded_image: int | None = None,
) -> set[int]:
    active = set()
    for block_id in active_blocks:
        active.update(data.block_images[block_id])
    if excluded_image is not None and excluded_image in data.image_to_block:
        bad_block = data.image_to_block[excluded_image]
        active.difference_update(data.block_images[bad_block])
    return active


def _transition_arcs(
    k: int,
    data: ImageData,
    active_blocks: set[int],
    path_edge_allowed: Callable[[int], bool],
    excluded_image: int | None = None,
) -> dict[int, list[Arc]]:
    """Build w -> beta(v) arcs for allowed path edges {w,v}.

    `path_edge_allowed(a)` receives the lower endpoint a of a path edge
    {a,a+1}.  For P3 it is always true.  For P4 it is `a odd`.
    """
    allowed = _allowed_images(data, active_blocks, excluded_image)
    arcs = {x: [] for x in allowed}
    for src in sorted(allowed):
        for neighbor in (src - 1, src + 1):
            if neighbor not in allowed:
                continue
            path_start = min(src, neighbor)
            if not (0 <= path_start <= k - 2):
                continue
            if not path_edge_allowed(path_start):
                continue
            dst = data.image_to_mate.get(neighbor)
            if dst in allowed:
                arcs[src].append(Arc(src, neighbor, dst, path_start))
    return arcs


def _find_directed_cycle(arcs: dict[int, list[Arc]], min_len: int) -> list[Arc] | None:
    """Return one directed cycle as arcs, or None."""
    color = {v: 0 for v in arcs}
    stack_vertices: list[int] = []
    stack_arcs: list[Arc] = []
    position: dict[int, int] = {}

    def dfs(u: int) -> list[Arc] | None:
        color[u] = 1
        position[u] = len(stack_vertices)
        stack_vertices.append(u)
        for arc in arcs[u]:
            v = arc.dst
            if v == u:
                if min_len <= 1:
                    return [arc]
                continue
            if color.get(v, 0) == 0:
                stack_arcs.append(arc)
                found = dfs(v)
                if found is not None:
                    return found
                stack_arcs.pop()
            elif color[v] == 1:
                start = position[v]
                cycle_arcs = stack_arcs[start:] + [arc]
                if len(cycle_arcs) >= min_len:
                    return cycle_arcs
        stack_vertices.pop()
        position.pop(u, None)
        color[u] = 2
        return None

    for v in sorted(arcs):
        if color[v] == 0:
            found = dfs(v)
            if found is not None:
                return found
    return None


def _cycle_support(
    k: int,
    pi: Sequence[int],
    cycle: Sequence[Arc],
) -> tuple[int, ...]:
    images = set()
    for arc in cycle:
        images.add(arc.src)
        images.add(arc.via_path_neighbor)
        images.add(arc.dst)
    # The dst is the block mate of via_path_neighbor, so src+via images
    # already cover the same support.  Keeping dst is harmless and makes
    # the reconstruction robust.
    return support_from_images(k, pi, sorted(images))


def _single_block_witness(
    k: int,
    pi: Sequence[int],
    active_blocks: set[int],
) -> dict | None:
    blocks = even_adjacent_blocks(k)
    for block_id in sorted(active_blocks):
        block = blocks[block_id]
        pred = predict_v6pp(k, pi, block)
        if pred["prediction"] == "minimal_fatal":
            return {
                "kind": "single_block",
                "support": list(block),
                "prediction": pred,
            }
    return None


def find_v6pp_positive_core(
    k: int,
    pi: Sequence[int],
    eps: Sequence[int],
) -> dict | None:
    """Return one V6''-positive core contained in eps, if one exists.

    This is the polynomial separation oracle used by the final
    fork-tree Horn decision layer.
    """
    _validate(k, pi, eps)
    eps_tuple = tuple(int(x) for x in eps)
    active_blocks = fully_selected_blocks(k, eps_tuple)
    data = image_data(k, pi)

    single = _single_block_witness(k, pi, active_blocks)
    if single is not None:
        return single

    # P3: any alternating cycle whose selected image set avoids k-1.
    p3_arcs = _transition_arcs(
        k,
        data,
        active_blocks,
        path_edge_allowed=lambda _start: True,
        excluded_image=k - 1,
    )
    p3_cycle = _find_directed_cycle(p3_arcs, min_len=2)
    if p3_cycle is not None:
        support = _cycle_support(k, pi, p3_cycle)
        return {
            "kind": "P3_alternating_cycle",
            "support": list(support),
            "cycle_images": [arc.src for arc in p3_cycle],
            "prediction": predict_v6pp(k, pi, support),
        }

    # P4: natural odd-start multi-interval cycle.
    p4_arcs = _transition_arcs(
        k,
        data,
        active_blocks,
        path_edge_allowed=lambda start: start % 2 == 1,
        excluded_image=None,
    )
    p4_cycle = _find_directed_cycle(p4_arcs, min_len=2)
    if p4_cycle is not None:
        support = _cycle_support(k, pi, p4_cycle)
        return {
            "kind": "P4_natural_odd_cycle",
            "support": list(support),
            "cycle_images": [arc.src for arc in p4_cycle],
            "prediction": predict_v6pp(k, pi, support),
        }

    return None


def assignment_extendable_v6pp(
    k: int,
    pi: Sequence[int],
    eps: Sequence[int],
) -> dict:
    """Decide one constrained fork-tree assignment modulo V6'' completeness."""
    witness = find_v6pp_positive_core(k, pi, eps)
    return {
        "k": k,
        "pi": list(pi),
        "eps": [int(x) for x in eps],
        "extendable": witness is None,
        "forbidden_core": witness,
    }


def brute_force_v6pp_positive_core_exists(
    k: int,
    pi: Sequence[int],
    eps: Sequence[int],
) -> dict:
    """Slow candidate-subset oracle used only for regression tests.

    Enumerates every union of even blocks and checks NF+V6''.  This is
    exponential in the number of blocks and is not part of the decider.
    """
    _validate(k, pi, eps)
    active_indices = {i for i, bit in enumerate(eps) if int(bit) == 1}
    blocks = even_adjacent_blocks(k)
    for size in range(1, len(blocks) + 1):
        for block_subset in combinations(blocks, size):
            support = tuple(sorted(i for block in block_subset for i in block))
            if not set(support).issubset(active_indices):
                continue
            if not is_cyclic_ladder_core(k, pi, support):
                continue
            pred = predict_v6pp(k, pi, support)
            if pred["prediction"] == "minimal_fatal":
                return {
                    "exists": True,
                    "support": list(support),
                    "prediction": pred,
                }
    return {"exists": False, "support": None, "prediction": None}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, required=True)
    parser.add_argument("--pi", type=str, required=True)
    parser.add_argument("--eps", type=str, required=True)
    parser.add_argument("--brute-check", action="store_true")
    args = parser.parse_args()
    pi = tuple(int(x) for x in args.pi.split(","))
    eps = tuple(int(x) for x in args.eps.split(","))
    out = assignment_extendable_v6pp(args.k, pi, eps)
    if args.brute_check:
        out["brute_candidate_check"] = brute_force_v6pp_positive_core_exists(
            args.k, pi, eps
        )
    print(json.dumps(out, indent=2, default=list))


if __name__ == "__main__":
    main()
