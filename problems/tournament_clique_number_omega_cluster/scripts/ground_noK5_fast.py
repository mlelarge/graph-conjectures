import sys, time
sys.path.insert(0,'scripts')
import core
from lexlib import lex_substitute, AC, is_tournament, C3
from pysat.formula import CNF
from pysat.solvers import Cadical153

AC7 = AC(7, {1,2,4})
T = lex_substitute(C3, lex_substitute(AC7, C3))
n, arcs = T
print("order", n, "tournament", is_tournament(n,arcs)); sys.stdout.flush()

beats = [[False]*n for _ in range(n)]
for (u,v) in arcs: beats[u][v]=True
# bitset adjacency: out[u] = set of v with u->v
out = [0]*n
for u in range(n):
    m=0
    for v in range(n):
        if beats[u][v]: m |= (1<<v)
    out[u]=m

def enumerate_transitive_chains(K):
    """yield transitive K-subsets as ordered chains s_1->...->s_K (s_1 source).
    build chain where each new vertex beats ALL previously chosen (so prepend as new source)
    -> simpler: extend chain at the SINK end: current sink s, next w with s->w and ALL prev->w.
    Maintain 'reach' = intersection mask of out-neighbours of all chosen, restricted to v>last to avoid dup."""
    res=[]
    def rec(chain, cand_mask):
        if len(chain)==K:
            res.append(tuple(chain)); return
        m=cand_mask
        while m:
            v = (m & -m).bit_length()-1
            m &= m-1
            # v must be beaten by all in chain (chain elements are sources w.r.t v)
            # extend: new candidate mask = cand_mask intersect out[v], and >v handled by ordering?
            # We need transitivity not order; to avoid dups enumerate by increasing vertex index of the *set*.
            rec(chain+[v], cand_mask & out[v] & ~((1<<(v+1))-1))
    # start: pick source s1 = any vertex, candidates = out[s1]
    for s in range(n):
        rec([s], out[s] & ~((1<<(s+1))-1))
    return res

# NOTE the above uses index-increasing to dedup but chain order isn't acyclic-by-index.
# Simpler/correct: enumerate transitive subsets via incremental: a transitive K-set has a
# linear order; we enumerate SETS by requiring we add vertices that are 'dominated' consistently.
# Use the standard: recursively build a chain s_1 -> s_2 -> ... where s_i -> s_j for i<j.
# To avoid duplicate SETS, we don't restrict by index but build the UNIQUE acyclic order, and
# only emit when it's the canonical (source-first) order. The recursion above keeps cand only
# among out-neighbours of ALL chosen => guarantees chosen-so-far all beat v => chain s1..s_{k} with
# each earlier beats later => acyclic source-first. Dedup by '>s' index restriction is WRONG since
# acyclic order != index order. Replace: dedup by requiring v's appended in increasing acyclic position
# is automatic (each set has exactly one source-first order). To avoid revisiting same set via diff
# build paths: each transitive set is built in exactly ONE way (always append current acyclic-next =
# the unique vertex beaten by all chosen and beating all remaining)... not unique mid-build.
# Safe approach: dedup with a seen-set of frozensets (memory heavy but correct).

def enumerate_transitive_sets(K, time_budget):
    t0=time.time()
    out_count=[0]
    chains=[]
    seen=set()
    def rec(chain_mask, chosen, cand_mask):
        if time.time()-t0>time_budget:
            raise TimeoutError
        if len(chosen)==K:
            chains.append(tuple(chosen)); return
        m=cand_mask
        while m:
            v=(m&-m).bit_length()-1
            m&=m-1
            rec(chain_mask|(1<<v), chosen+[v], cand_mask & out[v])
    # chosen list is acyclic source-first; each transitive set produced exactly once because
    # source-first acyclic order is unique. start each set from its source.
    for s in range(n):
        rec(1<<s, [s], out[s])
    return chains

t=time.time()
try:
    chains = enumerate_transitive_sets(5, 500)
    print(f"transitive 5-sets: {len(chains)}  ({time.time()-t:.1f}s)"); sys.stdout.flush()
except TimeoutError:
    print("ENUMERATION TIMEOUT at 500s -> no-K5 SAT INFEASIBLE at order 63"); sys.exit(0)

# build CNF
idx={}; nv=0
def lit(u,v):
    global nv
    if (u,v) in idx: return idx[(u,v)]
    if (v,u) in idx: return -idx[(v,u)]
    nv+=1; idx[(u,v)]=nv; return nv
for u in range(n):
    for v in range(u+1,n): lit(u,v)
cnf=CNF()
for u in range(n):
    for v in range(n):
        if v==u: continue
        for w in range(n):
            if w==u or w==v: continue
            cnf.append([-lit(u,v),-lit(v,w),lit(u,w)])
for ch in chains:
    cnf.append([lit(ch[i],ch[i+1]) for i in range(4)])
print("clauses:",len(cnf.clauses),"solving..."); sys.stdout.flush()
t=time.time()
with Cadical153(bootstrap_with=cnf.clauses) as m:
    sat=m.solve()
print(f"no-K5 SAT={sat} ({time.time()-t:.1f}s)  => omega_vec>=6 is {not sat}")
print("RESULT: omega_vec(C3[AC7[C3]]) >= 5:", not sat)
