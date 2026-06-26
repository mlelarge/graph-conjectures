"""Route (2), sharpened: the CREDIT / NO-DEADLOCK formulation of the H25 path
feasibility for the C3-outer VALUE leg (docs/h19_cancellation_argument_sketch.md).

Reformulation (user-supplied).  With  r_c(j) = k - g_c(m-j)  (non-decreasing, 0->k),
each cross constraint  f_Y(j_Y) + g_X(m-j_X) <= k+1  becomes

        f_Y(j_Y) - r_X(j_X) <= 1 ,

i.e. the CREDIT on arc X->Y,   cred_{(Y,X)} = 1 + r_X(j_X) - f_Y(j_Y) >= 0 ,  is the
constraint.  A unit step in copy c:  consumes 1 incoming credit when f_c rises (c is
the HEAD of pair (c, pred c)); creates 1 outgoing credit when r_c rises (c is the TAIL
of pair (succ c, c)); else free.  A 'safe' state has all credits >= 0 (= not 'bad').
A 'legal move' advances some copy to a safe state.  A DEAD-END is a reachable safe
non-terminal state with no legal move (a cyclic 3-way wait).

TARGET LEMMA:  choose three inner orders so that NO reachable safe state is a dead end.
Then any greedy legal-step run reaches (m,m,m) and the k+1 bound is automatic.

This script: (A) audits common enumerated shared profiles for QR_19 (the capped
enumeration misses the rare gold copy-2 full raiser; see route2_append_partners.py);
(B) builds the safe-state graph for a profile triple and reports #safe, reachable,
DEAD-ENDS + minimal cyclic deadlock certificates; (C) validates on the QR_19 gold
triple. Pure combinatorics on profiles; no oracle search. Foreground.
"""
import sys, os, json, time, itertools, argparse
sys.path.insert(0, os.path.dirname(__file__))
import core
from h25_path_feasibility import (lex_c3, omega_be_seq, profile_of, optimal_profiles,
                                  CYCLIC_PAIRS)

# pred/succ in C3 (arcs 0->1->2->0): pair with HEAD c is (c, pred[c]) in CYCLIC_PAIRS
PRED = {1: 0, 2: 1, 0: 2}     # X = pred[Y] for (Y,X) in CYCLIC_PAIRS


def qr19():
    QR = sorted({(x * x) % 19 for x in range(1, 19)})
    arcs = [(i, (i + d) % 19) for i in range(19) for d in QR]
    return 19, arcs


# --------------------------------------------------------------------------- #
#  Credit / safe-state machinery for a fixed profile triple.
# --------------------------------------------------------------------------- #
def make_safe(profs, m, k):
    """profs = [(f0,g0),(f1,g1),(f2,g2)].  Returns helpers over states (j0,j1,j2)."""
    f = [profs[c][0] for c in range(3)]
    g = [profs[c][1] for c in range(3)]

    def credit(state, Y, X):           # arc X->Y ; = 1 + r_X - f_Y ; >=0 iff safe on this pair
        rX = k - g[X][m - state[X]]
        return 1 + rX - f[Y][state[Y]]

    def safe(state):
        return all(credit(state, Y, X) >= 0 for (Y, X) in CYCLIC_PAIRS)

    return f, g, credit, safe


def demand_relief_map(prof, m, k):
    """Compress one profile to the levels relevant for deadlock.

    When f is about to rise from t-1 to t, record the current tail relief r and
    the successor-copy demand level 2+r forced by zero incoming credit.
    """
    f, g = prof
    r = [k - g[m - j] for j in range(m + 1)]
    out = {}
    for t in range(1, f[m] + 1):
        demand_positions = [
            j for j in range(m) if f[j] == t - 1 and f[j + 1] == t
        ]
        if len(demand_positions) != 1:
            raise ValueError(
                f"prefix profile must cross level {t} exactly once: "
                f"positions={demand_positions}"
            )
        j = demand_positions[0]
        out[t] = {
            "position": j,
            "relief": r[j],
            "successor_level": r[j] + 2,
        }
    return out


