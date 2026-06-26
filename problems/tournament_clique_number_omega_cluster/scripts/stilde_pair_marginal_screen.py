"""Pair-marginal rigidity screen for the Shearer/Loomis-Whitney lower-bound route.

Vector-1 finite oracle (engine-readiness scout, 2026-06-20).  The Shearer route to
lambda > 3/2 rests on a per-level pair-rigidity gap

    g_c(pi) = log2(q_c * q_{c+1}) - H(r_c, r_{c+1})        (>= 0 always)

where (r_0, r_1, r_2) = R(v) is the canonical rank triple of vertex v (longest
backward colour-c chain ending at v), H is the Shannon entropy of the *pair*
marginal of R under the uniform vertex distribution, and q_c is the colour-c
height.  The chain

    log2 Q  =  (1/2) sum_c log2(q_c q_{c+1})
            =  (1/2) sum_c [ H(r_c,r_{c+1}) + g_c ]
            >= H(R) + (1/2) sum_c g_c           (Shearer: H(R) <= (1/2) sum pairs)
            >= d*log2(3/2) + (1/2) sum_c g_c     (every cell transitive, <= 2^d)

gives  lambda >= (3/2) * 2^{ (sum_c g_c) / (2d) }.  So the route to lambda > 3/2
LIVES iff  S(d)/d := (sum_c g_c)/d  is bounded below by a constant delta > 0 that
does not decay with d, and DIES if S(d)/d -> 0.

This screen measures S(d)/d at the L_k- and F_k-optimal witness orders for
d = 2..5.  It is a cheap REFUTATION oracle: a decaying S(d)/d kills the Shearer
route (it provably cannot then certify lambda > 3/2).  It cannot by itself prove
lambda = 3/2.

Sanity invariants checked per witness:
  * g_c >= 0                              (entropy <= log box size)
  * H(R) <= (1/2) sum_c H(r_c, r_{c+1})   (Shearer)
  * H(R) >= d*log2(3/2)                   (transitive-cell bound)
  * S(d) <= 2*(log2 L_k - d*log2(3/2))    (the gap cannot exceed the true excess)
"""

from __future__ import annotations

import itertools
import json
import math
from collections import Counter

from decide_layer_labeling import decide_caps_labeling
from stilde_pod_profiles import layer_ranks


LOG2_3_2 = math.log2(1.5)

# Optimal cap triples (min product = L_k / F_k) at each depth.
#   L-optimal: min over q0 q1 q2.  F-optimal: min over q1 q2 with q0 = 1 (face).
# Two-free triples (1,1,2^d) are the L-optimum only for d <= 3.
WITNESS_CAPS = [
    ("L d=2 two-free", 2, (1, 1, 4)),
    ("F d=2 balanced", 2, (1, 2, 2)),
    ("L d=3 two-free", 3, (1, 1, 8)),
    ("F d=3 balanced", 3, (1, 2, 4)),
    ("L d=3 (2,2,2)",  3, (2, 2, 2)),
    ("L=F d=4",        4, (1, 3, 5)),
    ("L d=5 (2,3,4)",  5, (2, 3, 4)),
    ("L d=5 (1,4,6)",  5, (1, 4, 6)),
    ("L d=5 (2,2,6)",  5, (2, 2, 6)),
    ("F d=5 (1,5,5)",  5, (1, 5, 5)),
]


def _entropy(counter, total):
    h = 0.0
    for count in counter.values():
        p = count / total
        h -= p * math.log2(p)
    return h


