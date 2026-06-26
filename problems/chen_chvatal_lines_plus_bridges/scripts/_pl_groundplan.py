"""Ground-plan execution for the pl(G) = #proper-lines proposal.

For each connected pendant-free (min-deg>=2) graph with diam>=4 at order n:
  pl(G) = #{ distinct lines L with |L| < n }   (proper lines, omit >=1 vertex)
Prediction H5': pl(G) >= n for every such graph.

Also runs the depth-stratification (shell-quota) check.
"""
import sys, subprocess, itertools
from collections import deque, defaultdict

sys.path.insert(0, "scripts")
import core


def geng_g6(n, args=()):
    cmd = ["geng", "-c", "-q", *args, str(n)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"geng failed: {proc.stderr}")
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line:
            yield line


def diam_and_dist(n, edges):
    dist = core.all_pairs_distances(n, edges)
    d = max(dist[a][b] for a in range(n) for b in range(n))
    return d, dist


def proper_lines(n, edges, dist):
    """set of distinct proper lines (|L| < n)."""
    lines = set()
    for a, b in itertools.combinations(range(n), 2):
        L = core.line_of_pair(dist, n, a, b)
        if len(L) < n:
            lines.add(L)
    return lines


def run_order(n, falsify_only=False):
    min_pl = None
    n_violations = 0
    first_violation = None
    # depth stratification aggregates
    min_shell_quota_sum = None
    shell_quota_zero_example = None
    count = 0
    for g6 in geng_g6(n, args=("-d2",)):
        nn, edges = core.graph6_to_edges(g6)
        # pendant-free guaranteed by -d2 (min deg >=2). double check connected.
        d, dist = diam_and_dist(n, edges)
        if d < 4:
            continue
        count += 1
        plines = proper_lines(n, edges, dist)
        pl = len(plines)
        if min_pl is None or pl < min_pl:
            min_pl = pl
        if pl < n:
            n_violations += 1
            if first_violation is None:
                first_violation = (g6, pl, d)
        if falsify_only:
            continue
        # depth stratification per peripheral vertex v0 (ecc == d)
        ecc = [max(dist[v][u] for u in range(n)) for v in range(n)]
        # pick ALL peripheral v0; for the aggregate take the BEST (max) shell-quota sum
        # but report min over graphs of (max over v0 of quota_sum) and any shell-quota-0
        best_quota_sum_this_graph = None
        for v0 in range(n):
            if ecc[v0] != d:
                continue
            # shell of each vertex by distance from v0
            # depth(L) = max distance-from-v0 of an omitted vertex
            shell_quota = defaultdict(int)
            for L in plines:
                omitted = [u for u in range(n) if u not in L]
                depth = max(dist[v0][u] for u in omitted)  # proper => nonempty
                shell_quota[depth] += 1
            # check each non-empty shell 1..d hit by >=1 proper line of that depth
            shells_present = set()
            for u in range(n):
                shells_present.add(dist[v0][u])
            quota_sum = sum(shell_quota.values())
            # record zero-quota shells (non-empty shell k in 1..d with shell_quota[k]==0)
            zero_shells = [k for k in range(1, d + 1)
                           if k in shells_present and shell_quota.get(k, 0) == 0]
            if zero_shells and shell_quota_zero_example is None:
                shell_quota_zero_example = (g6, v0, zero_shells)
            if best_quota_sum_this_graph is None or quota_sum > best_quota_sum_this_graph:
                best_quota_sum_this_graph = quota_sum
        if best_quota_sum_this_graph is not None:
            if min_shell_quota_sum is None or best_quota_sum_this_graph < min_shell_quota_sum:
                min_shell_quota_sum = best_quota_sum_this_graph
    return {
        "n": n,
        "n_diam>=4_pendantfree": count,
        "min_pl": min_pl,
        "n_pl<n": n_violations,
        "first_violation": first_violation,
        "min_shell_quota_sum": min_shell_quota_sum,
        "shell_quota_zero_example": shell_quota_zero_example,
    }


def check_named(g6, label):
    nn, edges = core.graph6_to_edges(g6)
    d, dist = diam_and_dist(nn, edges)
    plines = proper_lines(nn, edges, dist)
    pl = len(plines)
    full_ell = core.ell(nn, edges)
    return {"g6": g6, "label": label, "n": nn, "diam": d,
            "ell": full_ell, "pl": pl, "pl>=n": pl >= nn}


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "census"
    if mode == "named":
        # G3 spine-route collapse witnesses
        for g6, lab in [("G?B@vo", "n8_G3_witness"), ("H?ABCp{", "n9_G3_witness")]:
            print(check_named(g6, lab))
    elif mode == "census":
        for n in [8, 9, 10]:
            print(run_order(n))
    elif mode == "n11":
        print(run_order(11, falsify_only=True))
