import sys, subprocess
sys.path.insert(0,"scripts")
import core
C3=core.C3(); S2P=core.S2_plus()
def in_class(D): return not (core.contains_induced(D,C3) or core.contains_induced(D,S2P))
def all_simple_graphs(n):
    gp=core.dc._geng_path()
    proc=subprocess.run([gp,"-q",str(n)],capture_output=True,text=True)
    for line in proc.stdout.splitlines():
        if line.strip():
            gn,ed=core.dc._graph6_to_edges(line); yield ed
def is_strong(n,arcs):
    if n<=1: return True
    succ=[[] for _ in range(n)]; pred=[[] for _ in range(n)]
    for (u,v) in arcs: succ[u].append(v); pred[v].append(u)
    def reach(adj,s):
        seen={s}; st=[s]
        while st:
            x=st.pop()
            for y in adj[x]:
                if y not in seen: seen.add(y); st.append(y)
        return seen
    return len(reach(succ,0))==n and len(reach(pred,0))==n
for n in range(2,8):
    mmax=0; over=0; cnt=0; argover=None
    for edges in all_simple_graphs(n):
        for arcs in core.all_orientations(edges):
            D=(n,arcs)
            if not in_class(D): continue
            if not is_strong(n,arcs): continue
            cnt+=1
            m=len(arcs)
            if m>mmax: mmax=m
            if m>2*n: over+=1; argover=arcs if argover is None else argover
    print(f"n={n} strong_members={cnt} max_arcs={mmax} 2n={2*n} m>2n_count={over} ex={argover}")
