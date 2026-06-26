import sys, time, random, signal
sys.path.insert(0, 'scripts')
import core
import networkx as nx

# ----- hard self-timeout guard (belt-and-suspenders; outer `timeout 900` too) -----
def _alarm(sig, frm):
    print("SELF-ALARM TIMEOUT", flush=True); sys.exit(2)
signal.signal(signal.SIGALRM, _alarm)
signal.alarm(880)

# --------------------------------------------------------------------------- #
# (1) Build QR_19[C3]
# --------------------------------------------------------------------------- #
QR = sorted({(x*x) % 19 for x in range(1, 19)})
arcs19 = [(i, (i+d) % 19) for i in range(19) for d in QR]
assert core.is_tournament(19, arcs19), "QR_19 not a tournament"
print("QR_19 residues", QR, "is_tournament", True, flush=True)

nT, nH = 19, 3
arcsH = [(0, 1), (1, 2), (2, 0)]
bT = core.beats_matrix(nT, arcs19)
bH = core.beats_matrix(nH, arcsH)

# vertex (t,h) -> id t*3+h
def vid(t, h): return t*nH + h
N = nT*nH
arcs = []
for t in range(nT):
    for h in range(nH):
        for tp in range(nT):
            for hp in range(nH):
                if (t, h) == (tp, hp): continue
                if bT[t][tp] or (t == tp and bH[h][hp]):
                    arcs.append((vid(t, h), vid(tp, hp)))
assert core.is_tournament(N, arcs), "QR_19[C3] not a tournament"
beats = core.beats_matrix(N, arcs)
print("QR_19[C3] order", N, "is_tournament", True, flush=True)

# fast backedge-clique of an explicit order (networkx find_cliques)
def clq(order):
    g = nx.Graph(); g.add_nodes_from(order)
    pos = {v: i for i, v in enumerate(order)}
    for idx in range(len(order)):
        a = order[idx]
        for jdx in range(idx+1, len(order)):
            b = order[jdx]            # a prec b
            if beats[b][a]:           # backward arc b->a => edge
                g.add_edge(a, b)
    if g.number_of_edges() == 0:
        return 1 if g.number_of_nodes() else 0
    return max(len(c) for c in nx.find_cliques(g))

# --------------------------------------------------------------------------- #
# (2) best rotation order of QR_19 alone => rank rk(t)
# --------------------------------------------------------------------------- #
best_w19, best_rot = None, None
for r in range(19):
    o19 = [(i+r) % 19 for i in range(19)]
    w = core.omega_of_order(19, arcs19, o19)
    if best_w19 is None or w < best_w19:
        best_w19, best_rot = w, o19
print("QR_19 best rotation backedge clique =", best_w19, "(expect 4)", flush=True)
rk = {t: i for i, t in enumerate(best_rot)}   # rank of t in best order

# --------------------------------------------------------------------------- #
# (3) UPPER BOUND on QR_19[C3] via merged key
#     key = (rk(t)/19 + [h==0], v)
# --------------------------------------------------------------------------- #
allV = [vid(t, h) for t in range(nT) for h in range(nH)]
def merged_key(v):
    t, h = divmod(v, nH)
    return (rk[t]/19.0 + (1.0 if h == 0 else 0.0), v)
order_full = sorted(allV, key=merged_key)
ub_full = clq(order_full)
print("UPPER BOUND omega_vec(QR_19[C3]) <= clq(merged order) =", ub_full, flush=True)

# composition-law lower bound: ov(QR_19)+ov(C3)-1 = 4+2-1 = 5
law_lb = 4 + 2 - 1
print("composition-law lower bound =", law_lb, flush=True)
ov_pinned = (ub_full == 5 and law_lb == 5)
print("=> omega_vec(QR_19[C3]) pinned == 5 :", ov_pinned, flush=True)

# --------------------------------------------------------------------------- #
# (4) DELETION search: Vd = V \ src, src = (best_rot[0], 0)
#     Goal: does SOME explicit order of the deletion have backedge clique <= 4?
# --------------------------------------------------------------------------- #
src = vid(best_rot[0], 0)
Vd = [v for v in allV if v != src]
print("deleted source vertex", divmod(src, nH), "order", len(Vd), flush=True)

# backedge graph builder restricted to a vertex subset (for SA / degeneracy)
# precompute neighbor relation: undirected "could be backedge" depends on order,
# so we work directly with the directed beats; clique(order) computes it.

results = {}

# (a) lexicographic band keys over (rk(t), d(h)) with signs
d_of = {0: 2, 1: 1, 2: 1}   # d_then_c style depth
def band_order(sign_rk, sign_d, rk_first):
    def key(v):
        t, h = divmod(v, nH)
        kr = sign_rk*rk[t]; kd = sign_d*d_of[h]
        return (kr, kd, v) if rk_first else (kd, kr, v)
    return sorted(Vd, key=key)
best_band = None
for srk in (1, -1):
    for sd in (1, -1):
        for rf in (True, False):
            o = band_order(srk, sd, rf)
            w = clq(o)
            tag = ("band", srk, sd, rf)
            if best_band is None or w < best_band[0]:
                best_band = (w, tag)
