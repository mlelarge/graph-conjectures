#!/usr/bin/env python3
"""Exhaustive census of ALL semicomplete digraphs on n=4,5 (full class, up to iso)
via nauty K_n -> directg (3 orientations per edge incl. digons), SAD-decided by
the project oracle.

Tests the citation [BJY2004 / BJGY2020]: every 2-arc-strong semicomplete digraph
has a strong arc decomposition EXCEPT S4 (=C4^2, n=4). So the predicted UNSAT list
over the 2-arc-strong semicompletes is EXACTLY {S4}.
"""
import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oracle  # noqa: E402

GENG = "/opt/homebrew/bin/geng"
DIRECTG = "/opt/homebrew/bin/directg"


def gen_semicomplete(n):
    """All semicomplete digraphs on n vertices up to iso (orientations+digons of K_n)."""
    edges = n * (n - 1) // 2
    p1 = subprocess.Popen([GENG, "-q", str(n), f"{edges}:{edges}"],
                          stdout=subprocess.PIPE)
    p2 = subprocess.Popen([DIRECTG, "-T", "-q"], stdin=p1.stdout,
                          stdout=subprocess.PIPE)
    p1.stdout.close()
    out, _ = p2.communicate()
    for line in out.decode().splitlines():
        toks = line.split()
        if not toks:
            continue
        nv = int(toks[0])
        ne = int(toks[1])
        nums = list(map(int, toks[2:]))
        arcs = [(nums[2 * i], nums[2 * i + 1]) for i in range(ne)]
        assert nv == n and len(arcs) == ne
        yield arcs


def canon_key(n, arcs):
    """Identify S4 = C4^2 (digon-free? no: C4^2 has digons). Compare by oracle UNSAT
    + invariants; we just report the arc set. S4 detection: n==4, 8 arcs, 2-regular
    each direction, = C_4 squared. We flag any UNSAT and check if iso to benchmark S4."""
    return (n, tuple(sorted(arcs)))


def is_iso_S4(n, arcs):
    """C_4^2 on 4 vertices: arcs i->i+1 and i->i+2 (mod 4). 8 arcs, every vertex
    out-deg 2 in-deg 2, and it is the unique 2-arc-strong semicomplete UNSAT we expect.
    We test isomorphism by canonical degree-sequence + the known oracle S4 benchmark
    arc set, comparing up to relabeling via brute permutation (n<=5 trivial)."""
    import itertools
    # reference S4 arcs (C_4^2): i -> i+1, i -> i+2 mod 4
    ref = set()
    for i in range(4):
        ref.add((i, (i + 1) % 4))
        ref.add((i, (i + 2) % 4))
    if n != 4 or len(arcs) != 8:
        return False
    A = set(arcs)
    for perm in itertools.permutations(range(4)):
        mapped = {(perm[u], perm[v]) for (u, v) in A}
        if mapped == ref:
            return True
    return False


def run(nmax):
    print(f"=== Semicomplete-digraph census, n=4..{nmax} ===")
    grand_unsat = []
    for n in range(4, nmax + 1):
        total = 0
        n_2arcstrong = 0
        n_sat = 0
        unsat = []
        disagree = []
        for arcs in gen_semicomplete(n):
            total += 1
            lam = oracle.arc_connectivity(n, arcs)
            if lam < 2:
                continue
            n_2arcstrong += 1
            res = oracle.check_construction(n, arcs, cross_check=True)
            cc = res.get("cross_check") or {}
            if res["sad"] == "DISAGREE" or cc.get("agree") is False:
                disagree.append((arcs, res))
                continue
            if res["sad"] == "SAT":
                n_sat += 1
            elif res["sad"] == "UNSAT":
                unsat.append((n, lam, arcs))
        print(f"--- n={n}: total semicomplete iso-classes = {total}; "
              f"2-arc-strong (lambda>=2) = {n_2arcstrong}; "
              f"SAT = {n_sat}; UNSAT = {len(unsat)}; "
              f"DISAGREE = {len(disagree)}")
        for (nn, lam, arcs) in unsat:
            iso = is_iso_S4(nn, arcs)
            print(f"    UNSAT: n={nn} lambda={lam} isoS4={iso} arcs={sorted(arcs)}")
            grand_unsat.append((nn, lam, arcs, iso))
        for (arcs, res) in disagree:
            print(f"    !!! DISAGREE: arcs={sorted(arcs)} res={res}")
    print("=== SUMMARY ===")
    non_s4 = [u for u in grand_unsat if not u[3]]
    print(f"Total UNSAT 2-arc-strong semicomplete iso-classes: {len(grand_unsat)}")
    print(f"  of which iso to S4: {sum(1 for u in grand_unsat if u[3])}")
    print(f"  of which NOT S4 (would KILL citation): {len(non_s4)}")
    pass_pred = (len(grand_unsat) == 1 and grand_unsat[0][3])
    print(f"PREDICTION (UNSAT list == {{S4}}): {'CONFIRMED' if pass_pred else 'REFUTED'}")
    return grand_unsat, non_s4


if __name__ == "__main__":
    nmax = 5
    if "--nmax" in sys.argv:
        nmax = int(sys.argv[sys.argv.index("--nmax") + 1])
    run(nmax)
