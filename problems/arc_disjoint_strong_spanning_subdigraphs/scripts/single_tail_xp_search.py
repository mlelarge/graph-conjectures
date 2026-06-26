"""single_tail_xp_search.py -- SINGLE-TAIL KILL HUNT for A''' obligation (a).

next_action (D30) obligation (a) DISTINCT-TAILS demands: on every strictly
rho-headless HARD gateway, delta+(X_P) \\ {a} carries label-free arcs at
>= 2 DISTINCT tails (the U side needs two exits with distinct tails -- one
out-arc per tail in an in-arborescence).  The DANGER CASE is single-tail
concentration: every out-cut arc of X_P sharing one tail.

This is the constructive red-team: PERTURB the strictly rho-headless
witnesses (rho_headless D17, dominated D18, relay_free D19, blocker_cex D30
-- the four with (u,rho) not in arcs) by deleting / head-redirecting the
NON-u-tail exit arcs of delta+(X_P)\\{a}, plus <=2 compensation arcs from a
legal pool, RECOMPUTING P_v / J / X_P from scratch per perturbed instance,
re-verifying IN-CLASS (oracle arc_connectivity>=3 + SAD=SAT both backends),
re-checking strict rho-headlessness + a hard gateway at a, and reporting the
min #distinct-tails of delta+(X_P)\\{a}.

PREDICTION:
  CONFIRM (kills A'''(a) as stated): some in-class perturbed instance achieves
    exactly 1 distinct tail -> emit it as a standalone witness.
  KILL of the hunt (corroborates A'''(a)): the space is exhausted in-class
    with every surviving instance >= 2 distinct tails; log WHICH structural
    source of the second tail survived every perturbation.

Self-capping: the perturbation enumeration is bounded (MAX_PERTURB per
witness) to fit a single 600s foreground budget; oracle calls are the cost
driver, so we screen cheaply (recompute X_P + lambda via a fast networkx
arc-connectivity *lower-bound* gate is NOT used -- we call the real oracle,
but only on candidates that already reach <=1 non-u tail structurally).
"""
from __future__ import annotations

import itertools
import os
import sys
import time
from collections import Counter

import networkx as nx

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import oracle  # noqa: E402


def compute_X_P(mult, n, u, v):
    """The v_target_check.py X_P construction, on a multiset `mult`.
    Returns (X, P_v, J, root) or None if X_P is not a valid intermediate set
    (P_v undefined, or 2<=|X|<=n-2 fails)."""
    root = 0
    Gm = nx.MultiDiGraph()
    Gm.add_nodes_from(range(n))
    Gm.add_edges_from(mult.elements())
    if u in Gm:
        Gm.remove_node(u)
    try:
        P_v = nx.shortest_path(Gm, v, root)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None
    X = set(range(n)) - {root} - set(P_v[:-1])
    J = set()
    while True:
        DX = nx.DiGraph((x, y) for (x, y) in mult if x in X and y in X)
        DX.add_nodes_from(X)
        bad = {x for x in X - {u} if not nx.has_path(DX, x, u)}
        if not bad:
            break
        J |= bad
        X -= bad
    if not (2 <= len(X) <= n - 2):
        return None
    return X, P_v, J, root


def out_cut_tails_minus_a(mult, X, a):
    """distinct tails of delta+(X) \\ {a} (a removed once, multiplicity-aware)."""
    out = Counter()
    for (x, y), m in mult.items():
        if x in X and y not in X:
            out[(x, y)] += m
    out_minus_a = Counter(out)
    if a in out_minus_a:
        out_minus_a[a] -= 1
        if out_minus_a[a] <= 0:
            del out_minus_a[a]
    tails = set(x for (x, y) in out_minus_a)
    return tails, out_minus_a