results["band_min"] = best_band
print("(a) band-key min clique =", best_band, flush=True)

# also the proven d_then_c style: c(t) by rank-thirds, d(h)
m = (nT-1)//2
def c_of_rank(t):
    r = rk[t]
    if r == 0: return 3
    if r <= m: return 2
    return 1
def dthenc_order():
    return sorted(Vd, key=lambda v: (d_of[v % nH], c_of_rank(v//nH), v))
w_dtc = clq(dthenc_order())
results["d_then_c"] = w_dtc
print("(a') d_then_c min clique =", w_dtc, flush=True)

# (b) greedy min-backedge / degeneracy-style order:
# build order by repeatedly appending the vertex that adds the fewest backedges
# to the current placed set (greedy to keep backedge graph sparse).
def greedy_order():
    placed = []
    placed_set = set()
    remaining = set(Vd)
    # adjacency among placed in backedge graph grows; pick next minimizing new edges
    while remaining:
        best_v, best_new = None, None
        for v in remaining:
            # if v placed last: edges v-a for placed a with beats[v][a]? No:
            # a placed earlier (a prec v): edge iff beats[v][a]. Plus future
            # vertices onto v handled later. Count immediate new edges.
            new = sum(1 for a in placed if beats[v][a])
            if best_new is None or new < best_new:
                best_new, best_v = new, v
        placed.append(best_v); placed_set.add(best_v); remaining.discard(best_v)
    return placed
w_greedy = clq(greedy_order())
results["greedy"] = w_greedy
print("(b) greedy min-backedge clique =", w_greedy, flush=True)

# (c) simulated annealing on the vertex permutation minimizing backedge clique
def sa(order0, steps=2000, seed=0):
    rng = random.Random(seed)
    order = list(order0)
    cur = clq(order)
    best = cur; best_order = list(order)
    T0 = 2.0
    for s in range(steps):
        if best <= 4:
            break
        T = T0*(1 - s/steps) + 1e-3
        i, j = rng.randrange(len(order)), rng.randrange(len(order))
        if i == j: continue
        order[i], order[j] = order[j], order[i]
        w = clq(order)
        if w <= cur or rng.random() < pow(2.718281828, -(w-cur)/T):
            cur = w
            if w < best:
                best = w; best_order = list(order)
        else:
            order[i], order[j] = order[j], order[i]
    return best, best_order
# seed SA from the best band order found
seed_order = band_order(*best_band[1][1:])
w_sa, sa_order = sa(seed_order, steps=2000, seed=1)
results["sa"] = w_sa
print("(c) simulated-annealing min clique =", w_sa, flush=True)

# (d) global "all h!=0 before h=0" with within-layer = QR_19 proven critical rank
def global_layer_order():
    nonzero = sorted([v for v in Vd if v % nH != 0], key=lambda v: (rk[v//nH], v % nH))
    zero = sorted([v for v in Vd if v % nH == 0], key=lambda v: (rk[v//nH], v))
    return nonzero + zero
w_glob = clq(global_layer_order())
results["global_layer"] = w_glob
print("(d) global h!=0-before-h=0 clique =", w_glob, flush=True)

min_clique = min([best_band[0], w_dtc, w_greedy, w_sa, w_glob])
print("=== DELETION MIN CLIQUE over all routes =", min_clique, "===", flush=True)

# --------------------------------------------------------------------------- #
# (5) decide CONFIRM vs KILL
# --------------------------------------------------------------------------- #
if min_clique <= 4:
    # find the winning order
    win = None
    for o, tag in [(band_order(*best_band[1][1:]), best_band[1]),
                   (dthenc_order(), "d_then_c"),
                   (greedy_order(), "greedy"),
                   (sa_order, "sa"),
                   (global_layer_order(), "global_layer")]:
        if clq(o) <= 4:
            win = (tag, clq(o), o); break
    print("CONFIRM: deletion has order with backedge clique <=4", win[0], win[1], flush=True)
    print("=== VERDICT: CONFIRM (route alive, QR_19[C3] candidate 5-critical) ===", flush=True)
else:
    print("All explicit routes wall at clique", min_clique, "(never 4)", flush=True)
    # dump an induced 5-vertex backedge clique witness from the merged full order
    gfull = nx.Graph(); gfull.add_nodes_from(order_full)
    pos = {v: i for i, v in enumerate(order_full)}
    for idx in range(len(order_full)):
        a = order_full[idx]
        for jdx in range(idx+1, len(order_full)):
            b = order_full[jdx]
            if beats[b][a]:
                gfull.add_edge(a, b)
    cliq5 = next((c for c in nx.find_cliques(gfull) if len(c) >= 5), None)
    print("sample 5-clique in merged full order:",
          [divmod(v, nH) for v in (cliq5 or [])][:5], flush=True)
    print("=== VERDICT: KILL (deletion-order minimization walls at 5, not 4) ===", flush=True)

print("SUMMARY_RESULTS", results, "min_clique", min_clique,
      "ov_pinned", ov_pinned, flush=True)
signal.alarm(0)
