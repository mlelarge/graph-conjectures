"""check_lexist_fixedroot.py -- red-team the FIXED-ROOT L-exist statement,
Irreducible Gateway Emptiness, and the fallback pivot claim
(docs/CRUX_A_LEXIST_PROOF_ATTEMPT_2026_06_11.md S10-S11).

WHY THIS CHECKER EXISTS. Every prior machine test (check_lexist.py D4,
lexist_contracted_part.py D5) roots both arborescences at head(a). The
RECOLOR application -- and the new Candidate Gateway Lemma -- live in the
FIXED-ROOT family: both in-arborescences rooted at the contracted vertex rho,
arc a arbitrary. S8 of the proof note records that the head-rooted statement
does not imply the fixed-root one. This checker supplies that missing
fixed-root red-team.

WHAT IT TESTS, per chord-contraction D^bullet (population identical to
lexist_contracted_part.py: capped construction-A census of 3-arc-strong
(1,0)-near-split hosts, deduped chord contractions, lambda(D^bullet)>=3):

  1. FIXED-ROOT L-EXIST. For every simple arc a=(u,v) with u != rho: over all
     arc-disjoint spanning in-arborescence pairs (T,U) rooted at rho with a in
     T and 2 <= |X_a^T| <= n-2, does SOME pair have a strict exit? Verdict
     FAIL = pairs with intermediate X exist but none is good (refutes the
     fixed-root statement on the population CRUX-A needs).

  2. LEMMA 2.1 ASSERT. For every (pair, a) examined, assert
     (#U-exits from X >= 2) <=> (some exit has strictly smaller subtree
     intersection). Machine-verifies P7(i) across the population.

  3. EXHAUSTIVE GATEWAY / PIVOT DIAGNOSTIC. For every FAILING pair in the
     gateway (one U-exit b=(t,y), every free exit has tail u), first test
     whether S5 repairs it immediately: t != u and some free c=(u,z) has
     z outside X_u^U. Only the remaining HARD gateways are tested for the
     S10 pivots q in (K\\X) cap V(zUu - u) and
     h in (K cap X) cap V(uUt - {u,t}).

The pair diagnostics do not stop when the first good pair for an arc is
found. That good pair decides the per-arc L-exist verdict, but later failing
pairs must still be scanned; otherwise a reported zero-gateway count is only
an enumeration-prefix statistic.

MULTIPLICITY COLLAPSE (exactness). A spanning in-arborescence uses each
simple arc at most once (one out-arc per vertex), so labeled pairs collapse
to STRUCTURAL tree pairs: (T,U) is realizable with disjoint labels iff every
simple arc used by both has multiplicity >= 2. Exits, subtrees, X, and the
strict-exit predicate depend only on the structural trees; an arc e leaving X
is FREE iff mult(e) - [e in T] - [e in U] >= 1. All verdicts are therefore
exact over the labeled object.

CONTROL. The tripled-path counterexample (P6, scripts/
lexist_path_counterexample.py) is run first with rho=2: the checker must
report FAIL there (it is not a chord contraction; it is the discriminating
control that FAIL detection works).
"""
from __future__ import annotations

import itertools
import json
import os
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from digraph import Digraph  # noqa: E402
from generators.near_split import (  # noqa: E402
    enumerate_construction_A,
    is_one_zero_near_split,
)


# --------------------------------------------------------------------------- #
#  Structural in-arborescence machinery (multiplicity-collapsed, exact)
# --------------------------------------------------------------------------- #

def in_arborescences(n, struct_out, root):
    """All structural spanning in-arborescences rooted at `root`.

    struct_out: dict tail -> sorted tuple of distinct heads.
    Yields succ dicts {v: head} for v != root (each non-root one out-arc,
    acyclic, all paths reach root).
    """
    nonroot = [v for v in range(n) if v != root]
    if any(not struct_out.get(v) for v in nonroot):
        return
    for choice in itertools.product(*[struct_out[v] for v in nonroot]):
        succ = dict(zip(nonroot, choice))
        ok = True
        for v in nonroot:
            seen, cur = set(), v
            while cur != root:
                if cur in seen:
                    ok = False
                    break
                seen.add(cur)
                cur = succ[cur]
            if not ok:
                break
        if ok:
            yield succ


def tree_arcs(succ):
    return frozenset(succ.items())  # {(tail, head)}


def subtree_through(succ, vertex, root, n):
    """Vertices whose succ-path to root passes through `vertex` (incl. itself)."""
    out = set()
    for v in range(n):
        if v == root:
            continue
        cur = v
        while True:
            if cur == vertex:
                out.add(v)
                break
            if cur == root:
                break
            cur = succ[cur]
    return out


def u_path(succ, start, stop, root):
    """Vertices on the succ-path from start to stop (inclusive); None if the
    path reaches root before stop."""
    path, cur = [start], start
    while cur != stop:
        if cur == root:
            return None
        cur = succ[cur]
        path.append(cur)
    return path