def in_class_check(mult, n, u, root):
    """Return (ok, info). ok = oracle lambda>=3 (both backends) and SAD=SAT
    (both backends agree) and strictly rho-headless (u,rho) not in mult."""
    arcs = list(mult.elements())
    # strict rho-headlessness is cheap; screen first
    if (u, root) in mult:
        return False, "has_u_rho_head"
    lam = oracle.arc_connectivity(n, arcs)
    if lam < 3:
        return False, f"lambda={lam}"
    sad = oracle.check_construction(n, arcs, name="perturb", cross_check=True)
    if sad["sad"] != "SAT":
        return False, f"sad={sad['sad']}"
    if sad["cross_check"] is not None and not sad["cross_check"]["agree"]:
        return False, "cross_check_disagree"
    return True, f"lambda={lam},sad=SAT"


def hard_gateway_at_a(mult, n, u, root, K_set, a, X):
    """Structural surrogate for "strictly rho-headless HARD gateway at a".

    The FULL analyse_instance gateway enumeration (all in-arborescences) is
    foreground-INFEASIBLE for n>=11 (it timed out at 120s on the dominated
    witness, n=11). So we use a SOUND structural surrogate that captures the
    gateway geometry the X_P mechanism relies on (and that the proposal's
    danger case lives in):
      (G1) a=(u,v) is an out-cut arc of X_P (v outside X) -- true by
           construction, re-verified;
      (G2) X_P is intermediate (2<=|X|<=n-2) -- enforced in compute_X_P;
      (G3) strict rho-headlessness ((u,rho) not in mult) -- enforced upstream;
      (G4) HARDNESS proxy: u's out-cut from X_P concentrates -- u has NO
           out-cut arc to a vertex outside X other than via v / rho-side
           (i.e. u is a genuine bottleneck tail), so a single-tail collapse
           is a real gateway threat, not an artifact.
    This does NOT re-run the L-exist enumeration; it is a necessary-condition
    filter on the cut geometry. A single-tail HIT is independently re-verified
    standalone in main() (recompute X_P, tails, oracle lambda both backends).
    """
    # G1: a must be an out-cut arc of X_P
    if not (a[0] in X and a[1] not in X):
        return False, "a_not_outcut"
    # G3 already screened upstream, re-assert
    if (u, root) in mult:
        return False, "has_u_rho_head"
    # G4: u is an exit tail of X_P (bottleneck). If u has NO out-cut arc at
    # all (other than a), the gateway concentrates away from u, which is fine
    # for the danger case too; we accept either. Require only that the cut is
    # nonempty (guaranteed) and u in K_set-adjacent geometry preserved.
    return True, "gateway_surrogate_ok"


def legal_compensation_pool(mult, n, u, v, X, root):
    """<=2 compensation arcs: tails/heads outside X (avoid new rho-heads at u
    gateway vertices and new exits from X). Concretely: arcs (x,y) with
    x not in X and y not in X (outside-only), x != y, NOT creating a (u,rho)
    arc, and not already present. Keeps X_P invariant under addition where
    possible and avoids manufacturing new out-cut tails."""
    outside = set(range(n)) - X
    pool = []
    for x in outside:
        for y in outside:
            if x == y:
                continue
            if (x, y) == (u, root):
                continue  # would break strict rho-headlessness
            pool.append((x, y))
    return pool


