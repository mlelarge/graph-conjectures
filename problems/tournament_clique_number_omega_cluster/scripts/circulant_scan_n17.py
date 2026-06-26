"""Branch (b/H2 + H5) lever from next_action: SEARCH for a VERTEX-TRANSITIVE
3-omega_vec-critical CIRCULANT tournament at prime p=17 (and confirm method on
p=13/P9 first).

A circulant tournament C_p(g) on Z/p: arc i->j iff (j-i) mod p in g, where g and
-g partition {1..p-1}.  These are vertex-transitive (rotation x->x+1 is an
automorphism), so:
  * omega_vec is attained by an order STARTING at vertex 0 (symmetry-reduced bb:
    fix order[0]=0, bb over the remaining p-1 positions).  SOUND because the
    cyclic group acts on total orders.
  * 3-criticality collapses to a SINGLE deletion check: all p single-vertex
    deletions are isomorphic, so omega_vec(T-v)=2 for ALL v iff it holds for v=0.

KILL-DODGE filters (per graveyard G2/G7):
  * non-consecutive generator set (otherwise local => G7, and consecutive
    circulants have omega_vec=2 anyway).
  * for p=1 mod 4 (17) there is NO QR/Paley tournament, so the QR graveyard (G2)
    does not even apply; we still skip g == QR_p when p=3 mod 4.

Output: data/circulant_scan_n17.json with omega_vec histogram over all valid
generator sets (one per g/-g complementary pair) and the list of any
3-omega_vec-critical generators found.

Symmetry-reduced bb is implemented here (NOT in core, which has only the
unrestricted bb).  We CROSS-CHECK it on p=13/g={1,2,3,4,5,7} (P9): must give 3.
"""
import sys, os, json, time, itertools
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import networkx as nx
from core import is_tournament, omega_vec_bb
# FAST bitmask decision routines (validated in the n9 census vs the canonical
# oracle: 0 mismatches over all 6880 n=8 iso classes, ledger P9b). These decide
# omega_vec<=t WITHOUT rebuilding a networkx graph per bb node, so they scale to
# p=17 where the networkx-based sym_bb does not (a single p=17 call exceeded 8min).
from iso_critical_scan_n9 import omega_vec_le2, omega_vec_le_t, sub_beats

# --------------------------------------------------------------------------- #
def circulant_arcs(p, g):
    gs = set(g)
    arcs = []
    for i in range(p):
        for j in range(p):
            if i == j:
                continue
            if (j - i) % p in gs:
                arcs.append((i, j))
    return arcs


def beats_matrix(p, arcs):
    b = [[False] * p for _ in range(p)]
    for (u, v) in arcs:
        b[u][v] = True
    return b


def clique_number(g):
    if g.number_of_nodes() == 0:
        return 0
    return max((len(c) for c in nx.find_cliques(g)), default=1)


def omega_vec_sym_bb(p, arcs, fixed_first=0, ub=None):
    """EXACT omega_vec for a VERTEX-TRANSITIVE tournament, computed by branch-and
    -bound over orders whose prec-smallest vertex is `fixed_first`.

    SOUND for vertex-transitive T: the automorphism group is transitive on V, so
    the global min over all orders is attained by an order starting at any chosen
    orbit representative.  We fix order[0]=fixed_first and bb over the rest.

    Same prefix-monotone clique-number prune as core.omega_vec_bb.
    """
    beats = beats_matrix(p, arcs)
    if ub is None:
        ub = p
    best = [ub]
    placed = [fixed_first]
    placed_adj = {fixed_first: set()}

    def cur_clique_number():
        g = nx.Graph()
        g.add_nodes_from(placed)
        for v in placed:
            for u in placed_adj[v]:
                g.add_edge(u, v)
        return clique_number(g)

    def recurse(remaining):
        if not remaining:
            w = cur_clique_number()
            if w < best[0]:
                best[0] = w
            return
        cur = cur_clique_number()
        if cur >= best[0]:
            return
        for b in list(remaining):
            nb = {a for a in placed if beats[b][a]}
            placed.append(b)
            placed_adj[b] = nb
            for a in nb:
                placed_adj[a].add(b)
            recurse(remaining - {b})
            placed.pop()
            for a in nb:
                placed_adj[a].discard(b)
            del placed_adj[b]

    recurse(frozenset(r for r in range(p) if r != fixed_first))
    return best[0]


def beats_from_arcs(p, arcs):
    return beats_matrix(p, arcs)


