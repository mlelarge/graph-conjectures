"""GROUND for the literature-reduction proposal (Round 7 candidate):
Reduce a_vec UPPER bound to R(3,t) via a_vec >= alpha(G), by running the
triangle-free process to SATURATION (no density cap), where Bohman-Keevash
say avg degree d ~ Theta(sqrt(n log n)) NOT c*sqrt(n).

Proposal CONFIRM signature:
  - alpha/sqrt(n log n) FLAT/bounded (not rising), AND
  - a_vec/alpha = O(1) bounded.
KILL signature:
  - alpha/sqrt(n log n) RISES with n (alpha super-sqrt(n log n)), OR
  - a_vec/alpha grows unboundedly.

EXACT throughout:
  alpha(G)  = exact independence number = core.acyclic_number on the BIDIRECTED graph
              (a set is acyclic in the bidirected digraph iff it is independent in G,
               since any edge becomes a 2-cycle). We verify this equivalence.
  a_vec     = exact core.acyclic_number on the best of several random orientations.

We run the process to SATURATION by setting m_cap huge.
"""
from __future__ import annotations
import os
import math, sys, random, signal, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from lit_reduction_test import triangle_free_process, random_orientation


def saturate(n, seed):
    """Run triangle-free process to full saturation (m_cap = all pairs)."""
    m_cap = n * (n - 1) // 2  # never reached; process stops at saturation
    return triangle_free_process(n, m_cap, seed=seed)


def alpha_exact_bidirected(n, edges):
    """alpha(G) via core.acyclic_number on the bidirected digraph.
    Each undirected edge {u,v} -> both (u,v) and (v,u): a 2-cycle.
    An induced acyclic set must avoid every 2-cycle => is an independent set.
    So acyclic_number(bidirected) = independence number = alpha(G)."""
    arcs = []
    for (u, v) in edges:
        arcs.append((u, v))
        arcs.append((v, u))
    return core.acyclic_number(n, arcs)


