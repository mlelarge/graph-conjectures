"""DK(alpha) DIRECTED-KARGER cut-counting census.

DK(alpha) conjecture (UNIVERSAL): for every lambda-arc-strong digraph D on
n>=3 vertices and every alpha>=1, the number of nonempty proper vertex sets X
with |delta^+(X)| <= alpha*lambda is at most n^{2*alpha}.

This script COUNTS, exactly, for each digraph:
    N(<= c) := #{ X : emptyset != X subsetneq V, |delta^+(X)| <= c }
for c = alpha*lambda over alpha in {1, 4/3, 5/3, 2}, by enumerating all
2^n - 2 proper nonempty subsets and summing arc-multiplicity leaving X.
lambda is computed exactly via the oracle's arc_connectivity (multiplicity
aware), for consistency with the SAD oracle.

The statistic of record is the MAX RATIO  N(<= alpha*lambda) / n^{2*alpha}.
DK predicts this ratio <= 1 for all alpha, all D.  A single instance with
ratio > 1 KILLS the exact form of DK.

Modes:
  --census-simple N   read base simple digraphs from stdin (geng|directg -T
                      stream), filter lambda>=3, record max ratio per alpha,
                      and the argmax digraph.
  --thicken N         like above but sweep multiplicity vectors {1..M}^arcs of
                      each base (multi-arc layer).  --maxmult M.
  --adversarial N     exact counts on built-in parameterized stress families
                      at sizes up to N (hub gadgets, chained digon gadgets,
                      doubled cycles C_n^2, random lambda>=3 multidigraphs);
                      expose any super-polynomial N(<=2lambda) growth.

All modes print a JSON summary at EOF.  No backgrounding; single foreground.
"""
import sys, os, json, time, itertools, argparse, random

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import oracle

ALPHAS = [("1", 1.0), ("4/3", 4.0 / 3.0), ("5/3", 5.0 / 3.0), ("2", 2.0)]


def out_cut_size(n, arcs_mult, X):
    """|delta^+(X)| = number of arcs (with multiplicity) from X to V\\X."""
    c = 0
    for (u, v) in arcs_mult:
        if u in X and v not in X:
            c += 1
    return c


def cut_counts(n, arcs_mult, lam):
    """For each alpha return N(<= alpha*lambda); enumerate all proper subsets.

    Returns dict alpha_label -> (count, ratio = count / n**(2*alpha)).
    """
    thresholds = {lbl: a * lam for (lbl, a) in ALPHAS}
    counts = {lbl: 0 for (lbl, _a) in ALPHAS}
    verts = list(range(n))
    # all nonempty proper subsets via bitmask 1 .. 2^n - 2
    for mask in range(1, (1 << n) - 1):
        X = frozenset(i for i in verts if (mask >> i) & 1)
        s = out_cut_size(n, arcs_mult, X)
        for (lbl, _a) in ALPHAS:
            if s <= thresholds[lbl]:
                counts[lbl] += 1
    out = {}
    for (lbl, a) in ALPHAS:
        denom = n ** (2.0 * a)
        out[lbl] = (counts[lbl], counts[lbl] / denom)
    return out


class RatioTracker:
    def __init__(self):
        self.worst = {lbl: {"ratio": -1.0, "count": 0, "n": 0,
                            "lambda": 0, "arcs": None}
                      for (lbl, _a) in ALPHAS}
        self.violations = []  # ratio > 1 instances (KILL)

    def update(self, n, arcs_mult, lam, tag=None):
        cc = cut_counts(n, arcs_mult, lam)
        for (lbl, _a) in ALPHAS:
            count, ratio = cc[lbl]
            if ratio > self.worst[lbl]["ratio"]:
                self.worst[lbl] = {"ratio": round(ratio, 5), "count": count,
                                   "n": n, "lambda": lam,
                                   "arcs": [list(a) for a in arcs_mult],
                                   "tag": tag}
            if ratio > 1.0:
                self.violations.append(
                    {"alpha": lbl, "ratio": round(ratio, 5),
                     "count": count, "n": n, "lambda": lam,
                     "arcs": [list(a) for a in arcs_mult], "tag": tag})
        return cc

    def summary(self):
        return {"worst_per_alpha": self.worst,
                "violations": self.violations,
                "DK_survives": len(self.violations) == 0}


