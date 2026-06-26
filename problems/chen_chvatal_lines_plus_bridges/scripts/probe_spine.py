"""Probe for H5 GEODESIC HALF-SPACE / SPINE charge route.

For every connected pendant-free graph with diam>=4 (geng -c -d2 N, filtered),
test the two finitely-checkable sub-claims of the proposed argument:

  (a) SPINE-INJECTIVITY: there exists SOME longest geodesic P = v_0..v_d
      such that phi(L_i) = min_{x in L_i} dist[x][v_d], applied to the
      d+1 spine lines L_i = line(v_0, v_i), i=0..d, takes d+1 DISTINCT
      values (so the spine lines are pairwise distinct as well).

  (b) OFF-SPINE CHARGE INJECTIVITY: for that same P, define for each
      off-spine vertex u  pi(u) = argmin_i dist[u][v_i] (smallest such i),
      and the charge  c(u) = line(u, v_{pi(u)+1}).  The map u |-> c(u)
      must be injective within each fixed pi-class.  (We require pi(u)+1 <= d
      so v_{pi(u)+1} exists; if pi(u)==d we use v_{pi(u)-1} as a fallback
      partner -- record such cases.)

PASS for a graph = (a) holds for >=1 longest geodesic AND (b) holds for
that same geodesic.

We report per N: total diam>=4 graphs, count where claim (a) holds for
SOME P, count where BOTH (a) and (b) hold for SOME common P, and dump
counterexample g6 for the first few failures of each kind.
"""
from __future__ import annotations
import json
import subprocess
import sys

import core


def longest_geodesics(dist, n, d):
    """Yield all shortest paths realizing the diameter d, as vertex lists.
    Reconstruct one geodesic per diametral pair (a,b) with dist[a][b]==d by
    greedy successor selection; yields ALL geodesics between each such pair."""
    adj = [[] for _ in range(n)]
    # rebuild adjacency from dist==1
    for u in range(n):
        for v in range(n):
            if u < v and dist[u][v] == 1:
                adj[u].append(v)
                adj[v].append(u)

    def all_paths(a, b):
        # enumerate all shortest a->b paths via DAG of distances
        results = []
        path = [a]

        def rec(cur):
            if cur == b:
                results.append(list(path))
                return
            for w in adj[cur]:
                if dist[a][w] == dist[a][cur] + 1 and dist[w][b] == dist[cur][b] - 1:
                    path.append(w)
                    rec(w)
                    path.pop()
        rec(a)
        return results

    seen_pairs = set()
    for a in range(n):
        for b in range(n):
            if a < b and dist[a][b] == d and (a, b) not in seen_pairs:
                seen_pairs.add((a, b))
                for p in all_paths(a, b):
                    yield p


