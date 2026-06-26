"""Independently test the lex lower-bound lemma omega_vec(S[H]) >= omega_vec(S)+omega_vec(H)-1
on small tournaments where omega_vec(S[H]) is computable exactly via SAT-CEGAR.

We test S, H small (so S[H] has few vertices), random + structured tournaments.
"""
import sys, itertools, random
import rt_sat_exact as RT
from pysat.solvers import Glucose4

def omega_vec_brute(V, arcmat):
    """Exact via exhaustive order search; V list of indices 0..N-1, arcmat[i][j]."""
    N = len(V)
    best = N+1
    def maxbk(perm):
        adj=[0]*N
        for p in range(N):
            for q in range(p+1,N):
                if arcmat[perm[q]][perm[p]]:
                    adj[p]|=1<<q; adj[q]|=1<<p
        bb=[0]
        def bk(R,P):
            if P==0:
                if R>bb[0]: bb[0]=R
                return
            if R+bin(P).count("1")<=bb[0]: return
            PP=P
            while PP:
                v=(PP&-PP).bit_length()-1
                bk(R+1,P&adj[v]); P&=~(1<<v); PP&=~(1<<v)
        bk(0,(1<<N)-1)
        return bb[0]
    for perm in itertools.permutations(range(N)):
        w=maxbk(perm)
        if w<best: best=w
    return best

def compose(Sn, Sarc, Hn, Harc):
    """S[H]: vertices (a,b), arc (a,b)->(a',b') iff [a!=a' and Sarc[a][a']] or [a==a' and Harc[b][b']]."""
    V=[(a,b) for a in range(Sn) for b in range(Hn)]
    idx={v:i for i,v in enumerate(V)}
    N=len(V)
    A=[[False]*N for _ in range(N)]
    for u in V:
        for v in V:
            if u==v: continue
            a,b=u; a2,b2=v
            arc = Sarc[a][a2] if a!=a2 else Harc[b][b2]
            A[idx[u]][idx[v]]=arc
    return V,A

def rand_tournament(k, seed):
    random.seed(seed)
    A=[[False]*k for _ in range(k)]
    for i in range(k):
        for j in range(i+1,k):
            if random.random()<0.5: A[i][j]=True
            else: A[j][i]=True
    return A

def omega_vec_from_matrix(A):
    N=len(A)
    Vidx=list(range(N))
    arc=lambda u,v: A[u][v]
    return RT.omega_vec_exact(Vidx, arc, lo=1, hi=N)

def main():
    fails=0
    tests=0
    # small composites: S size 3, H size 3 -> 9 vtx; S size 3,H size 4 ->12; S size 4,H size3->12
    for (sk,hk) in [(3,3),(3,4),(4,3),(4,4),(3,5),(5,3)]:
        for seed in range(6):
            Sarc=rand_tournament(sk,seed*7+1)
            Harc=rand_tournament(hk,seed*13+5)
            wS=omega_vec_brute(list(range(sk)),Sarc)
            wH=omega_vec_brute(list(range(hk)),Harc)
            V,A=compose(sk,Sarc,hk,Harc)
            wSH=omega_vec_from_matrix(A)
            if isinstance(wSH,str):
                print("timeout",sk,hk,seed); continue
            tests+=1
            lb=wS+wH-1
            mark="OK" if wSH>=lb else "VIOLATION"
            if wSH<lb:
                fails+=1
                print(f"  S{sk}H{hk} seed{seed}: wS={wS} wH={wH} -> lb={lb} but wSH={wSH}  *** {mark}")
        sys.stdout.flush()
    print(f"lex LB lemma: {tests} tests, {fails} violations")

if __name__=="__main__":
    main()
