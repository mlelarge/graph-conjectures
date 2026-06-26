import sys, os, math, random, time, signal
import networkx as nx

def build_saturated(n, seed):
    """Saturated triangle-free greedy: add random non-edges preserving
    triangle-freeness until none remain (graph is maximal triangle-free)."""
    rng = random.Random(seed)
    adj = [set() for _ in range(n)]
    pairs = [(i, j) for i in range(n) for j in range(i+1, n)]
    rng.shuffle(pairs)
    for (i, j) in pairs:
        # add edge iff no common neighbor (keeps triangle-free)
        if not (adj[i] & adj[j]):
            adj[i].add(j); adj[j].add(i)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in adj[i]:
            if i < j:
                G.add_edge(i, j)
    return G

def build_sparse(n, seed):
    """Sparse triangle-free process graph at target d ~ c*sqrt(n):
    target_m = 0.5*sqrt(n*logn)*n/2  (per ground_plan control)."""
    rng = random.Random(seed)
    logn = math.log(n)
    target_m = 0.5 * math.sqrt(n*logn) * n / 2.0
    adj = [set() for _ in range(n)]
    pairs = [(i, j) for i in range(n) for j in range(i+1, n)]
    rng.shuffle(pairs)
    m = 0
    G = nx.Graph(); G.add_nodes_from(range(n))
    for (i, j) in pairs:
        if m >= target_m:
            break
        if not (adj[i] & adj[j]):
            adj[i].add(j); adj[j].add(i)
            G.add_edge(i, j); m += 1
    return G

def triangle_free(G):
    return sum(nx.triangles(G).values()) == 0

class TO(Exception): pass
def _h(s,f): raise TO()

def exact_alpha(G, timeout=90):
    """alpha(G) = max clique in complement."""
    comp = nx.complement(G)
    signal.signal(signal.SIGALRM, _h)
    signal.alarm(timeout)
    try:
        best = 0
        for c in nx.find_cliques(comp):
            if len(c) > best: best = len(c)
        signal.alarm(0)
        return best
    except TO:
        signal.alarm(0)
        return None

def run(kind, ns, seeds):
    print(f"=== {kind} ===")
    print(f"{'n':>4} {'d':>6} {'d/sqrt(nlogn)':>13} {'alpha':>7} {'a/sqrt(nlogn)':>13} {'a/(sqrtn*logn)':>15} {'trifree':>8}")
    for n in ns:
        logn = math.log(n)
        ds=[]; alphas=[]; tf_all=True; ok=True
        for s in seeds:
            G = build_saturated(n,s) if kind=="saturated" else build_sparse(n,s)
            d = 2.0*G.number_of_edges()/n
            tf = triangle_free(G)
            tf_all = tf_all and tf
            a = exact_alpha(G)
            if a is None:
                ok=False; break
            ds.append(d); alphas.append(a)
        if not ok:
            print(f"{n:>4}  TIMEOUT (exact alpha exceeded cap)")
            continue
        d=sum(ds)/len(ds); a=sum(alphas)/len(alphas)
        snl=math.sqrt(n*logn); snln=math.sqrt(n)*logn
        print(f"{n:>4} {d:6.2f} {d/snl:13.3f} {a:7.2f} {a/snl:13.3f} {a/snln:15.3f} {str(tf_all):>8}")

if __name__=="__main__":
    seeds=[0,1,2]
    ns=[40,55,70,85,100]
    run("saturated", ns, seeds)
    run("sparse", ns, seeds)
