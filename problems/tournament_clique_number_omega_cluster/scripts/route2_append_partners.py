"""Route 2 experiment: append-built escapers and partner-map search.

For a k-omega-critical tournament H and a vertex v, any optimal order tau of
H-v gives an append-built escaper sigma=(tau,v).  This script asks whether sigma
can be chosen as a FULL RAISER,

    D_sigma(t) > t  for every 2 <= t <= k.

If so, the shared triple (sigma,sigma,sigma) is cycle-free, so no partner orders
are needed.  Otherwise it searches triples among the append-built maps found.

Targets:
  * AC_7, AC_9, AC_11;
  * the two saved order-8 3-critical classes;
  * S~_3;
  * the QR_19 gold escaper (control);
  * AC_7[C3], using a bounded adjacent-swap search around its proved deletion
    template as the first genuine partner-search case.

The output is data/route2_append_partners.json.  Every positive is independently
checked by the full credit-lattice analyzer.  Negative search results are scoped
to the explicitly reported candidate set.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
import itertools
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

import core
from confirm_deletion_template_k4 import (
    build as build_ac_c3,
    order_template as ac_c3_deletion_order,
)
from constructions import S_tilde
from extract_deletion_order import ac_gen
from h25_path_feasibility import lex_c3, omega_be_seq, optimal_profiles, profile_of
from route2_credit_deadlock import (
    analyse_triple,
    cyclic_wait_cycles,
    demand_relief_map,
    gold_triple,
)
from search_4critical_circulant import circ_arcs


HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")


def demand_signature(profile, m, k):
    dmap = demand_relief_map(profile, m, k)
    return tuple(dmap[t]["successor_level"] for t in range(2, k + 1))


def is_full_raiser(signature):
    return all(value > level for level, value in enumerate(signature, start=2))


def append_record(n, arcs, k, sigma, source):
    sigma = tuple(sigma)
    if sorted(sigma) != list(range(n)):
        raise ValueError(f"{source}: not a permutation")
    beats = core.beats_matrix(n, arcs)
    profile = profile_of(beats, sigma)
    full_width = profile[0][n]
    prefix_width = profile[0][n - 1]
    if full_width != k or prefix_width != k - 1:
        raise ValueError(
            f"{source}: append order widths are prefix={prefix_width}, "
            f"full={full_width}, expected {k-1},{k}"
        )
    signature = demand_signature(profile, n, k)
    return {
        "source": source,
        "order": sigma,
        "profile": profile,
        "demand_signature": signature,
        "full_raiser": is_full_raiser(signature),
        "appended_vertex": sigma[-1],
        "prefix_width": prefix_width,
        "full_width": full_width,
    }


def candidates_from_deleted_profile_representatives(
    name, n, arcs, k, vertices=(0,), profile_cap=500
):
    """Use one witness per distinct optimal profile of H-v.

    This is a certificate generator, not an exhaustive enumeration of append
    orders: two deletion orders with the same internal profile may interact
    differently with the appended vertex.
    """
    records = []
    per_vertex = {}
    for v in vertices:
        keep = [u for u in range(n) if u != v]
        nn, sub = core.subtournament(n, arcs, keep)
        profiles = optimal_profiles(nn, sub, k - 1, cap=profile_cap)
        per_vertex[str(v)] = {
            "deletion_profiles": len(profiles),
            "truncated": len(profiles) >= profile_cap,
        }
        for i, tau_local in enumerate(profiles.values()):
            tau = [keep[u] for u in tau_local]
            records.append(
                append_record(
                    n, arcs, k, tau + [v],
                    f"{name}:delete-{v}:profile-rep-{i}",
                )
            )
    return records, per_vertex


def greedy_interleaving(profiles, orders, n, k):
    """Build one explicit legal interleaving, choosing the first legal copy."""
    f = [profile[0] for profile in profiles]
    g = [profile[1] for profile in profiles]
    state = [0, 0, 0]
    copy_steps = []
    product_order = []

    def safe(candidate):
        for y, x in ((1, 0), (2, 1), (0, 2)):
            if f[y][candidate[y]] + g[x][n - candidate[x]] > k + 1:
                return False
        return True

    while tuple(state) != (n, n, n):
        for c in range(3):
            if state[c] == n:
                continue
            candidate = list(state)
            candidate[c] += 1
            if not safe(candidate):
                continue
            inner_vertex = orders[c][state[c]]
            product_order.append(c * n + inner_vertex)
            copy_steps.append(c)
            state = candidate
            break
        else:
            raise AssertionError(f"cycle-free triple reached dead-end at {state}")
    return copy_steps, product_order


def find_cycle_free_triple(records, n, arcs, k):
    representatives = {}
    for record in records:
        representatives.setdefault(record["demand_signature"], record)

    signatures = list(representatives)
    # Prefer one shared order, then two distinct maps, then three.
    placements = list(itertools.product(signatures, repeat=3))
    placements.sort(key=lambda triple: len(set(triple)))
    for triple in placements:
        profiles = [representatives[s]["profile"] for s in triple]
        if cyclic_wait_cycles(profiles, n, k)[1]:
            continue
        lattice = analyse_triple(profiles, n, k, record_deadlocks=False)
        if not lattice["feasible_no_deadlock"]:
            raise AssertionError("cycle-free maps failed full lattice validation")
        orders = [representatives[s]["order"] for s in triple]
        copy_steps, product_order = greedy_interleaving(
            profiles, orders, n, k
        )
        product_n, product_arcs = lex_c3(n, arcs)
        product_clique = core.omega_of_order(
            product_n, product_arcs, product_order
        )
        if product_clique != k + 1:
            raise AssertionError(
                f"explicit interleaving clique={product_clique}, expected {k+1}"
            )
        return {
            "signatures": triple,
            "orders": orders,
            "sources": [representatives[s]["source"] for s in triple],
            "n_distinct_maps": len(set(triple)),
            "copy_steps": copy_steps,
            "product_order": product_order,
            "product_clique_core_verified": product_clique,
            "lattice": {
                key: lattice[key]
                for key in (
                    "n_safe", "n_reachable", "terminal_reachable",
                    "n_dead_ends", "feasible_no_deadlock",
                )
            },
        }
    return None


def summarize_target(name, n, arcs, k, records, generation):
    map_hist = Counter(record["demand_signature"] for record in records)
    full_raisers = [record for record in records if record["full_raiser"]]
    triple = find_cycle_free_triple(records, n, arcs, k)
    return {
        "name": name,
        "n": n,
        "k": k,
        "generation": generation,
        "n_append_records": len(records),
        "n_distinct_maps": len(map_hist),
        "map_histogram": {
            ",".join(map(str, signature)): count
            for signature, count in sorted(map_hist.items())
        },
        "n_full_raisers": len(full_raisers),
        "full_raiser_witness": (
            {
                "source": full_raisers[0]["source"],
                "order": list(full_raisers[0]["order"]),
                "demand_signature": list(full_raisers[0]["demand_signature"]),
            }
            if full_raisers else None
        ),
        "cycle_free_triple": (
            {
                **triple,
                "signatures": [list(s) for s in triple["signatures"]],
                "orders": [list(order) for order in triple["orders"]],
            }
            if triple else None
        ),
    }


def ac_target(n):
    arcs = circ_arcs(n, ac_gen(n))
    canonical = append_record(
        n, arcs, 3, list(range(1, n)) + [0], f"AC_{n}:canonical-shift"
    )
    records, detail = candidates_from_deleted_profile_representatives(
        f"AC_{n}", n, arcs, 3, vertices=(0,)
    )
    records.append(canonical)
    return summarize_target(
        f"AC_{n}", n, arcs, 3, records,
        {
            "method": "canonical shift plus one witness per deletion-profile at v=0",
            "detail": detail,
        },
    )


def ac_canonical_target(n):
    arcs = circ_arcs(n, ac_gen(n))
    canonical = append_record(
        n, arcs, 3, list(range(1, n)) + [0], f"AC_{n}:canonical-shift"
    )
    return summarize_target(
        f"AC_{n}", n, arcs, 3, [canonical],
        {"method": "canonical shift only"},
    )


def saved_order8_targets():
    data = json.load(open(os.path.join(DATA, "iso_critical_scan.json")))
    out = []
    for i, example in enumerate(data["8"]["critical_examples"]):
        arcs = [tuple(arc) for arc in example["arcs"]]
        records, detail = candidates_from_deleted_profile_representatives(
            f"order8_critical_{i}", 8, arcs, 3, vertices=(0,)
        )
        out.append(summarize_target(
            f"order8_critical_{i}", 8, arcs, 3, records,
            {
                "method": "one witness per deletion-profile at v=0",
                "detail": detail,
            },
        ))
    return out


def stilde3_target():
    n, arcs = S_tilde(3)
    records, detail = candidates_from_deleted_profile_representatives(
        "S_tilde_3", n, arcs, 3, vertices=(0,)
    )
    return summarize_target(
        "S_tilde_3", n, arcs, 3, records,
        {
            "method": "one witness per deletion-profile at v=0",
            "detail": detail,
        },
    )


def qr19_gold_target():
    profiles = gold_triple()
    # Copy 2 is append-built: its full clique first reaches 4 at the last vertex.
    gold = json.load(open(os.path.join(DATA, "ground_h21_skeleton_sat.json")))
    order = tuple(v % 19 for v in gold["witness_order"] if v // 19 == 2)
    n = 19
    qr = sorted({(x * x) % 19 for x in range(1, 19)})
    arcs = [(i, (i + d) % 19) for i in range(19) for d in qr]
    record = append_record(n, arcs, 4, order, "QR_19:gold-copy-2")
    if record["profile"] != profiles[2]:
        raise AssertionError("gold copy-2 profile reconstruction mismatch")
    return summarize_target(
        "QR_19_gold_escaper", n, arcs, 4, [record],
        {"method": "SAT-gold copy 2, independently checked as append-built"},
    )


def adjacent_swap_append_search_ac7_c3(max_depth=5, max_states=7000):
    """Bounded partner search around the proved AC_7[C3]-0 deletion template."""
    n_outer = 7
    n, arcs, m = build_ac_c3(n_outer)
    k = 4
    beats = core.beats_matrix(n, arcs)
    base = tuple(ac_c3_deletion_order(m, deleted=0))
    queue = deque([(base, 0)])
    seen = {base}
    records_by_map = {}
    n_valid = 0

    while queue and len(seen) <= max_states:
        tau, depth = queue.popleft()
        if omega_be_seq(beats, list(tau)) != k - 1:
            continue
        n_valid += 1
        record = append_record(
            n, arcs, k, list(tau) + [0],
            f"AC_7[C3]:adjacent-swap-depth-{depth}",
        )
        records_by_map.setdefault(record["demand_signature"], record)
        if depth >= max_depth:
            continue
        for i in range(len(tau) - 1):
            neighbor = list(tau)
            neighbor[i], neighbor[i + 1] = neighbor[i + 1], neighbor[i]
            neighbor = tuple(neighbor)
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append((neighbor, depth + 1))

    records = list(records_by_map.values())
    result = summarize_target(
        "AC_7[C3]_local_partner_search", n, arcs, k, records,
        {
            "method": "BFS in adjacent-swap graph around proved d_then_c deletion order",
            "max_depth": max_depth,
            "max_states": max_states,
            "n_states_seen": len(seen),
            "n_valid_deletion_orders": n_valid,
            "negative_scope": "only this bounded connected neighborhood",
        },
    )
    return result


def run():
    t0 = time.time()
    targets = [ac_target(n) for n in (7, 9, 11)]
    targets.extend(ac_canonical_target(n) for n in (13, 15, 17, 19, 21, 23))
    targets.extend(saved_order8_targets())
    targets.append(stilde3_target())
    targets.append(qr19_gold_target())
    targets.append(adjacent_swap_append_search_ac7_c3())
    out = {
        "experiment": "route2_append_partners",
        "claim_form": "explicit positive certificates; bounded negatives scoped per target",
        "targets": targets,
        "elapsed_seconds": round(time.time() - t0, 3),
    }
    path = os.path.join(DATA, "route2_append_partners.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=2)
    return out, path


def main():
    parser = argparse.ArgumentParser()
    parser.parse_args()
    out, path = run()
    for target in out["targets"]:
        triple = target["cycle_free_triple"]
        print(
            f"{target['name']}: maps={target['map_histogram']} "
            f"full_raisers={target['n_full_raisers']} "
            f"cycle_free={'yes' if triple else 'no'}"
            + (
                f" distinct_maps={triple['n_distinct_maps']}"
                if triple else ""
            ),
            flush=True,
        )
    print(f"WROTE {path} elapsed={out['elapsed_seconds']}s", flush=True)


if __name__ == "__main__":
    main()
