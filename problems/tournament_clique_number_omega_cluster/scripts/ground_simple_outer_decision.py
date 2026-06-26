import sys, time
sys.path.insert(0, "scripts")
import core
from search_4critical_circulant import omega_vec_ge_K_via_sat, build_cnf_no_kclique
from ground_simple_outer_lex import lex_substitute, AC, is_tournament, C3

AC7 = AC(7, {1,2,4})
AC7_C3 = lex_substitute(AC7, C3)
C3_AC7_C3 = lex_substitute(C3, AC7_C3)
n, arcs = C3_AC7_C3
print("target C3[AC7[C3]] order:", n, "is_tournament:", is_tournament(n,arcs))
sys.stdout.flush()

# lower bound check: ge_5 should be True (lex lower bound 2+4-1=5)
t=time.time()
ge5, dt5, nc5 = omega_vec_ge_K_via_sat(n, arcs, 5)
print(f"ge_5 = {ge5}  (UNSAT means omega_vec>=5)  time={dt5:.3f}s nclauses_no5={nc5}")
sys.stdout.flush()

# the decision: ge_6.  CONFIRM if ge_6=False (omega_vec=5). KILL if ge_6=True (omega_vec>=6).
t=time.time()
print("building/solving no-K6 CNF (enumerating transitive 6-subsets)...")
sys.stdout.flush()
ge6, dt6, nc6 = omega_vec_ge_K_via_sat(n, arcs, 6)
print(f"ge_6 = {ge6}  time={dt6:.3f}s nclauses_no6={nc6}")
ov = "5" if (ge5 and not ge6) else ("(>=6)" if ge6 else "(<5?)")
print("=> omega_vec(C3[AC7[C3]]) =", ov)
print("VERDICT:", "CONFIRM (ov=5, simple-outer +1)" if (ge5 and not ge6) else "KILL (ov>=6, simple-outer overshoots)")