def pair_realizable(Tset, Uset, mult):
    return all(mult[e] >= 2 for e in Tset & Uset)


# --------------------------------------------------------------------------- #
#  Per-instance fixed-root analysis
# --------------------------------------------------------------------------- #

def analyse_instance(n, arcs, root, K_set, name=""):
    """arcs: list of (u,v) with multiplicity = repetition. Returns verdicts +
    gateway diagnostics for the fixed-root family rooted at `root`."""
    mult = Counter(arcs)
    struct_out = {}
    for (u, v) in mult:
        struct_out.setdefault(u, set()).add(v)
    struct_out = {u: tuple(sorted(vs)) for u, vs in struct_out.items()}

    arbs = [(succ, tree_arcs(succ)) for succ in in_arborescences(n, struct_out, root)]
    res = {
        "name": name, "n": n, "root": root, "n_struct_in_arbs": len(arbs),
        "arcs_tested": 0, "arcs_good": 0, "arcs_no_intermediate": 0,
        "arcs_no_pair": 0, "FAILS": [],
        "lemma21_checks": 0, "lemma21_violations": 0,
        "failing_pairs": 0, "gateway_pairs": 0,
        "gateway_safe_repairable": 0, "gateway_hard": 0,
        "pivot_ok": 0,
        "pivot_missing": Counter(),
    }

    simple_arcs = sorted(set(mult))
    for a in simple_arcs:
        u, v = a
        if u == root:
            continue
        res["arcs_tested"] += 1
        found_good = found_intermediate = found_pair = False
        for succT, Tset in arbs:
            if succT.get(u) != v:
                continue
            X = subtree_through(succT, u, root, n)
            inter = 2 <= len(X) <= n - 2
            for succU, Uset in arbs:
                if not pair_realizable(Tset, Uset, mult):
                    continue
                # a in T and U must leave a labeled copy for T:
                if a in Uset and mult[a] < 2:
                    continue
                found_pair = True
                if not inter:
                    continue
                found_intermediate = True
                exits = [(w, z) for (w, z) in Uset if w in X and z not in X]
                strict = [
                    b for b in exits
                    if (subtree_through(succU, b[0], root, n) & X) < X
                ]
                res["lemma21_checks"] += 1
                if (len(exits) >= 2) != bool(strict):
                    res["lemma21_violations"] += 1
                if strict:
                    found_good = True
                    continue
                # ---- failing pair: gateway / pivot diagnostics ----
                res["failing_pairs"] += 1
                t_tail, _ = exits[0]
                free = [
                    e for e in mult
                    if e[0] in X and e[1] not in X
                    and mult[e] - (e in Tset) - (e in Uset) >= 1
                ]
                if any(w != u for (w, _z) in free):
                    continue  # not gateway: Lemma 4.1 shrink applies
                res["gateway_pairs"] += 1
                m = succU[u]
                X_u_U = subtree_through(succU, u, root, n)
                safe = [e for e in free if e[1] not in X_u_U]
                if t_tail != u and safe:
                    res["gateway_safe_repairable"] += 1
                    continue

                res["gateway_hard"] += 1
                unsafe = [e for e in free if e[1] in X_u_U and e[1] not in X]
                if t_tail == u:
                    res["pivot_missing"]["t==u"] += 1
                    continue
                if not unsafe:
                    res["pivot_missing"]["no_unsafe"] += 1
                    continue
                if m == t_tail:
                    res["pivot_missing"]["m==t"] += 1
                    continue
                h_path = u_path(succU, u, t_tail, root)
                h_int = [w for w in (h_path or [])[1:-1]]
                h_ok = any(w in K_set and w in X for w in h_int)
                q_ok_some = False
                for (_w, z) in unsafe:
                    q_path = u_path(succU, z, u, root)
                    q_int = (q_path or [])[:-1]
                    if any(w in K_set and w not in X for w in q_int):
                        q_ok_some = True
                        break
                if h_ok and q_ok_some:
                    res["pivot_ok"] += 1
                elif not h_ok:
                    res["pivot_missing"]["h-interval-no-K-in-X"] += 1
                else:
                    res["pivot_missing"]["q-missing-on-unsafe-intervals"] += 1
        if found_good:
            res["arcs_good"] += 1
        elif not found_pair:
            res["arcs_no_pair"] += 1
        elif not found_intermediate:
            res["arcs_no_intermediate"] += 1
        else:
            res["FAILS"].append({"arc": list(a)})
    res["pivot_missing"] = dict(res["pivot_missing"])
    return res


# --------------------------------------------------------------------------- #
#  Population: chord contractions (identical to lexist_contracted_part.py)
# --------------------------------------------------------------------------- #

def chord_contraction_with_K(inst):
    e0 = tuple(inst.internal_arc)
    p, q = e0
    others = sorted(v for v in range(inst.n) if v != p and v != q)
    relabel = {p: 0, q: 0}
    for i, v in enumerate(others, start=1):
        relabel[v] = i
    k = 1 + len(others)
    arcs = []
    for (x, y) in inst.arcs:
        if (x, y) == e0:
            continue
        rx, ry = relabel[x], relabel[y]
        if rx != ry:
            arcs.append((rx, ry))
    K_set = {relabel[v] for v in inst.V2}
    return k, arcs, K_set


