"""Oracle CLI + benchmark for arXiv:2310.04265, Conjecture 3.12
(Aboulker, Aubian, Charbit, Lopes, "Clique number of tournaments").

CONJECTURE 3.12 (asymptotic, existence-of-binding-function):
  For every fixed k, the class of tournaments with twin-width <= k is
  chiVec-bounded: there is a function f with chiVec(T) <= f(omegaVec(T)) for
  every tournament T of twin-width <= k.

This is an ASYMPTOTIC claim and CANNOT be proved by finite enumeration.  The
oracle is SOUND for the DISPROOF / measurement direction: all three invariants
are exactly computable on small tournaments, and a counterexample would be a
concrete finite family with bounded tww, bounded omegaVec, growing chiVec.

Exact invariants (core.py):
  chiVec(T)   -- dichromatic number (SAT + lazy cycle; engine/lib/digraph_core)
  omegaVec(T) -- min over vertex orderings of omega(backedge graph) (exact B&B)
  tww(T)      -- twin-width via exact contraction search

The handle the paper hands us:
  S_k   = Delta(1, S_{k-1}, S_{k-1}) :  chiVec(S_k) = k, tww(S_k)=1 (k>=2),
          omegaVec(S_k) KNOWN only for k<=4 (=1,2,2,3); UNKNOWN for k>=5.
  S~_n  = Delta(S~_{n-1}, S~_{n-1}, S~_{n-1}) : tww=1, omegaVec(S~_n) >= n.

Primary measurement: extend omegaVec(S_k) beyond k=4 and track chiVec/omegaVec at
fixed twin-width.  (For the S_k family, chiVec=k and tww=1 are fixed/bounded; the
conjecture's binding function f is governed entirely by how omegaVec(S_k) grows.
If omegaVec(S_k) were ever to STAY bounded while chiVec=k grows, that family at
twin-width 1 would refute the conjecture.  The paper proves it does grow, but the
*rate* is open -- this oracle measures it.)
"""
from __future__ import annotations

import argparse
import json

import core
import constructions as C


# --------------------------------------------------------------------------- #
#  Grounding a proposed construction
# --------------------------------------------------------------------------- #

def check_construction(n, arcs, name="construction",
                       compute_chi=True, compute_omega=True, compute_tww=True,
                       tww_ub=None, chi_ub=None):
    """Exactly verify and measure an explicit tournament.

    Reports the three invariants of Conjecture 3.12 so a proposal can be scored:
    a counterexample needs tww and omegaVec bounded while chiVec grows.
    """
    is_tour = core.is_tournament(n, arcs)
    out = {
        "name": name, "n": n, "m_arcs": len(arcs),
        "is_tournament": is_tour,
    }
    if not is_tour:
        out["error"] = "NOT A TOURNAMENT (need exactly one arc per pair, no 2-cycles)"
        return out
    if compute_chi:
        out["chi_vec"] = core.chi_vec(n, arcs, ub=chi_ub)
    if compute_omega:
        out["omega_vec"] = core.omega_vec(n, arcs)
    if compute_tww:
        out["tww"] = core.tww(n, arcs, ub=tww_ub)
    if compute_chi and compute_omega:
        out["chi_over_omega"] = out["chi_vec"] / out["omega_vec"] if out["omega_vec"] else None
    return out


# --------------------------------------------------------------------------- #
#  Family measurement
# --------------------------------------------------------------------------- #

def measure_S(k, **kw):
    n, a = C.S(k)
    return check_construction(n, a, name=f"S_{k}", **kw)


def measure_S_tilde(m, **kw):
    n, a = C.S_tilde(m)
    return check_construction(n, a, name=f"S~_{m}", **kw)


# --------------------------------------------------------------------------- #
#  Exact small-n: max chiVec at given (tww-bounded) class -- truth scan
# --------------------------------------------------------------------------- #

