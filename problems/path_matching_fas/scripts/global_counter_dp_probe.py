"""Global-counter DP variants for Path-FAS on tournaments.

This probes the question: can the per-bag *partition* component of the
J-pathwidth DP state be replaced by a small global counter without
changing the answer?

The full DP state at each bag B of a (nice) path decomposition of the
interaction graph J(T) = H(T) U G_flex(T) is
    (sigma, degree, comp)
where sigma is the LFO restricted to B (a permutation of B), degree
is the per-bag-vertex current loaded-backedge degree in {0, 1, 2}, and
comp is the partition of B induced by the loaded-backedge linear-forest
components.

The expensive piece is comp: it ranges over Bell(|B|) partitions and
its purpose is *cycle detection* — when we load a new back-arc {u, v},
we must reject if u and v are already in the same component (would form
a cycle, violating linear-forest).

We test three reduced-state variants here.

  Variant A — DROP comp entirely.  State = (sigma, degree).  Cycle
  detection disabled (or, equivalently, we cheat: we never reject for
  cycles).  This should over-accept: NO instances may turn into YES.

  Variant B — replace comp by a single counter
              num_open_components = number of partition classes of B
              that contain at least one bag vertex of degree >= 1
              (i.e. components currently "touched" by some loaded edge
              in the bag).  Cycle detection uses a heuristic: when
              loading {u, v} both of degree 1, reject the load if
              num_open_components == 1 and u, v are the only bag
              vertices of positive degree (likely cycle case).  This is
              still loose.  In practice we keep a more conservative
              variant: drop the partition and instead track the
              number of degree-1 endpoints currently in the bag.

  Variant C — drop comp BUT additionally track the GLOBAL number of
              loaded back-arc cycles formed so far (computed exactly,
              by maintaining the full forest globally — not just on
              the bag).  This is the "honest" global counter: keep
              a full union-find on ALL vertices ever loaded, but the
              per-bag state record only (sigma, degree, cycles_formed).
              cycles_formed must be 0 for acceptance.  Since the
              union-find is part of the *trace* not the state key, this
              loses information: two states with the same key but
              different union-find histories share continuations.

For each variant we run the same correctness suite as the full DP and
report disagreements.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import random
import sys
import time
from typing import Dict, List, Sequence, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import networkx as nx  # noqa: E402

from J_pathwidth_dp import (  # noqa: E402
    J_graph,
    is_backedge_in_LFO,
    nice_path_decomposition,
)
from lfo_score_window import score_windows  # noqa: E402
from path_fas import decide_path_fas_bruteforce  # noqa: E402

Matrix = Sequence[Sequence[int]]


def _must_precede(windows: Sequence[Tuple[int, int]], u: int, v: int) -> bool:
    return windows[u][1] < windows[v][0]


def _allowed_positions(
    sigma: Tuple[int, ...],
    v: int,
    windows: Sequence[Tuple[int, int]],
) -> List[int]:
    positions: List[int] = []
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


# ---------------------------------------------------------------------------
# Variant A: drop comp entirely.  No cycle detection at all.
# ---------------------------------------------------------------------------


def path_fas_variant_A(
    T: Matrix,
    radius: int = 2,
) -> bool:
    """State = (sigma_tuple, deg_tuple).  No cycle detection.

    Over-accepts: any LFO whose back-arc graph has max degree 2 but
    contains a cycle (so 2-regular component = oriented even cycle)
    is accepted.  This is interesting only as a baseline.
    """
    n = len(T)
    windows = score_windows(T, radius)
    J, _, _, _ = J_graph(T, radius)
    decomposition, _ = nice_path_decomposition(J)

    # state: (sigma, degree_tuple)
    bag_states: Dict[Tuple, Tuple[Tuple[int, ...], Dict[int, int]]] = {((), ()): ((), {})}
    cur_bag = decomposition[0]
    for nxt_bag in decomposition[1:]:
        diff_intro = nxt_bag - cur_bag
        diff_forget = cur_bag - nxt_bag
        new_states: Dict[Tuple, Tuple[Tuple[int, ...], Dict[int, int]]] = {}
        if diff_intro:
            v = next(iter(diff_intro))
            for (sigma, deg) in bag_states.values():
                positions = _allowed_positions(sigma, v, windows)
                for pos in positions:
                    new_sigma = sigma[:pos] + (v,) + sigma[pos:]
                    new_deg = dict(deg)
                    new_deg[v] = 0
                    feasible = True
                    sigma_pos = {x: i for i, x in enumerate(new_sigma)}
                    for u in sigma:
                        if not J.has_edge(v, u):
                            continue
                        if is_backedge_in_LFO(T, v, u, sigma_pos):
                            if new_deg[v] >= 2 or new_deg[u] >= 2:
                                feasible = False
                                break
                            new_deg[v] += 1
                            new_deg[u] += 1
                    if not feasible:
                        continue
                    key = (new_sigma, tuple(new_deg[x] for x in new_sigma))
                    if key not in new_states:
                        new_states[key] = (new_sigma, new_deg)
        elif diff_forget:
            v = next(iter(diff_forget))
            for (sigma, deg) in bag_states.values():
                new_sigma = tuple(x for x in sigma if x != v)
                new_deg = {x: deg[x] for x in new_sigma}
                key = (new_sigma, tuple(new_deg[x] for x in new_sigma))
                if key not in new_states:
                    new_states[key] = (new_sigma, new_deg)
        else:
            new_states = dict(bag_states)
        bag_states = new_states
        cur_bag = nxt_bag
        if not bag_states:
            return False
    return len(bag_states) > 0


# ---------------------------------------------------------------------------
# Variant B: replace comp by (num_open_components, num_deg1_endpoints).
# Cycle detection is heuristic: forbid loading the *closing* edge that
# would necessarily form a cycle (when only one open component remains
# with both endpoints in the bag).  This is the "forest counter" route.
# ---------------------------------------------------------------------------


def path_fas_variant_B(
    T: Matrix,
    radius: int = 2,
) -> bool:
    """Replace comp by a global pair (num_open_paths, num_deg1_bag).

    num_open_paths: number of partition classes of the WHOLE so-far
        loaded back-arc graph that intersect the current bag.  (Computed
        via global union-find on the trace; recorded only as the count
        in the state key.)
    num_deg1_bag: number of bag vertices with degree 1.

    Cycle detection: enforce that loading {u, v} where u, v are in the
    same class would be rejected — but this requires knowing the class,
    so we *don't* enforce it in the state key.  We instead defer cycle
    check by maintaining a global union-find auxiliary structure
    *outside* the state key (so states that disagree on union-find but
    agree on the key get merged — losing information).

    This is precisely the "global-counter" experiment.  If two states
    with identical (sigma, degree, num_open_paths, num_deg1_bag) but
    different actual partitions extend differently, variant B will
    *collide* — accepting some NO instances or rejecting some YES.
    """
    n = len(T)
    windows = score_windows(T, radius)
    J, _, _, _ = J_graph(T, radius)
    decomposition, _ = nice_path_decomposition(J)

    # We maintain:
    #   bag_states: {key: list of (sigma, deg, parent, num_open_paths)}
    # where the *key* is a coarse summary and the value list carries
    # full extended info.  But for the *variant B DP* the key is the
    # summary, and we keep only ONE representative value per key
    # (collapsing the rest).  This is the lossy step.

    initial_value = ((), {}, {}, 0)  # sigma, deg, parent (global UF), num_open_paths
    bag_states: Dict[Tuple, Tuple[Tuple[int, ...], Dict[int, int], Dict[int, int], int]]
    bag_states = {((), (), 0, 0): initial_value}

    def find(parent: Dict[int, int], x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    cur_bag = decomposition[0]
    for nxt_bag in decomposition[1:]:
        diff_intro = nxt_bag - cur_bag
        diff_forget = cur_bag - nxt_bag
        new_states: Dict[Tuple, Tuple[Tuple[int, ...], Dict[int, int], Dict[int, int], int]] = {}
        if diff_intro:
            v = next(iter(diff_intro))
            for (sigma, deg, parent, num_open) in bag_states.values():
                positions = _allowed_positions(sigma, v, windows)
                for pos in positions:
                    new_sigma = sigma[:pos] + (v,) + sigma[pos:]
                    new_deg = dict(deg)
                    new_deg[v] = 0
                    new_parent = dict(parent)
                    new_parent[v] = v
                    new_num_open = num_open  # we'll update after processing edges
                    feasible = True
                    sigma_pos = {x: i for i, x in enumerate(new_sigma)}
                    # Track whether v starts a new component
                    v_active_component = False
                    for u in sigma:
                        if not J.has_edge(v, u):
                            continue
                        if is_backedge_in_LFO(T, v, u, sigma_pos):
                            if new_deg[v] >= 2 or new_deg[u] >= 2:
                                feasible = False
                                break
                            # Cycle check using local parent (auxiliary)
                            rv = find(new_parent, v)
                            ru = find(new_parent, u)
                            if rv == ru:
                                feasible = False
                                break
                            # Merge: each previously-open path becomes one.
                            # If v had degree 0 (no component yet) and u was
                            # in an open path, v joins that path: no change to num_open.
                            # If u was previously alone (degree 0), u was contributing
                            # one singleton — but singletons aren't open paths in our
                            # count.  We count "open paths" = #classes with ≥1 loaded edge.
                            v_had_edge = new_deg[v] > 0
                            u_had_edge = new_deg[u] > 0
                            if v_had_edge and u_had_edge:
                                # Two existing open paths merge into one.
                                new_num_open -= 1
                            elif (not v_had_edge) and (not u_had_edge):
                                # Two singletons form a new open path.
                                new_num_open += 1
                            # else: open path absorbs a singleton — no change.
                            new_parent[ru] = rv
                            new_deg[v] += 1
                            new_deg[u] += 1
                    if not feasible:
                        continue
                    # Build the LOSSY key for variant B.
                    deg_tuple = tuple(new_deg[x] for x in new_sigma)
                    num_deg1_bag = sum(1 for d in deg_tuple if d == 1)
                    key = (new_sigma, deg_tuple, new_num_open, num_deg1_bag)
                    if key not in new_states:
                        new_states[key] = (new_sigma, new_deg, new_parent, new_num_open)
        elif diff_forget:
            v = next(iter(diff_forget))
            for (sigma, deg, parent, num_open) in bag_states.values():
                new_sigma = tuple(x for x in sigma if x != v)
                new_deg = {x: deg[x] for x in new_sigma}
                new_parent = dict(parent)
                # Forgetting v: if v's component had no other bag vertex,
                # the component is closed.  Determine open count.
                # We recompute num_open by checking whether any other bag
                # vertex is in v's component.
                rv = find(new_parent, v)
                still_open = False
                for x in new_sigma:
                    if find(new_parent, x) == rv and new_deg.get(x, 0) > 0:
                        still_open = True
                        break
                new_num_open = num_open
                # If v had degree > 0 and no other bag vertex shares the
                # component, the path is closed externally (rest forgotten):
                # decrement open count.
                if deg.get(v, 0) > 0 and not still_open:
                    new_num_open -= 1
                deg_tuple = tuple(new_deg[x] for x in new_sigma)
                num_deg1_bag = sum(1 for d in deg_tuple if d == 1)
                key = (new_sigma, deg_tuple, new_num_open, num_deg1_bag)
                if key not in new_states:
                    new_states[key] = (new_sigma, new_deg, new_parent, new_num_open)
        else:
            new_states = dict(bag_states)
        bag_states = new_states
        cur_bag = nxt_bag
        if not bag_states:
            return False
    return len(bag_states) > 0


# ---------------------------------------------------------------------------
# Variant C: keep partition restricted to bag vertices only (no forgotten
# reps), as smallest-bag-vertex labels.  This is structurally similar to
# the full DP but verifies the claim: comp's information beyond
# "partition of bag vertices into classes" is irrelevant.  Should be
# equivalent to the full DP.
# ---------------------------------------------------------------------------


def path_fas_variant_C(
    T: Matrix,
    radius: int = 2,
) -> bool:
    """State = (sigma, degree, bag_partition).

    bag_partition stores, for each bag vertex, the smallest-index bag
    vertex in its component (under the loaded back-arc graph).  No
    forgotten-vertex info.  Forgotten components closed off when
    forgetting a vertex.

    This variant should match the full DP (it discards only forgotten-
    component label info, which the full DP also abstracts via
    smallest-bag-rank canonicalization).  We test it as a sanity check.
    """
    n = len(T)
    windows = score_windows(T, radius)
    J, _, _, _ = J_graph(T, radius)
    decomposition, _ = nice_path_decomposition(J)

    # State = (sigma, deg, bag_comp_dict)
    # bag_comp_dict[x] = smallest bag vertex in x's component
    initial = ((), {}, {})
    bag_states: Dict[Tuple, Tuple] = {((), (), ()): initial}

    cur_bag = decomposition[0]
    for nxt_bag in decomposition[1:]:
        diff_intro = nxt_bag - cur_bag
        diff_forget = cur_bag - nxt_bag
        new_states: Dict[Tuple, Tuple] = {}
        if diff_intro:
            v = next(iter(diff_intro))
            for (sigma, deg, bag_comp) in bag_states.values():
                positions = _allowed_positions(sigma, v, windows)
                for pos in positions:
                    new_sigma = sigma[:pos] + (v,) + sigma[pos:]
                    new_deg = dict(deg)
                    new_deg[v] = 0
                    new_bag_comp = dict(bag_comp)
                    new_bag_comp[v] = v
                    # Build a fresh local union-find for the current bag.
                    parent: Dict[int, int] = {x: new_bag_comp[x] for x in new_sigma}
                    for x in new_sigma:
                        r = new_bag_comp[x]
                        if r not in parent:
                            parent[r] = r

                    def find_local(x: int, _p=parent) -> int:
                        while _p[x] != x:
                            _p[x] = _p[_p[x]]
                            x = _p[x]
                        return x

                    def union_local(a: int, b: int, _p=parent) -> bool:
                        ra = find_local(a)
                        rb = find_local(b)
                        if ra == rb:
                            return False
                        # Always point larger to smaller (so smallest bag vertex
                        # remains rep).
                        if ra > rb:
                            ra, rb = rb, ra
                        _p[rb] = ra
                        return True

                    feasible = True
                    sigma_pos = {x: i for i, x in enumerate(new_sigma)}
                    for u in sigma:
                        if not J.has_edge(v, u):
                            continue
                        if is_backedge_in_LFO(T, v, u, sigma_pos):
                            if new_deg[v] >= 2 or new_deg[u] >= 2:
                                feasible = False
                                break
                            if find_local(v) == find_local(u):
                                feasible = False
                                break
                            new_deg[v] += 1
                            new_deg[u] += 1
                            union_local(v, u)
                    if not feasible:
                        continue
                    # Canonical bag partition: smallest bag vertex in each class.
                    canon: Dict[int, int] = {}
                    for x in new_sigma:
                        rep = find_local(x)
                        # We want the smallest bag vertex sharing rep with x.
                        # Iterate: pick the smallest x' in new_sigma with find_local(x') == rep.
                        # (Cache it.)
                        if rep not in canon:
                            canon[rep] = min(
                                y for y in new_sigma if find_local(y) == rep
                            )
                    final_bag_comp = {x: canon[find_local(x)] for x in new_sigma}
                    sig_key = (
                        new_sigma,
                        tuple(new_deg[x] for x in new_sigma),
                        tuple(final_bag_comp[x] for x in new_sigma),
                    )
                    if sig_key not in new_states:
                        new_states[sig_key] = (new_sigma, new_deg, final_bag_comp)
        elif diff_forget:
            v = next(iter(diff_forget))
            for (sigma, deg, bag_comp) in bag_states.values():
                new_sigma = tuple(x for x in sigma if x != v)
                new_deg = {x: deg[x] for x in new_sigma}
                # Drop v from bag_comp; remap if v was a rep.
                old_rep = bag_comp[v]
                # If v was rep (bag_comp[v] == v), some other bag vertex may
                # share v's component.  Find them.
                shared = [x for x in new_sigma if bag_comp[x] == old_rep]
                if old_rep == v and shared:
                    new_rep = min(shared)
                    new_bag_comp = {x: (new_rep if bag_comp[x] == old_rep else bag_comp[x]) for x in new_sigma}
                else:
                    # Either v wasn't rep, or no shared bag vertex remains.
                    new_bag_comp = {x: bag_comp[x] for x in new_sigma}
                    # If no shared bag vertex remained, the component is
                    # closed off, which is fine.  But we still need to
                    # ensure bag_comp[x] points to a bag vertex if x is in
                    # bag.  If v was rep and no shared, this is moot since
                    # those entries don't exist anymore.
                    # If v was rep and there ARE shared, we've already
                    # remapped above.
                # Final guard: bag_comp must only reference bag vertices.
                # Anything pointing to v (no longer in bag) gets remapped.
                for x in list(new_bag_comp):
                    if new_bag_comp[x] == v:
                        # x's rep was v but no shared was found -- promote x to its own rep
                        # (this can happen if v was alone in its component among bag vertices)
                        new_bag_comp[x] = x
                sig_key = (
                    new_sigma,
                    tuple(new_deg[x] for x in new_sigma),
                    tuple(new_bag_comp[x] for x in new_sigma),
                )
                if sig_key not in new_states:
                    new_states[sig_key] = (new_sigma, new_deg, new_bag_comp)
        else:
            new_states = dict(bag_states)
        bag_states = new_states
        cur_bag = nxt_bag
        if not bag_states:
            return False
    return len(bag_states) > 0


# ---------------------------------------------------------------------------
# Driver / probes.
# ---------------------------------------------------------------------------


VARIANTS = {
    "A": path_fas_variant_A,
    "B": path_fas_variant_B,
    "C": path_fas_variant_C,
}


def all_tournaments(n: int):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for bits in itertools.product([0, 1], repeat=len(pairs)):
        T = [[0] * n for _ in range(n)]
        for (i, j), b in zip(pairs, bits):
            if b:
                T[i][j] = 1
            else:
                T[j][i] = 1
        yield T


def random_tournament(n: int, rng: random.Random):
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < 0.5:
                T[i][j] = 1
            else:
                T[j][i] = 1
    return T


def probe(
    variant: str,
    n: int,
    count: int | None = None,
    seed: int = 20260527,
    exhaustive: bool = False,
    early_stop: int = 5,
) -> dict:
    fn = VARIANTS[variant]
    if exhaustive:
        gen = all_tournaments(n)
        label = "exhaustive"
    else:
        rng = random.Random(seed)
        gen = (random_tournament(n, rng) for _ in range(count or 100))
        label = f"{count or 100} random"
    t0 = time.time()
    total = 0
    mismatches: List[Tuple[int, List[List[int]], bool, bool]] = []
    for T in gen:
        total += 1
        try:
            dp = fn(T)
        except Exception as ex:  # noqa: BLE001
            print(f"  variant {variant} crashed on T (sample {total}): {ex}")
            continue
        bf = decide_path_fas_bruteforce(T)["found"]
        if dp != bf:
            mismatches.append((total, T, dp, bf))
            if len(mismatches) <= early_stop:
                print(f"  COLLISION at sample {total}: variant{variant}={dp} BF={bf}")
                if len(mismatches) == 1:
                    print(f"    smallest collision T: {T}")
        if len(mismatches) >= early_stop:
            pass  # keep counting but suppress further per-sample output
    dt = time.time() - t0
    print(f"variant={variant} n={n} ({label}): total={total} collisions={len(mismatches)} time={dt:.1f}s")
    return {
        "variant": variant,
        "n": n,
        "label": label,
        "total": total,
        "collisions": len(mismatches),
        "first_collisions": mismatches[:early_stop],
        "time": dt,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=list(VARIANTS.keys()), default="A")
    parser.add_argument("--n", type=int, default=5)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--exhaustive", action="store_true")
    parser.add_argument("--all-variants", action="store_true")
    parser.add_argument("--all-n", action="store_true",
                        help="Run exhaustive n=3..6 plus random n=7..9 across all variants")
    args = parser.parse_args()
    results = []
    if args.all_n:
        for v in ["A", "B", "C"]:
            for n_ in [3, 4, 5, 6]:
                results.append(probe(v, n_, exhaustive=True))
            for n_, k in [(7, 200), (8, 100), (9, 30)]:
                results.append(probe(v, n_, count=k))
    elif args.all_variants:
        for v in ["A", "B", "C"]:
            results.append(probe(v, args.n, count=args.count, exhaustive=args.exhaustive))
    else:
        results.append(probe(args.variant, args.n, count=args.count, exhaustive=args.exhaustive))
    # Optionally dump
    print("\nSummary:")
    for r in results:
        print(f"  {r['variant']} n={r['n']:>2} {r['label']:<14} collisions={r['collisions']}/{r['total']}")
