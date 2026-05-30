"""Single-Port Slide Lemma exploration (D77).

Toward proving Lemma C (the 2-port heart of the Fanout Barrier): no
gadget realizes R_T = EQ_2 = {00,11} on two disjoint ports P=(a,b),
Q=(c,d) with joint capacity on BOTH equality vectors.

The load-bearing local move is the SINGLE-PORT SLIDE.  Start from a
capacity witness sigma realizing 00 (all four port endpoints at
back-arc degree <= 1).  Flip P's bit by sliding endpoint a rightward
across its mate b (a sequence of adjacent transpositions).  The slide
either:
  * reaches a valid LFO with P flipped and Q unchanged -> realizes a
    MIXED vector (10), contradicting R_T = EQ_2; or
  * is BLOCKED -- at the first step that would add a back-arc, either a
    port/endpoint reaches back-degree 2 (saturation) or the new arc
    closes a cycle in the current loaded linear forest.

This module performs the slide step by step on every n=7 EQ_2
capacity gadget and classifies the first blocker, to ground the
exact-blocker classification the lemma needs.

Adjacent-transposition back-arc rule (move a rightward past neighbour v):
  * if T[a][v]  (a->v):  the {a,v} arc BECOMES a back-arc  (add: deg a,v +1)
  * if T[v][a]  (v->a):  the {a,v} arc STOPS being a back-arc (remove)
Only the swapped pair's arc changes; all other arcs are unaffected.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict, deque
from typing import Iterable, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fanout_barrier_checks import iter_gadget_instances  # noqa: E402
from port_relation_census import build_lfo_cache  # noqa: E402
from verify import verify  # noqa: E402


Matrix = list[list[int]]
EQ2 = frozenset({(0, 0), (1, 1)})


# ----------------------------------------------------------------------
# back-arc graph of an order
# ----------------------------------------------------------------------

def back_arc_edges(T: Matrix, order: Sequence[int]) -> list[tuple[int, int]]:
    n = len(T)
    pos = [0] * n
    for i, v in enumerate(order):
        pos[v] = i
    edges = []
    for u in range(n):
        for w in range(n):
            if T[u][w] and pos[u] > pos[w]:
                edges.append((u, w))
    return edges


def linear_forest_status(edges: Sequence[tuple[int, int]], n: int) -> dict:
    """Classify the undirected graph of `edges`: degrees, max-degree,
    acyclicity."""
    deg = [0] * n
    adj = defaultdict(list)
    for u, w in edges:
        deg[u] += 1
        deg[w] += 1
        adj[u].append(w)
        adj[w].append(u)
    max_deg = max(deg) if any(deg) else 0
    # acyclic via union-find on the undirected simple graph
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    has_cycle = False
    seen_pairs = set()
    for u, w in edges:
        key = (min(u, w), max(u, w))
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        ru, rw = find(u), find(w)
        if ru == rw:
            has_cycle = True
        else:
            parent[ru] = rw
    return {
        "deg": deg,
        "max_deg": max_deg,
        "has_cycle": has_cycle,
        "is_linear_forest": max_deg <= 2 and not has_cycle,
    }


# ----------------------------------------------------------------------
# single-port slide
# ----------------------------------------------------------------------

def slide_flip(T: Matrix, order: list[int], a: int, b: int) -> dict:
    """Slide endpoint a rightward across its mate b (assuming a is left of
    b in `order`), one adjacent transposition at a time.  Returns the
    first blocker classification, the crossed vertices, and the final
    order if it completes."""
    n = len(T)
    pos = {v: i for i, v in enumerate(order)}
    pa, pb = pos[a], pos[b]
    assert pa < pb, "call with a left of b"
    work = list(order)
    i = pa  # current position of a
    crossed = []
    # maintain back-arc degree incrementally would be ideal; for clarity
    # recompute the loaded graph after each transposition and classify.
    while i < pb:  # move a from position i to i+1, crossing work[i+1]
        v = work[i + 1]
        # tentatively swap
        work[i], work[i + 1] = work[i + 1], work[i]
        status = linear_forest_status(back_arc_edges(T, work), n)
        crossed.append(v)
        if not status["is_linear_forest"]:
            sat = [u for u in range(n) if status["deg"][u] >= 3]
            deg_block = status["max_deg"] >= 3
            cyc_block = status["has_cycle"]
            if deg_block and cyc_block:
                blocker = "degree_and_cycle"
            elif deg_block:
                blocker = "degree_saturation"
            else:
                blocker = "cycle"
            return {
                "completed": False,
                "blocker": blocker,
                "blocked_at_crossing": v,
                "saturated_vertices": sat,
                "crossed_so_far": list(crossed),
            }
        i += 1
        pb = {vv: ii for ii, vv in enumerate(work)}[b]  # b may have shifted
    return {
        "completed": True,
        "final_order": list(work),
        "crossed": crossed,
    }


def analyze_gadget(T: Matrix, ports, orient) -> dict:
    """For an EQ_2 gadget with capacity on 00, take each 00-capacity
    witness, flip each port, and record the blocker (or the mixed-vector
    contradiction if a flip ever completes to a valid LFO)."""
    n = len(T)
    (a, b), (c, d) = ports[0], ports[1]
    o = tuple(orient)
    cache = build_lfo_cache(T)
    # witnesses realizing 00 with all four port endpoints deg <= 1
    pv = [a, b, c, d]
    results = []
    completed_mixed = []
    for pos, deg in cache:
        bits = tuple((1 if pos[y] < pos[x] else 0) ^ oo
                     for (x, y), oo in zip(ports, o))
        if bits != (0, 0):
            continue
        if any(deg[v] >= 2 for v in pv):
            continue
        order = [0] * n
        for v in range(n):
            order[pos[v]] = v
        # flip port P = (a,b): slide whichever endpoint is left across mate
        for (x, y) in [ports[0], ports[1]]:
            px, py = pos[x], pos[y]
            left, right = (x, y) if px < py else (y, x)
            out = slide_flip(T, order, left, right)
            rec = {"port": (x, y), "left_moved": left}
            if out["completed"]:
                fin = out["final_order"]
                fpos = {v: i for i, v in enumerate(fin)}
                fbits = tuple((1 if fpos[yy] < fpos[xx] else 0) ^ oo
                              for (xx, yy), oo in zip(ports, o))
                valid = verify(T, fin)["is_linear_forest"]
                rec.update({"completed": True, "final_bits": fbits,
                            "final_valid_LFO": valid})
                if valid and fbits not in EQ2:
                    completed_mixed.append({"port": (x, y), "bits": fbits})
            else:
                rec.update({"completed": False, "blocker": out["blocker"],
                            "saturated": out["saturated_vertices"]})
            results.append(rec)
        break  # one witness suffices to illustrate
    return {
        "n": n, "ports": list(ports), "orientation": list(orient),
        "slide_results": results,
        "any_completed_mixed_valid": len(completed_mixed) > 0,
        "completed_mixed": completed_mixed[:3],
    }


def census_slide_blockers(n: int) -> dict:
    """Over all n EQ_2 gadgets with capacity on 00, classify the
    single-port-slide blockers."""
    blocker_counts = defaultdict(int)
    completed_mixed_valid = 0
    gadgets = 0
    examples = []
    for rec in iter_gadget_instances(n, 2):
        if rec["R"] != EQ2 or not rec["cap_zero"]:
            continue
        gadgets += 1
        out = analyze_gadget(rec["T"], rec["ports"], rec["orientation"])
        if out["any_completed_mixed_valid"]:
            completed_mixed_valid += 1
        for r in out["slide_results"]:
            if r["completed"]:
                blocker_counts[
                    "completed_valid_mixed" if r.get("final_valid_LFO")
                    and tuple(r["final_bits"]) not in EQ2
                    else "completed_other"] += 1
            else:
                blocker_counts[r["blocker"]] += 1
        if len(examples) < 3:
            examples.append(out)
    return {
        "n": n,
        "eq2_cap_on_00_gadgets": gadgets,
        "completed_mixed_valid_gadgets": completed_mixed_valid,
        "blocker_counts": dict(blocker_counts),
        "examples": examples,
    }


def both_values_saturation_profile(n: int) -> dict:
    """Recount EQ_2 capacity (correcting the one-value overclaim) and
    characterize the saturation mechanism for the both-values Lemma C.

    Returns, at (n, k=2):
      * eq2_instances, cap_on_00, cap_on_11, cap_on_both;
      * for every EQ_2 gadget with capacity on 00 but not 11, the
        minimum set of saturated port endpoints (by role a/b/c/d) over
        its 1-1 LFOs -- the saturation mechanism.
    """
    from fanout_barrier_checks import iter_gadget_instances
    from collections import Counter

    eq2 = cap0 = cap1 = capboth = 0
    sat_profiles: Counter = Counter()
    for rec in iter_gadget_instances(n, 2):
        if rec["R"] != frozenset({(0, 0), (1, 1)}):
            continue
        eq2 += 1
        c0, c1 = rec["cap_zero"], rec["cap_one"]
        cap0 += c0
        cap1 += c1
        if c0 and c1:
            capboth += 1
        if c0 and not c1:
            T = rec["T"]
            (a, b), (c, d) = rec["ports"]
            o = rec["orientation"]
            role = {a: "a", b: "b", c: "c", d: "d"}
            cache = build_lfo_cache(T)
            best = None
            for pos, deg in cache:
                bits = tuple((1 if pos[y] < pos[x] else 0) ^ oo
                             for (x, y), oo in zip(rec["ports"], o))
                if bits != (1, 1):
                    continue
                sat = tuple(v for v in (a, b, c, d) if deg[v] >= 2)
                if best is None or len(sat) < len(best):
                    best = sat
            roles = tuple(sorted(role[v] for v in best)) if best else ()
            sat_profiles[roles] += 1
    return {
        "n": n,
        "eq2_instances": eq2,
        "cap_on_00": cap0,
        "cap_on_11": cap1,
        "cap_on_both": capboth,
        "min_saturated_roles_on_11_for_cap00only": dict(sat_profiles),
    }


def flip_lemma_census(n: int) -> dict:
    """Test the flip lemma (step 4 of the Saturation sub-claim proof).

    For every (tournament, disjoint port pair P, Q) that admits a valid
    LFO realizing the both-back-arc value (1,1) with ALL FOUR port
    endpoints at degree exactly 1 (both port edges isolated K_2's),
    check:
      * mixed_realizable: is some mixed vector (1,0) or (0,1) in R_T?
        (the flip lemma's conclusion);
      * adjacent_reducible: is there such a both-isolated LFO with a,b
        OR c,d adjacent (the PROVED sub-case: swap the adjacent isolated
        pair, removing its port back-arc, to realize a mixed vector)?
    """
    from itertools import combinations, permutations
    from port_relation_census import all_tournaments
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    tested = 0
    mixed_realizable = 0
    adjacent_reducible = 0
    non_adjacent_examples = []
    for T in all_tournaments(n):
        lfos = []
        for P in permutations(range(n)):
            st = linear_forest_status(back_arc_edges(T, list(P)), n)
            if st["is_linear_forest"]:
                lfos.append((list(P), st["deg"]))
        for (a, b), (c, d) in combinations(pairs, 2):
            if len({a, b, c, d}) < 4:
                continue
            R = set()
            iso_orders = []
            for order, deg in lfos:
                pos = {v: i for i, v in enumerate(order)}
                bits = (1 if pos[b] < pos[a] else 0,
                        1 if pos[d] < pos[c] else 0)
                R.add(bits)
                if bits == (1, 1) and all(deg[v] == 1 for v in (a, b, c, d)):
                    iso_orders.append(pos)
            if not iso_orders:
                continue
            tested += 1
            if any(bv in R for bv in [(1, 0), (0, 1)]):
                mixed_realizable += 1
            if any(abs(pos[a] - pos[b]) == 1 or abs(pos[c] - pos[d]) == 1
                   for pos in iso_orders):
                adjacent_reducible += 1
            elif len(non_adjacent_examples) < 5:
                non_adjacent_examples.append(((a, b), (c, d)))
    return {
        "n": n,
        "both_isolated_configs": tested,
        "mixed_realizable": mixed_realizable,
        "flip_lemma_holds": mixed_realizable == tested,
        "adjacent_reducible": adjacent_reducible,
        "non_adjacent_count": tested - adjacent_reducible,
        "non_adjacent_examples": non_adjacent_examples,
    }


def single_vertex_relocation_coverage(n: int) -> dict:
    """For NON-ADJACENT both-isolated configs (no isolated LFO has an
    adjacent port pair), test whether a mixed vector is reachable by
    relocating a SINGLE vertex from a both-isolated order.  Reports the
    coverage; the shortfall is the residual needing multi-vertex moves."""
    from itertools import combinations, permutations
    from port_relation_census import all_tournaments
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]

    def bits(T, order, ports):
        pos = {v: i for i, v in enumerate(order)}
        (a, b), (c, d) = ports
        return (1 if pos[b] < pos[a] else 0, 1 if pos[d] < pos[c] else 0)

    non_adj = 0
    single_ok = 0
    for T in all_tournaments(n):
        lfos = []
        for P in permutations(range(n)):
            st = linear_forest_status(back_arc_edges(T, list(P)), n)
            if st["is_linear_forest"]:
                lfos.append((list(P), st["deg"]))
        for (a, b), (c, d) in combinations(pairs, 2):
            if len({a, b, c, d}) < 4:
                continue
            ports = ((a, b), (c, d))
            iso = []
            for order, deg in lfos:
                pos = {v: i for i, v in enumerate(order)}
                if bits(T, order, ports) == (1, 1) and all(
                        deg[v] == 1 for v in (a, b, c, d)):
                    iso.append((order, pos))
            if not iso:
                continue
            if any(abs(pos[a] - pos[b]) == 1 or abs(pos[c] - pos[d]) == 1
                   for _, pos in iso):
                continue  # adjacent-reducible (proved case)
            non_adj += 1
            found = False
            for order, _ in iso:
                for w in order:
                    rest = [v for v in order if v != w]
                    for p in range(n):
                        cand = rest[:p] + [w] + rest[p:]
                        if linear_forest_status(back_arc_edges(T, cand), n)["is_linear_forest"] \
                                and bits(T, cand, ports) in [(1, 0), (0, 1)]:
                            found = True
                            break
                    if found:
                        break
                if found:
                    break
            if found:
                single_ok += 1
    return {
        "n": n,
        "non_adjacent_configs": non_adj,
        "single_vertex_reaches_mixed": single_ok,
        "needs_multivertex": non_adj - single_ok,
    }


def three_cycle_characterization_check(n: int) -> dict:
    """Verify the 3-Cycle Characterization in the back-arc-status framing.

    Whenever a port {a,b}'s tournament arc is an ISOLATED degree-1
    back-arc in a valid LFO (the only back-arc at both a and b), every
    vertex w strictly between a and b forms a directed 3-cycle with
    {a,b}.  Returns the count of (between-vertex, port) instances and
    violations (should be 0).  Also checks the back-arc-framing flip
    lemma (both port arcs isolated back-arcs => a mixed arc-status is
    realizable)."""
    from itertools import combinations, permutations
    from port_relation_census import all_tournaments

    def arc(T, x, y):
        return (x, y) if T[x][y] else (y, x)

    def is_backarc(T, pos, x, y):
        u, v = arc(T, x, y)
        return pos[u] > pos[v]

    def is_3cycle(T, x, y, z):
        verts = (x, y, z)
        return {sum(1 for u in verts if u != w and T[w][u]) for w in verts} == {1}

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    total = 0
    threecyc = 0
    violations = []
    configs = 0
    flip_ok = 0
    for T in all_tournaments(n):
        lfos = []
        for P in permutations(range(n)):
            st = linear_forest_status(back_arc_edges(T, list(P)), n)
            if st["is_linear_forest"]:
                lfos.append((list(P), st["deg"]))
        for (a, b), (c, d) in combinations(pairs, 2):
            if len({a, b, c, d}) < 4:
                continue
            Rarc = set()
            iso = []
            for order, deg in lfos:
                pos = {v: i for i, v in enumerate(order)}
                sP = is_backarc(T, pos, a, b)
                sQ = is_backarc(T, pos, c, d)
                Rarc.add((int(sP), int(sQ)))
                if sP and sQ and all(deg[v] == 1 for v in (a, b, c, d)):
                    iso.append((order, pos))
            if not iso:
                continue
            configs += 1
            if (1, 0) in Rarc or (0, 1) in Rarc:
                flip_ok += 1
            order, pos = iso[0]
            for (x, y) in [(a, b), (c, d)]:
                lo, hi = sorted((pos[x], pos[y]))
                for k in range(lo + 1, hi):
                    w = order[k]
                    total += 1
                    if is_3cycle(T, x, y, w):
                        threecyc += 1
                    elif len(violations) < 5:
                        violations.append((x, y, w))
    return {
        "n": n,
        "isolated_configs": configs,
        "flip_mixed_arc_realizable": flip_ok,
        "flip_lemma_holds": flip_ok == configs,
        "between_vertex_instances": total,
        "form_3cycle": threecyc,
        "three_cycle_violations": len(violations),
        "three_cycle_holds": len(violations) == 0,
    }


def c_set_analysis(n: int) -> dict:
    """Analyze the 3-cycle-partner set C(P) in isolated configs.

      * C(P) == between-vertices of P (proved; isolation forces every
        3-cycle partner between the endpoints) -- count exact matches;
      * |C(P)| <= 4 is NECESSARY to flip P (charging) -- count holds;
      * |C(P)| <= 4 is NOT SUFFICIENT -- count ports with |C| <= 4 that
        are nonetheless not flippable.
    """
    from itertools import combinations, permutations
    from port_relation_census import all_tournaments

    def arc(T, x, y):
        return (x, y) if T[x][y] else (y, x)

    def is_backarc(T, pos, x, y):
        u, v = arc(T, x, y)
        return pos[u] > pos[v]

    def Cset(T, x, y):
        u, v = arc(T, x, y)
        return set(w for w in range(n)
                   if w not in (x, y) and T[v][w] and T[w][u])

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    c_eq_between = c_total = 0
    nec_holds = nec_total = 0
    suff_ok = suff_total = 0
    for T in all_tournaments(n):
        lfos = []
        for P in permutations(range(n)):
            st = linear_forest_status(back_arc_edges(T, list(P)), n)
            if st["is_linear_forest"]:
                lfos.append((list(P), st["deg"]))
        for (a, b), (c, d) in combinations(pairs, 2):
            if len({a, b, c, d}) < 4:
                continue
            Rarc = set()
            iso = None
            for o, deg in lfos:
                pos = {v: i for i, v in enumerate(o)}
                sP = is_backarc(T, pos, a, b)
                sQ = is_backarc(T, pos, c, d)
                Rarc.add((int(sP), int(sQ)))
                if sP and sQ and all(deg[v] == 1 for v in (a, b, c, d)) and iso is None:
                    iso = (o, pos)
            if iso is None:
                continue
            o, pos = iso
            for (x, y), flipval in [((a, b), (0, 1)), ((c, d), (1, 0))]:
                u, v = arc(T, x, y)
                lo, hi = sorted((pos[u], pos[v]))
                between = set(o[k] for k in range(lo + 1, hi))
                C = Cset(T, x, y)
                c_total += 1
                if C == between:
                    c_eq_between += 1
                flippable = flipval in Rarc
                nec_total += 1
                if (not flippable) or len(C) <= 4:
                    nec_holds += 1
                if len(C) <= 4:
                    suff_total += 1
                    if flippable:
                        suff_ok += 1
    return {
        "n": n,
        "C_equals_between": c_eq_between,
        "C_equals_between_total": c_total,
        "C_equals_between_holds": c_eq_between == c_total,
        "necessary_holds": nec_holds == nec_total,
        "sufficiency_rate": [suff_ok, suff_total],
        "sufficiency_holds": suff_ok == suff_total,
    }


def kernel_lemmas_check(n: int) -> dict:
    """Foundational checks for the minimal-counterexample KERNELIZATION
    route to D80 / Lemma C.

    Verifies (over all tournaments, iso-11 configs, back-arc framing):
      * FACT 1 (iso-11 preserved): deleting any non-port vertex from an
        iso-11 LFO leaves an iso-11 LFO of T-w.
      * FACT 2 (deletion only RELAXES): R_arc(T) subset R_arc(T-w) -- a
        deleted vertex can only ADD realizable port values.  (So a
        no-mixed counterexample can only be DESTROYED, never created, by
        deletion; minimal counterexample => every non-port vertex is
        essential = its deletion adds a mixed value.)
      * CLEAN-CUT INSERTABILITY: if w has a position in an LFO tau' of
        T-w with all in-neighbors before and out-neighbors after (a clean
        cut), inserting w there gives an LFO of T (w isolated, deg 0).
      * ESSENTIAL <=> ON-STRUCTURE (user step 2/3): an essential w
        (deletion adds a mixed value) always lies between some port's
        endpoints (w in C(P) cup C(Q)).  Reports any essential vertex
        that is OFF-structure (would refute the kernel localization).
    """
    from itertools import combinations, permutations
    from collections import Counter
    from port_relation_census import all_tournaments

    def arc(T, x, y):
        return (x, y) if T[x][y] else (y, x)

    def relation_and_iso11(Tm, m, P, Q):
        """R_arc (set of (sP,sQ)) and whether an iso-11 LFO exists."""
        (a, b), (c, d) = P, Q
        uP, vP = arc(Tm, a, b)
        uQ, vQ = arc(Tm, c, d)
        R = set()
        iso11 = False
        for perm in permutations(range(m)):
            st = linear_forest_status(back_arc_edges(Tm, list(perm)), m)
            if not st["is_linear_forest"]:
                continue
            pos = {v: i for i, v in enumerate(perm)}
            sP = 1 if pos[uP] > pos[vP] else 0
            sQ = 1 if pos[uQ] > pos[vQ] else 0
            R.add((sP, sQ))
            if sP and sQ and all(st["deg"][v] == 1 for v in (a, b, c, d)):
                iso11 = True
        return R, iso11

    def remap(T, keep):
        """Induced subtournament on sorted(keep), relabeled to 0..m-1."""
        ks = sorted(keep)
        idx = {v: i for i, v in enumerate(ks)}
        m = len(ks)
        Tm = [[0] * m for _ in range(m)]
        for i in ks:
            for j in ks:
                Tm[idx[i]][idx[j]] = T[i][j]
        return Tm, idx, m

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    mixed = {(0, 1), (1, 0)}
    fact1_viol = fact2_viol = cleancut_viol = 0
    essential_total = 0
    essential_offstructure = 0
    iso11_configs = 0
    for T in all_tournaments(n):
        # full-T LFOs once
        lfos = []
        for perm in permutations(range(n)):
            st = linear_forest_status(back_arc_edges(T, list(perm)), n)
            if st["is_linear_forest"]:
                lfos.append((list(perm), st["deg"]))
        for (a, b), (c, d) in combinations(pairs, 2):
            if len({a, b, c, d}) < 4:
                continue
            uP, vP = arc(T, a, b)
            uQ, vQ = arc(T, c, d)
            RT = set()
            iso_perm = None
            CP = CQ = None
            for perm, deg in lfos:
                pos = {v: i for i, v in enumerate(perm)}
                sP = 1 if pos[uP] > pos[vP] else 0
                sQ = 1 if pos[uQ] > pos[vQ] else 0
                RT.add((sP, sQ))
                if sP and sQ and all(deg[v] == 1 for v in (a, b, c, d)) \
                        and iso_perm is None:
                    iso_perm = perm
                    loP, hiP = sorted((pos[a], pos[b]))
                    loQ, hiQ = sorted((pos[c], pos[d]))
                    CP = {perm[i] for i in range(loP + 1, hiP)}
                    CQ = {perm[i] for i in range(loQ + 1, hiQ)}
            if iso_perm is None:
                continue
            iso11_configs += 1
            structure = CP | CQ
            for w in range(n):
                if w in (a, b, c, d):
                    continue
                keep = [v for v in range(n) if v != w]
                Tm, idx, m = remap(T, keep)
                Pm = (idx[a], idx[b])
                Qm = (idx[c], idx[d])
                Rm, iso11m = relation_and_iso11(Tm, m, Pm, Qm)
                # FACT 1: iso-11 preserved
                if not iso11m:
                    fact1_viol += 1
                # FACT 2: R_arc(T) subset R_arc(T-w) (map values directly;
                # back-arc status of a port is framing-invariant)
                if not RT.issubset(Rm):
                    fact2_viol += 1
                # essential: deletion adds a mixed value
                if (Rm & mixed) != (RT & mixed):
                    essential_total += 1
                    if w not in structure:
                        essential_offstructure += 1
                # CLEAN-CUT insertability check on T-w's mixed LFOs
                in_w = {v for v in keep if T[v][w]}
                out_w = {v for v in keep if T[w][v]}
                for perm in permutations(range(m)):
                    st = linear_forest_status(back_arc_edges(Tm, list(perm)), m)
                    if not st["is_linear_forest"]:
                        continue
                    posm = {v: i for i, v in enumerate(perm)}
                    uPm, vPm = arc(Tm, Pm[0], Pm[1])
                    uQm, vQm = arc(Tm, Qm[0], Qm[1])
                    sP = 1 if posm[uPm] > posm[vPm] else 0
                    sQ = 1 if posm[uQm] > posm[vQm] else 0
                    if (sP, sQ) not in mixed:
                        continue
                    # original-label order
                    ks = sorted(keep)
                    order_orig = [ks[v] for v in perm]
                    # clean cut: gap g with all in_w before, all out_w after
                    posorig = {v: i for i, v in enumerate(order_orig)}
                    has_cut = False
                    for g in range(m + 1):
                        before = set(order_orig[:g])
                        after = set(order_orig[g:])
                        if in_w <= before and out_w <= after:
                            has_cut = True
                            break
                    if has_cut:
                        # insert w at gap g in full T, verify LFO
                        ins = order_orig[:g] + [w] + order_orig[g:]
                        st2 = linear_forest_status(back_arc_edges(T, ins), n)
                        if not st2["is_linear_forest"]:
                            cleancut_viol += 1
                        break  # one witnessing mixed tau' suffices
    return {
        "n": n,
        "iso11_configs": iso11_configs,
        "fact1_iso11_preserved_violations": fact1_viol,
        "fact2_deletion_relaxes_violations": fact2_viol,
        "cleancut_insertability_violations": cleancut_viol,
        "essential_vertices_total": essential_total,
        "essential_offstructure": essential_offstructure,
        "essential_implies_onstructure": essential_offstructure == 0,
    }


def essential_locality_refutation(n: int) -> dict:
    """Red-team the Insertability/bound lemma (D81 open core): does any
    LOCAL invariant of a non-port vertex w characterize when w is
    DELETABLE (= not essential, i.e. deleting it does not add a mixed
    value)?  If a local sufficient condition for deletability existed, a
    large counterexample would have a deletable vertex and the kernel
    bound would follow.  This function tests the three natural candidate
    invariants over the iso-11 census (back-arc framing, essential as in
    `kernel_lemmas_check`: deletion changes R_arc cap {01,10}).

      * (C1) sigma-isolation: w has back-degree 0 in the iso-11 order
        sigma.  Candidate "sigma-isolated => deletable".
      * (C2) single-C membership: w lies in exactly one of C(P), C(Q)
        (an "outer rung", not the coupled core C(P) cap C(Q)).
        Candidate "single-C => deletable".
      * (C3) degree floor: w has min(indeg, outdeg) >= 2 in T.
        Candidate "essential => indeg>=2 and outdeg>=2" (so a low-degree
        vertex would be deletable).

    For each candidate we count essential vertices that VIOLATE it (an
    essential vertex satisfying the "deletable" hypothesis).  A nonzero
    count REFUTES that local criterion.  Also reports the essential
    sigma-back-degree distribution and role distribution (cP / cQ / both)
    as raw structure.

    IMPORTANT semantics caveat.  At n <= 7 every iso-11 config already
    realizes a mixed value (no counterexample exists), so "essential"
    here means "deletion unlocks the SECOND mixed value" -- whereas a
    minimal counterexample's essential means "unlocks the FIRST".  These
    refutations therefore strictly concern the n<=7 essentiality relation;
    they are strong heuristic (not proof) evidence that the
    counterexample-version is also non-local.
    """
    from itertools import combinations, permutations
    from collections import Counter
    from port_relation_census import all_tournaments

    def arc(T, x, y):
        return (x, y) if T[x][y] else (y, x)

    def lfos_of(Tm, m):
        out = []
        for p in permutations(range(m)):
            st = linear_forest_status(back_arc_edges(Tm, list(p)), m)
            if st["is_linear_forest"]:
                pos = {v: i for i, v in enumerate(p)}
                out.append((pos, st["deg"]))
        return out

    def Rarc(lf, Tm, P, Q):
        uP, vP = arc(Tm, *P)
        uQ, vQ = arc(Tm, *Q)
        R = set()
        for pos, _deg in lf:
            R.add((1 if pos[uP] > pos[vP] else 0,
                   1 if pos[uQ] > pos[vQ] else 0))
        return R

    def remap(T, keep):
        ks = sorted(keep)
        idx = {v: i for i, v in enumerate(ks)}
        m = len(ks)
        Tm = [[0] * m for _ in range(m)]
        for i in ks:
            for j in ks:
                Tm[idx[i]][idx[j]] = T[i][j]
        return Tm, idx, m

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    mixed = {(0, 1), (1, 0)}
    essential_total = 0
    c1_isolated_essential = 0     # sigma-isolated yet essential
    c2_singleC_essential = 0      # in exactly one of C(P),C(Q) yet essential
    c3_lowdeg_essential = 0       # min(indeg,outdeg) <= 1 yet essential
    sigdeg = Counter()
    roledist = Counter()
    lowdeg_profiles = Counter()
    for T in all_tournaments(n):
        full = []  # (order_list, pos, deg)
        for p in permutations(range(n)):
            st = linear_forest_status(back_arc_edges(T, list(p)), n)
            if st["is_linear_forest"]:
                pos = {v: i for i, v in enumerate(p)}
                full.append((list(p), pos, st["deg"]))
        for P, Q in combinations(pairs, 2):
            if len(set(P) | set(Q)) < 4:
                continue
            uP, vP = arc(T, *P)
            uQ, vQ = arc(T, *Q)
            iso = None
            for o, pos, deg in full:
                if (pos[uP] > pos[vP] and pos[uQ] > pos[vQ]
                        and all(deg[v] == 1 for v in (*P, *Q))):
                    iso = (o, pos, deg)
                    break
            if iso is None:
                continue
            o, pos, deg = iso
            loP, hiP = sorted((pos[P[0]], pos[P[1]]))
            loQ, hiQ = sorted((pos[Q[0]], pos[Q[1]]))
            CP = {o[i] for i in range(loP + 1, hiP)}
            CQ = {o[i] for i in range(loQ + 1, hiQ)}
            RTm = Rarc([(p, d) for _o, p, d in full], T, P, Q) & mixed
            for w in range(n):
                if w in (*P, *Q):
                    continue
                Tm, idx, m = remap(T, [v for v in range(n) if v != w])
                Rm = Rarc(lfos_of(Tm, m), Tm,
                          (idx[P[0]], idx[P[1]]), (idx[Q[0]], idx[Q[1]]))
                if (Rm & mixed) == RTm:
                    continue  # deletable (not essential)
                essential_total += 1
                sigdeg[deg[w]] += 1
                inCP, inCQ = w in CP, w in CQ
                roledist[("cP" if inCP else "")
                         + ("cQ" if inCQ else "") or "off"] += 1
                if deg[w] == 0:
                    c1_isolated_essential += 1
                if inCP ^ inCQ:
                    c2_singleC_essential += 1
                outd = sum(T[w][v] for v in range(n) if v != w)
                ind = sum(T[v][w] for v in range(n) if v != w)
                if min(ind, outd) <= 1:
                    c3_lowdeg_essential += 1
                    lowdeg_profiles[(ind, outd)] += 1
    return {
        "n": n,
        "essential_total": essential_total,
        "C1_sigma_isolated_essential": c1_isolated_essential,
        "C2_single_C_essential": c2_singleC_essential,
        "C3_lowdegree_essential": c3_lowdeg_essential,
        "C1_refuted": c1_isolated_essential > 0,
        "C2_refuted": c2_singleC_essential > 0,
        "C3_refuted": c3_lowdeg_essential > 0,
        "essential_sigma_backdeg_dist": dict(sigdeg),
        "essential_role_dist": dict(roledist),
        "C3_violator_degree_profiles": {str(k): v
                                        for k, v in lowdeg_profiles.items()},
    }


# ----------------------------------------------------------------------
# D84: explicit n=8 counterexamples REFUTING D80 (iso-11 => mixed value)
# ----------------------------------------------------------------------

# Two verified 8-vertex witnesses (found by the targeted rigid-core
# extension search /tmp + cross-checked by brute force and by an
# independent fresh linear-forest checker).  Both are iso-11 (a valid LFO
# realizes (1,1) with all four port endpoints at back-degree exactly 1)
# yet realize NO mixed value -- so "iso-11 => a mixed value" (D80) is
# FALSE at n=8.  The first has R_arc = {(1,1)}; the second is a full EQ_2
# gadget R_arc = {(0,0),(1,1)} that is iso-11 (capacity on the 11 value),
# refuting the §2b claim "no EQ_2 gadget has capacity on its 11 value"
# and the `eq2_with_iso11 = 0` census claim.
D80_COUNTEREXAMPLES_N8 = [
    {
        "T": [[0, 0, 0, 0, 1, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0, 1],
              [1, 1, 0, 0, 0, 1, 0, 0], [1, 1, 1, 0, 0, 0, 0, 1],
              [0, 1, 1, 1, 0, 1, 0, 0], [1, 1, 0, 1, 0, 0, 1, 0],
              [1, 1, 1, 1, 1, 0, 0, 1], [1, 0, 1, 0, 1, 1, 0, 0]],
        "P": (0, 4), "Q": (5, 6),
        "R_arc": [(1, 1)],
        "iso11_order": [6, 7, 4, 2, 5, 3, 1, 0],
    },
    {
        "T": [[0, 1, 0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 0, 0, 0, 1],
              [1, 0, 0, 0, 1, 0, 0, 0], [1, 0, 1, 0, 0, 1, 0, 1],
              [1, 1, 0, 1, 0, 0, 0, 0], [1, 1, 1, 0, 1, 0, 1, 1],
              [1, 1, 1, 1, 1, 0, 0, 0], [1, 0, 1, 0, 1, 0, 1, 0]],
        "P": (0, 1), "Q": (3, 5),
        "R_arc": [(0, 0), (1, 1)],
    },
]


def _independent_lfo_scan(T, P, Q):
    """Fully self-contained brute-force LFO scan (no project enumerator).

    Returns (n_lfos, R_arc, has_iso11) for ports P, Q.  A back-arc is an
    arc u->v with pos[u] > pos[v]; the order is an LFO iff those back-arcs
    form a linear forest (max undirected degree <= 2, acyclic).  iso-11 =
    a (1,1) LFO with all four port endpoints at back-degree exactly 1.
    """
    from itertools import permutations
    n = len(T)

    def arc(x, y):
        return (x, y) if T[x][y] else (y, x)

    uP, vP = arc(*P)
    uQ, vQ = arc(*Q)
    R = set()
    iso = False
    nlfo = 0
    for order in permutations(range(n)):
        pos = [0] * n
        for i, v in enumerate(order):
            pos[v] = i
        deg = [0] * n
        par = list(range(n))

        def find(a):
            while par[a] != a:
                par[a] = par[par[a]]
                a = par[a]
            return a

        ok = True
        for u in range(n):
            for v in range(n):
                if T[u][v] and pos[u] > pos[v]:
                    deg[u] += 1
                    deg[v] += 1
                    if deg[u] > 2 or deg[v] > 2:
                        ok = False
                        break
                    ru, rv = find(u), find(v)
                    if ru == rv:
                        ok = False
                        break
                    par[ru] = rv
            if not ok:
                break
        if not ok:
            continue
        nlfo += 1
        sP = 1 if pos[uP] > pos[vP] else 0
        sQ = 1 if pos[uQ] > pos[vQ] else 0
        R.add((sP, sQ))
        if sP and sQ and all(deg[v] == 1 for v in (*P, *Q)):
            iso = True
    return nlfo, frozenset(R), iso


def verify_d80_counterexamples() -> dict:
    """Independently re-verify every stored n=8 D80 counterexample.

    For each witness: confirm it is a valid tournament, recompute R_arc by
    a self-contained brute-force LFO scan, confirm an iso-11 LFO exists,
    and confirm R_arc has NO mixed value (so D80 fails)."""
    out = []
    for w in D80_COUNTEREXAMPLES_N8:
        T, P, Q = w["T"], w["P"], w["Q"]
        n = len(T)
        valid = (all(T[i][i] == 0 for i in range(n))
                 and all((T[i][j] == 1) != (T[j][i] == 1)
                         for i in range(n) for j in range(n) if i != j))
        nlfo, R, iso = _independent_lfo_scan(T, P, Q)
        mixed = R & {(0, 1), (1, 0)}
        out.append({
            "P": P, "Q": Q, "valid_tournament": valid, "n_lfos": nlfo,
            "R_arc": sorted(R), "has_iso11": iso,
            "no_mixed": not mixed,
            "is_d80_counterexample": valid and iso and not mixed,
            "matches_stored_R_arc": sorted(R) == [tuple(x) for x
                                                  in w["R_arc"]],
        })
    return {
        "n": 8,
        "witnesses": out,
        "all_are_counterexamples": all(o["is_d80_counterexample"]
                                       for o in out),
        "D80_refuted_at_n8": all(o["is_d80_counterexample"] for o in out),
    }


def eq2_capacity_census(n: int) -> dict:
    """THE decisive capacity-form Fanout-Barrier census (D85).

    After D84 killed D80 ("iso-11 => mixed"), the only question left for
    fanout is the capacity-form both-values Lemma C:

        Is there an EQ_2 gadget (R_arc = {(0,0),(1,1)} on two disjoint
        ports, back-arc framing) with JOINT CAPACITY on BOTH equality
        values -- i.e. some LFO realizes (0,0) with all four port
        endpoints at back-degree <= 1, AND some LFO realizes (1,1)
        likewise?  That is a FAITHFUL EQ_2 SPLITTER.

    This enumerates over tournament iso-reps (back-arc framing, the
    unambiguous one of D80 §2d -- NOT the orientation-XOR bit framing that
    double-counted in D78 §1), every disjoint 2-port tuple, finds the EQ_2
    gadgets, and counts capacity on 00, on 11, and on both.  Uses the
    pruned LFO enumerator (`enum_lfos_deg`), feasible at n = 8.

    cap_both > 0  => the Fanout Barrier is REFUTED (a faithful splitter
                     exists); next target is composing it with the D72
                     2-in-3 clause gadget.
    cap_both = 0  => the barrier survives its first real n = 8 test.
    """
    from itertools import combinations
    from fanout_barrier_checks import reps as _reps, disjoint as _disjoint
    from two_aux_eq3_search import enum_lfos_deg

    def arc(T, x, y):
        return (x, y) if T[x][y] else (y, x)

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    pts = [(p, q) for p, q in combinations(pairs, 2)
           if _disjoint((p, q))]
    EQ2 = frozenset({(0, 0), (1, 1)})

    eq2 = cap00 = cap11 = cap_both = 0
    splitter_examples = []
    for T in _reps(n):
        lfos = enum_lfos_deg(T)
        if not lfos:
            continue
        for P, Q in pts:
            a, b = P
            c, d = Q
            uP, vP = arc(T, *P)
            uQ, vQ = arc(T, *Q)
            R = set()
            cap = {(0, 0): False, (1, 1): False}
            for pos, deg in lfos:
                sP = 1 if pos[uP] > pos[vP] else 0
                sQ = 1 if pos[uQ] > pos[vQ] else 0
                R.add((sP, sQ))
                if (sP, sQ) in EQ2 and deg[a] <= 1 and deg[b] <= 1 \
                        and deg[c] <= 1 and deg[d] <= 1:
                    cap[(sP, sQ)] = True
            if frozenset(R) != EQ2:
                continue
            eq2 += 1
            if cap[(0, 0)]:
                cap00 += 1
            if cap[(1, 1)]:
                cap11 += 1
            if cap[(0, 0)] and cap[(1, 1)]:
                cap_both += 1
                if len(splitter_examples) < 3:
                    splitter_examples.append({
                        "T": [row[:] for row in T],
                        "ports": [P, Q],
                    })
    return {
        "n": n,
        "framing": "back-arc-status (unambiguous)",
        "eq2_gadgets": eq2,
        "cap_on_00": cap00,
        "cap_on_11": cap11,
        "cap_on_both": cap_both,
        "faithful_splitter_exists": cap_both > 0,
        "fanout_barrier_refuted": cap_both > 0,
        "splitter_examples": splitter_examples,
    }


def eq2_capacity_profile(n: int) -> dict:
    """Mine the capacity non-co-occurrence (D86): why do cap-00 and cap-11
    never co-occur in an EQ_2 gadget (D85: cap_both = 0 at n <= 8)?

    Classifies every EQ_2 gadget (R_arc = {00,11}, back-arc framing) into
    cap00_only / cap11_only / cap_both / no_capacity and tests whether any
    PORT-LOCAL invariant separates cap00 from cap11.  Records, per cap-11
    gadget, its port-local signature:
      * port-endpoint score order (out-degrees of uP,vP,uQ,vQ);
      * the 4-vertex port sub-tournament score sequence (quad-type);
      * the vP--uQ cross-arc direction;
      * the min saturated endpoint set on the 00 value.
    Then counts how many cap00 gadgets SHARE the cap-11 port-local
    signature (quad-type + vP->uQ).  A nonzero count means NO port-local
    separator exists -- the capacity difference is GLOBAL (consistent with
    the non-locality of D82/D83).

    NB cap-11 = iso-11 exactly: capacity on the both-back-arc value forces
    both port arcs to be isolated K_2's (each endpoint already has degree
    1 from its port arc; capacity caps it at 1), which is iso-11; and
    iso-11 trivially gives capacity on 11.  So this profile is also the
    iso-11-EQ_2 profile.
    """
    from itertools import combinations
    from collections import Counter
    from fanout_barrier_checks import reps as _reps, disjoint as _disjoint
    from two_aux_eq3_search import enum_lfos_deg

    def arc(T, x, y):
        return (x, y) if T[x][y] else (y, x)

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    pts = [(p, q) for p, q in combinations(pairs, 2) if _disjoint((p, q))]
    EQ2 = frozenset({(0, 0), (1, 1)})

    classes = Counter()
    cap11_scoreorder = Counter()
    cap11_quadtype = Counter()
    cap11_vpuq = Counter()
    cap11_minsat00 = Counter()
    cap00_quadtype = Counter()
    cap00_scoreorder = Counter()
    for T in _reps(n):
        lfos = enum_lfos_deg(T)
        if not lfos:
            continue
        for P, Q in pts:
            a, b = P
            c, d = Q
            uP, vP = arc(T, *P)
            uQ, vQ = arc(T, *Q)
            R = set()
            cap = {(0, 0): False, (1, 1): False}
            min00 = None
            roles = {uP: 'uP', vP: 'vP', uQ: 'uQ', vQ: 'vQ'}
            for pos, deg in lfos:
                sP = 1 if pos[uP] > pos[vP] else 0
                sQ = 1 if pos[uQ] > pos[vQ] else 0
                R.add((sP, sQ))
                if (sP, sQ) in EQ2 and deg[a] <= 1 and deg[b] <= 1 \
                        and deg[c] <= 1 and deg[d] <= 1:
                    cap[(sP, sQ)] = True
                if (sP, sQ) == (0, 0):
                    sat = frozenset(roles[x] for x in (uP, vP, uQ, vQ)
                                    if deg[x] >= 2)
                    if min00 is None or len(sat) < len(min00):
                        min00 = sat
            if frozenset(R) != EQ2:
                continue
            cl = ('cap_both' if cap[(0, 0)] and cap[(1, 1)]
                  else 'cap00_only' if cap[(0, 0)]
                  else 'cap11_only' if cap[(1, 1)] else 'no_capacity')
            classes[cl] += 1
            s = {r: sum(T[v]) for v, r in roles.items()}
            order = tuple(sorted(('uP', 'vP', 'uQ', 'vQ'), key=lambda r: s[r]))
            quad = tuple(sorted(sum(1 for y in (uP, vP, uQ, vQ)
                                    if y != x and T[x][y])
                                for x in (uP, vP, uQ, vQ)))
            vpuq = 'vP->uQ' if T[vP][uQ] else 'uQ->vP'
            if cl == 'cap11_only':
                cap11_scoreorder[order] += 1
                cap11_quadtype[quad] += 1
                cap11_vpuq[vpuq] += 1
                cap11_minsat00[tuple(sorted(min00)) if min00 is not None
                               else None] += 1
            elif cl == 'cap00_only':
                cap00_quadtype[quad] += 1
                cap00_scoreorder[order] += 1

    # port-local separator test: do cap00 gadgets share cap11's signature?
    cap11_quads = set(cap11_quadtype)
    cap11_orders = set(cap11_scoreorder)
    cap00_sharing_quad = sum(v for k, v in cap00_quadtype.items()
                             if k in cap11_quads)
    cap00_sharing_order = sum(v for k, v in cap00_scoreorder.items()
                              if k in cap11_orders)
    return {
        "n": n,
        "classes": dict(classes),
        "cap11_port_score_order": {str(k): v
                                   for k, v in cap11_scoreorder.items()},
        "cap11_quad_type": {str(k): v for k, v in cap11_quadtype.items()},
        "cap11_vP_uQ_arc": dict(cap11_vpuq),
        "cap11_minsat_on_00": {str(k): v for k, v in cap11_minsat00.items()},
        "cap00_sharing_cap11_quadtype": cap00_sharing_quad,
        "cap00_sharing_cap11_scoreorder": cap00_sharing_order,
        "port_local_separator_exists": (cap00_sharing_quad == 0
                                        and cap00_sharing_order == 0),
    }


def cap00_3cycle_bound(n: int) -> dict:
    """The cap-00 LEVER (D87): cap-00 ⟹ |C(P)| ≤ 2 and |C(Q)| ≤ 2, where
    C(P) = {w : v_P→w and w→u_P} are the 3-cycle partners of P's arc
    (= the between-vertices of P in any isolated order, by the 3-Cycle
    Characterization).

    Proof (charging in the cap-00 witness σ₀).  In σ₀ both port arcs are
    forward (u_P before v_P) and each endpoint has back-degree ≤ 1.  For
    w ∈ C(P): if w is before v_P then the arc v_P→w is a back-arc at v_P;
    if w is after v_P (hence after u_P) then w→u_P is a back-arc at u_P.
    So #{w∈C(P): before v_P} ≤ deg(v_P) ≤ 1 and #{after v_P} ≤ deg(u_P)
    ≤ 1, giving |C(P)| ≤ 2.  Symmetric for Q.

    Also records the OBSTRUCTION to finishing with this bound alone: a
    crossing iso-11 EQ_2 gadget with |C(P)| = |C(Q)| = 2 and NO mixed
    value (so it satisfies the cap-00 *conclusion* |C|≤2 yet is not
    cap-00) — proving |C|≤2 is necessary but NOT sufficient to force a
    mixed value.  And the iso-11 EQ_2 geometry (all crossing at n≤8, so
    the clean nested-case finish is vacuous here).
    """
    from itertools import combinations
    from collections import Counter
    from fanout_barrier_checks import reps as _reps, disjoint as _disjoint
    from two_aux_eq3_search import enum_lfos_deg

    def arc(T, x, y):
        return (x, y) if T[x][y] else (y, x)

    def cset(T, u, v):
        return [w for w in range(len(T))
                if w not in (u, v) and T[v][w] and T[w][u]]

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    pts = [(p, q) for p, q in combinations(pairs, 2) if _disjoint((p, q))]
    lever_violations = 0
    cap00_Csize = Counter()
    iso11_geom = Counter()
    iso11_Csize = Counter()
    insufficiency_witness = None
    for T in _reps(n):
        lfos = enum_lfos_deg(T)
        if not lfos:
            continue
        for P, Q in pts:
            a, b = P
            c, d = Q
            uP, vP = arc(T, *P)
            uQ, vQ = arc(T, *Q)
            R = set()
            cap00 = False
            iso_pos = None
            for pos, deg in lfos:
                sP = 1 if pos[uP] > pos[vP] else 0
                sQ = 1 if pos[uQ] > pos[vQ] else 0
                R.add((sP, sQ))
                if (sP, sQ) == (0, 0) and deg[a] <= 1 and deg[b] <= 1 \
                        and deg[c] <= 1 and deg[d] <= 1:
                    cap00 = True
                if (sP, sQ) == (1, 1) and deg[a] == 1 and deg[b] == 1 \
                        and deg[c] == 1 and deg[d] == 1 and iso_pos is None:
                    iso_pos = pos
            if frozenset(R) != frozenset({(0, 0), (1, 1)}):
                continue
            CP, CQ = cset(T, uP, vP), cset(T, uQ, vQ)
            if cap00:
                cap00_Csize[(len(CP), len(CQ))] += 1
                if len(CP) > 2 or len(CQ) > 2:
                    lever_violations += 1
            if iso_pos is not None:
                pos = iso_pos
                loP, hiP = sorted((pos[a], pos[b]))
                loQ, hiQ = sorted((pos[c], pos[d]))
                if hiP < loQ or hiQ < loP:
                    geo = 'disjoint'
                elif (loP < loQ and hiQ < hiP) or (loQ < loP and hiP < hiQ):
                    geo = 'nested'
                else:
                    geo = 'crossing'
                iso11_geom[geo] += 1
                iso11_Csize[(len(CP), len(CQ))] += 1
                if len(CP) <= 2 and len(CQ) <= 2 \
                        and insufficiency_witness is None:
                    insufficiency_witness = {"P": P, "Q": Q,
                                             "C_sizes": (len(CP), len(CQ)),
                                             "geometry": geo}
    return {
        "n": n,
        "lever_cap00_implies_Cle2_violations": lever_violations,
        "lever_holds": lever_violations == 0,
        "cap00_C_size_dist": {str(k): v for k, v in cap00_Csize.items()},
        "iso11_eq2_geometry": dict(iso11_geom),
        "iso11_eq2_C_size_dist": {str(k): v for k, v in iso11_Csize.items()},
        "Cle2_insufficiency_witness": insufficiency_witness,
    }


def eq2_outdeg_separator(n: int) -> dict:
    """The OUT-DEGREE SEPARATOR (D88), the global invariant the
    Crossing-Splice team surfaced (and the decision lead corrected).

    On the port-local-signature-matched EQ_2 family (4-vertex port-quad
    score-seq (1,1,2,2) AND cross-arc vP->uQ), with out-degrees taken in
    the full tournament T:
      (i)  iso-11  ==>  out(uP) < out(vP) AND out(uQ) < out(vQ)  [sign (<,<)];
      (ii) cap-00  ==>  NEITHER out(uP) < out(vP) NOR out(uQ) < out(vQ)
           (NOT necessarily strict (>,>) -- ties occur).
    (i) and (ii) are mutually exclusive, so cap_both = 0 on the matched
    family.  Moreover every iso-11 EQ_2 gadget is signature-matched, so
    the separator covers all iso-11 gadgets.  This RE-DERIVES the
    capacity-form barrier from a global out-degree invariant (verified
    n <= 8); it is NOT proved (empirical), and the residual difficulty is
    a single |C(P)|=|C(Q)|=2 crossing gadget at n = 8.

    The Crossing Splice Lemma itself is REFUTED as a local reorder: the
    uniform flip move (slide a port's far endpoint across its own C-set)
    always drives a C-vertex to back-degree 3 (excess +1, never a cycle).
    """
    from itertools import combinations
    from collections import Counter
    from fanout_barrier_checks import reps as _reps, disjoint as _disjoint
    from two_aux_eq3_search import enum_lfos_deg

    def arc(T, x, y):
        return (x, y) if T[x][y] else (y, x)

    def sgn(a, b):
        return '<' if a < b else '>' if a > b else '='

    def cset(T, u, v):
        return [w for w in range(len(T))
                if w not in (u, v) and T[v][w] and T[w][u]]

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    pts = [(p, q) for p, q in combinations(pairs, 2) if _disjoint((p, q))]
    EQ2 = frozenset({(0, 0), (1, 1)})
    iso_total = iso_matched = 0
    iso_signs = Counter()
    iso_unmatched = Counter()
    cap_matched_signs = Counter()
    both = 0
    crux = []
    for T in _reps(n):
        lfos = enum_lfos_deg(T)
        if not lfos:
            continue
        out = [sum(T[v]) for v in range(n)]
        for P, Q in pts:
            a, b = P
            c, d = Q
            uP, vP = arc(T, *P)
            uQ, vQ = arc(T, *Q)
            R = set()
            cap00 = iso11 = False
            for pos, deg in lfos:
                sP = 1 if pos[uP] > pos[vP] else 0
                sQ = 1 if pos[uQ] > pos[vQ] else 0
                R.add((sP, sQ))
                if (sP, sQ) == (0, 0) and deg[a] <= 1 and deg[b] <= 1 \
                        and deg[c] <= 1 and deg[d] <= 1:
                    cap00 = True
                if (sP, sQ) == (1, 1) and deg[a] == 1 and deg[b] == 1 \
                        and deg[c] == 1 and deg[d] == 1:
                    iso11 = True
            if frozenset(R) != EQ2:
                continue
            quad = tuple(sorted(sum(1 for y in (uP, vP, uQ, vQ)
                                    if y != x and T[x][y])
                                for x in (uP, vP, uQ, vQ)))
            matched = (quad == (1, 1, 2, 2) and T[vP][uQ] == 1)
            sp = (sgn(out[uP], out[vP]), sgn(out[uQ], out[vQ]))
            if iso11:
                iso_total += 1
                iso_signs[sp] += 1
                if matched:
                    iso_matched += 1
                else:
                    iso_unmatched[(quad, 'vP->uQ' if T[vP][uQ] else 'uQ->vP')] += 1
                if len(cset(T, uP, vP)) == 2 and len(cset(T, uQ, vQ)) == 2:
                    crux.append((P, Q))
            if cap00 and matched:
                cap_matched_signs[sp] += 1
            if iso11 and cap00:
                both += 1
    cap_total = sum(cap_matched_signs.values())
    cap_no_less = sum(v for k, v in cap_matched_signs.items() if '<' not in k)
    return {
        "n": n,
        "iso11_eq2_total": iso_total,
        "iso11_all_signature_matched": iso_unmatched == Counter(),
        "iso11_sign_patterns": {str(k): v for k, v in iso_signs.items()},
        "iso11_all_less_less": set(iso_signs) == {('<', '<')} and iso_total > 0,
        "cap00_matched_sign_patterns": {str(k): v
                                        for k, v in cap_matched_signs.items()},
        "cap00_matched_no_less": cap_no_less == cap_total and cap_total > 0,
        "cap00_matched_strict_gg": cap_matched_signs.get(('>', '>'), 0),
        "cap_both": both,
        "crux_iso11_C22_gadgets": crux,
        "separator_holds": (set(iso_signs) == {('<', '<')}
                            and cap_no_less == cap_total
                            and both == 0 and iso_unmatched == Counter()),
    }


def rung_compression_refutation(n: int) -> dict:
    """Red-team the RUNG-COMPRESSION LEMMA (D83), the global-coupled-ladder
    replacement for local deletion (D82).

    Setup.  In an iso-11 order σ the non-port on-structure vertices are the
    *rungs* (in C(P) ∪ C(Q)).  Their back-arc graph in σ is a linear forest
    (paths / isolated vertices) — the ladder.  The compression lemma hopes:
    contracting between two same-(role, parity) rungs preserves iso-11 AND
    absence of mixed values, so a long ladder shortens to an O(1) kernel.

    This function measures, over iso-rep iso-11 configs (back-arc framing),
    whether any natural same-type contraction PRESERVES the realized mixed
    set R_arc ∩ {01,10} (the proxy for "preserves absence of mixed", since
    no genuine no-mixed config exists at n ≤ 7):

      * rung-forest shapes (numrungs, sorted back-arc degrees);
      * TWIN pairs (two rungs with identical arcs to all four port
        endpoints) and how many are BOTH essential — the memory mechanism;
      * remove MIDDLE / LEAF of a 3-rung back-arc path: applicable vs
        mixed-preserved (the literal contraction);
      * remove an ISOLATED rung;
      * RIGID cores: distribution of (#rungs, #rungs whose deletion
        preserves the mixed set), and the count of ALL-essential configs
        (no safe single deletion), reported for all configs and for the
        counterexample-like SINGLE-MIXED configs (|R_arc ∩ mixed| = 1).

    A nonzero "not-preserved" count for a contraction REFUTES that
    contraction; an all-essential (rigid) config with k rungs shows single
    deletion cannot shorten a k-rung core.  Same n ≤ 7 essentiality caveat
    as D82 applies (see docstring of `essential_locality_refutation`).
    """
    from itertools import combinations
    from collections import Counter
    from fanout_barrier_checks import reps as _reps

    def arc(T, x, y):
        return (x, y) if T[x][y] else (y, x)

    def mixed_set(cache, T, P, Q):
        uP, vP = arc(T, *P)
        uQ, vQ = arc(T, *Q)
        R = set()
        for pos, _deg in cache:
            R.add((1 if pos[uP] > pos[vP] else 0,
                   1 if pos[uQ] > pos[vQ] else 0))
        return frozenset(R & {(0, 1), (1, 0)})

    def induced(T, keep):
        ks = sorted(keep)
        idx = {v: i for i, v in enumerate(ks)}
        m = len(ks)
        Tm = [[0] * m for _ in range(m)]
        for i in ks:
            for j in ks:
                Tm[idx[i]][idx[j]] = T[i][j]
        return Tm, idx

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    pts = [(a, b, c, d) for (a, b), (c, d) in combinations(pairs, 2)
           if len({a, b, c, d}) == 4]
    shapes = Counter()
    twin_total = twin_both_ess = 0
    rm_mid = [0, 0]
    rm_mid_samerole = [0, 0]
    rm_leaf = [0, 0]
    rm_iso = [0, 0]
    safe_dist = Counter()
    rigid_by_rungs = Counter()
    total_by_rungs = Counter()
    rigid_single = Counter()
    total_single = Counter()
    for T in _reps(n):
        cache = build_lfo_cache(T)
        if not cache:
            continue
        delc = {}

        def getdel(w):
            if w not in delc:
                Tm, idx = induced(T, [v for v in range(n) if v != w])
                delc[w] = (Tm, idx, build_lfo_cache(Tm))
            return delc[w]

        for (a, b, c, d) in pts:
            P, Q = (a, b), (c, d)
            uP, vP = arc(T, *P)
            uQ, vQ = arc(T, *Q)
            iso = None
            for pos, deg in cache:
                if (pos[uP] > pos[vP] and pos[uQ] > pos[vQ]
                        and all(deg[v] == 1 for v in (a, b, c, d))):
                    iso = (pos, deg)
                    break
            if iso is None:
                continue
            pos, deg = iso
            order = [None] * n
            for v in range(n):
                order[pos[v]] = v
            loP, hiP = sorted((pos[a], pos[b]))
            loQ, hiQ = sorted((pos[c], pos[d]))
            CP = {order[i] for i in range(loP + 1, hiP)}
            CQ = {order[i] for i in range(loQ + 1, hiQ)}
            rungs = [v for v in range(n)
                     if v not in (a, b, c, d) and (v in CP or v in CQ)]
            if not rungs:
                continue
            RTm = mixed_set(cache, T, P, Q)

            def role(w):
                return ('P' if w in CP else '') + ('Q' if w in CQ else '')

            def preserves(w):
                Tm, idx, cm = getdel(w)
                return mixed_set(cm, Tm, (idx[a], idx[b]),
                                 (idx[c], idx[d])) == RTm

            radj = {w: set() for w in rungs}
            for x, y in combinations(rungs, 2):
                u, v = arc(T, x, y)
                if pos[u] > pos[v]:
                    radj[x].add(y)
                    radj[y].add(x)
            shapes[(len(rungs),
                    tuple(sorted(len(radj[w]) for w in rungs)))] += 1
            for x, y in combinations(rungs, 2):
                if all(T[x][p] == T[y][p] for p in (uP, vP, uQ, vQ)):
                    twin_total += 1
                    if (not preserves(x)) and (not preserves(y)):
                        twin_both_ess += 1
            if len(rungs) == 3 and \
                    sorted(len(radj[w]) for w in rungs) == [1, 1, 2]:
                mid = next(w for w in rungs if len(radj[w]) == 2)
                ends = [w for w in rungs if len(radj[w]) == 1]
                pr = preserves(mid)
                rm_mid[0] += 1
                rm_mid[1] += int(pr)
                if role(ends[0]) == role(ends[1]) == role(mid):
                    rm_mid_samerole[0] += 1
                    rm_mid_samerole[1] += int(pr)
                for lf in ends:
                    rm_leaf[0] += 1
                    rm_leaf[1] += int(preserves(lf))
            for w in rungs:
                if len(radj[w]) == 0:
                    rm_iso[0] += 1
                    rm_iso[1] += int(preserves(w))
            nsafe = sum(1 for w in rungs if preserves(w))
            k = len(rungs)
            safe_dist[(k, nsafe)] += 1
            total_by_rungs[k] += 1
            if nsafe == 0:
                rigid_by_rungs[k] += 1
            if len(RTm) == 1:
                total_single[k] += 1
                if nsafe == 0:
                    rigid_single[k] += 1
    return {
        "n": n,
        "rung_forest_shapes": {str(k): v for k, v in shapes.items()},
        "twin_pairs_total": twin_total,
        "twin_pairs_both_essential": twin_both_ess,
        "remove_middle_3path": {"applicable": rm_mid[0],
                                "mixed_preserved": rm_mid[1]},
        "remove_middle_3path_samerole": {"applicable": rm_mid_samerole[0],
                                         "mixed_preserved": rm_mid_samerole[1]},
        "remove_leaf_3path": {"applicable": rm_leaf[0],
                              "mixed_preserved": rm_leaf[1]},
        "remove_isolated_rung": {"applicable": rm_iso[0],
                                 "mixed_preserved": rm_iso[1]},
        "safe_rung_dist": {str(k): v for k, v in sorted(safe_dist.items())},
        "rigid_configs_by_rungs": dict(rigid_by_rungs),
        "total_configs_by_rungs": dict(total_by_rungs),
        "rigid_single_mixed_by_rungs": dict(rigid_single),
        "total_single_mixed_by_rungs": dict(total_single),
        "compression_lemma_refuted": (
            rm_mid[1] < rm_mid[0] or rm_leaf[1] < rm_leaf[0]
            or twin_both_ess > 0),
    }


def two_port_coupled_flip(n: int) -> dict:
    """Two-port coupled flip analysis (both-values framing).

    Over isolated configs that realize BOTH the both-back-arc value
    (11, both ports isolated K_2) AND the both-forward value (00):
      * (flipP, flipQ) distribution -- (False,False) should never occur
        (the two-port coupled flip theorem: at least one port flippable);
      * obstruction type for nonflippable ports: 'degree' (some vertex
        reaches back-degree 3 in every P-forward/Q-back order) vs
        'cycle' (a cycle forms but degrees stay <= 2).
    """
    from itertools import combinations, permutations
    from collections import Counter
    from port_relation_census import all_tournaments

    def arc(T, x, y):
        return (x, y) if T[x][y] else (y, x)

    def is_ba(T, pos, x, y):
        u, v = arc(T, x, y)
        return pos[u] > pos[v]

    def obstruction(T, ports, tv):
        (a, b), (c, d) = ports
        best = None
        for P in permutations(range(n)):
            pos = {v: i for i, v in enumerate(P)}
            if (int(is_ba(T, pos, a, b)), int(is_ba(T, pos, c, d))) != tv:
                continue
            edges = back_arc_edges(T, list(P))
            deg = [0] * n
            for u, w in edges:
                deg[u] += 1
                deg[w] += 1
            st = linear_forest_status(edges, n)
            score = (0 if st["is_linear_forest"] else 1,
                     sum(1 for v in range(n) if deg[v] >= 3),
                     int(st["has_cycle"]))
            if best is None or score < best:
                best = score
        return best

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    flipdist = Counter()
    obstype = Counter()
    configs = 0
    for T in all_tournaments(n):
        lfos = []
        for P in permutations(range(n)):
            st = linear_forest_status(back_arc_edges(T, list(P)), n)
            if st["is_linear_forest"]:
                lfos.append((list(P), st["deg"]))
        for (a, b), (c, d) in combinations(pairs, 2):
            if len({a, b, c, d}) < 4:
                continue
            ports = ((a, b), (c, d))
            Rarc = set()
            iso = False
            for o, deg in lfos:
                pos = {v: i for i, v in enumerate(o)}
                sP = is_ba(T, pos, a, b)
                sQ = is_ba(T, pos, c, d)
                Rarc.add((int(sP), int(sQ)))
                if sP and sQ and all(deg[v] == 1 for v in (a, b, c, d)):
                    iso = True
            if not iso or (0, 0) not in Rarc:
                continue
            configs += 1
            fP = (0, 1) in Rarc
            fQ = (1, 0) in Rarc
            flipdist[(fP, fQ)] += 1
            if not fP:
                ob = obstruction(T, ports, (0, 1))
                obstype["degree" if ob[1] > 0 else "cycle" if ob[2] else "?"] += 1
            if not fQ:
                ob = obstruction(T, ports, (1, 0))
                obstype["degree" if ob[1] > 0 else "cycle" if ob[2] else "?"] += 1
    return {
        "n": n,
        "isolated_11_and_00_configs": configs,
        "flip_distribution": {str(k): v for k, v in flipdist.items()},
        "both_nonflippable": flipdist[(False, False)],
        "coupled_flip_theorem_holds": flipdist[(False, False)] == 0,
        "nonflippable_obstruction_types": dict(obstype),
    }


def coupling_structure(n: int, verbose_examples: int = 0) -> dict:
    """Characterize the blocking-cycle structure for nonflippable ports
    in isolated-11 + 00 configs, and test whether the 00 hypothesis is
    essential.

    For a nonflippable port P (no P-forward/Q-back LFO), look at all
    P-forward/Q-back orders that are degree-feasible (max back-degree
    <= 2): each has a back-arc cycle.  Record, over the minimal such
    cycles, (i) the cycle LENGTH and (ii) the multiset of vertex ROLES
    (uP/vP port endpoints, uQ/vQ, cP = in C(P), cQ = in C(Q), other).
    Also classify the geometry of the two intervals in sigma (disjoint /
    nested / crossing).
    """
    from itertools import combinations, permutations
    from collections import Counter
    from port_relation_census import all_tournaments

    def arc(T, x, y):
        return (x, y) if T[x][y] else (y, x)

    def is_ba(T, pos, x, y):
        u, v = arc(T, x, y)
        return pos[u] > pos[v]

    def min_cycle_in_backarcs(edges, n):
        """Shortest cycle (vertex list) in the undirected back-arc graph,
        or None."""
        adj = defaultdict(set)
        for u, w in edges:
            adj[u].add(w)
            adj[w].add(u)
        best = None
        for s in range(n):
            # BFS for shortest cycle through s
            dist = {s: 0}
            par = {s: -1}
            dq = deque([s])
            while dq:
                x = dq.popleft()
                for y in adj[x]:
                    if y not in dist:
                        dist[y] = dist[x] + 1
                        par[y] = x
                        dq.append(y)
                    elif par[x] != y:
                        # found a cycle; reconstruct (approx shortest)
                        cyc = [x]
                        a2 = x
                        while a2 != s:
                            a2 = par[a2]
                            cyc.append(a2)
                        cyc2 = [y]
                        b2 = y
                        while b2 != s:
                            b2 = par[b2]
                            cyc2.append(b2)
                        ring = cyc + cyc2[::-1][1:]
                        if best is None or len(set(ring)) < len(best):
                            best = list(dict.fromkeys(ring))
            if best is not None and len(best) == 3:
                break
        return best

    def role_of(x, ports_named, CP, CQ):
        uP, vP, uQ, vQ = ports_named
        if x == uP:
            return "uP"
        if x == vP:
            return "vP"
        if x == uQ:
            return "uQ"
        if x == vQ:
            return "vQ"
        if x in CP and x in CQ:
            return "cPQ"
        if x in CP:
            return "cP"
        if x in CQ:
            return "cQ"
        return "other"

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    cyc_len = Counter()
    role_profiles = Counter()
    geometry = Counter()
    # essentiality of the 00 hypothesis
    iso11_no00_total = 0
    iso11_no00_both_nonflip = 0
    examples = []

    for T in all_tournaments(n):
        lfos = []
        for Pm in permutations(range(n)):
            st = linear_forest_status(back_arc_edges(T, list(Pm)), n)
            if st["is_linear_forest"]:
                lfos.append((list(Pm), st["deg"]))
        for (a, b), (c, d) in combinations(pairs, 2):
            if len({a, b, c, d}) < 4:
                continue
            ports = ((a, b), (c, d))
            Rarc = set()
            iso_order = None
            for o, deg in lfos:
                pos = {v: i for i, v in enumerate(o)}
                sP = is_ba(T, pos, a, b)
                sQ = is_ba(T, pos, c, d)
                Rarc.add((int(sP), int(sQ)))
                if sP and sQ and all(deg[v] == 1 for v in (a, b, c, d)) \
                        and iso_order is None:
                    iso_order = o
            if iso_order is None:
                continue
            has00 = (0, 0) in Rarc
            fP = (0, 1) in Rarc
            fQ = (1, 0) in Rarc
            if not has00:
                iso11_no00_total += 1
                if not fP and not fQ:
                    iso11_no00_both_nonflip += 1
                continue  # essentiality bucket only

            # geometry in iso_order
            pos = {v: i for i, v in enumerate(iso_order)}
            uP, vP = arc(T, a, b)   # uP->vP, back-arc => vP before uP
            uQ, vQ = arc(T, c, d)
            loP, hiP = sorted((pos[a], pos[b]))
            loQ, hiQ = sorted((pos[c], pos[d]))
            CP = {iso_order[i] for i in range(loP + 1, hiP)}
            CQ = {iso_order[i] for i in range(loQ + 1, hiQ)}
            if hiP < loQ or hiQ < loP:
                geo = "disjoint"
            elif (loP < loQ and hiQ < hiP) or (loQ < loP and hiP < hiQ):
                geo = "nested"
            else:
                geo = "crossing"

            for (x, y), flip in ((ports[0], fP), (ports[1], fQ)):
                if flip:
                    continue
                tv = (0, 1) if (x, y) == ports[0] else (1, 0)
                # find degree-feasible flipped orders, take min back-arc cycle
                best_ring = None
                for Pm in permutations(range(n)):
                    p2 = {v: i for i, v in enumerate(Pm)}
                    if (int(is_ba(T, p2, a, b)),
                            int(is_ba(T, p2, c, d))) != tv:
                        continue
                    edges = back_arc_edges(T, list(Pm))
                    st = linear_forest_status(edges, n)
                    if st["max_deg"] >= 3 or not st["has_cycle"]:
                        continue
                    ring = min_cycle_in_backarcs(edges, n)
                    if ring and (best_ring is None
                                 or len(ring) < len(best_ring)):
                        best_ring = ring
                if best_ring is None:
                    role_profiles[("NO_DEGREE_FEASIBLE_CYCLE",)] += 1
                    continue
                cyc_len[len(best_ring)] += 1
                pr = tuple(sorted(
                    role_of(z, (uP, vP, uQ, vQ), CP, CQ) for z in best_ring))
                role_profiles[pr] += 1
                geometry[geo] += 1
                if len(examples) < verbose_examples:
                    examples.append({
                        "T_upper": [[T[i][j] for j in range(n)]
                                    for i in range(n)],
                        "ports": ports, "flip_target": tv,
                        "iso11_order": list(iso_order),
                        "uP_vP": (uP, vP), "uQ_vQ": (uQ, vQ),
                        "CP": sorted(CP), "CQ": sorted(CQ),
                        "geometry": geo,
                        "blocking_cycle": best_ring,
                        "cycle_roles": list(pr),
                    })
    return {
        "n": n,
        "cycle_length_distribution": dict(cyc_len),
        "role_profile_distribution": {str(k): v
                                      for k, v in role_profiles.items()},
        "interval_geometry": dict(geometry),
        "essentiality_of_00": {
            "iso11_without_00_configs": iso11_no00_total,
            "of_those_both_nonflippable": iso11_no00_both_nonflip,
        },
        "examples": examples,
    }


def intrinsic_vs_coupled(n: int) -> dict:
    """For each nonflippable port P in an iso-11 config, decide whether
    the obstruction is INTRINSIC (P stays nonflippable even when Q is
    left free) or COUPLED (P is flippable once the Q-back constraint is
    dropped -- so the block genuinely needs Q to stay a back-arc).

    'P flippable with Q free' = some LFO has P's arc forward (sP=0),
    Q unconstrained.  'P flippable with Q back' = some LFO has sP=0,
    sQ=1 (the D80 mixed target).  A nonflippable-with-Q-back port that
    is flippable-with-Q-free is a genuine coupling; one that is
    nonflippable even with Q free is intrinsic.
    """
    from itertools import combinations, permutations
    from collections import Counter
    from port_relation_census import all_tournaments

    def arc(T, x, y):
        return (x, y) if T[x][y] else (y, x)

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    counts = Counter()
    for T in all_tournaments(n):
        lfos = []
        for Pm in permutations(range(n)):
            st = linear_forest_status(back_arc_edges(T, list(Pm)), n)
            if st["is_linear_forest"]:
                lfos.append((list(Pm), st["deg"]))
        for (a, b), (c, d) in combinations(pairs, 2):
            if len({a, b, c, d}) < 4:
                continue
            uP, vP = arc(T, a, b)
            uQ, vQ = arc(T, c, d)
            Rarc = set()
            pforward_qfree = False  # exists LFO with sP=0 (Q free)
            qforward_pfree = False
            iso11 = False
            for o, deg in lfos:
                pos = {v: i for i, v in enumerate(o)}
                sP = 1 if pos[uP] > pos[vP] else 0
                sQ = 1 if pos[uQ] > pos[vQ] else 0
                Rarc.add((sP, sQ))
                if sP == 0:
                    pforward_qfree = True
                if sQ == 0:
                    qforward_pfree = True
                if sP and sQ and all(deg[v] == 1 for v in (a, b, c, d)):
                    iso11 = True
            if not iso11:
                continue
            fP = (0, 1) in Rarc  # P flippable with Q back
            fQ = (1, 0) in Rarc
            for flip_qback, flip_qfree, tag in (
                    (fP, pforward_qfree, "P"),
                    (fQ, qforward_pfree, "Q")):
                if flip_qback:
                    continue  # this port IS flippable (Q-back) -- not blocked
                # P (or Q) is nonflippable with the other port back:
                if flip_qfree:
                    counts["coupled"] += 1   # flippable once other port free
                else:
                    counts["intrinsic"] += 1  # blocked even with other free
    return {
        "n": n,
        "nonflippable_ports_classification": dict(counts),
        "all_coupled": counts.get("intrinsic", 0) == 0,
    }


def iso11_eq2_backarc_count(n: int) -> dict:
    """DECISIVE n=7 check for D80, in the unambiguous BACK-ARC framing.

    D80 ("iso-11 => a mixed value is realizable") is equivalent to: NO
    EQ_2 gadget has an iso-11 LFO (both port arcs back-arcs, all four
    endpoints degree exactly 1).  The D78 bit-framing table reported
    "16 cap_on_11" -- but that counts orientations, not back-arc-framing
    iso-11 configs.  This function recomputes everything in back-arc
    framing over tournament iso-reps and counts:
      * eq2_gadgets        : (T, disjoint port pair) with R_arc = {00,11};
      * eq2_with_iso11     : of those, how many admit an iso-11 LFO
                             (= D80 counterexamples; predict 0);
      * iso11_gadgets_total: gadgets admitting an iso-11 LFO (any R_arc);
      * iso11_eq2_examples : up to 3 witnesses if eq2_with_iso11 > 0.
    """
    from itertools import combinations
    from fanout_barrier_checks import reps, disjoint

    def arc(T, x, y):
        return (x, y) if T[x][y] else (y, x)

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    pts = [pt for pt in combinations(pairs, 2) if disjoint(pt)]
    EQ2_arc = frozenset({(0, 0), (1, 1)})

    eq2_gadgets = 0
    eq2_with_iso11 = 0
    iso11_gadgets_total = 0
    iso11_no_mixed = 0   # iso-11 gadgets with R_arc subset of {00,11} (D80 fail)
    examples = []
    mixed = {(0, 1), (1, 0)}
    for T in reps(n):
        cache = build_lfo_cache(T)
        if not cache:
            continue
        for (a, b), (c, d) in pts:
            uP, vP = arc(T, a, b)   # uP->vP; back-arc iff pos[uP] > pos[vP]
            uQ, vQ = arc(T, c, d)
            R = set()
            iso11 = False
            for pos, deg in cache:
                sP = 1 if pos[uP] > pos[vP] else 0
                sQ = 1 if pos[uQ] > pos[vQ] else 0
                R.add((sP, sQ))
                if sP and sQ and all(deg[v] == 1 for v in (a, b, c, d)):
                    iso11 = True
            if iso11:
                iso11_gadgets_total += 1
                if not (R & mixed):   # no mixed value realizable => D80 fails
                    iso11_no_mixed += 1
                    if len(examples) < 3:
                        examples.append({
                            "T": [row[:] for row in T],
                            "ports": [(a, b), (c, d)],
                            "R_arc": sorted(R),
                        })
            if frozenset(R) == EQ2_arc:
                eq2_gadgets += 1
                if iso11:
                    eq2_with_iso11 += 1
    return {
        "n": n,
        "framing": "back-arc-status (unambiguous)",
        "eq2_gadgets": eq2_gadgets,
        "eq2_with_iso11": eq2_with_iso11,
        "iso11_gadgets_total": iso11_gadgets_total,
        "iso11_with_no_mixed": iso11_no_mixed,
        "D80_holds_iso11_implies_mixed": iso11_no_mixed == 0,
        "iso11_no_mixed_examples": examples,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=6)
    parser.add_argument("--saturation", action="store_true",
                        help="Run both_values_saturation_profile(n).")
    parser.add_argument("--flip-lemma", action="store_true",
                        help="Run flip_lemma_census(n).")
    parser.add_argument("--single-vertex", action="store_true",
                        help="Run single_vertex_relocation_coverage(n).")
    parser.add_argument("--three-cycle", action="store_true",
                        help="Run three_cycle_characterization_check(n).")
    parser.add_argument("--c-set", action="store_true",
                        help="Run c_set_analysis(n).")
    parser.add_argument("--coupled-flip", action="store_true",
                        help="Run two_port_coupled_flip(n).")
    parser.add_argument("--coupling-structure", action="store_true",
                        help="Run coupling_structure(n) (blocking-cycle shape).")
    parser.add_argument("--iso11-eq2", action="store_true",
                        help="Run iso11_eq2_backarc_count(n) (decisive n=7 D80 check).")
    parser.add_argument("--intrinsic-coupled", action="store_true",
                        help="Run intrinsic_vs_coupled(n) (block intrinsic vs coupled).")
    parser.add_argument("--kernel-lemmas", action="store_true",
                        help="Run kernel_lemmas_check(n) (kernelization foundation).")
    parser.add_argument("--essential-locality", action="store_true",
                        help="Run essential_locality_refutation(n) (D82).")
    parser.add_argument("--rung-compression", action="store_true",
                        help="Run rung_compression_refutation(n) (D83).")
    parser.add_argument("--verify-d80-ce", action="store_true",
                        help="Run verify_d80_counterexamples() (D84).")
    parser.add_argument("--eq2-capacity", action="store_true",
                        help="Run eq2_capacity_census(n) (D85, decisive).")
    parser.add_argument("--eq2-profile", action="store_true",
                        help="Run eq2_capacity_profile(n) (D86, separator mine).")
    parser.add_argument("--cap00-bound", action="store_true",
                        help="Run cap00_3cycle_bound(n) (D87, the cap-00 lever).")
    parser.add_argument("--outdeg-sep", action="store_true",
                        help="Run eq2_outdeg_separator(n) (D88, out-degree separator).")
    args = parser.parse_args()
    if args.saturation:
        print(json.dumps(both_values_saturation_profile(args.n), indent=2, default=list))
    elif args.flip_lemma:
        print(json.dumps(flip_lemma_census(args.n), indent=2, default=list))
    elif args.single_vertex:
        print(json.dumps(single_vertex_relocation_coverage(args.n), indent=2, default=list))
    elif args.three_cycle:
        print(json.dumps(three_cycle_characterization_check(args.n), indent=2, default=list))
    elif args.c_set:
        print(json.dumps(c_set_analysis(args.n), indent=2, default=list))
    elif args.coupled_flip:
        print(json.dumps(two_port_coupled_flip(args.n), indent=2, default=list))
    elif args.coupling_structure:
        print(json.dumps(coupling_structure(args.n, verbose_examples=3),
                         indent=2, default=list))
    elif args.iso11_eq2:
        print(json.dumps(iso11_eq2_backarc_count(args.n), indent=2, default=list))
    elif args.intrinsic_coupled:
        print(json.dumps(intrinsic_vs_coupled(args.n), indent=2, default=list))
    elif args.kernel_lemmas:
        print(json.dumps(kernel_lemmas_check(args.n), indent=2, default=list))
    elif args.essential_locality:
        print(json.dumps(essential_locality_refutation(args.n), indent=2, default=list))
    elif args.rung_compression:
        print(json.dumps(rung_compression_refutation(args.n), indent=2, default=list))
    elif args.verify_d80_ce:
        print(json.dumps(verify_d80_counterexamples(), indent=2, default=list))
    elif args.eq2_capacity:
        print(json.dumps(eq2_capacity_census(args.n), indent=2, default=list))
    elif args.eq2_profile:
        print(json.dumps(eq2_capacity_profile(args.n), indent=2, default=list))
    elif args.cap00_bound:
        print(json.dumps(cap00_3cycle_bound(args.n), indent=2, default=list))
    elif args.outdeg_sep:
        print(json.dumps(eq2_outdeg_separator(args.n), indent=2, default=list))
    else:
        print(json.dumps(census_slide_blockers(args.n), indent=2, default=list))


if __name__ == "__main__":
    main()