def _arc_conn(n, arcs):
    return Digraph.from_arcs(range(n), list(arcs)).arc_connectivity()


def run_cell(v1, v2, orient_cap=64, bridge_cap=32):
    seen, agg = set(), {
        "cell": f"({v1},{v2})", "n_Dbullet": 0, "arcs_tested": 0,
        "arcs_good": 0, "arcs_no_intermediate": 0, "arcs_no_pair": 0,
        "FAILS": [], "lemma21_checks": 0, "lemma21_violations": 0,
        "failing_pairs": 0, "gateway_pairs": 0,
        "gateway_safe_repairable": 0, "gateway_hard": 0,
        "pivot_ok": 0,
        "pivot_missing": Counter(),
    }
    for inst in enumerate_construction_A(
        v1, v2, cap_per_v2_orientation=orient_cap,
        bridge_cap_per_pair=bridge_cap,
    ):
        D = inst.build()
        ok, _ = is_one_zero_near_split(D, list(inst.V1), list(inst.V2))
        if not ok or _arc_conn(inst.n, list(inst.arcs)) < 3:
            continue
        k, arcs, K_set = chord_contraction_with_K(inst)
        key = (k, tuple(sorted(arcs)))
        if key in seen:
            continue
        seen.add(key)
        if _arc_conn(k, arcs) < 3:
            continue
        r = analyse_instance(k, arcs, 0, K_set, name=inst.name)
        agg["n_Dbullet"] += 1
        for f in ("arcs_tested", "arcs_good", "arcs_no_intermediate",
                  "arcs_no_pair", "lemma21_checks", "lemma21_violations",
                  "failing_pairs", "gateway_pairs",
                  "gateway_safe_repairable", "gateway_hard", "pivot_ok"):
            agg[f] += r[f]
        for kk, vv in r["pivot_missing"].items():
            agg["pivot_missing"][kk] += vv
        for f in r["FAILS"]:
            agg["FAILS"].append({"host": inst.name, "k": k, **f})
    agg["pivot_missing"] = dict(agg["pivot_missing"])
    return agg


def control_tripled_path():
    arcs = []
    for (u, v) in [(1, 0), (0, 2), (2, 3)]:
        arcs += [(u, v)] * 3 + [(v, u)] * 3
    # not a chord contraction; K-set empty (no semicomplete triple): pure
    # FAIL-detection control, rooted at 2 (= head of the 0->2 arc).
    return analyse_instance(4, arcs, 2, K_set=set(), name="tripled-path-P6")


def control_safe_gateway():
    """An in-class six-vertex contraction with safe-repairable gateways.

    This prevents the diagnostic loop from again reporting zero gateways
    merely because it stopped at the first good pair for the same arc.
    """
    arcs = [
        (0, 2), (0, 3), (0, 4), (0, 4), (0, 5), (0, 5),
        (1, 2), (1, 3), (1, 4),
        (2, 0), (2, 1), (2, 4),
        (3, 1), (3, 2), (3, 4),
        (4, 0), (4, 0), (4, 1), (4, 3), (4, 5),
        (5, 0), (5, 0), (5, 2), (5, 3),
    ]
    return analyse_instance(
        6, arcs, 0, K_set={2, 3, 4, 5}, name="safe-gateway-control"
    )


def main():
    ctrl = control_tripled_path()
    ctrl_fail_ok = any(f["arc"] == [0, 2] for f in ctrl["FAILS"])
    gateway_ctrl = control_safe_gateway()
    print(json.dumps({
        "control": {
            "name": ctrl["name"],
            "FAILS": ctrl["FAILS"],
            "fail_detected_at_0->2": ctrl_fail_ok,
            "lemma21_violations": ctrl["lemma21_violations"],
        },
        "gateway_control": {
            "name": gateway_ctrl["name"],
            "gateway_pairs": gateway_ctrl["gateway_pairs"],
            "gateway_safe_repairable": gateway_ctrl["gateway_safe_repairable"],
            "gateway_hard": gateway_ctrl["gateway_hard"],
        },
    }, indent=2))
    if not ctrl_fail_ok:
        raise AssertionError("control failed: checker cannot detect the P6 counterexample")
    if (
        gateway_ctrl["gateway_pairs"] == 0
        or gateway_ctrl["gateway_pairs"]
        != gateway_ctrl["gateway_safe_repairable"]
        or gateway_ctrl["gateway_hard"] != 0
    ):
        raise AssertionError("control failed: safe gateway classification is wrong")

    cells = [(2, 3), (3, 3), (2, 4), (2, 5), (3, 4), (4, 3)]
    for (v1, v2) in cells:
        out = run_cell(v1, v2)
        print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
