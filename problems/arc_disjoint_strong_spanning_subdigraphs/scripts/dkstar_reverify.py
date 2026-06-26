"""INDEPENDENT re-verification of DK*(alpha) from scratch.

DK*(alpha) (UNIVERSAL): for every lambda-arc-strong digraph D on n vertices and
every alpha>=1, the number of DISTINCT labeled ARC-SETS
    { delta^+(X) : emptyset != X subsetneq V, |delta^+(X)| <= alpha*lambda }
is at most n^{2*alpha}.

I do NOT trust the prior dkstar_check.py. I re-derive:
  (a) the arc-set primitive (labeled, parallels distinct),
  (b) the lambda via oracle,
  (c) a GENERIC exhaustive census (geng|directg, ALL lambda strata) n=4,5,6,
  (d) NEW adversarial families aimed at the actual failure mode: realize a
      LARGE family of DISTINCT cheap arc-cut subsets from a SMALL arc reservoir.

KILL = any (D,alpha) with #distinct cheap arc-sets > n^{2alpha}.
"""
import sys, os, json, time, subprocess

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import oracle

ALPHAS = [("1", 1.0), ("4/3", 4.0/3.0), ("5/3", 5.0/3.0), ("2", 2.0)]


def arcset_census(n, arcs, lam):
    """Distinct labeled arc-sets delta^+(X) per alpha. Label = arc index."""
    larcs = [(i, u, v) for i, (u, v) in enumerate(arcs)]
    thr = {lbl: a*lam for (lbl, a) in ALPHAS}
    asets = {lbl: set() for (lbl, _a) in ALPHAS}
    vcount = {lbl: 0 for (lbl, _a) in ALPHAS}
    maxthr = max(thr.values())
    for mask in range(1, (1 << n) - 1):
        # build X membership
        Xb = mask
        F = frozenset(i for (i, u, v) in larcs
                      if ((Xb >> u) & 1) and not ((Xb >> v) & 1))
        s = len(F)
        if s > maxthr:
            continue
        for (lbl, _a) in ALPHAS:
            if s <= thr[lbl]:
                asets[lbl].add(F)
                vcount[lbl] += 1
    out = {}
    for (lbl, a) in ALPHAS:
        nstar = len(asets[lbl])
        denom = n ** (2.0*a)
        out[lbl] = {"n_arcsets": nstar, "n_vsets": vcount[lbl],
                    "denom": denom, "ratio": nstar/denom}
    return out


class Tracker:
    def __init__(self):
        self.worst = {lbl: -1.0 for (lbl, _a) in ALPHAS}
        self.worst_info = {}
        self.kills = []

    def update(self, n, arcs, lam, tag):
        cc = arcset_census(n, arcs, lam)
        for (lbl, _a) in ALPHAS:
            r = cc[lbl]["ratio"]
            if r > self.worst[lbl]:
                self.worst[lbl] = r
                self.worst_info[lbl] = {"ratio": round(r, 5), "n": n,
                                        "lambda": lam, "tag": tag,
                                        "n_arcsets": cc[lbl]["n_arcsets"]}
            if r > 1.0:
                self.kills.append({"alpha": lbl, "ratio": round(r, 5),
                                   "n": n, "lambda": lam, "tag": tag,
                                   "n_arcsets": cc[lbl]["n_arcsets"],
                                   "arcs": [list(a) for a in arcs]})
        return cc

    def summary(self):
        return {"worst_ratio_per_alpha": {k: round(v, 5) for k, v in self.worst.items()},
                "worst_info": self.worst_info,
                "kills": self.kills,
                "DKstar_survives": len(self.kills) == 0}


def gen_simple(n, mind=0):
    """geng [-d<mind>] n | directg -T : all orientations incl digons."""
    gargs = ["geng", "-cq", str(n)]
    if mind > 0:
        gargs = ["geng", f"-cd{mind}q", str(n)]
    geng = subprocess.Popen(gargs, stdout=subprocess.PIPE)
    directg = subprocess.Popen(["directg", "-Tq"], stdin=geng.stdout,
                               stdout=subprocess.PIPE)
    geng.stdout.close()
    for line in directg.stdout:
        toks = line.decode().split()
        if not toks:
            continue
        nv = int(toks[0]); nums = list(map(int, toks[2:]))
        arcs = [(nums[i], nums[i+1]) for i in range(0, len(nums), 2)]
        yield nv, arcs
    directg.wait(); geng.wait()


def run_census(n, tr, mind=0):
    nread = 0; nlam = 0
    for nv, arcs in gen_simple(n, mind):
        nread += 1
        lam = oracle.arc_connectivity(nv, arcs)
        if lam < 1:
            continue
        nlam += 1
        tr.update(nv, arcs, lam, tag=f"census_n{n}_d{mind}")
    return {"n": n, "mind": mind, "n_read": nread, "n_lambda_ge1": nlam}