def pair_marginal_screen(order, depth):
    """Measure the per-level pair-rigidity gap S(d) of one witness order."""
    ranks = [layer_ranks(order, depth, c) for c in range(3)]
    total = 3 ** depth
    heights = [max(r.values()) for r in ranks]

    triple = Counter(tuple(r[v] for r in ranks) for v in order)
    h_triple = _entropy(triple, total)

    pair_entropy = []
    box_log = []
    gaps = []
    for c in range(3):
        nxt = (c + 1) % 3
        marginal = Counter((ranks[c][v], ranks[nxt][v]) for v in order)
        hp = _entropy(marginal, total)
        box = math.log2(heights[c] * heights[nxt])
        pair_entropy.append(hp)
        box_log.append(box)
        gaps.append(box - hp)

    sum_gaps = sum(gaps)
    log2_Q = sum(math.log2(h) for h in heights)
    # The gap can never exceed twice the true per-level excess of L_k over (3/2)^d.
    excess_cap = 2 * (log2_Q - depth * LOG2_3_2)
    return {
        "depth": depth,
        "heights": heights,
        "product": heights[0] * heights[1] * heights[2],
        "H_triple": h_triple,
        "H_triple_lower_bound": depth * LOG2_3_2,
        "shearer_rhs": 0.5 * sum(pair_entropy),
        "pair_entropies": pair_entropy,
        "box_logs": box_log,
        "gaps": gaps,
        "sum_gaps": sum_gaps,
        "sum_gaps_per_level": sum_gaps / depth,
        "excess_cap": excess_cap,
        "log2_Q": log2_Q,
        "lambda_lb_from_this_witness": 1.5 * 2 ** (sum_gaps / (2 * depth)),
        # invariants
        "ok_gaps_nonneg": all(g >= -1e-9 for g in gaps),
        "ok_shearer": h_triple <= 0.5 * sum(pair_entropy) + 1e-9,
        "ok_triple_lb": h_triple >= depth * LOG2_3_2 - 1e-9,
        "ok_excess_cap": sum_gaps <= excess_cap + 1e-9,
    }


def exhaustive_min_product(depth):
    """Max-over-minimizers of S(d): the worst-case gap among ALL optimal orders.

    Closes the adversarial-minimizer hole at a depth small enough to enumerate
    (d=2: 9! = 362880 orders).  Confirms no L_k-optimal order evades the cap.
    """
    n = 3 ** depth
    best_product = None
    minimizers = 0
    worst = None
    for order in itertools.permutations(range(n)):
        ranks = [layer_ranks(order, depth, c) for c in range(3)]
        heights = [max(r.values()) for r in ranks]
        product = heights[0] * heights[1] * heights[2]
        if best_product is None or product < best_product:
            best_product = product
            minimizers = 0
            worst = None
        if product == best_product:
            minimizers += 1
            screen = pair_marginal_screen(list(order), depth)
            if worst is None or screen["sum_gaps"] > worst["sum_gaps"]:
                worst = screen
    return {
        "depth": depth,
        "L_k": best_product,
        "num_minimizers": minimizers,
        "max_sum_gaps_over_minimizers": worst["sum_gaps"],
        "max_S_per_level": worst["sum_gaps"] / depth,
        "excess_cap": worst["excess_cap"],
        "worst_lambda_lb": worst["lambda_lb_from_this_witness"],
        "L_k_root": best_product ** (1.0 / depth),
    }


def run():
    rows = []
    for label, depth, caps in WITNESS_CAPS:
        result = decide_caps_labeling(depth, caps)
        if not result["sat"]:
            rows.append({"label": label, "depth": depth, "caps": caps,
                         "sat": False})
            print(f"{label:18s} caps={caps} -> UNSAT (skip)", flush=True)
            continue
        screen = pair_marginal_screen(result["witness_order"], depth)
        screen["label"] = label
        screen["caps"] = caps
        rows.append(screen)
        ok = all(screen[k] for k in
                 ("ok_gaps_nonneg", "ok_shearer", "ok_triple_lb", "ok_excess_cap"))
        print(
            f"{label:18s} caps={caps} heights={tuple(screen['heights'])} "
            f"S(d)={screen['sum_gaps']:.4f} S/d={screen['sum_gaps_per_level']:.4f} "
            f"cap={screen['excess_cap']:.4f} "
            f"lam_lb={screen['lambda_lb_from_this_witness']:.4f} "
            f"inv={'OK' if ok else 'FAIL'}",
            flush=True,
        )
    out = "data/pair_marginal_screen.json"
    with open(out, "w") as handle:
        json.dump(rows, handle, indent=2)
    print(f"\nwrote {out}", flush=True)

    print("\n=== trend of S(d)/d at the optimal witnesses ===", flush=True)
    for tag in ("L", "F"):
        series = [(r["depth"], r["sum_gaps_per_level"]) for r in rows
                  if r.get("label", "").startswith(tag) and "sum_gaps_per_level" in r]
        if series:
            pretty = ", ".join(f"d={d}:{v:.4f}" for d, v in series)
            print(f"  {tag}-optimal: {pretty}", flush=True)
    return rows


if __name__ == "__main__":
    run()
