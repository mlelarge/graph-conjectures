"""GROUND H23: random-interleaving positive-probability mechanism for H19.

Fix the three PROVEN clique-4 inner sigmas of QR_19 extracted from the G59 gold
object (data/ground_h21_skeleton_sat.json). A random interleaving is a uniform
word w in {0,1,2}^{3m} with m of each symbol; copy c's vertices are placed at the
w==c positions, in sigma_c order. We compute the EXACT merged backedge max clique
for many such words on three objects:

  C3[QR_19]  m=19  target <=5 (=ov+1)   -- the gold object (H21 provably fails)
  C3[AC_7]   m=7   target <=4           -- positive control (H21 succeeds, ov=3)
  C3[H7]     m=7   target <=3           -- PROVABLY impossible (H16 ctrex, ov=2)

sigmas are FIXED (gold orders / oracle-optimal); randomness is ONLY over the word.
This is NOT an optimal-sigma DFS (G54/G55 compliant).
"""
import sys, os, json, time, itertools, random
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from lexlib import lex_substitute, C3, AC, is_tournament

t0 = time.time()
OUT = {"object_results": {}}


def merged_order_from_word(word, sigmas, m):
    """word: list in {0,1,2}^{3m}, m of each. sigmas[c]: order on inner indices 0..m-1.
    Copy c occupies global labels [c*m, c*m+m-1]; the j-th time symbol c appears in
    word, we place copy c's j-th vertex (in sigma_c order) -> global label c*m+sigmas[c][j].
    Returns the merged total order (list of 3m global labels)."""
    ptr = [0, 0, 0]
    order = []
    for c in word:
        j = ptr[c]
        order.append(c * m + sigmas[c][j])
        ptr[c] += 1
    return order


def run_object(name, m, inner_arcs, sigmas, target, N_samples, seed):
    n, arcs = lex_substitute(C3, (m, inner_arcs))
    assert is_tournament(n, arcs), f"{name} not a tournament"
    # provenance: each fixed sigma's inner backedge clique
    inner_cliques = [core.omega_of_order(m, inner_arcs, sigmas[c]) for c in range(3)]
    rng = random.Random(seed)
    base = [0] * m + [1] * m + [2] * m
    hist = Counter()
    hits = 0
    best_val = None
    best_order = None
    for _ in range(N_samples):
        w = base[:]
        rng.shuffle(w)
        order = merged_order_from_word(w, sigmas, m)
        val = core.omega_of_order(n, arcs, order)
        hist[val] += 1
        if best_val is None or val < best_val:
            best_val = val
            best_order = order[:]
        if val <= target:
            hits += 1
    res = {
        "order": n, "m": m, "N_samples": N_samples, "seed": seed,
        "fixed_inner_cliques": inner_cliques,
        "target_le": target,
        "clique_histogram": {str(k): v for k, v in sorted(hist.items())},
        "hits_le_target": hits,
        "hit_rate": hits / N_samples,
        "best_clique": best_val,
        "best_order": best_order,
    }
    print(f"[{name}] order={n} N={N_samples} target<={target} "
          f"hist={dict(sorted(hist.items()))} hits={hits} best={best_val}", flush=True)
    return res


# ---------------- C3[QR_19]: load gold sigmas from H21 data ----------------
d = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data",
                                 "ground_h21_skeleton_sat.json")))
wo = d["witness_order"]; sig = d["witness_copy_signature"]
copies = [list(range(0, 19)), list(range(19, 38)), list(range(38, 57))]
sigmas_qr = [[], [], []]
for pos, v in enumerate(wo):
    c = sig[pos]
    assert copies[c][0] <= v <= copies[c][-1], (pos, v, c)
    sigmas_qr[c].append(v - copies[c][0])
for c in range(3):
    assert sorted(sigmas_qr[c]) == list(range(19)), ("sigma_qr not perm", c)
QR = sorted({(x * x) % 19 for x in range(1, 19)})
arcs_qr = [(i, (i + dd) % 19) for i in range(19) for dd in QR]
assert core.is_tournament(19, arcs_qr), "QR_19 not a tournament"
ic = [core.omega_of_order(19, arcs_qr, sigmas_qr[c]) for c in range(3)]
assert ic == [4, 4, 4], f"PROVENANCE FAIL: inner cliques {ic} != [4,4,4]"
OUT["object_results"]["C3[QR_19]"] = run_object(
    "C3[QR_19]", 19, arcs_qr, sigmas_qr, target=5, N_samples=800, seed=0)