def run_with_timeout(fn, args, timeout):
    """Run fn(*args) in a child process; kill its group on timeout. Returns int or None."""
    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(r)
        os.setpgid(0, 0)
        try:
            val = fn(*args)
            os.write(w, str(val).encode())
        except Exception as e:
            os.write(w, ("ERR:" + str(e)).encode())
        finally:
            os.close(w)
            os._exit(0)
    os.close(w)
    os.setpgid(pid, pid)
    import time
    start = time.time()
    out = b""
    while True:
        if time.time() - start > timeout:
            try:
                os.killpg(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            os.waitpid(pid, 0)
            os.close(r)
            return None
        wpid, status = os.waitpid(pid, os.WNOHANG)
        if wpid == pid:
            out = os.read(r, 1 << 20)
            os.close(r)
            break
        time.sleep(0.05)
    s = out.decode()
    if s.startswith("ERR:") or s == "":
        return None
    return int(s)


def main():
    ns = [40, 60, 80, 100]
    n_seeds = 4
    n_orient = 4
    AVEC_TIMEOUT = 150  # seconds per a_vec exact call
    print(f"{'n':>4} {'seed':>4} {'dbar':>6} {'alpha':>6} {'a_vec':>6} "
          f"{'d/snln':>7} {'al/snln':>8} {'al/snlog':>9} {'av/snln':>8} {'av/al':>6}")
    rows = []
    for n in ns:
        snln = math.sqrt(n * math.log(n))         # sqrt(n log n)  (conjecture target)
        snlogn = math.sqrt(n) * math.log(n)        # sqrt(n) * log n  (P2 scale)
        for s in range(n_seeds):
            n2, edges = saturate(n, seed=4242 + 13 * s + n)
            assert core.is_triangle_free(n2, edges), "process produced a triangle!"
            d = 2 * len(edges) / n2
            alpha = alpha_exact_bidirected(n2, edges)
            # best (min) a_vec over several random orientations
            best_av = None
            for o in range(n_orient):
                arcs = random_orientation(edges, seed=999 * o + s + n)
                assert core.is_oriented(arcs)
                av = run_with_timeout(core.acyclic_number, (n2, arcs), AVEC_TIMEOUT)
                if av is None:
                    continue
                if best_av is None or av < best_av:
                    best_av = av
            av_str = str(best_av) if best_av is not None else "TIMEOUT"
            if best_av is not None:
                print(f"{n:>4} {s:>4} {d:>6.2f} {alpha:>6} {best_av:>6} "
                      f"{d/snln:>7.3f} {alpha/snln:>8.3f} {alpha/snlogn:>9.3f} "
                      f"{best_av/snln:>8.3f} {best_av/alpha:>6.3f}")
            else:
                print(f"{n:>4} {s:>4} {d:>6.2f} {alpha:>6} {av_str:>6} "
                      f"{d/snln:>7.3f} {alpha/snln:>8.3f} {alpha/snlogn:>9.3f} "
                      f"{'--':>8} {'--':>6}")
            rows.append((n, s, d, alpha, best_av, snln, snlogn))

    # aggregate per n (use min alpha and min a_vec = the extremal-leaning proxy)
    print("\n=== per-n aggregate (min over seeds) ===")
    print(f"{'n':>4} {'dbar':>6} {'alpha':>6} {'a_vec':>6} {'d/snln':>7} "
          f"{'al/snln':>8} {'al/snlog':>9} {'av/snln':>8} {'av/al':>6}")
    agg = {}
    for (n, s, d, alpha, av, snln, snlogn) in rows:
        agg.setdefault(n, []).append((d, alpha, av, snln, snlogn))
    summary = []
    for n in ns:
        ds = [r[0] for r in agg[n]]
        als = [r[1] for r in agg[n]]
        avs = [r[2] for r in agg[n] if r[2] is not None]
        snln = agg[n][0][3]; snlogn = agg[n][0][4]
        dbar = sum(ds) / len(ds)
        almin = min(als)
        avmin = min(avs) if avs else None
        av_al = (avmin / almin) if avmin is not None else None
        print(f"{n:>4} {dbar:>6.2f} {almin:>6} "
              f"{(avmin if avmin is not None else 0):>6} {dbar/snln:>7.3f} "
              f"{almin/snln:>8.3f} {almin/snlogn:>9.3f} "
              f"{(avmin/snln if avmin else 0):>8.3f} "
              f"{(av_al if av_al else 0):>6.3f}")
        summary.append((n, dbar, almin, avmin, snln, snlogn))

    print("\n=== VERDICT DIAGNOSTICS ===")
    al_snln = [(n, almin / snln) for (n, dbar, almin, avmin, snln, snlogn) in summary]
    al_snlog = [(n, almin / snlogn) for (n, dbar, almin, avmin, snln, snlogn) in summary]
    d_snln = [(n, dbar / snln) for (n, dbar, almin, avmin, snln, snlogn) in summary]
    print("alpha/sqrt(n logn): " + ", ".join(f"{n}:{r:.3f}" for n, r in al_snln)
          + f"   rise {al_snln[-1][1]/al_snln[0][1]:.3f}")
    print("alpha/(sqrtn*logn): " + ", ".join(f"{n}:{r:.3f}" for n, r in al_snlog)
          + f"   rise {al_snlog[-1][1]/al_snlog[0][1]:.3f}")
    print("dbar/sqrt(n logn) : " + ", ".join(f"{n}:{r:.3f}" for n, r in d_snln)
          + f"   rise {d_snln[-1][1]/d_snln[0][1]:.3f}")
    avs_ok = [(n, avmin) for (n, dbar, almin, avmin, snln, snlogn) in summary if avmin is not None]
    av_al = [(n, avmin / almin) for (n, dbar, almin, avmin, snln, snlogn) in summary if avmin is not None]
    av_snln = [(n, avmin / snln) for (n, dbar, almin, avmin, snln, snlogn) in summary if avmin is not None]
    if av_al:
        print("a_vec/alpha       : " + ", ".join(f"{n}:{r:.3f}" for n, r in av_al))
        print("a_vec/sqrt(nlogn) : " + ", ".join(f"{n}:{r:.3f}" for n, r in av_snln))


if __name__ == "__main__":
    main()
