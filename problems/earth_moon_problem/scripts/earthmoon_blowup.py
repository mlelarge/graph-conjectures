#!/usr/bin/env python3
"""
Parameterized SMS Earth–Moon biplanarity encoding for an arbitrary clique
blowup of an odd cycle.

Generalises KSS's `--earthmoon_candidate1` (C_5[4,4,4,4,3], 19 vertices) and
`--earthmoon_candidate2` (C_7[K_4], 28 vertices) to any odd-cycle clique
blowup specified by `--weights`. The resulting encoding is the same one KSS
ship for the two named candidates: directed-graph representation of the
biplanar decomposition with thickness-2 propagator, all underlying-graph
edges fixed, no chromatic clauses (the blowup's chromatic number is known
externally — see `cycle_blowup.py verify`).

The script imports pysms's `PlanarGraphBuilder` from the vendored SMS clone
at `<project>/external/sat-modulo-symmetries/encodings/planarity.py`. The
SMS clone must be checked out to the `v1.0.0` tag and built (`pysms` in the
project venv); see `docs/spike_sms_build.md`.

Forwarded-argument convention: anything not consumed by the planarity
parser or by `--weights` is forwarded verbatim to `smsg`/`smsd` (`-v` and
`--directed` are auto-set, do not pass them).

Usage:
    earthmoon_blowup.py --weights 3,4,4,3,5 [--args-SMS "..."] [forwarded smsg args]
    earthmoon_blowup.py --weights 4,4,4,4,3 --dry-run --cnf-file /tmp/c1.cnf

Examples:
    # The two named KSS candidates, reproduced through this wrapper:
    earthmoon_blowup.py --weights 4,4,4,4,3
    earthmoon_blowup.py --weights 4,4,4,4,4,4,4

    # The two new C_5 candidates the enumerator surfaced:
    earthmoon_blowup.py --weights 3,3,5,3,5
    earthmoon_blowup.py --weights 3,4,4,3,5
"""
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
        f"Clone the SMS repo into external/ and check out tag v1.0.0; see "
        f"docs/spike_sms_build.md."
    )
sys.path.insert(0, SMS_ENCODINGS)

from planarity import PlanarGraphBuilder, getPlanarParser  # noqa: E402

sys.path.insert(0, THIS_DIR)
from cycle_blowup import invariants  # noqa: E402


def build_partition(weights):
    """Return the per-fibre vertex partition for the blowup, vertices 0..n-1."""
    partition = []
    cursor = 0
    for w in weights:
        partition.append(list(range(cursor, cursor + w)))
        cursor += w
    return partition


def add_blowup_constraints(builder, weights):
    """Inject the candidate1/2-style fixed-graph constraints + thickness-2 propagator.

    Replicates the logic in `encodings/planarity.py`'s
    `args.earthmoon_candidate{1,2}` block, generalised to arbitrary weights.
    The partition is laid out as consecutive integer ranges by fibre order,
    matching KSS's convention.
    """
    n = sum(weights)
    if builder.n != n:
        raise ValueError(f"builder vertex count {builder.n} != sum(weights) {n}")
    if not builder.directed:
        raise ValueError("blowup encoding requires --directed")

    partition = build_partition(weights)
    edges = set()
    for fibre in partition:
        for i, j in combinations(fibre, 2):
            edges.add((i, j))
    L = len(partition)
    for k in range(L - 1):
        for u in partition[k]:
            for v in partition[k + 1]:
                edges.add((u, v))
    for u in partition[0]:
        for v in partition[-1]:
            edges.add((u, v))

    for i, j in sorted(edges):
        builder.append([builder.var_edge_dir(j, i)])
    for i, j in combinations(range(n), 2):
        if (i, j) not in edges:
            builder.append([-builder.var_edge_dir(i, j)])
            builder.append([-builder.var_edge_dir(j, i)])

    builder.paramsSMS["thickness2"] = "5"
    builder.paramsSMS["initial-partition"] = " ".join(str(len(P)) for P in partition)


def main():
    # Pre-extract --weights so we can auto-inject -v <n> for the parent parser,
    # which requires --vertices.
    import argparse as _argparse

    pre = _argparse.ArgumentParser(add_help=False)
    pre.add_argument("--weights", required=True)
    pre_ns, _rest = pre.parse_known_args()
    weights = tuple(int(x) for x in pre_ns.weights.split(","))
    n = sum(weights)
    if not any(a in ("-v", "--vertices") for a in sys.argv):
        sys.argv += ["-v", str(n)]

    parser = getPlanarParser()
    parser.add_argument(
        "--weights",
        required=True,
        help="comma-separated clique-fibre sizes for the cycle blowup, e.g. 3,4,4,3,5",
    )
    args, forwarding_args = parser.parse_known_args()

    inv = invariants(weights)
    assert inv["n"] == n

    print(
        f"# weights={weights} L={inv['L']} n={n} m={inv['m']} "
        f"omega={inv['omega']} alpha={inv['alpha']} chi={inv['chi']} "
        f"slack={inv['edge_slack']}",
        file=sys.stderr,
    )

    args.vertices = n
    args.directed = True

    builder = PlanarGraphBuilder(
        n,
        directed=True,
        staticInitialPartition=getattr(args, "static_partition", False),
        underlyingGraph=getattr(args, "underlying_graph", False),
    )
    builder.add_constraints_by_arguments(args)
    add_blowup_constraints(builder, weights)

    # Dispatch on --no-solve mirrors pysms.graph_builder's __main__: if set,
    # dump DIMACS to --cnf-file (or stdout) and skip smsg.
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
