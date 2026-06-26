"""H7: SOUND complete non-existence scan -> m(3) >= 11 (push to n=10).

Same sound recipe as m3_lb_scan_n9.py (connected K4-free base graphs x ALL
TT3-free orientations via the early-TT3-prune backtracking generator, keep
is_C3, exact chi capped ub=3), with TWO engineering changes forced by the
~45x base-graph blowup at n=10 (11,716,571 connected graphs on 10 vertices
vs 261,080 at n=9):

  1. STREAMING geng.  m3_lb_scan_n9.py materialised the whole connected-graph
     list (core.all_simple_graphs does proc.stdout.splitlines()).  At n=10 that
     is 11.7M graph6 lines and blows memory / wall before any scan starts.
     Here we Popen geng -c -q n and feed line-by-line into a worker Pool so
     memory stays bounded.

  2. SHARDING.  --shards S --shard I scans only base graphs whose streaming
     index satisfies idx % S == I.  This lets the full n=10 scan be split into
     S independent jobs (deterministic, disjoint, exhaustive union = full scan)
     so it can be run across sessions / machines and resumed.  --limit L caps a
     shard to its first L K4-free base graphs (for a timed throughput probe).

Soundness (unchanged from n9 scan, re-stated):
  * K4-free base-graph prune is LOSSLESS (every K4-tournament has a TT3).
  * CONNECTED base graphs lossless for the m(3) lower bound (chi_vec = max over
    weak components; a chi>=3 component on <10 vtx would contradict m(3)>=10).
  * early-TT3 prune is EXACT: every TT3-free COMPLETE orientation is still
    enumerated and handed to the SAME is_C3 / dichromatic_number oracle.
  * Sharding by idx%S is a partition of the base-graph stream: the union over
    I in 0..S-1 is the full scan, shards are disjoint, so max_chi over all
    shards = max_chi of the full scan and a witness in any shard is a global
    witness.  A NO-witness conclusion m(3)>=11 requires ALL S shards clean.

MANDATORY cross-validation: the underlying _orient generator + is_C3 +
dichromatic pipeline is byte-identical to m3_lb_scan_n9.py (imported), which
already reproduced brute counts 2186/25258/479168 and max_chi=2 at n=6,7,8.
This script additionally re-checks n in {6,7,8} when called as
    m3_lb_scan_n10.py --xval
to confirm the STREAMING + SHARDING wrapper did not perturb the counts.
"""
import sys, os, time, json, argparse, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from multiprocessing import Pool
import digraph_core as _dc

# reuse the validated, byte-identical primitives from the n9 scan
from m3_lb_scan_n9 import has_k4, _orient, worker as _n9_worker


def stream_connected_graphs(n):
    """Yield (n, edges) for every connected simple graph on n vertices, one at a
    time, via a streaming Popen of nauty geng -c -q n (bounded memory)."""
    gp = _dc._geng_path()
    proc = subprocess.Popen([gp, "-q", "-c", str(n)],
                            stdout=subprocess.PIPE, text=True)
    try:
        for line in proc.stdout:
            line = line.strip()
            if line:
                yield _dc._graph6_to_edges(line)
    finally:
        proc.stdout.close()
        proc.wait()


def gen_tasks(n, shards, shard, limit):
    """Stream connected K4-free base graphs in this shard (idx % shards ==
    shard), capped at `limit` if given.  idx counts ALL connected graphs (the
    shard partition is over the raw stream, before K4 filtering, so it is a
    fixed deterministic partition)."""
    kept = 0
    for idx, (gn, edges) in enumerate(stream_connected_graphs(n)):
        if idx % shards != shard:
            continue
        if has_k4(n, edges):
            continue
        yield (n, idx, edges)
        kept += 1
        if limit and kept >= limit:
            return


def run(n, shards, shard, limit, processes, chunksize, progress_every, out):
    t = time.time()
    max_chi = 0
    total_c3 = 0
    witness = None
    n_base = 0
    with Pool(processes=processes) as pool:
        for (mc, nc3, w) in pool.imap_unordered(
                _n9_worker, gen_tasks(n, shards, shard, limit),
                chunksize=chunksize):
            n_base += 1
            total_c3 += nc3
            if mc > max_chi:
                max_chi = mc
            if w is not None and witness is None:
                witness = w
                print(f"[n={n} shard {shard}/{shards}] chi>=3 WITNESS "
                      f"-> m(3) <= {n}: arcs= {w}", flush=True)
            if n_base % progress_every == 0:
                el = time.time() - t
                rate = n_base / el if el else 0
                print(f"  [n={n} shard {shard}/{shards}] kept_base={n_base} "
                      f"elapsed={el:.0f}s rate={rate:.1f} base/s "
                      f"max_chi={max_chi} total_c3={total_c3}", flush=True)
    wall = time.time() - t
    res = {"n": n, "shards": shards, "shard": shard, "limit": limit,
           "kept_base_graphs": n_base, "n_C3": total_c3,
           "max_chi_in_C3": max_chi, "witness": witness,
           "wall_s": round(wall, 1),
           "rate_base_per_s": round(n_base / wall, 3) if wall else None}
    print("=" * 64, flush=True)
    print(f"[n={n} shard {shard}/{shards}] kept_base={n_base} "
          f"n_C3={total_c3} max_chi={max_chi} wall={wall:.0f}s "
          f"witness={'YES' if witness else 'no'}", flush=True)
    if out:
        with open(out, "w") as f:
            json.dump(res, f, indent=2)
        print(f"[saved] {out}", flush=True)
    return res


def xval(processes):
    """Re-run n=6,7,8 through the STREAMING+SHARDING wrapper (shards=1) and
    assert the brute counts + max_chi match, confirming the wrapper is sound."""
    expect = {6: 2186, 7: 25258, 8: 479168}
    ok = True
    for n in (6, 7, 8):
        r = run(n, 1, 0, None, processes, 2, 10_000_000, None)
        good = (r["n_C3"] == expect[n] and r["max_chi_in_C3"] == 2)
        print(f"[xval n={n}] n_C3={r['n_C3']} (expect {expect[n]}) "
              f"max_chi={r['max_chi_in_C3']} (expect 2) -> "
              f"{'OK' if good else 'MISMATCH'}", flush=True)
        ok = ok and good
    print(f"\n[xval] {'ALL OK -- streaming+sharding wrapper is sound' if ok else 'MISMATCH -- DO NOT TRUST n=10'}",
          flush=True)
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("n", type=int, nargs="?", default=10)
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0,
                    help="cap kept K4-free base graphs (0 = no cap)")
    ap.add_argument("-p", "--processes", type=int, default=14)
    ap.add_argument("--chunksize", type=int, default=1)
    ap.add_argument("--progress-every", type=int, default=200)
    ap.add_argument("--out", type=str, default=None)
    ap.add_argument("--xval", action="store_true",
                    help="cross-validate the wrapper on n=6,7,8 and exit")
    args = ap.parse_args()
    if args.xval:
        xval(args.processes)
        return
    run(args.n, args.shards, args.shard, args.limit or 0,
        args.processes, args.chunksize, args.progress_every, args.out)


if __name__ == "__main__":
    main()
