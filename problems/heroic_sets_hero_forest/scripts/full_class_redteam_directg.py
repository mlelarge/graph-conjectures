"""FAST full-class red-team for Conjecture 6.2 over Forb_ind(K2_digon, ->C3, S2+),
using nauty `directg -o` for ISO-FREE orientation enumeration (no duplicate iso
classes, ~4x fewer than naive all-orientations) and a tight in-class filter so the
SAT dicolouring solver is only invoked on genuine in-class members.

Orientations of simple graphs are automatically digon-free (K2_digon-free).
For each iso-class we test induced ->C3-free AND S2+-free; survivors are the FULL
class. H1 predicts every survivor is 2-dicolourable; we flag any with chi_d>=3
(i.e. NOT 2-dicolourable) -- a SOUND DISPROOF of Conj 6.2.

Fast in-class checks (H has 3 vertices, so do it locally, not perm(n,3)):
  * S2+-free  <=> for every vertex x, its out-neighbourhood N+(x) induces a
                  TOURNAMENT (every pair of out-neighbours is adjacent).
  * ->C3-free <=> no directed 3-cycle x->y->z->x.

Pipeline: geng n | directg -o -s part/parts -T  ->  parse (nv ne edges)  ->
filter  ->  is_k_dicolourable(...,2). Parallelised by directg's -s split.

Modes:
  count <n> [parts]                : just enumerate+filter, report in-class count
                                     & confirm 2-dicolourable (no witness search end)
  shard <n> <part> <parts>         : process one directg shard, print JSON
  run <n> [parts]                  : spawn `parts` shards in parallel, merge.
"""
import sys, json, subprocess, os, itertools, multiprocessing as mp

_ENGINE_LIB = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine", "lib")
if _ENGINE_LIB not in sys.path:
    sys.path.insert(0, _ENGINE_LIB)
import digraph_core as dc  # noqa: E402

GENG = "/opt/homebrew/bin/geng"
DIRECTG = "/opt/homebrew/bin/directg"


def parse_T_stream(proc_stdout):
    """directg -T emits lines: 'nv ne  v0 w0 v1 w1 ...' (arc v->w pairs)."""
    for line in proc_stdout:
        line = line.strip()
        if not line:
            continue
        toks = line.split()
        nv = int(toks[0]); ne = int(toks[1])
        nums = list(map(int, toks[2:]))
        arcs = [(nums[2 * i], nums[2 * i + 1]) for i in range(ne)]
        yield nv, arcs


def in_class(n, arcs):
    """True iff (n,arcs) is in Forb_ind(K2_digon, ->C3, S2+).
    digon-free is guaranteed by directg -o (one direction per edge)."""
    outadj = [set() for _ in range(n)]
    adj = [set() for _ in range(n)]   # underlying adjacency (either direction)
    for (u, v) in arcs:
        outadj[u].add(v)
        adj[u].add(v); adj[v].add(u)
    # S2+-free: every out-neighbourhood induces a tournament (pairwise adjacent)
    for x in range(n):
        nb = list(outadj[x])
        for i in range(len(nb)):
            for j in range(i + 1, len(nb)):
                a, b = nb[i], nb[j]
                if b not in adj[a]:        # a,b both out-neighbours of x, non-adjacent
                    return False            # => induced S2+ on {x,a,b}
    # ->C3-free: no directed triangle x->y->z->x
    for x in range(n):
        for y in outadj[x]:
            for z in outadj[y]:
                if x in outadj[z]:
                    return False
    return True


def shard(n, part, parts):
    """Process one directg shard; return dict with counts + any witness."""
    p1 = subprocess.Popen([GENG, "-q", str(n)], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(
        [DIRECTG, "-q", "-o", "-T", f"-s{part}/{parts}"],
        stdin=p1.stdout, stdout=subprocess.PIPE, text=True, bufsize=1 << 20)
    p1.stdout.close()
    in_cnt = 0
    total = 0
    maxchi = 0
    witness = None
    for (nv, arcs) in parse_T_stream(p2.stdout):
        total += 1
        if not in_class(nv, arcs):
            continue
        in_cnt += 1
        # H1: predict 2-dicolourable.  Flag any that is NOT.
        if dc.is_k_dicolourable(nv, arcs, 2):
            if maxchi < 2:
                maxchi = 2
        else:
            # chi_d >= 3 -> SOUND DISPROOF.  Get exact value too.
            chi = dc.dichromatic_number(nv, arcs)
            witness = {"n": nv, "arcs": arcs, "chi_d": chi}
            maxchi = max(maxchi, chi)
            break
    p2.stdout.close()
    p2.wait()
    p1.wait()
    return {"n": n, "part": part, "parts": parts,
            "total_oriented": total, "in_class": in_cnt,
            "max_chi_d": maxchi, "witness": witness}


def _shard_worker(args):
    return shard(*args)


def run(n, parts):
    jobs = [(n, p, parts) for p in range(parts)]
    with mp.Pool(processes=min(parts, os.cpu_count() or 1)) as pool:
        results = pool.map(_shard_worker, jobs)
    total = sum(r["total_oriented"] for r in results)
    in_cnt = sum(r["in_class"] for r in results)
    maxchi = max(r["max_chi_d"] for r in results)
    witness = next((r["witness"] for r in results if r["witness"]), None)
    return {"label": f"directg full-class exhaustive n={n}",
            "parts": parts,
            "total_oriented_isofree": total,
            "in_class_members": in_cnt,
            "max_chi_d": maxchi,
            "violation": witness}


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "shard":
        n = int(sys.argv[2]); part = int(sys.argv[3]); parts = int(sys.argv[4])
        print(json.dumps(shard(n, part, parts), indent=2))
    elif mode == "run":
        n = int(sys.argv[2])
        parts = int(sys.argv[3]) if len(sys.argv) > 3 else (os.cpu_count() or 4)
        print(json.dumps(run(n, parts), indent=2))
    elif mode == "count":
        n = int(sys.argv[2])
        parts = int(sys.argv[3]) if len(sys.argv) > 3 else (os.cpu_count() or 4)
        print(json.dumps(run(n, parts), indent=2))
