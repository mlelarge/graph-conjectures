"""Ground-test the 'proper-lines' proposal:
  pl(G) = #{ distinct lines L with |L| < n }  (lines omitting >=1 vertex)
Prediction H5': every connected pendant-free graph with diam>=4 has pl(G) >= n.

Runs the FULL census via geng for given n, restricted to pendant-free
(min-deg-2, geng -d2 guarantees min-deg>=2 hence no pendant edge) and diam>=4.
Reports min pl, count of pl<n, and any witness with pl<n.
Also runs the depth-stratification shell-quota check and the named G3 witnesses.
"""
import subprocess, sys, itertools
from collections import deque
sys.path.insert(0, "scripts")
import core

GENG = "geng"

def diameter(n, edges):
    dist = core.all_pairs_distances(n, edges)
    d = 0
    for i in range(n):
        for j in range(n):
            if dist[i][j] is None:
                return None
            d = max(d, dist[i][j])
    return d

def proper_lines(n, edges):
    """return (set of distinct lines, set of proper lines (|L|<n))."""
    dist = core.all_pairs_distances(n, edges)
    lines = set()
    for a, b in itertools.combinations(range(n), 2):
        lines.add(core.line_of_pair(dist, n, a, b))
    proper = {L for L in lines if len(L) < n}
    return lines, proper, dist

def ecc(dist, n, v):
    return max(dist[v][u] for u in range(n))

def depth_stratify(n, edges):
    """For each peripheral v0 (ecc==diam), bucket proper lines by
    depth(L)=max{ d(v0,z): z in V\\L }. Return (min_shell_quota_sum_over_peripheral,
    bool any_shell_quota_zero among the d shells 1..diam)."""
    dist = core.all_pairs_distances(n, edges)
    d = max(dist[i][j] for i in range(n) for j in range(n))
    _, proper, _ = proper_lines(n, edges)
    results = []
    any_zero = False
    for v0 in range(n):
        if ecc(dist, n, v0) != d:
            continue
        # shells reachable from v0
        buckets = {k: 0 for k in range(0, d+1)}
        for L in proper:
            omitted = [z for z in range(n) if z not in L]
            dep = max(dist[v0][z] for z in omitted)  # proper => omitted nonempty
            buckets[dep] += 1
        quota_sum = sum(buckets.values())  # == #proper lines (total)
        # check shells 1..d each get >=1 (claim 2a)
        shells_present = set()
        for u in range(n):
            shells_present.add(dist[v0][u])
        zero_shell = any(buckets[k] == 0 for k in range(1, d+1) if k in shells_present)
        if zero_shell:
            any_zero = True
        results.append(quota_sum)
    return (min(results) if results else None), any_zero

def census(n):
    cmd = [GENG, "-c", "-d2", str(n)]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    total = 0
    diam4 = 0
    min_pl = None
    n_pl_lt = 0
    witnesses = []
    min_quota = None
    zero_shell_graphs = 0
    for line in p.stdout:
        g6 = line.strip()
        if not g6:
            continue
        nn, edges = core.graph6_to_edges(g6)
        total += 1
        # geng -d2 => min deg >=2 => pendant-free already
        dm = diameter(nn, edges)
        if dm is None or dm < 4:
            continue
        diam4 += 1
        lines, proper, dist = proper_lines(nn, edges)
        pl = len(proper)
        if min_pl is None or pl < min_pl:
            min_pl = pl
        if pl < nn:
            n_pl_lt += 1
            if len(witnesses) < 5:
                witnesses.append((g6, pl, nn))
        qs, zsh = depth_stratify(nn, edges)
        if qs is not None and (min_quota is None or qs < min_quota):
            min_quota = qs
        if zsh:
            zero_shell_graphs += 1
    p.wait()
    return dict(n=n, total_pendantfree=total, diam4=diam4, min_pl=min_pl,
                n_pl_lt_n=n_pl_lt, witnesses=witnesses, min_shell_quota=min_quota,
                graphs_with_a_zero_shell=zero_shell_graphs)

def check_g6(g6):
    n, edges = core.graph6_to_edges(g6)
    pend = core.has_pendant_edge(n, edges)
    dm = diameter(n, edges)
    lines, proper, _ = proper_lines(n, edges)
    return dict(g6=g6, n=n, pendant=pend, diam=dm, ell=len(lines),
                pl=len(proper), pl_ge_n=(len(proper) >= n))

if __name__ == "__main__":
    print("== named G3 spine-route witnesses ==")
    for g6 in ["G?B@vo", "H?ABCp{"]:
        print(check_g6(g6))
    ns = [int(x) for x in sys.argv[1:]] or [8, 9, 10]
    for n in ns:
        print(f"== census n={n} (pendant-free via -d2, diam>=4) ==")
        r = census(n)
        print(r)
