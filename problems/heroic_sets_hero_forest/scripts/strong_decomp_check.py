import sys, subprocess
sys.path.insert(0, "scripts")
import core

C3 = core.C3(); S2P = core.S2_plus()

def in_class(D):
    return not (core.contains_induced(D, C3) or core.contains_induced(D, S2P))

def all_simple_graphs(n):
    gp = core.dc._geng_path()
    proc = subprocess.run([gp, "-q", str(n)], capture_output=True, text=True)
    for line in proc.stdout.splitlines():
        if line.strip():
            gn, ed = core.dc._graph6_to_edges(line)
            yield ed

def tarjan_scc(n, arcs):
    succ = [[] for _ in range(n)]
    for (u, v) in arcs:
        succ[u].append(v)
    index = [None]*n; low = [0]*n; onstack = [False]*n
    idx = [0]; stack = []; comps = []
    import sys as _s
    _s.setrecursionlimit(10000)
    def strong(v):
        index[v] = low[v] = idx[0]; idx[0]+=1
        stack.append(v); onstack[v]=True
        for w in succ[v]:
            if index[w] is None:
                strong(w); low[v]=min(low[v], low[w])
            elif onstack[w]:
                low[v]=min(low[v], index[w])
        if low[v]==index[v]:
            comp=[]
            while True:
                w=stack.pop(); onstack[w]=False; comp.append(w)
                if w==v: break
            comps.append(comp)
    for v in range(n):
        if index[v] is None: strong(v)
    return comps

def main():
    for n in range(2, 8):
        whole_max = 0
        comp_max = 0
        bad_comp = None
        mismatch = None
        cnt = 0
        for edges in all_simple_graphs(n):
            for arcs in core.all_orientations(edges):
                D = (n, arcs)
                if not in_class(D):
                    continue
                cnt += 1
                whole = core.dichromatic_number(D)
                if whole > whole_max: whole_max = whole
                comps = tarjan_scc(n, arcs)
                cmax = 1
                for comp in comps:
                    if len(comp) <= 1:
                        continue
                    s = set(comp)
                    sub_arcs = [(u, v) for (u, v) in arcs if u in s and v in s]
                    remap = {v: i for i, v in enumerate(comp)}
                    sub = (len(comp), [(remap[u], remap[v]) for (u, v) in sub_arcs])
                    c = core.dichromatic_number(sub)
                    if c > cmax: cmax = c
                    if c >= 3 and bad_comp is None:
                        bad_comp = (sub, c)
                if cmax > comp_max: comp_max = cmax
                # chi_d of whole should equal max over SCC component chi_d (singletons=1)
                if whole != cmax and mismatch is None:
                    mismatch = (arcs, whole, cmax)
        print(f"n={n} members={cnt} whole_max_chi={whole_max} max_comp_chi={comp_max} "
              f"bad_comp={bad_comp} mismatch(whole!=maxSCC)={mismatch}")

if __name__ == "__main__":
    main()
