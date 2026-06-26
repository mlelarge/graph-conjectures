"""D40 / next_action lever (1): H20 DISCRIMINATOR.

Compute dic + dic-vertex-criticality of QR_19 (order 19, P15, ov=4) and
AC4_21 (order 21, P14, ov=4) with the validated mono-triangle-free SAT dic
encoding (same code path as ground_lift_lemma_step1.py).

H20 barrier says dic grows multiplicatively under lex while ov grows
additively, so the Aubian-Coulomb Prop 6.2 input needs a k-dic-vertex-critical
tournament with ov = dic = k.  At k=4 the two candidates are QR_19 and AC4_21
(both ov=4 proven, P15/P14).  Discriminator:
  - if dic(T) = 4 AND T is 4-dic-vertex-critical  -> H20's required input
    EXISTS at k=4; phase 2 (C3[T], order 57/63, 5-criticality) is unlocked.
  - if dic(T) >= 5, or dic=4 but not vertex-critical -> the candidate dies;
    both dying = the preprint's open input remains open at k=4 from the
    known ov=4 witnesses, hardening H20.

Soundness: dic(T)<=k <=> exists k-coloring with no monochromatic directed
triangle (acyclic tournament == transitive == C3-free), exact SAT both
directions (Cadical153).  Both candidates are circulants => vertex-transitive
(rotation x->x+1 is an automorphism) => deletion check at v=0 suffices;
vertex-transitivity is machine-checked, not assumed.
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
from lexlib import AC, is_tournament
from ground_lift_lemma_step1 import dic, dicolorable, dic_vertex_critical, sub, directed_triangles
import core

def check_vertex_transitive_rotation(n, arcs):
    """rotation x->x+1 mod n is an automorphism iff arc set is rotation-closed."""
    aset = set(arcs)
    return all((((u+1) % n, (v+1) % n) in aset) for (u, v) in arcs)

def main():
    QR19 = sorted({pow(x, 2, 19) for x in range(1, 19)})           # {1,4,5,6,7,9,11,16,17}
    AC4_21_G = [1, 2, 4, 7, 8, 9, 11, 15, 16, 18]                  # P14 generator
    cases = [("QR_19", AC(19, QR19)), ("AC4_21", AC(21, AC4_21_G))]
    # EXTENDED KILL SCOPE: every known 4-omega_vec-critical circulant
    # (data/k4_sandwich_witnesses.json: 2 at n=19 incl QR_19+reverse, 12 at n=25)
    wfile = os.path.join(os.path.dirname(__file__), '..', 'data',
                         'k4_sandwich_witnesses.json')
    wits = json.load(open(wfile))['k4_4critical_witnesses']
    for i, w in enumerate(wits):
        nm = f"k4crit_n{w['n']}_{i}"
        if w['n'] == 19 and sorted(w['g']) == QR19:
            continue  # = QR_19, already case 1
        cases.append((nm, AC(w['n'], w['g'])))
    out = {}
    for name, (n, arcs) in cases:
        assert is_tournament(n, arcs), name
        vt = check_vertex_transitive_rotation(n, arcs)
        assert vt, f"{name} not rotation-closed?!"
        t0 = time.time()
        d = dic(n, arcs)
        t1 = time.time()
        # vertex-criticality at the measured dic value, v=0 by vertex-transitivity
        crit, dels = dic_vertex_critical(n, arcs, d, vt=True)
        t2 = time.time()
        # independent leg: explicit dic(T-0) by full ladder (not just (d-1)-colorability)
        nn, aa = sub(n, arcs, 0)
        d_del = dic(nn, aa)
        t3 = time.time()
        ntris = len(directed_triangles(n, arcs))
        hit = (d == 4 and crit)
        out[name] = dict(n=n, dic=d, dic_of_deletion_v0=d_del,
                         dic_vertex_critical=bool(crit),
                         vertex_transitive_rotation=bool(vt),
                         n_directed_triangles=ntris,
                         h20_input_hit=bool(hit),
                         t_dic=round(t1-t0, 3), t_crit=round(t2-t1, 3),
                         t_del_ladder=round(t3-t2, 3))
        print(f"{name:13s} n={n} dic={d} dic(T-0)={d_del} "
              f"{d}-dic-vertex-critical={crit} (vt verified={vt}, "
              f"#tris={ntris})  H20-INPUT-HIT(dic=4 AND crit)={hit}", flush=True)
    path = os.path.join(os.path.dirname(__file__), '..', 'data',
                        'h20_discriminator_qr19_ac421.json')
    json.dump(out, open(path, 'w'), indent=1)
    print("saved", os.path.abspath(path), flush=True)

if __name__ == '__main__':
    main()