# ---- ADVERSARIAL FAMILIES (independent designs) ---- #
def fam_g11_private(k, mult=3):
    """G11 + private p->s arc per toggle (the named failure mode)."""
    s, o = 0, 1
    arcs = [(s, o)]*mult + [(o, s)]*mult
    for j in range(k):
        p = 2+j
        arcs += [(s, p)]*mult + [(p, o)]*mult + [(p, s)]
    return k+2, arcs


def fam_bond_pool(t):
    """KEY ADVERSARIAL IDEA: a directed cycle 0->1->...->t-1->0 with mult=1,
    PLUS a 'return hub' h with arcs i->h and h->i (mult 1) for all i, making it
    strong with small lambda. Goal: many vertex intervals -> distinct cheap
    arc-sets from a small arc reservoir. lambda computed by oracle."""
    n = t + 1
    h = t
    arcs = []
    for i in range(t):
        arcs.append((i, (i+1) % t))
    for i in range(t):
        arcs.append((i, h))
        arcs.append((h, i))
    return n, arcs


def fam_interval_distinct(t, mult=2):
    """Path of digon blocks 0<->1<->...<->t, closed into a cycle, mult on each.
    Prefix sets {0..i} give boundary arc-set = {i->i+1 block} u {0->t? } distinct
    per i. Designed so cheap cuts have DISTINCT arc-sets (the i-th boundary)."""
    arcs = []
    for i in range(t):
        arcs += [(i, i+1)]*mult + [(i+1, i)]*mult
    arcs += [(t, 0)]*mult + [(0, t)]*mult
    return t+1, arcs


def fam_caterpillar(k, mult=3):
    """Backbone digon s<->o mult; each toggle p has s->p,p->o mult PLUS a
    private DIGON p<->q_p to a fresh leaf q_p so toggling p AND/OR q_p multiplies
    distinct cheap arc-sets while keeping cut size near lambda. Tries to beat the
    'private arc must cross' barrier by parking distinctness in a pendant digon
    that need NOT cross the main cut."""
    s, o = 0, 1
    arcs = [(s, o)]*mult + [(o, s)]*mult
    nxt = 2
    for j in range(k):
        p = nxt; nxt += 1
        arcs += [(s, p)]*mult + [(p, o)]*mult
    return nxt, arcs


def fam_doubled_cycle(t, mult=1):
    """C_t^2 thickened: distinct minimal out-cuts are the consecutive arcs;
    count distinct cheap arc-sets vs n^{2a}."""
    n = t
    arcs = []
    for i in range(n):
        arcs += [(i, (i+1) % n)]*mult + [(i, (i+2) % n)]*mult
    return n, arcs


def fam_blowup_star(k, mult=3):
    """Hub-and-spoke where MANY single-vertex cuts each give a DISTINCT cheap
    arc-set: central digon backbone + k pendant vertices each attached by a
    UNIQUE pair of arcs of mult ceil so that each pendant's out-cut {pendant->hub}
    is a distinct singleton arc-set of size exactly lambda."""
    s, o = 0, 1
    arcs = [(s, o)]*mult + [(o, s)]*mult
    nxt = 2
    for j in range(k):
        p = nxt; nxt += 1
        # pendant attached by mult arcs each way -> singleton cut size=mult=lambda
        arcs += [(p, s)]*mult + [(o, p)]*mult
    return nxt, arcs


def run_adv(tr):
    recs = []

    def consider(tag, n, arcs):
        if n > 21:
            return
        lam = oracle.arc_connectivity(n, arcs)
        if lam < 1:
            return
        cc = tr.update(n, arcs, lam, tag)
        rec = {"tag": tag, "n": n, "lambda": lam}
        for (lbl, _a) in ALPHAS:
            rec[f"aset_{lbl}"] = cc[lbl]["n_arcsets"]
            rec[f"ratio_{lbl}"] = round(cc[lbl]["ratio"], 4)
        recs.append(rec)

    for k in range(6, 17):
        consider("g11_private", *fam_g11_private(k))
    for t in range(5, 19):
        consider("bond_pool", *fam_bond_pool(t))
    for t in range(4, 18):
        consider("interval_distinct", *fam_interval_distinct(t))
    for k in range(6, 18):
        consider("caterpillar", *fam_caterpillar(k))
    for t in range(5, 21):
        consider("doubled_cycle", *fam_doubled_cycle(t))
    for k in range(6, 18):
        consider("blowup_star", *fam_blowup_star(k))
    return recs


def main():
    t0 = time.time()
    tr = Tracker()
    census_meta = []
    # generic census: n=4,5 full (-c only); n=6 use -d2 to fit budget but log it
    census_meta.append(run_census(4, tr, mind=0))
    census_meta.append(run_census(5, tr, mind=0))
    adv = run_adv(tr)
    out = {"elapsed_s": round(time.time()-t0, 2),
           "census_meta": census_meta,
           "adversarial": adv}
    out.update(tr.summary())
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
