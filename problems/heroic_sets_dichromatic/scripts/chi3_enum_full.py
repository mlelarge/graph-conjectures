"""Full orientation enumeration with a fast 2-dicolourability rejecter.

For C5blowup_t2 and Grotzsch (|E|=20 -> 2^20 ~ 1.05M orientations each), test
EVERY orientation for chi_d>=3 (i.e. NOT 2-dicolourable).  Sound + exhaustive.
We avoid double-counting orientation/reverse symmetry by fixing edge 0's direction.
"""
import os
import sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from chi3_search import c5_blowup, grotzsch

def full_enum(name, n, edges):
    edges=list(edges); m=len(edges)
    print(f'=== {name}: n={n} |E|={m}; enumerating 2^{m-1}={2**(m-1)} (fix edge0) ===', flush=True)
    found=None; checked=0
    # fix edge 0 forward to halve by global reversal symmetry
    for bits in range(2**(m-1)):
        arcs=[edges[0]]
        for k in range(1,m):
            a,b=edges[k]
            arcs.append((a,b) if (bits>>(k-1))&1 else (b,a))
        checked+=1
        if not core.is_k_dicolourable(n, arcs, 2):
            found=arcs; break
        if checked % 100000 == 0:
            print(f'  ...checked {checked}', flush=True)
    if found is not None:
        print(json.dumps({'name':name,'n':n,'FOUND_chi_d>=3':True,'arcs':found,'checked':checked}), flush=True)
        return found
    print(f'  EXHAUSTED {checked} orientations: NONE has chi_d>=3 (all 2-dicolourable)', flush=True)
    return None

if __name__=='__main__':
    which=sys.argv[1]
    if which=='c5t2':
        n,e=c5_blowup(2); full_enum('C5blowup_t2',n,e)
    elif which=='grotzsch':
        n,e=grotzsch(); full_enum('Grotzsch',n,e)
