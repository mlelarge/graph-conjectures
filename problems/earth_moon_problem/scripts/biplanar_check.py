#!/usr/bin/env python3
"""
Test whether a specific graph is biplanar (thickness 2) using SMS v1.0.0.

This is a layer-aware companion to `earthmoon_blowup.py`: instead of forcing
a cycle clique-blowup as the underlying graph, this script forces an
arbitrary fixed graph specified by an edge list (or by a `--join p,q`
short-hand that builds $K_p + \\overline{K_q}$).

Usage:
    biplanar_check.py --join 6,6              # K_6 + bar K_6
    biplanar_check.py --join 7,5              # K_7 + bar K_5
    biplanar_check.py --chunk-overlap 6,5,3   # K_6 chunk, 5 attached vertices, 3 also adjacent to w
    biplanar_check.py --edges 0-1,0-2,1-2     # custom edge list
    biplanar_check.py --edges 0-1,0-2,1-2 --partition 3
    biplanar_check.py --join 4,8 --no-solve --cnf-file /tmp/k4_bk8.cnf

SAT means the underlying graph admits a biplanar (thickness-2) decomposition
under the SMS Earth-Moon encoding (directed-graph layer split + thickness-2
propagator). UNSAT means it does not.
"""
import argparse
import os
import sys
from itertools import combinations

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(THIS_DIR)
SMS_DIR = os.path.join(PROJECT_DIR, "external", "sat-modulo-symmetries")
SMS_ENCODINGS = os.path.join(SMS_DIR, "encodings")

if not os.path.isdir(SMS_ENCODINGS):
    sys.exit(
        f"Error: SMS encodings directory not found at {SMS_ENCODINGS}. "
        f"See docs/spike_sms_build.md."
    )
sys.path.insert(0, SMS_DIR)
sys.path.insert(0, SMS_ENCODINGS)

from planarity import PlanarGraphBuilder, getPlanarParser  # noqa: E402


def parse_edges(edges_str):
    """Parse a comma-separated edge list like '0-1,0-2,1-2'."""
    edges = set()
    for token in edges_str.split(","):
        token = token.strip()
        if not token:
            continue
        a, b = token.split("-")
        i, j = int(a), int(b)
        if i == j:
            raise ValueError(f"self-loop not allowed: {token}")
        edges.add((min(i, j), max(i, j)))
    return edges


def join_kp_kq(p, q):
    """Return $K_p + \\overline{K_q}$ on $p + q$ vertices.

    Vertices $0..p-1$ form $K_p$; vertices $p..p+q-1$ are independent
    (form $\\overline{K_q}$); every $i < p$ is joined to every $j \\ge p$.
    """
    n = p + q
    edges = set()
    for i, j in combinations(range(p), 2):
        edges.add((i, j))
    for i in range(p):
        for j in range(p, n):
            edges.add((i, j))
    return n, edges


def chunk_overlap_graph(t, a, s):
    """Return the local (t, epsilon=1, a)-overlap graph.

    Vertices:
        0..t-1          chunk C = K_t
        t               merged vertex w, adjacent to all of C
        t+1..t+s        outside vertices attached to C and w
        t+s+1..t+a      outside vertices attached to C only

    The parameter s is the overlap between the a chunk-serving outside
    vertices and w's outside-neighbour set. The cases s=0 and s=a are the
    weak and saturated endpoints discussed in the Q0 notes.
    """
    if not (0 <= s <= a):
        raise ValueError(f"need 0 <= s <= a, got t={t}, a={a}, s={s}")
    n = t + 1 + a
    w = t
    attached = list(range(t + 1, n))
    overlap = set(attached[:s])
    edges = set()
    for i, j in combinations(range(t), 2):
        edges.add((i, j))
    for i in range(t):
        edges.add((i, w))
    for x in attached:
        for i in range(t):
            edges.add((i, x))
        if x in overlap:
            edges.add((w, x))

    partition = [t, 1]
    if s > 0:
        partition.append(s)
    if a - s > 0:
        partition.append(a - s)
    return n, edges, partition


def parse_partition(partition_str):
    return [int(x) for x in partition_str.split(",") if x.strip()]


