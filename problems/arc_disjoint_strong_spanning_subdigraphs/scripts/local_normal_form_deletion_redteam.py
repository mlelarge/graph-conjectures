"""Bounded deletion red-team for the D68 local normal form.

D68 isolates LNF-1/LNF-2 as the remaining local normal-form facts.  This
script tries to refute them near D42 by deleting one or two relevant core
arcs while preserving the sealed-chain gates and original hard gateway.

Only arcs on local cuts of base out-size at most three are relevant for a
two-deletion search: deleting two arcs cannot make any larger local cut
drop below two.  This keeps the search focused and reproducible.
"""
from __future__ import annotations

import itertools
import os
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from chain_feed_deletion_stress import (  # noqa: E402
    V1_HOST,
    first_failed_gate,
    host_arcs_from_dbullet,
    original_hard_pair_survives,
    structural_gates,
)
from chain_feed_repair_search import cheap_chain_gates  # noqa: E402
from chain_kernel_witness import dbullet_arcs  # noqa: E402
from d42_split_predicate_tester import relabel_core_arcs  # noqa: E402
from local_normal_form_audit import (  # noqa: E402
    Q0,
    Q_MINUS,
    all_subsets,
    out_edges,
)


N_HOST = 24
V2_HOST = tuple(v for v in range(N_HOST) if v not in V1_HOST)
OUTSIDE = frozenset(V2_HOST) - Q0
EXPECTED_INTERNAL = {(tuple(sorted(Q_MINUS)), ((2, 6),))}
EXPECTED_EXTERNAL = {((10,), ((10, 23),))}


def core_edges_from_dbullet(arcs):
    host = host_arcs_from_dbullet(arcs)
    core_arcs = relabel_core_arcs(host, V2_HOST)
    return tuple((V2_HOST[u], V2_HOST[v]) for u, v in core_arcs)


def host_core_arc_to_dbullet(edge):
    u, v = edge
    assert u in V2_HOST and v in V2_HOST
    return (u - 1, v - 1)


def risky_deletion_arcs(base_edges):
    risky = set()

    for S in all_subsets(Q0):
        outs = out_edges(base_edges, S, Q0)
        if len(outs) <= 3:
            risky.update(outs)

    for B in all_subsets(OUTSIDE):
        outs = out_edges(base_edges, B, OUTSIDE)
        if len(outs) <= 3:
            risky.update(outs)

    for h in Q0:
        for w in OUTSIDE:
            S = (set(Q0) - {h}) | {w}
            outs = out_edges(base_edges, S)
            if len(outs) <= 3:
                risky.update(outs)

    base = Counter(dbullet_arcs())
    out = []
    for edge in sorted(risky):
        db = host_core_arc_to_dbullet(edge)
        if base[db] == 1:
            out.append(db)
    return tuple(out)


def lnf_violation(arcs):
    edges = core_edges_from_dbullet(arcs)
    q0_out = out_edges(edges, Q0)
    if q0_out:
        return {"type": "q0_not_zero", "q0_out": q0_out}

    internal = []
    for S in all_subsets(Q0):
        outs = out_edges(edges, S, Q0)
        if len(outs) <= 1:
            internal.append((tuple(sorted(S)), tuple(outs)))

    external = []
    for B in all_subsets(OUTSIDE):
        outs = out_edges(edges, B, OUTSIDE)
        if len(outs) <= 1:
            external.append((tuple(sorted(B)), tuple(outs)))

    single_exchange = []
    for h in Q0:
        for w in OUTSIDE:
            S = (set(Q0) - {h}) | {w}
            outs = out_edges(edges, S)
            if len(outs) <= 1:
                single_exchange.append((h, w, tuple(outs)))

    bad_internal = [row for row in internal if row not in EXPECTED_INTERNAL]
    bad_external = [row for row in external if row not in EXPECTED_EXTERNAL]
    if bad_internal or bad_external or single_exchange:
        return {
            "type": "lnf",
            "internal": internal,
            "external": external,
            "bad_internal": bad_internal,
            "bad_external": bad_external,
            "single_exchange": single_exchange,
        }
    return None


def safe_cheap_chain_gates(arcs):
    try:
        return cheap_chain_gates(arcs)
    except Exception as exc:  # networkx raises when the sealed path is gone.
        return False, type(exc).__name__


def main():
    base_arcs = tuple(dbullet_arcs())
    base_edges = core_edges_from_dbullet(base_arcs)
    candidates = risky_deletion_arcs(base_edges)

    print("Local normal-form deletion red-team")
    print(f"risky_candidate_arcs={len(candidates)}")
    print(f"candidates={candidates}")

    lnf_violations = 0
    cheap_pass = 0
    full_checks = 0
    gate_failures = Counter()
    gate_examples = {}
    hard_failures = 0
    hits = []

    for size in (1, 2):
        checked = 0
        for deleted in itertools.combinations(candidates, size):
            checked += 1
            deleted_set = set(deleted)
            arcs = tuple(e for e in base_arcs if e not in deleted_set)
            violation = lnf_violation(arcs)
            if violation is None:
                continue
            lnf_violations += 1

            cheap_ok, cheap_reason = safe_cheap_chain_gates(arcs)
            if not cheap_ok:
                gate_failures[f"cheap:{cheap_reason}"] += 1
                gate_examples.setdefault(
                    f"cheap:{cheap_reason}",
                    {"deleted": deleted, "violation": violation},
                )
                continue
            cheap_pass += 1

            gates = structural_gates(arcs)
            full_checks += 1
            if not gates["structural_ok"]:
                gate = first_failed_gate({"gates": gates})
                gate_failures[gate] += 1
                gate_examples.setdefault(
                    gate,
                    {
                        "deleted": deleted,
                        "violation": violation,
                        "lambda_db": gates["lambda_db"],
                        "lambda_host": gates["lambda_host"],
                        "db_min_cut": gates["db_min_cut"],
                    },
                )
                continue

            hard_ok, hard_info = original_hard_pair_survives(arcs)
            if not hard_ok:
                hard_failures += 1
                gate_failures["hard_pair"] += 1
                gate_examples.setdefault(
                    "hard_pair",
                    {"deleted": deleted, "violation": violation, "hard_info": hard_info},
                )
                continue

            hits.append({
                "deleted": deleted,
                "violation": violation,
                "hard_info": hard_info,
            })
        print(f"  size={size} checked={checked}")

    print(f"lnf_violations_before_gates={lnf_violations}")
    print(f"cheap_pass={cheap_pass}")
    print(f"full_checks={full_checks}")
    print(f"hard_failures={hard_failures}")
    print(f"gate_failures={dict(sorted(gate_failures.items()))}")
    print(f"gate_examples={gate_examples}")
    print(f"hits={hits[:5]}")

    assert not hits
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
