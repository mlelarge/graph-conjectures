"""Scan all 2^11 = 2048 one-vertex extensions of Pal_11 (= QR_11, g={1,3,4,5,9}).

For each extension T12 (vertex 11 added; arc 11->i iff bit i set, else i->11),
test no-K4 via the validated betweenness SAT encoder (no_Kclique_cnf, K=4).
SAT => there is an order whose backedge graph has no K4 => ov(T12) <= 3, and the
returned order's clique is exact-verified (sound, no UNSAT-trust).
UNSAT => ov(T12) >= 4 (an explicit order-12 ov>=4 witness): confirm with exact
core.omega_vec.

Conditional on BBKP 'every 4-chromatic order-12 tournament contains Pal_11', if
ALL 2048 are no-K4 (ov<=3) then min ov=4 order >= 13.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from pysat.solvers import Cadical153, Glucose42
from ground_bbkp_witness import no_Kclique_cnf, order_from_model

def pal11_arcs():
    g = {1, 3, 4, 5, 9}
    n = 11
    return n, [(i, j) for i in range(n) for j in range(n)
               if i != j and (j - i) % n in g]

def main():
    n0, base = pal11_arcs()
    assert core.is_tournament(11, base)
    t_start = time.time()
    unsat = []
    sat_count = 0
    bad_cert = []
    for mask in range(2048):
        T = list(base)
        for i in range(11):
            if (mask >> i) & 1:
                T.append((11, i))
            else:
                T.append((i, 11))
        cls, P, ncl = no_Kclique_cnf(12, T, 4)
        with Cadical153(bootstrap_with=cls) as m:
            sat = m.solve()
            model = m.get_model() if sat else None
        if sat:
            order = order_from_model(12, model, P)
            w = core.omega_of_order(12, T, order)  # exact clique of the returned order
            if w >= 4:
                bad_cert.append((mask, w))  # SAT but certificate clique >=4: bug
            else:
                sat_count += 1
        else:
            unsat.append(mask)
        if mask % 256 == 255:
            print(f'  ...{mask+1}/2048  sat={sat_count} unsat={len(unsat)} '
                  f'({time.time()-t_start:.1f}s)', flush=True)

    print(f'\nDONE in {time.time()-t_start:.1f}s')
    print(f'SAT (ov<=3, cert-verified): {sat_count}')
    print(f'UNSAT (candidate ov>=4):    {len(unsat)}')
    print(f'bad certs (SAT but cliq>=4):{len(bad_cert)} {bad_cert[:5]}')

    # For any UNSAT: confirm exactly with core.omega_vec and double-check with Glucose42.
    for mask in unsat:
        T = list(base)
        for i in range(11):
            if (mask >> i) & 1: T.append((11, i))
            else: T.append((i, 11))
        ov = core.omega_vec(12, T)
        cls, P, ncl = no_Kclique_cnf(12, T, 4)
        with Glucose42(bootstrap_with=cls) as m:
            sat2 = m.solve()
        print(f'  UNSAT mask={mask}: exact ov={ov}, glucose42 sat={bool(sat2)}')

    if not unsat and not bad_cert:
        print('\nRESULT: all 2048 extensions have ov<=3 (cert-verified).')
        print('=> conditional on BBKP contains-Pal_11, min ov=4 order >= 13.')

if __name__ == '__main__':
    main()
