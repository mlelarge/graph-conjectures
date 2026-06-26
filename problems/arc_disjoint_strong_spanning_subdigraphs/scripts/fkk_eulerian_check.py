"""H4 / FKK-bridge red-team: does every Eulerian lambda>=3 simple digraph admit
a cycle decomposition whose cycle-HYPERGRAPH is 2-partition-connected?

Bridge claim under test (UNIVERSAL form): every Eulerian 3-arc-strong digraph D
has at least ONE directed-cycle decomposition C (arc-partition into directed
cycles, guaranteed to exist by Veblen since D is Eulerian) such that the
hypergraph H(C) with one hyperedge per cycle (= the vertex set of that cycle)
is 2-partition-connected:
    for EVERY partition P of V,  #{cycles meeting >= 2 parts} >= 2*(|P|-1).

This is the FKK 2-partition-connectivity precondition; if it holds, FKK splits
C into two classes each spanning+connected, and (because each part is a union
of directed cycles in which every arc lies on a cycle) each part is STRONG ->
SAD with constant lambda.

CONFIRM: every Eulerian lambda>=3 instance in the generic n<=NMAX universe has a
witness decomposition.  KILL: one instance where EXHAUSTIVE enumeration of all
directed-cycle decompositions finds NONE 2-partition-connected.

Input universe: geng -d3 n | directg -T  (canonical, duplicate-free simple
digraphs whose underlying graph has min degree >= 3), filtered to Eulerian AND
lambda^arc >= 3 by the oracle.  Run per n; we drive geng/directg from here.

For each refuted instance we also oracle-SAD-decide D (secondary record: the
reduction is one-way sufficient, so a refuted D may still be SAD via non-cycle
parts).
"""
import sys, os, json, time, subprocess, itertools, random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oracle

GENG = "/opt/homebrew/bin/geng"
DIRECTG = "/opt/homebrew/bin/directg"


# --------------------------------------------------------------------------- #
#  Cycle-decomposition machinery on a multiset of arcs
# --------------------------------------------------------------------------- #

def is_eulerian_arcs(n, arcs):
    """in-deg == out-deg at every vertex and (weakly) the support touches all
    arcs' vertices; strong connectivity is checked separately via the oracle."""
    indeg = [0] * n
    outdeg = [0] * n
    for u, v in arcs:
        outdeg[u] += 1
        indeg[v] += 1
    return all(indeg[i] == outdeg[i] for i in range(n))


def all_cycle_decompositions(n, arcs, cap=200000):
    """Yield every partition of the arc MULTISET into directed cycles.

    A directed-cycle decomposition: repeatedly, starting from the lowest
    remaining arc, walk forward choosing each next arc out of the current head,
    until we return to the start vertex -> one cycle; recurse on the rest.
    Backtracking over all choices enumerates ALL decompositions (Eulerian
    guarantees >=1).  `cap` bounds the number of decompositions explored.

    Arcs are represented as a list; we track availability by index.
    yields: list of cycles, each cycle = list of vertices (closed walk, the
    return-to-start vertex omitted so the cycle's vertex SET is set(cycle)).
    """
    arcs = list(arcs)
    m = len(arcs)
    # out-adjacency: vertex -> list of (arc_index, head)
    out_by = [[] for _ in range(n)]
    for i, (u, v) in enumerate(arcs):
        out_by[u].append((i, v))
    used = [False] * m
    count = [0]

    def lowest_unused():
        for i in range(m):
            if not used[i]:
                return i
        return None

    def walk_cycles(decomp):
        if count[0] > cap:
            return
        start_arc = lowest_unused()
        if start_arc is None:
            count[0] += 1
            yield [list(c) for c in decomp]
            return
        su, sv = arcs[start_arc]
        start_vertex = su
        # build one cycle starting with start_arc, backtracking over arc choices
        # state: current head, path-vertices, used-arc indices for this cycle
        def extend(cur, path_arcs, path_verts):
            if count[0] > cap:
                return
            if cur == start_vertex and path_arcs:
                # completed a directed cycle
                for ai in path_arcs:
                    used[ai] = True
                decomp.append(path_verts[:])
                yield from walk_cycles(decomp)
                decomp.pop()
                for ai in path_arcs:
                    used[ai] = False
                return
            for ai, head in out_by[cur]:
                if used[ai] or ai in path_arcs:
                    continue
                path_arcs.append(ai)
                path_verts.append(cur)
                yield from extend(head, path_arcs, path_verts)
                path_arcs.pop()
                path_verts.pop()

        yield from extend(start_vertex, [start_arc] and [], [])
        # NOTE: we must seed extend with the forced first arc = start_arc, so:

    # The above had a seeding bug; reimplement cleanly:
    return _all_decomps_clean(n, arcs, out_by, cap)