def check_graph(g6, n, edges):
    dist = core.all_pairs_distances(n, edges)
    # diameter
    d = 0
    for u in range(n):
        for v in range(n):
            if dist[u][v] is not None and dist[u][v] > d:
                d = dist[u][v]
    if d < 4:
        return None  # not in scope

    geodesics = list(longest_geodesics(dist, n, d))

    spine_ok_some = False
    both_ok_some = False
    spine_fail_example = None
    charge_fail_example = None

    on_some_geo_spine_ok = False

    for P in geodesics:
        v0 = P[0]
        vd = P[-1]
        # spine lines L_i = line(v0, v_i), i=0..d
        spine_lines = [core.line_of_pair(dist, n, v0, P[i]) for i in range(len(P))]
        # phi(L) = min_{x in L} dist[x][vd]
        phis = []
        for L in spine_lines:
            phis.append(min(dist[x][vd] for x in L))
        spine_distinct_phi = (len(set(phis)) == len(phis))
        spine_lines_distinct = (len(set(spine_lines)) == len(spine_lines))

        if not spine_distinct_phi or not spine_lines_distinct:
            if spine_fail_example is None:
                spine_fail_example = {
                    "g6": g6, "n": n, "d": d, "P": list(P),
                    "phis": phis,
                    "phi_distinct": spine_distinct_phi,
                    "lines_distinct": spine_lines_distinct,
                }
            continue  # this geodesic fails (a)

        # (a) holds for this P
        on_some_geo_spine_ok = True

        # (b) off-spine charge injectivity for this same P
        Pset = set(P)
        # pi(u) = argmin_i dist[u][v_i]  (smallest index achieving min)
        charge_by_pi = {}  # pi -> dict line->u
        charge_ok = True
        local_fail = None
        for u in range(n):
            if u in Pset:
                continue
            # nearest spine index
            best_i = 0
            best_d = dist[u][P[0]]
            for i in range(1, len(P)):
                if dist[u][P[i]] < best_d:
                    best_d = dist[u][P[i]]
                    best_i = i
            pi = best_i
            partner_idx = pi + 1 if pi + 1 < len(P) else pi - 1
            partner = P[partner_idx]
            c = core.line_of_pair(dist, n, u, partner)
            bucket = charge_by_pi.setdefault(pi, {})
            if c in bucket:
                charge_ok = False
                local_fail = {
                    "g6": g6, "n": n, "d": d, "P": list(P),
                    "pi": pi, "u": u, "u_collides_with": bucket[c],
                    "partner_idx": partner_idx,
                }
                break
            bucket[c] = u

        if charge_ok:
            both_ok_some = True
            spine_ok_some = True
            return {
                "status": "PASS",
                "g6": g6, "n": n, "d": d,
            }
        else:
            if charge_fail_example is None:
                charge_fail_example = local_fail

    spine_ok_some = on_some_geo_spine_ok
    if spine_ok_some and not both_ok_some:
        return {
            "status": "SPINE_OK_CHARGE_FAIL",
            "g6": g6, "n": n, "d": d,
            "charge_fail": charge_fail_example,
        }
    if not spine_ok_some:
        return {
            "status": "SPINE_FAIL",
            "g6": g6, "n": n, "d": d,
            "spine_fail": spine_fail_example,
        }
    return {"status": "PASS", "g6": g6, "n": n, "d": d}


def run_n(N):
    cmd = ["geng", "-c", "-q", "-d2", str(N)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    total_diam4 = 0
    n_pass = 0
    n_spine_ok = 0
    spine_fails = []
    charge_fails = []
    for line in proc.stdout.splitlines():
        s = line.strip()
        if not s:
            continue
        n, edges = core.graph6_to_edges(s)
        if core.has_pendant_edge(n, edges):
            continue
        r = check_graph(s, n, edges)
        if r is None:
            continue
        total_diam4 += 1
        if r["status"] == "PASS":
            n_pass += 1
            n_spine_ok += 1
        elif r["status"] == "SPINE_OK_CHARGE_FAIL":
            n_spine_ok += 1
            if len(charge_fails) < 8:
                charge_fails.append(r)
        else:  # SPINE_FAIL
            if len(spine_fails) < 8:
                spine_fails.append(r)
    return {
        "N": N,
        "total_diam_ge4_pendant_free": total_diam4,
        "n_both_claims_hold": n_pass,
        "n_spine_claim_holds_some_geodesic": n_spine_ok,
        "n_spine_fail": total_diam4 - n_spine_ok,
        "n_charge_fail_given_spine": n_spine_ok - n_pass,
        "spine_fail_examples": spine_fails,
        "charge_fail_examples": charge_fails,
    }


if __name__ == "__main__":
    Ns = [int(x) for x in sys.argv[1:]] or [8, 9, 10]
    results = {}
    for N in Ns:
        res = run_n(N)
        results[str(N)] = res
        print(json.dumps(res, indent=2), flush=True)
    print("=== SUMMARY ===")
    print(json.dumps({n: {
        "total": r["total_diam_ge4_pendant_free"],
        "both_hold": r["n_both_claims_hold"],
        "spine_hold": r["n_spine_claim_holds_some_geodesic"],
        "spine_fail": r["n_spine_fail"],
        "charge_fail": r["n_charge_fail_given_spine"],
    } for n, r in results.items()}, indent=2))