def add_fixed_edge_constraints(builder, n, edges, partition=None):
    """Force the underlying graph of the SMS directed-graph encoding to be
    exactly the given edge set on $n$ vertices.

    Mirrors the $K_5$ / $K_{3,3}$-free + maximal-planar-$G_1$ scheme from
    candidate1/candidate2 in `encodings/planarity.py`, generalised to any
    fixed edge set. The `partition` argument is critical: it tells SMS's
    minimality-check propagator which vertex permutations are valid
    automorphisms of the fixed graph; without it SMS may over-prune via
    permutations that change the underlying graph, producing spurious
    UNSAT. Pass a list of part sizes summing to $n$ (e.g. `[6, 6]` for
    $K_6 + \\overline{K_6}$).
    """
    for i, j in sorted(edges):
        builder.append([builder.var_edge_dir(j, i)])
    for i, j in combinations(range(n), 2):
        if (i, j) not in edges:
            builder.append([-builder.var_edge_dir(i, j)])
            builder.append([-builder.var_edge_dir(j, i)])
    builder.paramsSMS["thickness2"] = "5"
    if partition is not None:
        assert sum(partition) == n, f"partition {partition} doesn't sum to {n}"
        builder.paramsSMS["initial-partition"] = " ".join(map(str, partition))


def main():
    pre = argparse.ArgumentParser(add_help=False)
    grp = pre.add_mutually_exclusive_group(required=True)
    grp.add_argument("--join", type=str,
                     help="format p,q for K_p + bar K_q")
    grp.add_argument("--chunk-overlap", type=str,
                     help="format t,a,s for a K_t chunk, a attached outside vertices, s also adjacent to w")
    grp.add_argument("--edges", type=str,
                     help="comma-separated edges like 0-1,1-2,0-2")
    pre.add_argument("--partition", type=str,
                     help="comma-separated initial partition part sizes for custom --edges")
    pre_ns, _rest = pre.parse_known_args()

    if pre_ns.join:
        p, q = map(int, pre_ns.join.split(","))
        n, edges = join_kp_kq(p, q)
        label = f"K_{p}+bar_K_{q}"
        partition = [p, q]
    elif pre_ns.chunk_overlap:
        t, a, s = map(int, pre_ns.chunk_overlap.split(","))
        n, edges, partition = chunk_overlap_graph(t, a, s)
        label = f"chunk_overlap_t{t}_a{a}_s{s}"
    else:
        edges = parse_edges(pre_ns.edges)
        n = max(max(i, j) for i, j in edges) + 1 if edges else 0
        label = "custom"
        partition = parse_partition(pre_ns.partition) if pre_ns.partition else None

    # Pre-inject -v / --directed into sys.argv for the parent parser.
    if not any(a in ("-v", "--vertices") for a in sys.argv):
        sys.argv += ["-v", str(n)]
    if "--directed" not in sys.argv:
        sys.argv += ["--directed"]

    parser = getPlanarParser()
    parser.add_argument("--join", type=str, help=argparse.SUPPRESS)
    parser.add_argument("--chunk-overlap", type=str, help=argparse.SUPPRESS)
    parser.add_argument("--edges", type=str, help=argparse.SUPPRESS)
    parser.add_argument("--partition", type=str, help=argparse.SUPPRESS)
    args, forwarding_args = parser.parse_known_args()

    args.vertices = n
    args.directed = True

    builder = PlanarGraphBuilder(
        n,
        directed=True,
        staticInitialPartition=getattr(args, "static_partition", False),
        underlyingGraph=getattr(args, "underlying_graph", False),
    )
    builder.add_constraints_by_arguments(args)
    add_fixed_edge_constraints(builder, n, edges, partition=partition)

    print(
        f"# label={label} n={n} edges={len(edges)} budget={6*n-12}",
        file=sys.stderr,
    )

    if args.no_solve:
        if args.cnf_file:
            with open(args.cnf_file, "w") as fh:
                builder.print_dimacs(fh)
        else:
            builder.print_dimacs(sys.stdout)
    else:
        builder.solveArgs(args, forwarding_args)


if __name__ == "__main__":
    main()