def _all_decomps_clean(n, arcs, out_by, cap):
    m = len(arcs)
    used = [False] * m
    count = [0]
    results = []

    def lowest_unused():
        for i in range(m):
            if not used[i]:
                return i
        return None

    def rec_decomp(decomp):
        if count[0] > cap:
            return
        s = lowest_unused()
        if s is None:
            count[0] += 1
            results.append([list(c) for c in decomp])
            return
        su, _ = arcs[s]
        start_vertex = su
        # enumerate all simple directed cycles through arc s, returning to su
        stack = [(s, su)]  # (arc_index, head_so_far)

        def extend(path_arcs, path_verts, cur):
            if count[0] > cap:
                return
            if cur == start_vertex and path_arcs:
                for ai in path_arcs:
                    used[ai] = True
                decomp.append(path_verts[:])
                rec_decomp(decomp)
                decomp.pop()
                for ai in path_arcs:
                    used[ai] = False
                return
            for ai, head in out_by[cur]:
                if used[ai] or ai in path_arcs:
                    continue
                # avoid revisiting an interior vertex (simple cycle) except closing
                if head in path_verts and head != start_vertex:
                    continue
                path_arcs.append(ai)
                path_verts.append(cur)
                extend(path_arcs, path_verts, head)
                path_arcs.pop()
                path_verts.pop()

        # force first arc = s
        _, sh = arcs[s]
        extend([s], [su], sh)

    rec_decomp([])
    return results


# --------------------------------------------------------------------------- #
#  2-partition-connectivity of the cycle-hypergraph
# --------------------------------------------------------------------------- #

def partitions(collection):
    """All set-partitions of a list (Bell number many)."""
    collection = list(collection)
    if len(collection) == 1:
        yield [collection]
        return
    first = collection[0]
    for smaller in partitions(collection[1:]):
        for i, subset in enumerate(smaller):
            yield smaller[:i] + [[first] + subset] + smaller[i + 1:]
        yield [[first]] + smaller


def is_2_partition_connected(n, cycle_vertex_sets):
    """H(C) hyperedges = cycle vertex sets.  2-partition-connected iff for every
    partition P of V, #hyperedges crossing (meeting >=2 parts) >= 2(|P|-1)."""
    verts = list(range(n))
    for P in partitions(verts):
        part_of = {}
        for idx, block in enumerate(P):
            for v in block:
                part_of[v] = idx
        kparts = len(P)
        if kparts == 1:
            continue
        crossing = 0
        for hs in cycle_vertex_sets:
            blocks = set(part_of[v] for v in hs)
            if len(blocks) >= 2:
                crossing += 1
        if crossing < 2 * (kparts - 1):
            return False
    return True


def has_2pc_decomposition(n, arcs, dec_cap=200000, max_decs_test=200000):
    """Return (found, n_decs_examined). True if SOME directed-cycle decomposition
    has a 2-partition-connected cycle-hypergraph."""
    decs = all_cycle_decompositions(n, arcs, cap=dec_cap)
    if not decs:
        return None, 0  # no decomposition found (shouldn't happen if Eulerian)
    examined = 0
    for dec in decs:
        examined += 1
        if examined > max_decs_test:
            break
        cyc_sets = [set(c) for c in dec]
        if is_2_partition_connected(n, cyc_sets):
            return True, examined
    return False, examined


# --------------------------------------------------------------------------- #
#  Driver: generate universe, filter Eulerian + lambda>=3, test bridge
# --------------------------------------------------------------------------- #

def iter_universe(n):
    """Yield (nv, arcs) over geng -d3 n | directg -T."""
    geng = subprocess.Popen([GENG, "-d3", str(n)], stdout=subprocess.PIPE)
    directg = subprocess.Popen([DIRECTG, "-T"], stdin=geng.stdout,
                               stdout=subprocess.PIPE, text=True)
    geng.stdout.close()
    for line in directg.stdout:
        line = line.strip()
        if not line:
            continue
        toks = line.split()
        nv = int(toks[0]); ne = int(toks[1])
        nums = list(map(int, toks[2:]))
        arcs = [(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]
        assert len(arcs) == ne
        yield nv, arcs
    directg.wait()
    geng.wait()


def main():
    nmax = 6
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--nmax":
            nmax = int(args[i + 1])
    t0 = time.time()
    per_n = {}
    all_refuted = []
    for n in range(3, nmax + 1):
        n_euler_l3 = 0
        n_witness = 0
        n_refuted = 0
        n_nodecomp = 0
        for nv, arcs in iter_universe(n):
            if not is_eulerian_arcs(nv, arcs):
                continue
            lam = oracle.arc_connectivity(nv, arcs)
            if lam < 3:
                continue
            # strong connectivity is implied by lambda>=3; confirm Eulerian
            # (oracle's is_eulerian needs strong-conn which lam>=3 gives)
            n_euler_l3 += 1
            found, examined = has_2pc_decomposition(nv, arcs)
            if found is None:
                n_nodecomp += 1
            elif found:
                n_witness += 1
            else:
                n_refuted += 1
                # secondary: SAD-decide D itself
                r = oracle.check_construction(nv, arcs, cross_check=True)
                all_refuted.append({
                    "n": nv, "lambda": lam,
                    "arcs": [list(a) for a in arcs],
                    "decs_examined": examined,
                    "sad": r["sad"], "cross_check": r.get("cross_check"),
                })
        per_n[n] = {
            "eulerian_lambda_ge3": n_euler_l3,
            "with_2pc_witness": n_witness,
            "refuted": n_refuted,
            "no_decomposition_found": n_nodecomp,
        }
    summary = {
        "nmax": nmax,
        "per_n": per_n,
        "total_refuted": len(all_refuted),
        "refuted_instances": all_refuted,
        "elapsed_s": round(time.time() - t0, 2),
        "BRIDGE_holds": len(all_refuted) == 0,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