# ---------------- C3[AC_7] control (ov=3, target <=4) ----------------
m7, arcs_ac7 = AC(7, [1, 2, 4])      # AC_7 = Paley(7), ov=3 (the proposal's ov=3 control)
assert is_tournament(m7, arcs_ac7), "AC_7 not a tournament"
# oracle-optimal order of AC_7 (n=7 brute force over all 7! orders)
ov_ac7, best_ord_ac7 = None, None
for perm in itertools.permutations(range(7)):
    val = core.omega_of_order(7, arcs_ac7, list(perm))
    if ov_ac7 is None or val < ov_ac7:
        ov_ac7, best_ord_ac7 = val, list(perm)
        if ov_ac7 <= 1:
            break
print(f"AC_7 omega_vec (brute) = {ov_ac7}, optimal order = {best_ord_ac7}", flush=True)
OUT["AC_7_omega_vec"] = ov_ac7
OUT["AC_7_optimal_order"] = best_ord_ac7
sigmas_ac7 = [best_ord_ac7[:], best_ord_ac7[:], best_ord_ac7[:]]
OUT["object_results"]["C3[AC_7]"] = run_object(
    "C3[AC_7]", 7, arcs_ac7, sigmas_ac7, target=4, N_samples=400, seed=0)

# ---------------- C3[H7] control (H16 ctrex inner, ov=2, target <=3 impossible) -----
arcs_str = "01 02 30 40 05 60 12 13 14 51 61 23 24 25 62 34 53 36 45 46 56".split()
H7 = [(int(s[0]), int(s[1])) for s in arcs_str]
assert is_tournament(7, H7), "H7 not a tournament"
ov_h7 = core.omega_vec(7, H7)
assert ov_h7 == 2, f"H7 omega_vec must be 2, got {ov_h7}"
# optimal order of H7 (achieving omega_vec=2)
ovh, best_ord_h7 = None, None
for perm in itertools.permutations(range(7)):
    val = core.omega_of_order(7, H7, list(perm))
    if ovh is None or val < ovh:
        ovh, best_ord_h7 = val, list(perm)
        if ovh <= 2:
            break
print(f"H7 omega_vec={ov_h7}, optimal order={best_ord_h7}", flush=True)
OUT["H7_omega_vec"] = ov_h7
OUT["H7_optimal_order"] = best_ord_h7
sigmas_h7 = [best_ord_h7[:], best_ord_h7[:], best_ord_h7[:]]
OUT["object_results"]["C3[H7]"] = run_object(
    "C3[H7]", 7, H7, sigmas_h7, target=3, N_samples=400, seed=0)

# ---------------- re-verify any C3[QR_19] hit with the oracle clique routine -----
qr = OUT["object_results"]["C3[QR_19]"]
if qr["hits_le_target"] > 0 and qr["best_clique"] <= 5:
    nfull, afull = lex_substitute(C3, (19, arcs_qr))
    reverify = core.omega_of_order(nfull, afull, qr["best_order"])
    OUT["C3[QR_19]_best_reverified_clique"] = reverify
    print(f"RE-VERIFY C3[QR_19] best order via core.omega_of_order -> {reverify}", flush=True)

OUT["elapsed_s"] = round(time.time() - t0, 2)

# ---------------- verdict logic per the falsifiable prediction ----------------
qr_hits = qr["hits_le_target"]
ac7_rate = OUT["object_results"]["C3[AC_7]"]["hit_rate"]
qr_rate = qr["hit_rate"]
h7_hits = OUT["object_results"]["C3[H7]"]["hits_le_target"]
OUT["prediction_eval"] = {
    "qr19_hits_le5": qr_hits,
    "qr19_hit_rate": qr_rate,
    "ac7_hit_rate_le4": ac7_rate,
    "h7_hits_le3": h7_hits,
    "harness_h7_ok": (h7_hits == 0),
    "ac7_higher_than_qr19": (ac7_rate > qr_rate),
    "CONFIRM": (qr_hits >= 1 and h7_hits == 0 and ac7_rate > qr_rate),
    "KILL": (qr_hits == 0 and h7_hits == 0),
}
out_path = os.path.join(os.path.dirname(__file__), "..", "data",
                        "ground_h23_random_interleave.json")
json.dump(OUT, open(out_path, "w"), indent=1)
print("\n=== SUMMARY ===")
print(json.dumps(OUT["prediction_eval"], indent=1))
print("elapsed", OUT["elapsed_s"], "s; wrote", out_path)
