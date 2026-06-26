"""Search for a total order on Paley(p) whose backedge graph has clique number 5.

If found, combined with dom(Paley(p))>=5 (Property 3.2) it pins omega_vec=5 exactly,
giving the first DIRECT vertex-transitive k=5 circulant witness.

Strategy: clique-guided repair + block-reversal simulated annealing on the order.
Hard internal time cap via signal.alarm. FOREGROUND only.
"""
import sys, os, json, random, signal, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import core
import networkx as nx

TIMEUP = False
def _alarm(sig, frm):
    global TIMEUP
    TIMEUP = True
signal.signal(signal.SIGALRM, _alarm)

def paley_arcs(p):
    g = set((x*x) % p for x in range(1, p))
    arcs = [(i, (i+d) % p) for i in range(p) for d in g]
    return arcs

def backedge_clique(p, beats, order):
    """clique number of backedge graph for `order` (order[0] = prec-smallest)."""
    g = nx.Graph()
    g.add_nodes_from(range(p))
    for i in range(p):
        a = order[i]
        for j in range(i+1, p):
            b = order[j]
            if beats[b][a]:
                g.add_edge(a, b)
    return max((len(c) for c in nx.find_cliques(g)), default=1), g

def main():
    p = int(sys.argv[1])
    seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 880
    arcs = paley_arcs(p)
    assert core.is_tournament(p, arcs), "not a tournament"
    beats = core.beats_matrix(p, arcs)

    signal.alarm(seconds)
    rng = random.Random(12345)
    target = 5

    # seed: identity order
    cur = list(range(p))
    cur_w, _ = backedge_clique(p, beats, cur)
    best = cur_w
    best_order = cur[:]
    print(f"[seed identity] backedge clique = {cur_w}", flush=True)

    # also try a few random seeds, keep best start
    for _ in range(8):
        if TIMEUP: break
        o = list(range(p)); rng.shuffle(o)
        w, _ = backedge_clique(p, beats, o)
        if w < best:
            best, best_order, cur, cur_w = w, o[:], o[:], w
    print(f"[best seed] backedge clique = {best}", flush=True)

    def count_max_cliques(g, w):
        return sum(1 for c in nx.find_cliques(g) if len(c) == w)

    # Phase 1: clique-guided repair. find a max clique, reposition one of its
    # vertices to try to break it, accepting non-worsening (count) moves.
    iters = 0
    cur_w, cur_g = backedge_clique(p, beats, cur)
    cur_cnt = count_max_cliques(cur_g, cur_w)
    while not TIMEUP and best > target:
        iters += 1
        # pick a max clique
        cliques = [c for c in nx.find_cliques(cur_g) if len(c) == cur_w]
        if not cliques:
            break
        C = rng.choice(cliques)
        v = rng.choice(C)
        pos = cur.index(v)
        # try moving v to several candidate positions
        improved = False
        cand_positions = rng.sample(range(p), min(p, 24))
        for np_ in cand_positions:
            if np_ == pos: continue
            o = cur[:]
            o.pop(pos)
            o.insert(np_, v)
            w, g = backedge_clique(p, beats, o)
            if w < cur_w or (w == cur_w and count_max_cliques(g, w) < cur_cnt):
                cur, cur_w, cur_g = o, w, g
                cur_cnt = count_max_cliques(g, w)
                improved = True
                if cur_w < best:
                    best, best_order = cur_w, cur[:]
                    print(f"[repair it{iters}] NEW BEST backedge clique = {best}", flush=True)
                break
        if not improved:
            # Phase 2 escape: block reversal SA step
            i, j = sorted(rng.sample(range(p), 2))
            o = cur[:]
            o[i:j+1] = o[i:j+1][::-1]
            w, g = backedge_clique(p, beats, o)
            dw = w - cur_w
            if dw <= 0 or rng.random() < 0.05:
                cur, cur_w, cur_g = o, w, g
                cur_cnt = count_max_cliques(g, w)
                if cur_w < best:
                    best, best_order = cur_w, cur[:]
                    print(f"[blockrev it{iters}] NEW BEST backedge clique = {best}", flush=True)
        if iters % 200 == 0:
            print(f"[it{iters}] cur_w={cur_w} cur_cnt={cur_cnt} best={best}", flush=True)

    signal.alarm(0)
    # verify best via canonical core.omega_of_order
    verify_w = core.omega_of_order(p, arcs, best_order)
    print(f"[done] iters={iters} best={best} verify(core.omega_of_order)={verify_w}", flush=True)
    out = {
        "p": p, "best_backedge_clique": best, "verify_omega_of_order": verify_w,
        "iters": iters, "target": target, "reached_target": best <= target,
        "best_order": best_order,
    }
    outpath = os.path.join(os.path.dirname(__file__), "..", "data", f"search_direct_k5_p{p}.json")
    with open(outpath, "w") as f:
        json.dump(out, f)
    print(f"[saved] {os.path.abspath(outpath)}", flush=True)

if __name__ == "__main__":
    main()
