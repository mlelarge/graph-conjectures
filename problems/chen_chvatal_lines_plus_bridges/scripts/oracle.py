"""Oracle CLI + benchmark for arXiv:1606.06011, Conjecture 2.2
(Beaudou-Kahn-Rochet, "A new class of graphs that satisfies the
Chen-Chvatal Conjecture").

Conjecture 2.2:  there is a FINITE set F_0 of connected graphs such that
every connected graph G not in F_0 either has a pendant edge OR satisfies
    ell(G) + br(G) >= |G|.

Exact invariants (all in core.py, no heuristics):
    ell(G) = number of distinct LINES (metric-betweenness lines, BFS metric)
    br(G)  = number of bridges (networkx)
    pendant edge present iff some vertex has degree 1.

A graph is BAD (an obstruction candidate / F_0 member) iff it is
connected, pendant-edge-free, and ell(G)+br(G) < |G|.

The disproof route flagged by the paper itself: the variant WITHOUT the
pendant-edge escape is already FALSE (replace a bridge by an arbitrarily
long path => infinitely many bad graphs).  So the live question is whether
the pendant-free bad graphs form a FINITE set.  This oracle:

  * `check <name>`           exact invariants of a named construction.
  * `scan <n> [--connected]` enumerate ALL connected graphs on n vertices
                             (geng -c) and report every BAD one (connected,
                             pendant-free, ell+br < n), with counts.
  * `landmarks`              recompute the paper's Lemma-3.1 anchors.
  * `g6 <graph6>`            invariants of one graph6 string.

The oracle is SOUND: every reported value is the exact invariant, computed
by full BFS-metric / networkx, no sampling.  A proposal that contradicts
it is killed instantly.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

import core
import constructions as C


# --------------------------------------------------------------------------- #
#  the agent workhorse: check an explicit construction
# --------------------------------------------------------------------------- #

def check_construction(n, edges, name="construction"):
    """Exactly verify and classify an explicit connected graph against
    Conjecture 2.2."""
    out = {"name": name}
    out.update(core.invariants(n, edges))
    return out


# --------------------------------------------------------------------------- #
#  enumeration: find all BAD graphs on n vertices
# --------------------------------------------------------------------------- #

def _geng_connected(n, args=()):
    """Yield (n, edges) for every connected graph on n vertices via geng -c."""
    cmd = ["geng", "-c", "-q", *args, str(n)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"geng failed: {proc.stderr}")
    for line in proc.stdout.splitlines():
        if line.strip():
            yield core.graph6_to_edges(line)


def _geng_connected_g6(n, args=()):
    """Yield (graph6_string, n, edges) for connected graphs on n vertices."""
    cmd = ["geng", "-c", "-q", *args, str(n)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"geng failed: {proc.stderr}")
    for line in proc.stdout.splitlines():
        s = line.strip()
        if s:
            nn, ee = core.graph6_to_edges(s)
            yield s, nn, ee


def scan(n, min_degree=2):
    """Enumerate all connected graphs on n vertices; report BAD ones.

    A pendant-free graph has min degree >= 2, so we let geng prune with
    `-d2` (delta>=2): this is EXACT (it cannot drop any pendant-free graph)
    and a big speedup.  Every survivor is double-checked with the exact
    has_pendant_edge predicate anyway.

    Returns a dict with counts and the list of bad graphs (graph6 + invariants).
    """
    # geng -d<min_degree>: minimum degree at least min_degree.
    args = (f"-d{min_degree}",) if min_degree else ()
    n_total = 0
    n_pendant_free = 0
    bad = []
    for g6, nn, ee in _geng_connected_g6(n, args):
        n_total += 1
        if core.has_pendant_edge(nn, ee):
            continue
        n_pendant_free += 1
        L = core.all_lines(nn, ee)
        el = len(L)
        br = core.bridges_count(nn, ee)
        if el + br < nn:
            bad.append({
                "graph6": g6,
                "n": nn,
                "m_edges": len(ee),
                "ell": el,
                "br": br,
                "ell_plus_br": el + br,
                "deficit": nn - (el + br),
            })
    return {
        "n": n,
        "geng_args": list(args),
        "n_connected_mindeg": n_total,
        "n_pendant_free": n_pendant_free,
        "n_bad": len(bad),
        "bad": bad,
    }


# --------------------------------------------------------------------------- #
#  known-value anchors (paper Lemma 3.1 + F_0)
# --------------------------------------------------------------------------- #

def landmarks():
    """Reproduce the paper's Lemma 3.1 anchors and the F_0 membership of the
    small bad graphs we can build unambiguously."""
    res = {}
    # Lemma 3.1: ell(C4)=1; ell(H)=|H|-1 for every other H in
    # F={C4,K2,3,W4,W4',K6',K8'}.  We verify the unambiguous members.
    for name in ["C4", "K23", "W4"]:
        nn, ee = C.NAMED[name]()
        el = core.ell(nn, ee)
        res[name] = {
            "n": nn, "ell": el,
            "expected_ell": 1 if name == "C4" else nn - 1,
            "matches_lemma_3_1": el == (1 if name == "C4" else nn - 1),
            "is_bad": core.is_bad(nn, ee),
        }
    return res


# --------------------------------------------------------------------------- #
#  CLI
# --------------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_chk = sub.add_parser("check", help="check a named construction")
    p_chk.add_argument("name", choices=sorted(C.NAMED))

    p_g6 = sub.add_parser("g6", help="invariants of a graph6 string")
    p_g6.add_argument("graph6")

    p_scan = sub.add_parser("scan", help="enumerate connected graphs, find BAD ones")
    p_scan.add_argument("n", type=int)
    p_scan.add_argument("--mindeg", type=int, default=2,
                        help="geng -d minimum degree prune (2 = pendant-free; exact)")
    p_scan.add_argument("--full", action="store_true",
                        help="dump every bad graph (default: also dumps, kept for symmetry)")

    sub.add_parser("landmarks", help="reproduce Lemma 3.1 / F_0 anchors")

    args = ap.parse_args()
    if args.cmd == "check":
        n, e = C.NAMED[args.name]()
        res = check_construction(n, e, name=args.name)
    elif args.cmd == "g6":
        n, e = core.graph6_to_edges(args.graph6)
        res = check_construction(n, e, name=args.graph6)
    elif args.cmd == "scan":
        res = scan(args.n, min_degree=args.mindeg)
    elif args.cmd == "landmarks":
        res = landmarks()

    print(json.dumps(res, indent=2, default=str))


if __name__ == "__main__":
    main()
