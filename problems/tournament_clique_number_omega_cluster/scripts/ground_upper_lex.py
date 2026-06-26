import sys, time, random, itertools
sys.path.insert(0,'scripts')
import core
from lexlib import lex_substitute, AC, is_tournament, C3

AC7 = AC(7, {1,2,4})
AC7_C3 = lex_substitute(AC7, C3)          # order 21
T = lex_substitute(C3, AC7_C3)            # order 63
n, arcs = T
print("order", n, "tournament", is_tournament(n,arcs)); sys.stdout.flush()

# best per-factor orders.
# For a factor (m, a), find a good order minimizing backedge clique (small m -> brute over rotations).
def best_order_factor(m, a):
    best=None; bestw=None
    base=list(range(m))
    # try all rotations + a few random
    cands=[base[i:]+base[:i] for i in range(m)]
    rng=random.Random(7)
    for _ in range(200):
        o=base[:]; rng.shuffle(o); cands.append(o)
    for o in cands:
        w=core.omega_of_order(m,a,o)
        if bestw is None or w<bestw:
            bestw=w; best=o
    return best, bestw

# factor orders
oC3, wC3 = best_order_factor(3, C3[1])
oAC7, wAC7 = best_order_factor(7, AC7[1])
oAC7C3, wAC7C3 = best_order_factor(21, AC7_C3[1])
print(f"factor optima: C3 w={wC3}, AC7 w={wAC7}, AC7[C3] w={wAC7C3}")
sys.stdout.flush()

# Build composite orders by priority of coordinate levels.
# vertex flat = ((c*7)+b)*3 + d  where c in C3 outer(0..2), b in AC7(0..6), d in C3 inner(0..2)
# Actually T = C3[ AC7[C3] ]: outer index o in 0..2 (C3), inner index in 0..20 (AC7[C3]).
# AC7[C3]: index = b*3+d, b in 0..6 (AC7), d in 0..2 (inner C3).
# flat = o*21 + (b*3+d).
def flat(o,b,d): return o*21 + (b*3+d)

# rank maps from per-factor best orders
rkC3 = {v:i for i,v in enumerate(oC3)}        # outer C3
rkB  = {v:i for i,v in enumerate(oAC7)}       # AC7
rkD  = {v:i for i,v in enumerate(oC3)}        # inner C3 (same as C3 order)
rkAC7C3 = {v:i for i,v in enumerate(oAC7C3)}  # combined inner block order

def order_by_key(keyfn):
    items=[]
    for o in range(3):
        for b in range(7):
            for d in range(3):
                items.append((keyfn(o,b,d), flat(o,b,d)))
    items.sort()
    return [v for _,v in items]

orders = {}
# outer_then_inner: outer C3 first, then AC7, then inner C3
orders['outer_b_d']   = order_by_key(lambda o,b,d:(rkC3[o], rkB[b], rkD[d]))
# inner_then_outer: AC7 first, then inner C3, then outer
orders['b_d_outer']   = order_by_key(lambda o,b,d:(rkB[b], rkD[d], rkC3[o]))
# inner C3 first
orders['d_b_outer']   = order_by_key(lambda o,b,d:(rkD[d], rkB[b], rkC3[o]))
# outer over (AC7[C3] combined order)
orders['outer_then_innerblock'] = order_by_key(lambda o,b,d:(rkC3[o], rkAC7C3[b*3+d]))
orders['innerblock_then_outer'] = order_by_key(lambda o,b,d:(rkAC7C3[b*3+d], rkC3[o]))
# merged sum keys
orders['mergedsum'] = order_by_key(lambda o,b,d:(rkC3[o]+rkB[b]+rkD[d], rkC3[o], rkB[b], rkD[d]))
orders['mergedsum2'] = order_by_key(lambda o,b,d:(rkC3[o]*7+rkB[b], rkD[d]))

best_overall=None
for name,o in orders.items():
    assert sorted(o)==list(range(63))
    w=core.omega_of_order(n,arcs,o)
    print(f"order {name}: backedge clique = {w}")
    if best_overall is None or w<best_overall: best_overall=w
    sys.stdout.flush()

# random-restart sweep
rng=random.Random(2024)
base=list(range(63))
t=time.time()
rbest=99
for _ in range(3000):
    o=base[:]; rng.shuffle(o)
    w=core.omega_of_order(n,arcs,o)
    if w<rbest: rbest=w
    if rbest<=5: break
print(f"random sweep best = {rbest} ({time.time()-t:.1f}s)")
best_overall=min(best_overall,rbest)
print("BEST UPPER BOUND omega_vec(C3[AC7[C3]]) <=", best_overall)
print("lex lower bound = 5 (proven: 2+ov(AC7[C3])-1 = 2+4-1)")
if best_overall<=5:
    print("VERDICT: CONFIRM (upper=lower=5, simple-outer adds exactly +1)")
elif best_overall==6:
    print("VERDICT: KILL-evidence (best structured upper=6 > lower 5; simple-outer overshoots like D22)")
else:
    print("VERDICT: inconclusive upper", best_overall)
