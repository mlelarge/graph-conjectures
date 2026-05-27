"""Generic cyclic ladder probe for fork-tree fatal sets.

This is the size-independent version of the two-, three-, and
four-interval ladder probes.  A cyclic m-interval ladder uses m
even-odd toggle blocks and m B-image intervals of size 2; each selected
block hits two intervals, and the block/interval incidence graph is a
simple cycle.

The probe deliberately tests *minimal fatality*, not raw
nonextendability.  Some larger ladder prefixes are nonextendable while
already containing smaller fatal subsets; those are not minimal fatal
sets and should not be counted by the quotient detector.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import deque
from itertools import combinations
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rectangle_detachability_probe import (  # noqa: E402
    even_adjacent_blocks,
    find_completion_suffix,
    fork_prefix_state,
    two_interval_ladder_sets,
)


def _adjacent_pair_intervals(images: Sequence[int]) -> list[set[int]] | None:
    if len(images) % 2 != 0:
        return None
    sorted_images = sorted(images)
    # Cyclic ladders live above the root-side B_0 position.  If a
    # selected interval uses image 0, the chain-bottom obstruction is
    # already absorbed and the V5 trigger logic no longer applies.
    if sorted_images and sorted_images[0] == 0:
        return None
    intervals: list[set[int]] = []
    for i in range(0, len(sorted_images), 2):
        a, b = sorted_images[i], sorted_images[i + 1]
        if b != a + 1:
            return None
        if i > 0 and a <= sorted_images[i - 1]:
            return None
        intervals.append({a, b})
    return intervals


def _is_simple_cycle(edges: Sequence[frozenset[int]], interval_count: int) -> bool:
    if interval_count < 3:
        return False
    edge_set = set(edges)
    if len(edge_set) != interval_count:
        return False
    degree = [0] * interval_count
    adjacency = [set() for _ in range(interval_count)]
    for edge in edge_set:
        if len(edge) != 2:
            return False
        a, b = tuple(edge)
        degree[a] += 1
        degree[b] += 1
        adjacency[a].add(b)
        adjacency[b].add(a)
    if degree != [2] * interval_count:
        return False
    seen = {0}
    queue = deque([0])
    while queue:
        v = queue.popleft()
        for w in adjacency[v]:
            if w not in seen:
                seen.add(w)
                queue.append(w)
    return len(seen) == interval_count


def _is_simple_cycle_on_vertices(
    edges: Sequence[frozenset[int]],
    vertices: Sequence[int],
) -> bool:
    vertex_set = set(vertices)
    if len(vertex_set) < 3:
        return False
    edge_set = set(edges)
    if len(edge_set) != len(vertex_set):
        return False
    degree = {v: 0 for v in vertex_set}
    adjacency = {v: set() for v in vertex_set}
    for edge in edge_set:
        if len(edge) != 2 or not edge.issubset(vertex_set):
            return False
        a, b = tuple(edge)
        degree[a] += 1
        degree[b] += 1
        adjacency[a].add(b)
        adjacency[b].add(a)
    if any(d != 2 for d in degree.values()):
        return False
    start = next(iter(vertex_set))
    seen = {start}
    queue = deque([start])
    while queue:
        v = queue.popleft()
        for w in adjacency[v]:
            if w not in seen:
                seen.add(w)
                queue.append(w)
    return seen == vertex_set


def cyclic_ladder_sets(
    k: int,
    pi: Sequence[int],
    interval_count: int,
) -> list[tuple[int, ...]]:
    """Enumerate cyclic ladder candidates with `interval_count` intervals."""
    blocks = even_adjacent_blocks(k)
    if len(blocks) < interval_count:
        return []
    ladders: set[tuple[int, ...]] = set()
    for block_indices in combinations(range(len(blocks)), interval_count):
        selected_blocks = [blocks[i] for i in block_indices]
        selected = tuple(sorted(sum(selected_blocks, ())))
        images = [pi[i] for i in selected]
        if len(set(images)) != 2 * interval_count:
            continue
        intervals = _adjacent_pair_intervals(images)
        if intervals is None or len(intervals) != interval_count:
            continue
        block_edges: list[frozenset[int]] = []
        ok = True
        for block in selected_blocks:
            block_images = {pi[i] for i in block}
            hit = [idx for idx, interval in enumerate(intervals) if block_images & interval]
            if len(block_images) != 2 or len(hit) != 2:
                ok = False
                break
            if any(len(block_images & intervals[idx]) != 1 for idx in hit):
                ok = False
                break
            block_edges.append(frozenset(hit))
        if ok and _is_simple_cycle(block_edges, interval_count):
            ladders.add(selected)
    return sorted(ladders)


def _virtual_trigger_status(state: dict) -> dict:
    active_intervals = set(state["active_intervals"])
    active_images = [
        image
        for idx, interval in enumerate(state["intervals"])
        if idx in active_intervals
        for image in interval
    ]
    if not active_images:
        return {"prediction": "not_a_candidate", "reason": "no_active_images"}
    img_lo = min(active_images)
    img_hi = max(active_images)
    active_real_vertices = {
        v
        for edge in state["edges"]
        if edge["kind"] == "real"
        for v in edge["block"]
    }
    filler_indices = [i for i in range(state["k"]) if i not in active_real_vertices]

    for fi in filler_indices:
        if state["pi"][fi] > img_hi:
            return {
                "prediction": "minimal_fatal",
                "reason": "P3_image_above",
                "filler": fi,
                "image": state["pi"][fi],
                "image_low": img_lo,
                "image_high": img_hi,
            }

    if state["k"] % 2 == 1:
        lone = state["k"] - 1
        if lone in filler_indices and state["pi"][lone] < img_lo:
            return {
                "prediction": "minimal_fatal",
                "reason": "P3prime_lone_filler_image_below",
                "filler": lone,
                "image": state["pi"][lone],
                "image_low": img_lo,
                "image_high": img_hi,
            }

    return {
        "prediction": "not_minimal_fatal",
        "reason": "no_chain_end_trigger",
        "image_low": img_lo,
        "image_high": img_hi,
    }


def _virtual_state_summary(state: dict) -> dict:
    vertices = sorted(state["active_intervals"])
    edge_sets = [frozenset(edge["endpoints"]) for edge in state["edges"]]
    active_real_blocks = [
        edge["block"] for edge in state["edges"] if edge["kind"] == "real"
    ]
    virtual_edges = [
        edge["endpoints"] for edge in state["edges"] if edge["kind"] == "virtual"
    ]
    return {
        "step": state["step"],
        "active_intervals": vertices,
        "cycle_ok": _is_simple_cycle_on_vertices(edge_sets, vertices),
        "active_real_blocks": [list(block) for block in active_real_blocks],
        "virtual_edges": [list(edge) for edge in virtual_edges],
        "absorbed_blocks": [list(block) for block in state["absorbed_blocks"]],
        "trigger": _virtual_trigger_status(state),
    }


def cyclic_ladder_structure(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
) -> dict | None:
    """Return interval/block incidence data for one cyclic ladder."""
    selected = tuple(sorted(selected))
    if len(selected) % 2 != 0:
        return None
    interval_count = len(selected) // 2
    if interval_count < 3:
        return None
    intervals = _adjacent_pair_intervals([pi[i] for i in selected])
    if intervals is None or len(intervals) != interval_count:
        return None
    selected_blocks = [
        block for block in even_adjacent_blocks(k)
        if set(block).issubset(selected)
    ]
    if len(selected_blocks) != interval_count:
        return None

    block_edges: list[dict] = []
    edge_sets: list[frozenset[int]] = []
    for block in selected_blocks:
        block_images = {pi[i] for i in block}
        hit = [idx for idx, interval in enumerate(intervals) if block_images & interval]
        if len(block_images) != 2 or len(hit) != 2:
            return None
        if any(len(block_images & intervals[idx]) != 1 for idx in hit):
            return None
        edge = frozenset(hit)
        edge_sets.append(edge)
        block_edges.append({
            "block": block,
            "images": tuple(sorted(block_images)),
            "interval_edge": tuple(sorted(edge)),
        })
    if not _is_simple_cycle(edge_sets, interval_count):
        return None
    return {
        "selected": selected,
        "intervals": [tuple(sorted(interval)) for interval in intervals],
        "block_edges": block_edges,
    }


def initial_virtual_ladder_state(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
) -> dict | None:
    """Build the initial virtual-ladder state before contractions."""
    structure = cyclic_ladder_structure(k, pi, selected)
    if structure is None:
        return None
    edges = [
        {
            "kind": "real",
            "endpoints": tuple(edge["interval_edge"]),
            "block": tuple(edge["block"]),
            "images": tuple(edge["images"]),
        }
        for edge in structure["block_edges"]
    ]
    return {
        "step": 0,
        "k": k,
        "pi": tuple(pi),
        "intervals": tuple(tuple(interval) for interval in structure["intervals"]),
        "active_intervals": tuple(range(len(structure["intervals"]))),
        "edges": edges,
        "absorbed_blocks": tuple(),
    }


def contract_top_interval(state: dict) -> dict:
    """Peel the current top interval and contract its two incident edges."""
    active = set(state["active_intervals"])
    top = max(active, key=lambda idx: max(state["intervals"][idx]))
    incident = [edge for edge in state["edges"] if top in edge["endpoints"]]
    if len(incident) != 2:
        raise ValueError(f"top interval has {len(incident)} incident edges, expected 2")
    other_endpoints = sorted(
        next(v for v in edge["endpoints"] if v != top)
        for edge in incident
    )
    absorbed = set(tuple(block) for block in state["absorbed_blocks"])
    for edge in incident:
        if edge["kind"] == "real":
            absorbed.add(tuple(edge["block"]))
        else:
            absorbed.update(tuple(block) for block in edge.get("absorbed_blocks", ()))
    absorbed_tuple = tuple(sorted(absorbed))

    next_edges = [edge for edge in state["edges"] if top not in edge["endpoints"]]
    next_edges.append({
        "kind": "virtual",
        "endpoints": tuple(other_endpoints),
        "absorbed_blocks": absorbed_tuple,
    })
    next_active = tuple(sorted(active - {top}))
    return {
        **state,
        "step": state["step"] + 1,
        "active_intervals": next_active,
        "edges": next_edges,
        "absorbed_blocks": absorbed_tuple,
    }


def virtual_contraction_sequence(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
    stop_at: int = 3,
) -> dict:
    """Return virtual-ladder summaries after repeatedly contracting the top.

    The sequence stops at `stop_at` active intervals because a simple
    graph cycle on two vertices would require parallel edges, which this
    representation intentionally does not use.
    """
    state = initial_virtual_ladder_state(k, pi, selected)
    if state is None:
        return {"status": "not_a_cyclic_ladder", "states": []}
    states = [_virtual_state_summary(state)]
    while len(state["active_intervals"]) > stop_at:
        state = contract_top_interval(state)
        states.append(_virtual_state_summary(state))
    first_trigger = next(
        (
            row for row in states
            if row["trigger"]["prediction"] == "minimal_fatal"
        ),
        None,
    )
    return {
        "status": "ok",
        "states": states,
        "first_trigger_step": (
            None if first_trigger is None else first_trigger["step"]
        ),
        "first_trigger": first_trigger,
    }


def contracted_trigger_real_witness(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
    time_budget_sec: float | None = None,
) -> dict:
    """Translate the first contracted trigger into a real toggle witness.

    If the first trigger occurs at step 0, the witness is the original
    selected ladder.  If it occurs later and the triggering filler is in
    an absorbed real block, that block is a concrete smaller real
    minimal-fatal candidate.  This is the semantic bridge from virtual
    contraction to the original fork-tree.
    """
    sequence = virtual_contraction_sequence(k, pi, selected)
    if sequence["status"] != "ok":
        return {"status": sequence["status"]}
    first = sequence["first_trigger"]
    if first is None:
        return {
            "status": "no_trigger",
            "sequence": sequence,
        }

    step = first["step"]
    trigger = first["trigger"]
    if step == 0:
        cert = targeted_minimal_fatal_certificate(
            k, pi, selected, time_budget_sec=time_budget_sec
        )
        return {
            "status": "original_trigger",
            "trigger_step": 0,
            "trigger": trigger,
            "witness": list(selected),
            "certificate": {
                "minimal_fatal": cert["minimal_fatal"],
                "reason": cert["reason"],
            },
            "sequence": sequence,
        }

    filler = trigger.get("filler")
    if filler is None:
        return {
            "status": "unsupported_trigger_without_filler",
            "trigger_step": step,
            "trigger": trigger,
            "sequence": sequence,
        }
    absorbed_blocks = [tuple(block) for block in first["absorbed_blocks"]]
    witness_block = next(
        (block for block in absorbed_blocks if filler in block),
        None,
    )
    if witness_block is None:
        return {
            "status": "trigger_not_absorbed",
            "trigger_step": step,
            "trigger": trigger,
            "absorbed_blocks": [list(block) for block in absorbed_blocks],
            "sequence": sequence,
        }

    cert = targeted_minimal_fatal_certificate(
        k, pi, witness_block, time_budget_sec=time_budget_sec
    )
    return {
        "status": "absorbed_block_witness",
        "trigger_step": step,
        "trigger": trigger,
        "witness": list(witness_block),
        "certificate": {
            "minimal_fatal": cert["minimal_fatal"],
            "reason": cert["reason"],
        },
        "absorbed_blocks": [list(block) for block in absorbed_blocks],
        "sequence": sequence,
    }


def contained_pair_witness(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
    time_budget_sec: float | None = None,
) -> dict | None:
    """Return a real size-2 fatal pair contained in selected, if any."""
    selected_set = set(selected)
    for block in even_adjacent_blocks(k):
        if not set(block).issubset(selected_set):
            continue
        cert = targeted_minimal_fatal_certificate(
            k, pi, block, time_budget_sec=time_budget_sec
        )
        if cert["minimal_fatal"]:
            return {
                "status": "contained_pair_witness",
                "witness": list(block),
                "certificate": {
                    "minimal_fatal": cert["minimal_fatal"],
                    "reason": cert["reason"],
                },
            }
    return None


def contained_ladder_witness(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
    time_budget_sec: float | None = None,
) -> dict | None:
    """Return a proper contained minimal-fatal ladder witness, if any."""
    selected_set = set(selected)
    selected_size = len(selected_set)
    candidates: list[tuple[int, ...]] = []
    candidates.extend(two_interval_ladder_sets(k, pi))
    max_interval_count = max(2, selected_size // 2 - 1)
    for interval_count in range(3, max_interval_count + 1):
        candidates.extend(cyclic_ladder_sets(k, pi, interval_count))

    for cand in sorted(set(candidates), key=lambda item: (len(item), item)):
        cand_set = set(cand)
        if not cand_set < selected_set:
            continue
        cert = targeted_minimal_fatal_certificate(
            k, pi, cand, time_budget_sec=time_budget_sec
        )
        if cert["minimal_fatal"]:
            return {
                "status": "contained_ladder_witness",
                "witness": list(cand),
                "certificate": {
                    "minimal_fatal": cert["minimal_fatal"],
                    "reason": cert["reason"],
                },
            }
    return None


def contracted_obstructive_witness(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
    time_budget_sec: float | None = None,
) -> dict:
    """Find the first contracted trigger that is semantically obstructive.

    Later triggers from original external fillers are ignored.  They can
    be virtual artifacts, as pinned by the D24 counterexample.  The
    obstructive triggers are:

      * any trigger at step 0, whose witness is the original selected set;
      * a later trigger whose filler lies in an absorbed real block.
    """
    sequence = virtual_contraction_sequence(k, pi, selected)
    if sequence["status"] != "ok":
        return {"status": sequence["status"]}

    ignored_external = []
    for row in sequence["states"]:
        trigger = row["trigger"]
        if trigger["prediction"] != "minimal_fatal":
            continue
        step = row["step"]
        if step == 0:
            cert = targeted_minimal_fatal_certificate(
                k, pi, selected, time_budget_sec=time_budget_sec
            )
            if not cert["minimal_fatal"]:
                pair_witness = contained_pair_witness(
                    k, pi, selected, time_budget_sec=time_budget_sec
                )
                if pair_witness is not None:
                    return {
                        **pair_witness,
                        "trigger_step": 0,
                        "trigger": trigger,
                        "ignored_external_triggers": ignored_external,
                        "sequence": sequence,
                    }
                ladder_witness = contained_ladder_witness(
                    k, pi, selected, time_budget_sec=time_budget_sec
                )
                if ladder_witness is not None:
                    return {
                        **ladder_witness,
                        "trigger_step": 0,
                        "trigger": trigger,
                        "ignored_external_triggers": ignored_external,
                        "sequence": sequence,
                    }
                return {
                    "status": "step0_trigger_nonminimal_unexplained",
                    "trigger_step": 0,
                    "trigger": trigger,
                    "witness": list(selected),
                    "certificate": {
                        "minimal_fatal": cert["minimal_fatal"],
                        "reason": cert["reason"],
                    },
                    "ignored_external_triggers": ignored_external,
                    "sequence": sequence,
                }
            return {
                "status": "original_trigger",
                "trigger_step": 0,
                "trigger": trigger,
                "witness": list(selected),
                "certificate": {
                    "minimal_fatal": cert["minimal_fatal"],
                    "reason": cert["reason"],
                },
                "ignored_external_triggers": ignored_external,
                "sequence": sequence,
            }

        filler = trigger.get("filler")
        if filler is None:
            return {
                "status": "unsupported_trigger_without_filler",
                "trigger_step": step,
                "trigger": trigger,
                "ignored_external_triggers": ignored_external,
                "sequence": sequence,
            }
        absorbed_blocks = [tuple(block) for block in row["absorbed_blocks"]]
        witness_block = next(
            (block for block in absorbed_blocks if filler in block),
            None,
        )
        if witness_block is None:
            ignored_external.append({
                "step": step,
                "trigger": trigger,
                "absorbed_blocks": [list(block) for block in absorbed_blocks],
            })
            continue

        cert = targeted_minimal_fatal_certificate(
            k, pi, witness_block, time_budget_sec=time_budget_sec
        )
        return {
            "status": "absorbed_block_witness",
            "trigger_step": step,
            "trigger": trigger,
            "witness": list(witness_block),
            "certificate": {
                "minimal_fatal": cert["minimal_fatal"],
                "reason": cert["reason"],
            },
            "absorbed_blocks": [list(block) for block in absorbed_blocks],
            "ignored_external_triggers": ignored_external,
            "sequence": sequence,
        }

    pair_witness = contained_pair_witness(
        k, pi, selected, time_budget_sec=time_budget_sec
    )
    if pair_witness is not None:
        return {
            **pair_witness,
            "trigger_step": None,
            "ignored_external_triggers": ignored_external,
            "sequence": sequence,
        }

    ladder_witness = contained_ladder_witness(
        k, pi, selected, time_budget_sec=time_budget_sec
    )
    if ladder_witness is not None:
        return {
            **ladder_witness,
            "trigger_step": None,
            "ignored_external_triggers": ignored_external,
            "sequence": sequence,
        }

    internal_gap = predict_three_interval_internal_gap_fatal(k, pi, selected)
    if internal_gap["prediction"] == "minimal_fatal":
        cert = targeted_minimal_fatal_certificate(
            k, pi, selected, time_budget_sec=time_budget_sec
        )
        if cert["minimal_fatal"]:
            return {
                "status": "internal_gap_witness",
                "trigger_step": None,
                "trigger": internal_gap,
                "witness": list(selected),
                "certificate": {
                    "minimal_fatal": cert["minimal_fatal"],
                    "reason": cert["reason"],
                },
                "ignored_external_triggers": ignored_external,
                "sequence": sequence,
            }

    completion = completion_certificate(
        k, pi, selected, time_budget_sec=time_budget_sec
    )
    if completion.get("status") == "ok" and not completion.get("detachable"):
        cert = targeted_minimal_fatal_certificate(
            k, pi, selected, time_budget_sec=time_budget_sec
        )
        if cert["minimal_fatal"]:
            return {
                "status": "unclassified_minimal_fatal",
                "witness": list(selected),
                "certificate": {
                    "minimal_fatal": cert["minimal_fatal"],
                    "reason": cert["reason"],
                },
                "ignored_external_triggers": ignored_external,
                "sequence": sequence,
            }
    return {
        "status": "no_obstructive_trigger",
        "ignored_external_triggers": ignored_external,
        "selected_detachable": completion.get("detachable"),
        "completion_status": completion.get("status"),
        "sequence": sequence,
    }


def top_interval_peel_summary(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
) -> dict:
    """Describe the corrected graph operation for peeling the top interval.

    Deleting the top interval and its two incident block-edges leaves a
    path, not a smaller cycle.  The correct inductive graph operation is
    contraction: replace those two incident edges by a virtual edge
    joining their other endpoints.
    """
    structure = cyclic_ladder_structure(k, pi, selected)
    if structure is None:
        return {"status": "not_a_cyclic_ladder"}
    interval_count = len(structure["intervals"])
    top = interval_count - 1
    edges = [
        frozenset(edge["interval_edge"])
        for edge in structure["block_edges"]
    ]
    incident = [edge for edge in edges if top in edge]
    if len(incident) != 2:
        return {"status": "bad_top_degree", "incident": [tuple(e) for e in incident]}
    other_endpoints = sorted(next(v for v in edge if v != top) for edge in incident)
    deleted_edges = [edge for edge in edges if top not in edge]
    virtual_edge = frozenset(other_endpoints)
    contracted_edges = deleted_edges + [virtual_edge]
    contracted_interval_count = interval_count - 1
    return {
        "status": "ok",
        "top_interval": top,
        "incident_edges": [tuple(sorted(edge)) for edge in incident],
        "other_endpoints": other_endpoints,
        "deleted_edges": [tuple(sorted(edge)) for edge in deleted_edges],
        "delete_is_cycle": _is_simple_cycle(deleted_edges, contracted_interval_count),
        "virtual_edge": tuple(sorted(virtual_edge)),
        "contracted_edges": [tuple(sorted(edge)) for edge in contracted_edges],
        "contracted_is_cycle": _is_simple_cycle(
            contracted_edges,
            contracted_interval_count,
        ),
    }


def predict_cyclic_ladder_minimal_fatal(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
) -> dict:
    """Unified V5 chain-end predictor for minimal fatality."""
    selected = tuple(sorted(selected))
    if len(selected) < 4:
        return {"prediction": "not_a_candidate", "reason": "size_too_small"}
    if len(selected) % 2 != 0:
        return {"prediction": "not_a_candidate", "reason": "odd_size"}
    images = sorted({pi[i] for i in selected})
    if len(images) != len(selected):
        return {"prediction": "not_a_candidate", "reason": "image_size"}
    intervals = _adjacent_pair_intervals(images)
    if intervals is None:
        return {"prediction": "not_a_candidate", "reason": "not_adjacent_intervals"}

    img_lo = images[0]
    img_hi = images[-1]
    selected_set = set(selected)
    filler_indices = [i for i in range(k) if i not in selected_set]

    for fi in filler_indices:
        if pi[fi] > img_hi:
            return {
                "prediction": "minimal_fatal",
                "reason": "P3_image_above",
                "filler": fi,
                "image": pi[fi],
            }

    if k % 2 == 1:
        lone = k - 1
        if lone in filler_indices and pi[lone] < img_lo:
            return {
                "prediction": "minimal_fatal",
                "reason": "P3prime_lone_filler_image_below",
                "filler": lone,
                "image": pi[lone],
            }

    return {
        "prediction": "not_minimal_fatal",
        "reason": "no_chain_end_trigger",
    }


def internal_gap_profile(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
) -> dict:
    """Describe image gaps between consecutive selected intervals.

    For a permutation pi, every image value missing from the selected
    intervals belongs to a filler index.  Thus "the internal gap is
    completely filled by fillers" is not an extra condition; it follows
    tautologically from the existence of the gap.  The meaningful
    distinction in the probes is whether the selected intervals are the
    natural B-chain pairs {1,2}, {3,4}, ...
    """
    structure = cyclic_ladder_structure(k, pi, selected)
    if structure is None:
        return {"status": "not_a_cyclic_ladder"}

    intervals = [tuple(interval) for interval in structure["intervals"]]
    selected_set = set(selected)
    filler_indices = [i for i in range(k) if i not in selected_set]
    filler_by_image = {pi[i]: i for i in filler_indices}
    gaps = []
    for idx, (left, right) in enumerate(zip(intervals, intervals[1:])):
        values = tuple(range(left[-1] + 1, right[0]))
        if not values:
            continue
        gaps.append({
            "between": (idx, idx + 1),
            "values": values,
            "filler_indices": tuple(filler_by_image[v] for v in values),
            "fully_filled_by_fillers": all(v in filler_by_image for v in values),
        })

    return {
        "status": "ok",
        "intervals": intervals,
        "gaps": gaps,
        "has_internal_gap": bool(gaps),
        "natural_odd_pairs": all(interval[0] % 2 == 1 for interval in intervals),
        "filler_images": tuple(sorted((pi[i], i) for i in filler_indices)),
    }


def predict_three_interval_internal_gap_fatal(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
) -> dict:
    """P4 candidate for no-chain-end three-interval ladders.

    This deliberately does not replace P3/P3'.  It refines the residual
    case where the chain-end predictor sees no obstruction.  The current
    empirical criterion is:

      no P3/P3' + three intervals + internal image gap + natural
      odd-start B-pairs  =>  minimal fatal.

    Misaligned gaps are detachable or nonminimal in the pinned small
    catalogues.
    """
    structure = cyclic_ladder_structure(k, pi, selected)
    if structure is None:
        return {"prediction": "not_a_candidate", "reason": "not_a_cyclic_ladder"}
    if len(structure["intervals"]) != 3:
        return {"prediction": "not_a_candidate", "reason": "not_three_interval"}

    chain_end = predict_cyclic_ladder_minimal_fatal(k, pi, selected)
    if chain_end["prediction"] == "minimal_fatal":
        return chain_end
    if chain_end["prediction"] != "not_minimal_fatal":
        return chain_end

    profile = internal_gap_profile(k, pi, selected)
    if not profile["has_internal_gap"]:
        return {
            "prediction": "not_minimal_fatal",
            "reason": "no_internal_gap",
            "profile": profile,
        }
    if profile["natural_odd_pairs"]:
        return {
            "prediction": "minimal_fatal",
            "reason": "P4_natural_odd_internal_gap",
            "profile": profile,
        }
    return {
        "prediction": "not_minimal_fatal",
        "reason": "P4_misaligned_internal_gap",
        "profile": profile,
    }


def completion_certificate(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
    time_budget_sec: float | None = None,
) -> dict:
    setup = fork_prefix_state(k, pi, selected)
    if setup is None:
        return {"status": "invalid_or_pruned", "detachable": False}
    T, cut, state = setup
    out = find_completion_suffix(T, cut, state, time_budget_sec=time_budget_sec)
    return {"status": "ok", **out}


def targeted_minimal_fatal_certificate(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
    time_budget_sec: float | None = None,
) -> dict:
    """Check minimal fatality of one selected set without sweeping 2^k."""
    selected = tuple(sorted(selected))
    base = completion_certificate(k, pi, selected, time_budget_sec=time_budget_sec)
    if base["status"] != "ok":
        return {
            "minimal_fatal": False,
            "reason": "invalid_or_pruned",
            "selected": list(selected),
            "base": base,
        }
    if base["detachable"]:
        return {
            "minimal_fatal": False,
            "reason": "selected_detachable",
            "selected": list(selected),
            "base": base,
        }

    deletions = []
    for x in selected:
        subset = tuple(y for y in selected if y != x)
        cert = completion_certificate(k, pi, subset, time_budget_sec=time_budget_sec)
        deletions.append({"removed": x, **cert})
    if all(row["status"] == "ok" and row["detachable"] for row in deletions):
        return {
            "minimal_fatal": True,
            "reason": "selected_not_detachable_all_deletions_detachable",
            "selected": list(selected),
            "base": base,
            "deletions": deletions,
        }
    return {
        "minimal_fatal": False,
        "reason": "some_deletion_not_detachable",
        "selected": list(selected),
        "base": base,
        "deletions": deletions,
    }


def construct_cyclic_ladder(
    k: int,
    interval_count: int,
    low_start: int | None = None,
) -> tuple[int, ...] | None:
    """Construct a canonical cyclic ladder on the first m blocks.

    Block E_i gets the high image of interval i and the low image of
    interval i+1 mod m.  The remaining indices receive the unused
    images in increasing order.
    """
    m = interval_count
    if k < 2 * m:
        return None
    if low_start is None:
        low_start = 1 if k % 2 == 1 else 2
    if low_start < 0 or low_start + 2 * m - 1 >= k:
        return None

    pi = [-1] * k
    for i in range(m):
        pi[2 * i] = low_start + 2 * i + 1
        pi[2 * i + 1] = low_start + 2 * ((i + 1) % m)
    used = set(pi[: 2 * m])
    remaining_images = [v for v in range(k) if v not in used]
    for idx, image in zip(range(2 * m, k), remaining_images):
        pi[idx] = image
    if any(v < 0 for v in pi):
        return None
    return tuple(pi)


def evaluate_constructed(
    k: int,
    interval_count: int,
    low_start: int | None = None,
    time_budget_sec: float | None = None,
) -> dict:
    pi = construct_cyclic_ladder(k, interval_count, low_start=low_start)
    if pi is None:
        return {"error": "construction_failed", "k": k, "interval_count": interval_count}
    selected = tuple(range(2 * interval_count))
    candidates = cyclic_ladder_sets(k, pi, interval_count)
    prediction = predict_cyclic_ladder_minimal_fatal(k, pi, selected)
    certificate = targeted_minimal_fatal_certificate(
        k, pi, selected, time_budget_sec=time_budget_sec
    )
    contraction = virtual_contraction_sequence(k, pi, selected)
    witness = contracted_trigger_real_witness(
        k, pi, selected, time_budget_sec=time_budget_sec
    )
    obstructive = contracted_obstructive_witness(
        k, pi, selected, time_budget_sec=time_budget_sec
    )
    return {
        "k": k,
        "interval_count": interval_count,
        "pi": list(pi),
        "selected": list(selected),
        "candidates": [list(c) for c in candidates],
        "prediction": prediction,
        "certificate": {
            "minimal_fatal": certificate["minimal_fatal"],
            "reason": certificate["reason"],
            "base_detachable": certificate.get("base", {}).get("detachable"),
            "deletion_detachable": [
                row.get("detachable") for row in certificate.get("deletions", [])
            ],
        },
        "contraction": {
            "status": contraction["status"],
            "first_trigger_step": contraction.get("first_trigger_step"),
            "states": contraction.get("states", []),
        },
        "real_witness": {
            "status": witness["status"],
            "trigger_step": witness.get("trigger_step"),
            "witness": witness.get("witness"),
            "certificate": witness.get("certificate"),
        },
        "obstructive_witness": {
            "status": obstructive["status"],
            "trigger_step": obstructive.get("trigger_step"),
            "witness": obstructive.get("witness"),
            "certificate": obstructive.get("certificate"),
            "selected_detachable": obstructive.get("selected_detachable"),
            "ignored_external_triggers": obstructive.get("ignored_external_triggers"),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=11)
    parser.add_argument("--interval-count", type=int, default=5)
    parser.add_argument("--low-start", type=int, default=None)
    parser.add_argument("--time-budget-sec", type=float, default=None)
    args = parser.parse_args()
    print(json.dumps(
        evaluate_constructed(
            args.k,
            args.interval_count,
            low_start=args.low_start,
            time_budget_sec=args.time_budget_sec,
        ),
        indent=2,
        default=list,
    ))


if __name__ == "__main__":
    main()