def parse_stream_line(line):
    toks = line.split()
    nv = int(toks[0]); ne = int(toks[1])
    nums = list(map(int, toks[2:]))
    arcs = [(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]
    assert len(arcs) == ne, (ne, len(arcs), line)
    return nv, arcs


def run_census_simple(n_expected):
    t0 = time.time()
    tr = RatioTracker()
    n_read = 0
    n_lam_ge3 = 0
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        nv, arcs = parse_stream_line(line)
        n_read += 1
        lam = oracle.arc_connectivity(nv, arcs)
        if lam < 3:
            continue
        n_lam_ge3 += 1
        tr.update(nv, arcs, lam, tag="simple")
    s = {"mode": "census-simple", "n": n_expected,
         "n_digraphs_read": n_read, "n_lambda_ge3": n_lam_ge3,
         "elapsed_s": round(time.time() - t0, 2)}
    s.update(tr.summary())
    print(json.dumps(s, indent=2))


def run_thicken(n_expected, M):
    t0 = time.time()
    tr = RatioTracker()
    n_bases = 0
    n_multi = 0
    n_lam_ge3 = 0
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        nv, base_arcs = parse_stream_line(line)
        n_bases += 1
        ne = len(base_arcs)
        for mult in itertools.product(range(1, M + 1), repeat=ne):
            arcs = []
            for (u, v), k in zip(base_arcs, mult):
                arcs.extend([(u, v)] * k)
            n_multi += 1
            lam = oracle.arc_connectivity(nv, arcs)
            if lam < 3:
                continue
            n_lam_ge3 += 1
            tr.update(nv, arcs, lam, tag="thicken")
    s = {"mode": "thicken", "n": n_expected, "maxmult": M,
         "n_bases_read": n_bases, "n_multidigraphs": n_multi,
         "n_lambda_ge3": n_lam_ge3,
         "elapsed_s": round(time.time() - t0, 2)}
    s.update(tr.summary())
    print(json.dumps(s, indent=2))


# --------------------------------------------------------------------------- #
#  Adversarial parameterized families
# --------------------------------------------------------------------------- #

def fam_doubled_cycle(n):
    """C_n^2: arcs i->i+1 and i->i+2 (mod n).  lambda=2 (NOT >=3) but a
    classic max-many-small-cuts object; included as a stress reference."""
    arcs = []
    for i in range(n):
        arcs.append((i, (i + 1) % n))
        arcs.append((i, (i + 2) % n))
    return arcs


def fam_doubled_cycle_thick(n):
    """Thicken each arc of C_n^2 to multiplicity 2 -> lambda=4.  Many small
    directed cuts (the consecutive-arc structure) at lambda>=3."""
    arcs = []
    for i in range(n):
        arcs += [(i, (i + 1) % n)] * 2
        arcs += [(i, (i + 2) % n)] * 2
    return arcs


def fam_tripled_cycle(n):
    """C_n^3: i->i+1,i+2,i+3 each mult 1.  lambda=3, locally-semicomplete-ish,
    many consecutive small out-cuts (intervals)."""
    arcs = []
    for i in range(n):
        for d in (1, 2, 3):
            arcs.append((i, (i + d) % n))
    return arcs


def fam_hub_gadget(n, mult=3):
    """Hub vertex 0 with multiplicity-`mult` arcs to/from every other vertex,
    plus a directed cycle on 1..n-1 to keep it strong.  Stresses delta^-
    imbalance (the proposal's named failure mode)."""
    arcs = []
    for v in range(1, n):
        arcs += [(0, v)] * mult
        arcs += [(v, 0)] * mult
    for v in range(1, n):
        nxt = v + 1 if v + 1 < n else 1
        arcs += [(v, nxt)] * 3
    return arcs


def fam_chained_digon(n):
    """Chain of digon gadgets: vertices 0..n-1 on a directed cycle, each arc
    thickened to mult 3, plus back-digons i<->i+1 at mult 3.  Eulerian-ish,
    many small balanced cuts."""
    arcs = []
    for i in range(n):
        j = (i + 1) % n
        arcs += [(i, j)] * 3
        arcs += [(j, i)] * 3
    return arcs


def fam_complete_bidirected(n):
    """K_n^*: every ordered pair an arc.  lambda=n-1.  Few small cuts but a
    control (the SAT control from the ledger)."""
    arcs = []
    for u in range(n):
        for v in range(n):
            if u != v:
                arcs.append((u, v))
    return arcs


def fam_random_regular(n, deg=3, seed=0):
    """Random near-regular multidigraph: each vertex gets `deg` random out-arcs
    and we symmetrize a bit to push lambda>=3.  Generic-random stress."""
    rng = random.Random(seed)
    arcs = []
    for u in range(n):
        for _ in range(deg + 1):
            v = rng.randrange(n)
            if v != u:
                arcs.append((u, v))
            # also a back arc to help strong-ness
            w = rng.randrange(n)
            if w != u:
                arcs.append((w, u))
    return arcs


def run_adversarial(n_max):
    t0 = time.time()
    tr = RatioTracker()
    records = []
    # n ranges chosen so each enumeration (2^n subsets) stays cheap; cap n<=18.
    def consider(tag, nv, arcs):
        # enumerating 2^nv subsets: keep nv <= 20
        if nv > 20:
            return
        lam = oracle.arc_connectivity(nv, arcs)
        cc = tr.update(nv, arcs, lam, tag=tag)
        rec = {"tag": tag, "n": nv, "lambda": lam}
        for (lbl, _a) in ALPHAS:
            count, ratio = cc[lbl]
            rec[f"N(<= {lbl}*lam)"] = count
            rec[f"ratio_{lbl}"] = round(ratio, 5)
        records.append(rec)

    for nv in range(4, min(n_max, 18) + 1):
        consider("Cn2", nv, fam_doubled_cycle(nv))
        consider("Cn2_thick2", nv, fam_doubled_cycle_thick(nv))
        consider("Cn3", nv, fam_tripled_cycle(nv))
        consider("hub_mult3", nv, fam_hub_gadget(nv, 3))
        consider("chained_digon", nv, fam_chained_digon(nv))
    for nv in range(4, min(n_max, 10) + 1):
        consider("Kstar", nv, fam_complete_bidirected(nv))
    for nv in range(8, min(n_max, 18) + 1):
        for seed in range(4):
            consider(f"random_d3_s{seed}", nv,
                     fam_random_regular(nv, 3, seed))

    s = {"mode": "adversarial", "n_max": n_max,
         "n_instances": len(records),
         "elapsed_s": round(time.time() - t0, 2),
         "records": records}
    s.update(tr.summary())
    print(json.dumps(s, indent=2))


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--census-simple", type=int, metavar="N")
    g.add_argument("--thicken", type=int, metavar="N")
    g.add_argument("--adversarial", type=int, metavar="N")
    ap.add_argument("--maxmult", type=int, default=2)
    args = ap.parse_args()

    if args.census_simple is not None:
        run_census_simple(args.census_simple)
    elif args.thicken is not None:
        run_thicken(args.thicken, args.maxmult)
    elif args.adversarial is not None:
        run_adversarial(args.adversarial)


if __name__ == "__main__":
    main()
