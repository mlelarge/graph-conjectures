def beats_set(n, arcs):
    b = [[False]*n for _ in range(n)]
    for (u,v) in arcs:
        b[u][v] = True
    return b

def lex_substitute(outer, inner):
    (no, ao) = outer
    (ni, ai) = inner
    bo = beats_set(no, ao)
    bi = beats_set(ni, ai)
    N = no*ni
    arcs = []
    for o1 in range(no):
        for a1 in range(ni):
            u = o1*ni + a1
            for o2 in range(no):
                for a2 in range(ni):
                    v = o2*ni + a2
                    if u >= v: continue
                    beat = bi[a1][a2] if o1==o2 else bo[o1][o2]
                    arcs.append((u,v) if beat else (v,u))
    return N, arcs

def AC(n, g):
    gs = set(x % n for x in g)
    arcs = []
    for i in range(n):
        for j in range(n):
            if i==j: continue
            if (j-i)%n in gs: arcs.append((i,j))
    return n, arcs

def is_tournament(n, arcs):
    seen=set()
    for (u,v) in arcs:
        if (v,u) in seen: return False
        seen.add((u,v))
    return len(arcs)==n*(n-1)//2

C3 = (3, [(0,1),(1,2),(2,0)])