def cyclic_wait_cycles(profs, m, k):
    """Return all cyclic demand/relief fixed points for copies 0->1->2->0.

    A level triple (t0,t1,t2) is a cycle when the relief available at copy c's
    demand for tc forces the successor copy to demand level t_(c+1). Each such
    cycle gives a safe dead-end at the three corresponding demand positions.
    """
    maps = [demand_relief_map(profs[c], m, k) for c in range(3)]
    cycles = []
    for t0, rec0 in maps[0].items():
        t1 = rec0["successor_level"]
        if t1 not in maps[1]:
            continue
        t2 = maps[1][t1]["successor_level"]
        if t2 not in maps[2]:
            continue
        if maps[2][t2]["successor_level"] != t0:
            continue
        cycles.append({
            "levels": (t0, t1, t2),
            "state": (
                maps[0][t0]["position"],
                maps[1][t1]["position"],
                maps[2][t2]["position"],
            ),
        })
    return maps, cycles


def analyse_triple(profs, m, k, record_deadlocks=True):
    """Full safe-state analysis for a profile triple. Returns a summary dict."""
    f, g, credit, safe = make_safe(profs, m, k)
    target = (m, m, m)

    # all safe lattice points
    all_states = [(a, b, c) for a in range(m + 1) for b in range(m + 1)
                  for c in range(m + 1)]
    safe_states = [s for s in all_states if safe(s)]
    safe_set = set(safe_states)

    # reachable safe states by monotone unit steps from (0,0,0)
    from collections import deque
    reach = set()
    if (0, 0, 0) in safe_set:
        reach.add((0, 0, 0)); dq = deque([(0, 0, 0)])
        while dq:
            s = dq.popleft()
            for c in range(3):
                if s[c] < m:
                    t = list(s); t[c] += 1; t = tuple(t)
                    if t in safe_set and t not in reach:
                        reach.add(t); dq.append(t)

    # legal moves / dead-ends among reachable
    def legal_moves(s):
        mv = []
        for c in range(3):
            if s[c] < m:
                t = list(s); t[c] += 1; t = tuple(t)
                if t in safe_set:
                    mv.append(c)
        return mv

    dead_ends = [s for s in reach if s != target and not legal_moves(s)]
    demand_maps, wait_cycles = cyclic_wait_cycles(profs, m, k)
    wait_cycle_states = {tuple(c["state"]) for c in wait_cycles}
    safe_dead_ends = {
        s for s in safe_set if s != target and not legal_moves(s)
    }

    # minimal cyclic deadlock certificates: for each dead-end, which head-pair blocks
    # each advanceable copy (the pair (c,pred c) that would go negative)
    certs = []
    if record_deadlocks:
        for s in sorted(dead_ends, key=lambda s: sum(s)):
            blockers = {}
            for c in range(3):
                if s[c] < m:
                    Y, X = c, PRED[c]
                    t = list(s); t[c] += 1; t = tuple(t)
                    blockers[c] = {"pair": (Y, X), "credit_after": credit(t, Y, X)}
            certs.append({"state": s, "sum": sum(s), "blockers": blockers,
                          "credits_here": {f"{Y}<-{X}": credit(s, Y, X)
                                           for (Y, X) in CYCLIC_PAIRS}})

    return {
        "n_safe": len(safe_states),
        "n_reachable": len(reach),
        "terminal_reachable": target in reach,
        "n_dead_ends": len(dead_ends),
        "dead_end_min_certs": certs[:5],
        "demand_relief_maps": demand_maps,
        "cyclic_wait_cycles": wait_cycles,
        "cycle_states_equal_all_safe_dead_ends": wait_cycle_states == safe_dead_ends,
        "feasible_no_deadlock": (target in reach) and (len(dead_ends) == 0),
    }