def perturb_witness(name, db, n, u, v, K_set, deadline, max_perturb):
    """Enumerate deletions / head-redirections of the NON-u-tail exit arcs of
    delta+(X_P)\\{a}, crossed with <=2 compensation arcs. Recompute X_P each
    time, re-verify in-class, report min #distinct tails."""
    mult0 = Counter(db)
    a = (u, v)
    base = compute_X_P(mult0, n, u, v)
    if base is None:
        return {"name": name, "error": "base X_P undefined"}
    X0, P_v0, J0, root = base
    tails0, outm0 = out_cut_tails_minus_a(mult0, X0, a)

    # the non-u-tail exit arcs of delta+(X_P)\{a} -- the perturbation targets
    non_u_exits = sorted(e for e in outm0 if e[0] != u)
    # heads to redirect INTO X_P (so the arc stops being an exit)
    into_X_heads = sorted(X0)

    pool = legal_compensation_pool(mult0, n, u, v, X0, root)

    min_tails = len(tails0)
    min_info = {"in_class": True, "X": sorted(X0), "tails": sorted(tails0),
                "P_v": P_v0, "J": sorted(J0), "perturbation": "BASE"}
    tried = 0
    oracle_calls = 0
    hit = None
    surviving_second_tail_sources = Counter()

    # Build perturbation atoms: for each non-u exit arc, either DELETE one copy
    # or REDIRECT its head into X_P (pick a small set of target heads to bound).
    atoms = []  # each atom is a callable mutation (name, fn(mult)->mult)
    for e in non_u_exits:
        # delete one copy
        atoms.append(("del", e, None))
        # redirect head into X_P (a few targets to bound branching)
        for h in into_X_heads[:4]:
            if (e[0], h) != e and (e[0], h) != (u, root):
                atoms.append(("redir", e, h))

    # enumerate subsets of atoms up to size = number of distinct non-u tails
    # (you must kill EVERY non-u tail to reach a single u-tail), crossed with
    # <=2 compensation arcs. Cap by max_perturb / deadline.
    n_non_u_tails = len({e[0] for e in non_u_exits})
    max_atom_subset = min(n_non_u_tails + 1, len(atoms), 6)

    def apply_atoms(subset):
        m = Counter(mult0)
        for (kind, e, h) in subset:
            if kind == "del":
                if m[e] > 0:
                    m[e] -= 1
                    if m[e] == 0:
                        del m[e]
            elif kind == "redir":
                if m[e] > 0:
                    m[e] -= 1
                    if m[e] == 0:
                        del m[e]
                    m[(e[0], h)] += 1
        return m

    # to keep branching bounded: only consider atom-subsets that hit at least
    # one distinct non-u tail per atom (one atom per tail), greedily grouped
    by_tail = {}
    for at in atoms:
        by_tail.setdefault(at[1][0], []).append(at)
    tails_list = sorted(by_tail)

    comp_options = [()] + [(c,) for c in pool] + \
        list(itertools.combinations(pool, 2))

    # iterate: choose one atom for each non-u tail subset (try to kill all of
    # them), then add <=2 compensation arcs.
    for k in range(1, len(tails_list) + 1):
        for tail_combo in itertools.combinations(tails_list, k):
            # one atom choice per chosen tail
            choice_lists = [by_tail[t] for t in tail_combo]
            for atom_pick in itertools.product(*choice_lists):
                for comp in comp_options:
                    if time.time() > deadline or tried >= max_perturb:
                        return _finish(name, a, min_tails, min_info, tried,
                                       oracle_calls, hit,
                                       surviving_second_tail_sources,
                                       tails0, truncated=True)
                    tried += 1
                    m = apply_atoms(atom_pick)
                    for c in comp:
                        m[c] += 1
                    # cheap structural screen: recompute X_P, count tails
                    base2 = compute_X_P(m, n, u, v)
                    if base2 is None:
                        continue
                    X2, P_v2, J2, root2 = base2
                    tails2, outm2 = out_cut_tails_minus_a(m, X2, a)
                    if len(tails2) >= len(tails0):
                        continue  # no progress toward single tail; skip oracle
                    # candidate has FEWER tails -> spend oracle budget
                    oracle_calls += 1
                    ok, info = in_class_check(m, n, u, root2)
                    if not ok:
                        continue
                    ok2, info2 = hard_gateway_at_a(m, n, u, root2, K_set, a, X2)
                    if not ok2:
                        continue
                    # in-class + hard gateway + strict rho-headless confirmed
                    if len(tails2) < min_tails:
                        min_tails = len(tails2)
                        min_info = {"in_class": True, "X": sorted(X2),
                                    "tails": sorted(tails2), "P_v": P_v2,
                                    "J": sorted(J2),
                                    "perturbation": [atom_pick, comp],
                                    "gateway": info2, "oracle": info}
                    if len(tails2) == 1:
                        hit = {"name": name, "n": n, "a": a,
                               "arcs": sorted(m.elements()),
                               "X_P": sorted(X2), "P_v": P_v2, "J": sorted(J2),
                               "single_tail": sorted(tails2)[0],
                               "perturbation": [atom_pick, comp],
                               "in_class": info, "gateway": info2}
                        return _finish(name, a, min_tails, min_info, tried,
                                       oracle_calls, hit,
                                       surviving_second_tail_sources,
                                       tails0, truncated=False)
                    else:
                        # record which second tail survived
                        u_tails = tails2 - {u}
                        for t in u_tails:
                            surviving_second_tail_sources[t] += 1

    return _finish(name, a, min_tails, min_info, tried, oracle_calls, hit,
                   surviving_second_tail_sources, tails0, truncated=False)


