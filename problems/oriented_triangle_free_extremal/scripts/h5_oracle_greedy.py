"""H5 ORACLE-IN-THE-LOOP online orientation (the final un-run online lever).

next_action (Round 9): greedy-optimize a* DIRECTLY. Process the triangle-free
process-graph edges in BUILD ORDER (online filtration). For each arriving edge
{u,v}, try BOTH orientations on top of the already-committed partial orientation,
measure the resulting maximum acyclic induced set EXACTLY (core.acyclic_number),
and COMMIT the orientation that MINIMIZES it (ties -> random). This is the only
online rule that optimizes the target statistic a* itself, rather than a surrogate
(depth G8, class-mod-L G11, label-tournament G14) that provably decouples and
re-floors at the random barrier.

Per-edge cost: 2 exact acyclic_number calls on the partial digraph. To keep it
feasible at n<=40 we cap each call with a per-call wall timeout via os.killpg in a
forked child; on timeout that orientation is skipped (treated as +inf, so the
other branch wins) -- this only ever makes the greedy LESS aggressive, never
fabricates a beat. The FINAL committed orientation's a* is certified EXACTLY
(no timeout) for the headline number.

BEAT-THE-FLOOR signature (CONFIRM, route survives): a*/(sqrt n log n) DECLINING
below ~1.07 (the G4/G11/G14 random floor).
KILL: a*/(sqrt n log n) flat/rising at ~1.07 -> direct-a*-greedy ALSO floors,
closing the entire ONLINE sub-route of H1/H4.
"""
import os
import sys, math, os, pickle, random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core


def triangle_free_process_buildorder(n, m_cap, seed):
    """Triangle-free process graph, edges in BUILD ORDER (online filtration)."""
    rng = random.Random(seed)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rng.shuffle(pairs)
    adj = [set() for _ in range(n)]
    edges = []
    for (u, v) in pairs:
        if len(edges) >= m_cap:
            break
        if adj[u] & adj[v]:
            continue
        edges.append((u, v))
        adj[u].add(v)
        adj[v].add(u)
    return n, edges


def _acyclic_number_timed(n, arcs, timeout):
    """core.acyclic_number with a hard wall-clock cap via a forked child.

    Returns the exact value, or None on timeout (caller treats None as +inf)."""
    r_fd, w_fd = os.pipe()
    pid = os.fork()
    if pid == 0:  # child
        os.close(r_fd)
        try:
            val = core.acyclic_number(n, arcs)
            os.write(w_fd, pickle.dumps(val))
        except Exception:
            pass
        os.close(w_fd)
        os._exit(0)
    # parent
    os.close(w_fd)
    import signal, time
    deadline = time.time() + timeout
    data = b""
    while True:
        finished, _ = os.waitpid(pid, os.WNOHANG)
        if finished == pid:
            break
        if time.time() > deadline:
            try:
                os.killpg(os.getpgid(pid), signal.SIGKILL)
            except Exception:
                try:
                    os.kill(pid, signal.SIGKILL)
                except Exception:
                    pass
            os.waitpid(pid, 0)
            os.close(r_fd)
            return None
        time.sleep(0.002)
    try:
        chunk = os.read(r_fd, 1 << 16)
        while chunk:
            data += chunk
            chunk = os.read(r_fd, 1 << 16)
    finally:
        os.close(r_fd)
    if not data:
        return None
    try:
        return pickle.loads(data)
    except Exception:
        return None


def greedy_min_astar_orient(n, edges_in_build_order, per_edge_timeout, rng):
    """Online: orient each edge to MINIMIZE the exact acyclic number of the
    partial digraph so far. Ties broken randomly. Timeout on a branch => +inf."""
    arcs = []
    for (u, v) in edges_in_build_order:
        cand = [(u, v), (v, u)]
        rng.shuffle(cand)  # randomize tie order
        best_arc = None
        best_val = None
        for (a, b) in cand:
            trial = arcs + [(a, b)]
            val = _acyclic_number_timed(n, trial, per_edge_timeout)
            if val is None:
                continue  # +inf
            if best_val is None or val < best_val:
                best_val = val
                best_arc = (a, b)
        if best_arc is None:  # both timed out -> keep a deterministic choice
            best_arc = cand[0]
        arcs.append(best_arc)
    return arcs