# --------------------------------------------------------------------------- #
#  (A) CAPPED AUDIT: how do the commonly enumerated shared profiles behave?
# --------------------------------------------------------------------------- #
def audit_qr19(profile_cap=4000, bound=5, k=4, time_budget=600):
    nH, aH = qr19()
    m = nH
    t0 = time.time()
    profs = optimal_profiles(nH, aH, k, cap=profile_cap)
    P = list(profs.keys())
    truncated = len(P) >= profile_cap
    print(f"[AUDIT] QR_19: distinct OPTIMAL profile pairs enumerated = {len(P)}"
          f"{' (TRUNCATED at cap)' if truncated else ' (COMPLETE)'}  "
          f"[{time.time()-t0:.1f}s]", flush=True)

    # shared single order feasible?  (min_distinct == 1)
    shared_ok = []
    shared_cycle_free = 0
    cycle_deadend_mismatches = 0
    for p in P:
        r = analyse_triple([p, p, p], m, k, record_deadlocks=False)
        if r["terminal_reachable"]:
            shared_ok.append(p)
        if not r["cyclic_wait_cycles"]:
            shared_cycle_free += 1
        if not r["cycle_states_equal_all_safe_dead_ends"]:
            cycle_deadend_mismatches += 1
    print(f"[AUDIT] shared single optimal profile feasible @bound {bound}: "
          f"{len(shared_ok)} / {len(P)} profiles", flush=True)
    print(f"[AUDIT] shared profiles with cycle-free demand/relief maps: "
          f"{shared_cycle_free} / {len(P)}; "
          f"cycle/dead-end mismatches={cycle_deadend_mismatches}", flush=True)

    # two distinct optimal profiles feasible? (sample to stay foreground-bounded)
    pair_ok = None
    if not shared_ok:
        cnt = 0
        for p, q in itertools.permutations(P[:min(len(P), 120)], 2):
            for assign in ((p, p, q), (p, q, p), (q, p, p)):
                cnt += 1
                if analyse_triple(list(assign), m, k,
                                  record_deadlocks=False)["terminal_reachable"]:
                    pair_ok = assign
                    break
            if pair_ok or time.time() - t0 > time_budget:
                break
        print(f"[AUDIT] two-distinct-profile feasible @bound {bound}: "
              f"{'YES' if pair_ok else 'none found'} "
              f"(sampled {cnt} placements over first {min(len(P),120)} profiles)", flush=True)

    return {"n_profiles": len(P), "truncated": truncated,
            "shared_feasible": len(shared_ok),
            "shared_cycle_free": shared_cycle_free,
            "cycle_deadend_mismatches": cycle_deadend_mismatches,
            "pair_feasible": bool(pair_ok)}


# --------------------------------------------------------------------------- #
#  (C) gold triple validation
# --------------------------------------------------------------------------- #
def gold_triple():
    nH, aH = qr19()
    beatsH = core.beats_matrix(nH, aH)
    gold = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data",
                                       "ground_h21_skeleton_sat.json")))
    wo = gold["witness_order"]
    sig = {c: [v % 19 for v in wo if v // 19 == c] for c in range(3)}
    return [profile_of(beatsH, tuple(sig[c])) for c in range(3)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["gold", "audit", "all"], default="all")
    ap.add_argument("--cap", type=int, default=4000)
    args = ap.parse_args()
    k, bound, m = 4, 5, 19

    if args.mode in ("gold", "all"):
        print("=== (C) QR_19 GOLD TRIPLE: credit / no-deadlock analysis ===", flush=True)
        profs = gold_triple()
        res = analyse_triple(profs, m, k)
        print(f"  safe states            = {res['n_safe']}", flush=True)
        print(f"  reachable safe states  = {res['n_reachable']}", flush=True)
        print(f"  terminal reachable     = {res['terminal_reachable']}", flush=True)
        print(f"  DEAD-ENDS (reachable)  = {res['n_dead_ends']}", flush=True)
        print(f"  cyclic wait cycles     = {len(res['cyclic_wait_cycles'])}", flush=True)
        print(f"  cycle states == all safe dead-ends = "
              f"{res['cycle_states_equal_all_safe_dead_ends']}", flush=True)
        for c, drmap in enumerate(res["demand_relief_maps"]):
            compact = {
                t: (rec["position"], rec["relief"], rec["successor_level"])
                for t, rec in drmap.items()
                if 2 <= t <= k
            }
            print(f"  demand/relief map copy {c}: "
                  f"t -> (position, relief, successor level) = {compact}", flush=True)
        print(f"  FEASIBLE_NO_DEADLOCK   = {res['feasible_no_deadlock']}  "
              f"(=> every greedy legal-step run reaches the end)", flush=True)
        if res["dead_end_min_certs"]:
            print("  minimal deadlock certs:", flush=True)
            for cdef in res["dead_end_min_certs"]:
                print("   ", cdef, flush=True)

    if args.mode in ("audit", "all"):
        print("\n=== (A) CAPPED AUDIT of common shared QR_19 profiles ===", flush=True)
        print("    NOTE: the rare gold copy-2 full raiser is a shared-order solution "
              "but is missed by this enumeration.", flush=True)
        audit_qr19(profile_cap=args.cap, bound=bound, k=k)


if __name__ == "__main__":
    main()