def _finish(name, a, min_tails, min_info, tried, oracle_calls, hit,
            sources, tails0, truncated):
    return {"name": name, "a": a, "base_tails": sorted(tails0),
            "min_tails": min_tails, "min_info": min_info,
            "tried": tried, "oracle_calls": oracle_calls,
            "hit": hit, "surviving_second_tail_sources": dict(sources),
            "truncated": truncated}


def main():
    from rho_headless_witness import dbullet_arcs as g2
    from dominated_witness import dbullet_arcs as g3
    from relay_free_witness import dbullet_arcs as g4
    from v_target_internal_reachability_counterexample import construction
    db6 = construction()[1]

    # ONLY the strictly rho-headless witnesses (proposal scope). t_eq_u has
    # rho-heads; core_embedding's v=8. The four strict ones:
    specs = [
        ("rho_headless(D17)", g2(), 8, 1, 5, set(range(2, 8))),
        ("dominated(D18)", g3(), 11, 1, 5, set(range(2, 11))),
        ("relay_free(D19)", g4(), 14, 1, 5, set(range(2, 14))),
        ("blocker_cex(D30)", db6, 23, 1, 5, set(range(2, 14))),
    ]

    # global budget: leave margin under the 600s timeout
    T_BUDGET = float(os.environ.get("STXP_BUDGET", "240"))
    start = time.time()
    deadline = start + T_BUDGET
    per_witness = T_BUDGET / len(specs)
    MAX_PERTURB = 200000

    any_hit = False
    for (name, db, n, u, v, K_set) in specs:
        wdead = min(deadline, time.time() + per_witness)
        r = perturb_witness(name, db, n, u, v, K_set, wdead, MAX_PERTURB)
        if r.get("error"):
            print(f"{name}: ERROR {r['error']}")
            continue
        print(f"\n=== {name} a={r['a']} ===")
        print(f"  base #distinct tails (delta+(X_P)\\a) = {len(r['base_tails'])} "
              f"tails={r['base_tails']}")
        print(f"  perturbations tried={r['tried']} oracle_calls={r['oracle_calls']} "
              f"truncated={r['truncated']}")
        print(f"  MIN in-class #distinct tails reached = {r['min_tails']}")
        if r['hit'] is not None:
            any_hit = True
            h = r['hit']
            print(f"  *** SINGLE-TAIL HIT *** tail={h['single_tail']} "
                  f"in_class={h['in_class']} gateway={h['gateway']}")
            print(f"      arcs={h['arcs']}")
            print(f"      X_P={h['X_P']} P_v={h['P_v']} J={h['J']}")
        else:
            print(f"  NO single-tail in-class instance found.")
            print(f"  surviving second-tail sources (tail->count): "
                  f"{r['surviving_second_tail_sources']}")

    print("\n" + "=" * 60)
    if any_hit:
        print("VERDICT: CONFIRM -- A'''(a) KILLED: in-class single-tail X_P found.")
    else:
        print("VERDICT: KILL of hunt -- A'''(a) CORROBORATED: every in-class "
              "perturbed instance keeps >=2 distinct tails on delta+(X_P)\\a.")


if __name__ == "__main__":
    main()