def scan_small_tournaments(n, tww_max=None, omega_max=None, want_chi_ge=None,
                           limit=None, verbose=False):
    """Enumerate ALL tournaments on n vertices (via geng + orientations of K_n is
    too many; instead enumerate via nauty 'gentourng' if available, else all
    orientations of the complete graph for tiny n) and report, for each, the
    triple (tww, omegaVec, chiVec).  Optionally filter to a tww/omega bound and
    surface any with chiVec >= want_chi_ge -- a local search for the conjecture's
    contrapositive (bounded tww + bounded omega + large chi).

    Small n only (the tournament count explodes: 1,1,2,4,12,56,456,6880,... for
    n=1..8 up to isomorphism).
    """
    results = []
    found = []
    cnt = 0
    for (tn, arcs) in _all_tournaments(n):
        cnt += 1
        if limit is not None and cnt > limit:
            break
        w = core.tww(n, arcs, ub=(tww_max + 1 if tww_max is not None else None))
        if tww_max is not None and w > tww_max:
            continue
        om = core.omega_vec(n, arcs)
        if omega_max is not None and om > omega_max:
            continue
        ch = core.chi_vec(n, arcs)
        rec = {"tww": w, "omega_vec": om, "chi_vec": ch, "arcs": list(arcs)}
        results.append(rec)
        if want_chi_ge is not None and ch >= want_chi_ge:
            found.append(rec)
        if verbose and cnt % 200 == 0:
            print(f"  ..scanned {cnt} tournaments")
    return {"n": n, "n_tournaments_scanned": cnt, "kept": len(results),
            "found_chi_ge": found if want_chi_ge is not None else None,
            "max_chi_among_kept": max((r["chi_vec"] for r in results), default=0)}


def _all_tournaments(n):
    """Yield (n, arcs) for tournaments on n vertices.  Uses nauty 'gentourng' if
    on PATH (one per isomorphism class); otherwise all orientations of K_n."""
    import subprocess
    try:
        proc = subprocess.run(["gentourng", "-q", str(n)],
                              capture_output=True, text=True)
        if proc.returncode == 0 and proc.stdout.strip():
            for line in proc.stdout.splitlines():
                arcs = _parse_gentourng_line(n, line)
                if arcs is not None:
                    yield n, arcs
            return
    except FileNotFoundError:
        pass
    # fallback: all orientations of K_n (NOT up to iso; only for tiny n)
    import itertools
    edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    m = len(edges)
    for mask in range(1 << m):
        arcs = [(u, v) if (mask >> i) & 1 else (v, u)
                for i, (u, v) in enumerate(edges)]
        yield n, arcs


def _parse_gentourng_line(n, line):
    """gentourng outputs, for each tournament, the upper-triangle adjacency as a
    bit string row by row.  We decode arc i->j (i<j) iff bit set, else j->i."""
    s = line.strip()
    if not s:
        return None
    bits = [c for c in s if c in "01"]
    if len(bits) != n * (n - 1) // 2:
        return None
    arcs = []
    idx = 0
    for i in range(n):
        for j in range(i + 1, n):
            if bits[idx] == "1":
                arcs.append((i, j))
            else:
                arcs.append((j, i))
            idx += 1
    return arcs


# --------------------------------------------------------------------------- #
#  CLI
# --------------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_s = sub.add_parser("S", help="measure S_k = Delta(1,S_{k-1},S_{k-1})")
    p_s.add_argument("k", type=int)
    p_s.add_argument("--no-omega", action="store_true",
                     help="skip omegaVec (expensive for k>=5)")

    p_st = sub.add_parser("Stilde", help="measure S~_m = Delta(S~,S~,S~)")
    p_st.add_argument("m", type=int)
    p_st.add_argument("--no-omega", action="store_true")

    p_scan = sub.add_parser("scan", help="scan all tournaments on n vertices")
    p_scan.add_argument("n", type=int)
    p_scan.add_argument("--tww-max", type=int, default=None)
    p_scan.add_argument("--omega-max", type=int, default=None)
    p_scan.add_argument("--chi-ge", type=int, default=None)
    p_scan.add_argument("-v", "--verbose", action="store_true")

    args = ap.parse_args()
    if args.cmd == "S":
        res = measure_S(args.k, compute_omega=not args.no_omega)
    elif args.cmd == "Stilde":
        res = measure_S_tilde(args.m, compute_omega=not args.no_omega)
    elif args.cmd == "scan":
        res = scan_small_tournaments(args.n, tww_max=args.tww_max,
                                     omega_max=args.omega_max,
                                     want_chi_ge=args.chi_ge,
                                     verbose=args.verbose)
    print(json.dumps(res, indent=2, default=str))


if __name__ == "__main__":
    main()
