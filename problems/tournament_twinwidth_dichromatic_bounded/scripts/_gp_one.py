import sys, time
sys.path.insert(0, '.')
import core, constructions as C

sub = C.substitute_into_C3
TT1 = C.single_vertex()
TT2 = C.transitive_tournament(2)
S3 = C.S(3)

CANDS = {
    'D(S3,S3,TT1)': sub(S3, S3, TT1),
    'D(S3,TT1,S3)': sub(S3, TT1, S3),
    'D(TT1,S3,S3)': sub(TT1, S3, S3),
    'D(S3,S3,TT2)': sub(S3, S3, TT2),
    'D(TT2,S3,S3)': sub(TT2, S3, S3),
}

nm = sys.argv[1]
n, a = CANDS[nm]
A = core._adj(n, a)
t0 = time.time()
ch = core.chi_vec(n, a)
t1 = time.time()
# PROVE omegaVec>=3 by exhaustively refuting any ordering with back-edge clique <= 2.
le2 = core._exists_order_within(n, A, 2)   # True => omegaVec <= 2 (would KILL the bound)
t2 = time.time()
om = '<=2' if le2 else '>=3'
bound_ok = 'N/A(omega<=2 => KILL)' if le2 else (ch <= 3 ** (3 - 1))
print('RESULT %s n=%d chiVec=%d omegaVec_le2=%s omegaVec%s bound_chi<=3^(omega-1)=%s  (chi %.1fs, omega %.1fs)'
      % (nm, n, ch, le2, om, bound_ok, t1 - t0, t2 - t1), flush=True)