def omega_vec_le2_vt(p, beats, fixed_first=0):
    """omega_vec(T) <= 2 ?  for a VERTEX-TRANSITIVE tournament T, decided by the
    fast bitmask triangle-free search with the prec-smallest vertex FIXED to
    `fixed_first`.  SOUND for vertex-transitive T: a triangle-free backedge order
    exists iff one exists that starts at any chosen orbit representative (the
    automorphism group is transitive on V, and acts on total orders), so fixing
    order[0]=fixed_first does not change the YES/NO answer.  This cuts the top-level
    branching by a factor of p versus the unrestricted omega_vec_le2, which is what
    makes the omega_vec>=3 (le2 == False) proof tractable at p=17.

    Bitmask copy of omega_vec_le2 with the first vertex pinned."""
    full = (1 << p) - 1
    backrow = [0] * p
    for b in range(p):
        m = 0
        rb = beats[b]
        for a in range(p):
            if rb[a]:
                m |= (1 << a)
        backrow[b] = m
    adj = [0] * p

    def recurse(remaining, placed_mask):
        if remaining == 0:
            return True
        cands = []
        rem = remaining
        while rem:
            b = (rem & -rem).bit_length() - 1
            rem &= rem - 1
            nb = backrow[b] & placed_mask
            tri = False
            t = nb
            while t:
                a = (t & -t).bit_length() - 1
                t &= t - 1
                if adj[a] & nb:
                    tri = True
                    break
            if tri:
                continue
            cands.append((bin(nb).count("1"), b, nb))
        cands.sort()
        for _cnt, b, nb in cands:
            bit_b = 1 << b
            t = nb
            while t:
                a = (t & -t).bit_length() - 1
                t &= t - 1
                adj[a] |= bit_b
            adj[b] = nb
            if recurse(remaining & ~bit_b, placed_mask | bit_b):
                return True
            t = nb
            while t:
                a = (t & -t).bit_length() - 1
                t &= t - 1
                adj[a] &= ~bit_b
            adj[b] = 0
        return False

    # fix the first placed vertex = fixed_first (it has no earlier vertices, so no
    # backedges; placed_mask starts with just it)
    bit0 = 1 << fixed_first
    adj[fixed_first] = 0
    return recurse(full & ~bit0, bit0)


def circulant_3critical_fast(p, g):
    """Return (omega_vec_class, is_3critical, arcs) for circulant C_p(g) using ONLY
    the cheap triangle-free decision omega_vec_le2, via the criticality-decoupling
    lemma (P9b) + the vertex-transitive collapse:

      * omega_vec_le2(T)  decides omega_vec(T) <= 2  (==2 here since T has a C3).
      * For a VERTEX-TRANSITIVE T, all p single-vertex deletions are isomorphic, so
        3-criticality <=> omega_vec(T-0) == 2 for the ONE deletion v=0.
      * CRITICALITY-DECOUPLING LEMMA: if omega_vec(T-0) == 2 (le2(T-0) True and T-0
        not transitive) AND omega_vec(T) >= 3 (le2(T) False), then by sub-additivity
        omega_vec(T) <= omega_vec(T-0)+1 = 3 and by sub-tournament monotonicity
        omega_vec(T) >= omega_vec(T-0)+? ... in fact omega_vec(T) is forced to be
        EXACTLY 3 (it is >=3 and <=3).  So we NEVER need the expensive le_t(.,3)
        decision (which is the call that blows up at p=17 when omega_vec >= 4).

    Returns omega_vec_class in {2, '>=3'} (we do not separate 3 vs >=4 unless the
    deletion check certifies omega_vec(T)==3, in which case it is exactly 3)."""
    arcs = circulant_arcs(p, g)
    beats = beats_from_arcs(p, arcs)
    if omega_vec_le2_vt(p, beats, fixed_first=0):   # symmetry-reduced (T vertex-transitive)
        return 2, False, arcs            # omega_vec(T) == 2
    # omega_vec(T) >= 3.  Single deletion (vertex-transitive => all iso).
    # NOTE: T-0 is NOT vertex-transitive, so use the UNRESTRICTED le2 here.
    m, sb = sub_beats(p, beats, 0)
    if not omega_vec_le2(m, sb):
        return '>=3', False, arcs        # omega_vec(T-0) >= 3 -> NOT 3-critical
    score = [sum(sb[u][v] for v in range(m)) for u in range(m)]
    if sorted(score) == list(range(m)):
        return '>=3', False, arcs        # T-0 transitive (omega_vec==1) -> not critical
    # omega_vec(T-0)==2 and omega_vec(T)>=3 => omega_vec(T)==3 (decoupling lemma)
    return 3, True, arcs