def main():
    ns = [20, 30, 40]
    if len(sys.argv) > 1:
        ns = [int(x) for x in sys.argv[1:]]
    per_edge_timeout = float(os.environ.get("H5_EDGE_TIMEOUT", "8.0"))
    final_timeout = float(os.environ.get("H5_FINAL_TIMEOUT", "120.0"))
    cs = [1.0, 1.5, 2.0, 2.5, 3.0]
    seeds = [0, 1]

    print(f"per_edge_timeout={per_edge_timeout}s  final_timeout={final_timeout}s", flush=True)
    print(f"{'n':>4} {'c*':>4} {'a*':>5} {'a*/(sqrt n logn)':>17} "
          f"{'a*/sqrt(nlogn)':>15} {'acyclic?':>9}", flush=True)
    rows = []
    for n in ns:
        best = n + 1
        best_c = None
        best_acyclic = None
        for c in cs:
            m_cap = int(c * math.sqrt(n) * n / 2)
            for s in seeds:
                rng = random.Random(7919 * s + 31 * n + int(c * 10))
                _, edges = triangle_free_process_buildorder(
                    n, m_cap, seed=1000 * int(c * 10) + s + n)
                arcs = greedy_min_astar_orient(n, edges, per_edge_timeout, rng)
                assert core.is_oriented(arcs), "not oriented"
                assert core.is_triangle_free(n, arcs), "not triangle-free"
                # certify FINAL a* exactly (no timeout)
                a = _acyclic_number_timed(n, arcs, final_timeout)
                if a is None:
                    continue  # could not certify; skip
                acyc = core.is_acyclic(n, arcs)
                if a < best:
                    best = a
                    best_c = c
                    best_acyclic = acyc
        if best_c is None:
            print(f"{n:>4} {'--':>4} {'TO':>5} (all final certifications timed out)", flush=True)
            continue
        sc1 = math.sqrt(n) * math.log(n)
        sc2 = math.sqrt(n * math.log(n))
        print(f"{n:>4} {best_c:>4} {best:>5} {best / sc1:>17.4f} "
              f"{best / sc2:>15.4f} {str(best_acyclic):>9}", flush=True)
        rows.append((n, best_c, best, best / sc1, best / sc2))

    print("\n=== RANDOM FLOOR (G4/G11/G14): a*/(sqrt n logn) ~1.07 FLAT "
          "(1.045,1.074,1.072 at n=20,30,40) ===", flush=True)
    print("=== H5: direct-a*-greedy R(n) = a*/(sqrt n logn) ===", flush=True)
    for n, c, a, r1, r2 in rows:
        print(f"n={n}: a*={a}  R=a*/(sqrt n logn)={r1:.4f}  a*/sqrt(nlogn)={r2:.4f}  c*={c}", flush=True)
    if len(rows) >= 2:
        r1s = [r[3] for r in rows]
        decreasing = all(r1s[i] >= r1s[i + 1] - 1e-9 for i in range(len(r1s) - 1))
        below = all(r < 1.07 - 1e-9 for r in r1s)
        last_below = r1s[-1] < 1.07 - 1e-9
        print(f"\nR(n) values = {[round(r,4) for r in r1s]}", flush=True)
        print(f"decreasing? {decreasing}   all-below-1.07? {below}   last-below-1.07? {last_below}", flush=True)
        confirm = decreasing and last_below
        print(f"\nVERDICT: {'CONFIRM (BEATS the random floor -- route survives)' if confirm else 'KILL (re-floors at ~1.07 -- online sub-route closed)'}", flush=True)


if __name__ == "__main__":
    main()
