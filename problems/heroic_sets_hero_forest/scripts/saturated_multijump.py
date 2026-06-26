"""SMC(n,J) saturated multi-jump circulant builder + sweep.

build(n,J): circulant on Z_n with jump set J (|J|>=2). For each vertex i,
saturate its out-neighbourhood N+(i) into a transitive tournament by orienting
each missing pair forward (ascending by (v-i) mod n). Reject if any saturation
would create a digon (reverse arc already present).
"""
import sys, json, itertools
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import core


def build(n, J):
    arcs = set()
    for i in range(n):
        for j in J:
            arcs.add((i, (i + j) % n))
    # saturate each out-neighbourhood into a transitive tournament
    for i in range(n):
        Np = sorted([v for (u, v) in arcs if u == i], key=lambda v: (v - i) % n)
        for a in range(len(Np)):
            for b in range(a + 1, len(Np)):
                u, v = Np[a], Np[b]
                if (u, v) in arcs:
                    continue
                if (v, u) in arcs:
                    return None  # would create a digon
                arcs.add((u, v))
    # final digon check (saturation could have introduced a reverse later)
    for (u, v) in arcs:
        if (v, u) in arcs:
            return None
    # no self loops
    for (u, v) in arcs:
        if u == v:
            return None
    return sorted(arcs)


def in_class(n, arcs):
    """oriented & ->C3-free & S2+-free, via core."""
    if not core.is_oriented(arcs):
        return False
    D = (n, list(arcs))
    if core.contains_induced(D, core.C3()):
        return False
    if core.contains_induced(D, core.S2_plus()):
        return False
    return True


def main():
    n_lo = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    n_hi = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    chi_d_max_n = int(sys.argv[3]) if len(sys.argv) > 3 else 18
    overall_max = 0
    first_witness = None
    for n in range(n_lo, n_hi + 1):
        inclass = 0
        builtcount = 0
        maxchi = 0
        for r in (2, 3):
            if r > n - 1:
                continue
            for rest in itertools.combinations(range(2, n), r - 1):
                J = (1,) + rest  # canonical: 1 in J
                D = build(n, J)
                if D is None:
                    continue
                builtcount += 1
                if not in_class(n, D):
                    continue
                inclass += 1
                if n <= chi_d_max_n:
                    cd = core.dichromatic_number(n, D)
                    if cd > maxchi:
                        maxchi = cd
                    if cd >= 3 and first_witness is None:
                        first_witness = (n, list(J), D, cd)
        if n <= chi_d_max_n:
            overall_max = max(overall_max, maxchi)
            print(f"n={n}: built={builtcount} in_class={inclass} max_chi_d={maxchi}", flush=True)
        else:
            print(f"n={n}: built={builtcount} in_class={inclass} (chi_d skipped)", flush=True)
    print("OVERALL max_chi_d (n<=%d) = %d" % (chi_d_max_n, overall_max))
    if first_witness:
        print("WITNESS chi_d>=3:", json.dumps(first_witness))
    else:
        print("NO chi_d>=3 witness found")


if __name__ == '__main__':
    main()