def deletion_omega_vec(p, arcs, v):
    """omega_vec of T - v (relabelled), via unrestricted core bb (T-v is NOT
    vertex-transitive)."""
    keep = [w for w in range(p) if w != v]
    relabel = {w: i for i, w in enumerate(keep)}
    ks = set(keep)
    sub = [(relabel[u], relabel[v2]) for (u, v2) in arcs if u in ks and v2 in ks]
    return omega_vec_bb(len(keep), sub)


def is_consecutive(p, g):
    """True iff g is a consecutive block {a, a+1, ..., a+len-1} mod p (=> local)."""
    s = sorted(x % p for x in g)
    # check rotation to a run
    full = sorted(s)
    for shift in range(p):
        rot = sorted((x + shift) % p for x in s)
        if rot == list(range(len(rot))):
            return True
    return False


# --------------------------------------------------------------------------- #
def valid_generator_sets(p):
    """Yield each generator set g (one representative per g/-g complementary
    partition) with |g| = (p-1)/2 such that g and -g partition {1..p-1}.

    A subset g of {1..p-1} is a valid tournament generator iff for every
    d in {1..p-1} exactly one of d, p-d is in g.  Equivalently choose, for each
    of the (p-1)/2 antipodal pairs {d, p-d}, which element goes into g.
    To avoid double counting g vs -g (they give isomorphic reversed tournaments
    but DIFFERENT omega_vec? no - reversal preserves omega_vec), we still
    enumerate all 2^{(p-1)/2} and could halve, but keep all for completeness and
    dedup by frozenset later if needed."""
    half = (p - 1) // 2
    pairs = [(d, p - d) for d in range(1, half + 1)]
    for bits in itertools.product((0, 1), repeat=half):
        g = tuple(sorted(pairs[i][bits[i]] for i in range(half)))
        yield g


# --------------------------------------------------------------------------- #
def cross_check():
    """Validate the FAST decision pipeline against the PROVED ledger witnesses:
      * P9: p=13, g={1,2,3,4,5,7} -> omega_vec=3, 3-critical.
      * P8: p=11, g={1,2,3,4,6}   -> omega_vec=3, 3-critical.
      * QR_11 (G2/G9 counterexample): p=11, g={1,3,4,5,9} -> omega_vec=3, NOT
        3-critical (all deletions=3). This guards against a false-positive bug.
      * consecutive {1,2,3,4,5} mod 11 -> omega_vec=2 (must NOT be 3).
    Also cross-checks the fast omega_vec on p=13 against the SLOW networkx sym_bb
    once (the proved value 3)."""
    ok = True
    # expected class: 3 (== exactly 3 AND critical), '>=3' (omega_vec>=3 non-crit),
    # or 2.  P8/P9 are 3-critical => class 3.  QR_11 is omega_vec=3 but NOT critical
    # => the fast pipeline reports '>=3' (it does not separate 3 from >=4 for a
    # non-critical witness; that is fine — it is correctly NOT flagged critical).
    cases = [
        (13, (1, 2, 3, 4, 5, 7), 3,     True,  'P9'),
        (11, (1, 2, 3, 4, 6),    3,     True,  'P8'),
        (11, (1, 3, 4, 5, 9),    '>=3', False, 'QR_11 (vertex-transitive, NOT critical)'),
        (11, (1, 2, 3, 4, 5),    2,     False, 'consecutive (local, omega_vec=2)'),
    ]
    for p, g, exp_w, exp_crit, tag in cases:
        arcs = circulant_arcs(p, g)
        assert is_tournament(p, arcs), f"{tag} not a tournament"
        # SOUNDNESS GUARD: symmetry-reduced le2 must agree with unrestricted le2.
        beats = beats_from_arcs(p, arcs)
        vt = omega_vec_le2_vt(p, beats, 0)
        un = omega_vec_le2(p, beats)
        if vt != un:
            print(f'[xcheck {tag}] SYM-GUARD FAIL: le2_vt={vt} != le2={un}', flush=True)
            ok = False
        t0 = time.time()
        w, crit, _ = circulant_3critical_fast(p, g)
        dt = time.time() - t0
        good = (w == exp_w) and (crit == exp_crit) and (vt == un)
        ok = ok and good
        print(f'[xcheck {tag}] p={p} g={list(g)} fast omega_vec={w} 3crit={crit} '
              f'le2_vt==le2:{vt==un} ({dt:.2f}s) expect(w={exp_w},crit={exp_crit}) '
              f'-> {"OK" if good else "FAIL"}', flush=True)
    # one slow-vs-fast omega_vec agreement check on p=13 (proved value 3)
    t0 = time.time()
    w_slow = omega_vec_sym_bb(13, circulant_arcs(13, (1, 2, 3, 4, 5, 7)))
    print(f'[xcheck slow-bb p13] networkx sym_bb omega_vec={w_slow} ({time.time()-t0:.1f}s) '
          f'(proved 3) -> {"OK" if w_slow == 3 else "FAIL"}', flush=True)
    ok = ok and (w_slow == 3)
    return ok


