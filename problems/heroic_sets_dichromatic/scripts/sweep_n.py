import os
import sys, json, time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import core

n=int(sys.argv[1])
t0=time.time()
graphs=list(core.triangle_free_graphs(n))
found=None; gi=0
for (gn,edges) in graphs:
    gi+=1
    edges=list(edges); m=len(edges)
    if m==0: continue
    # enumerate orientations, fix edge0 forward (global reversal symmetry)
    for bits in range(2**(m-1)):
        arcs=[edges[0]]
        for k in range(1,m):
            a,b=edges[k]
            arcs.append((a,b) if (bits>>(k-1))&1 else (b,a))
        if not core.is_k_dicolourable(n, arcs, 2):
            found={'n':n,'arcs':arcs,'graph_index':gi,'underlying_edges':edges}
            break
    if found: break
    if gi % 50 == 0:
        print(f'  ...{gi}/{len(graphs)} graphs done, t={time.time()-t0:.0f}s', flush=True)
if found:
    print('RESULT '+json.dumps({'chi_d>=3_EXISTS':True, **found}), flush=True)
else:
    print(f'RESULT {{"chi_d>=3_EXISTS": false, "n": {n}, "graphs_checked": {gi}, "verdict":"ALL triangle-free oriented digraphs on n={n} are 2-dicolourable"}}', flush=True)
print(f'elapsed {time.time()-t0:.0f}s', flush=True)