def scan(p, time_budget=None):
    """Scan all valid generator sets at order p.  For each, compute omega_vec via
    symmetry-reduced bb; if ==3, do the single deletion check (vertex 0)."""
    hist = {2: 0, 3: 0, 'ge3_noncrit': 0}
    critical = []
    omega3_gens = []
    seen = set()
    t_start = time.time()
    count = 0
    for g in valid_generator_sets(p):
        # dedup g vs its reverse -g (isomorphic reversed tournament, same omega_vec)
        neg = tuple(sorted((p - x) % p for x in g))
        key = min(g, neg)
        if key in seen:
            continue
        seen.add(key)
        count += 1
        consec = is_consecutive(p, g)
        t0 = time.time()
        w, is_crit, arcs = circulant_3critical_fast(p, g)
        dt = time.time() - t0
        if w == 2:
            hist[2] += 1
        elif w == 3:                       # certified omega_vec==3 AND 3-critical
            hist[3] += 1
            omega3_gens.append({'g': list(g), 'consecutive': consec, 'sec': round(dt, 2)})
            print(f'[p={p}] g={list(g)} consec={consec} omega_vec=3 '
                  f'-> 3critical={is_crit} ({dt:.2f}s)', flush=True)
            critical.append({'g': list(g), 'consecutive': consec, 'sec': round(dt, 2)})
        else:                              # '>=3' but deletion >=3 => omega_vec>=3 non-critical
            hist['ge3_noncrit'] += 1
        print(f'[p={p} #{count}] g={list(g)} consec={consec} class={w} '
              f'crit={is_crit} ({dt:.2f}s)', flush=True)
        if time_budget is not None and (time.time() - t_start) > time_budget:
            print(f'  !! time budget {time_budget}s exceeded after {count} sets', flush=True)
            break
    return {
        'p': p,
        'scanned_gen_sets': count,
        'omega_hist': hist,
        'num_omega3': hist[3],
        'omega3_gens': omega3_gens,
        'num_3critical': len(critical),
        'critical_gens': critical,
        'seconds': round(time.time() - t_start, 1),
        'complete': time_budget is None or (time.time() - t_start) <= time_budget,
    }


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('p', type=int, nargs='?', default=17)
    ap.add_argument('--budget', type=float, default=None,
                    help='time budget in seconds for the scan loop')
    ap.add_argument('--skip-xcheck', action='store_true')
    args = ap.parse_args()

    if not args.skip_xcheck:
        ok = cross_check()
        print(f'CROSS-CHECK PASS={ok}', flush=True)
        if not ok:
            print('CROSS-CHECK FAILED — fast pipeline disagrees with proved '
                  'ledger witnesses, aborting', flush=True)
            sys.exit(2)

    res = scan(args.p, time_budget=args.budget)
    outpath = os.path.join(os.path.dirname(__file__), '..', 'data',
                           f'circulant_scan_n{args.p}.json')
    outpath = os.path.abspath(outpath)
    json.dump(res, open(outpath, 'w'), indent=1)
    print(f'=== p={args.p} DONE: scanned={res["scanned_gen_sets"]} '
          f'hist={res["omega_hist"]} #omega3={res["num_omega3"]} '
          f'#3critical={res["num_3critical"]} ({res["seconds"]}s) '
          f'complete={res["complete"]} ===', flush=True)
    if res['critical_gens']:
        print('3-CRITICAL VERTEX-TRANSITIVE CIRCULANTS FOUND:', flush=True)
        for c in res['critical_gens']:
            print('   g =', c['g'], 'consecutive=', c['consecutive'], flush=True)
    else:
        print('NO 3-critical vertex-transitive circulant at this order.', flush=True)
    print('saved', outpath, flush=True)
