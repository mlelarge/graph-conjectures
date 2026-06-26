"""INDEPENDENT re-verification of: for EVERY tournament H, dic(C3[H]) = ceil(3*dic(H)/2).

Self-contained: own SAT dic, own lex product, own gentourng parse, own triangle test.
Does NOT import prior grounding scripts (trust nothing).
"""
import sys, subprocess, math, itertools
from pysat.solvers import Cadical153


def gentourng(n):
    out = subprocess.run(['gentourng', str(n)], capture_output=True, text=True, timeout=600)
    if out.returncode != 0:
        raise RuntimeError(out.stderr[:400])
    res = []
    C = n * (n - 1) // 2
    for line in out.stdout.split():
        line = line.strip()
        if not line:
            continue
        assert set(line) <= set('01') and len(line) == C, (n, line)
        arcs = []
        idx = 0
        for i in range(n):
            for j in range(i + 1, n):
                arcs.append((i, j) if line[idx] == '1' else (j, i))
                idx += 1
        res.append(arcs)
    return res


def beats(n, arcs):
    b = [[False] * n for _ in range(n)]
    for (u, v) in arcs:
        b[u][v] = True
    return b


def is_tournament(n, arcs):
    b = beats(n, arcs)
    for i in range(n):
        for j in range(i + 1, n):
            if b[i][j] == b[j][i]:
                return False
    return len(arcs) == n * (n - 1) // 2


def dir_triangles(n, arcs):
    b = beats(n, arcs)
    tris = []
    for u, v, w in itertools.combinations(range(n), 3):
        if (b[u][v] and b[v][w] and b[w][u]) or (b[v][u] and b[w][v] and b[u][w]):
            tris.append((u, v, w))
    return tris


def dicolorable(n, arcs, k, tris):
    # exists k-coloring with no monochromatic directed triangle
    if k >= n:
        return True
    if not tris:
        return k >= 1
    if k <= 0:
        return False
    var = lambda v, c: v * k + c + 1
    cls = [[var(v, c) for c in range(k)] for v in range(n)]
    for (u, v, w) in tris:
        for c in range(k):
            cls.append([-var(u, c), -var(v, c), -var(w, c)])
    cls.append([var(0, 0)])  # symmetry break
    with Cadical153(bootstrap_with=cls) as m:
        return m.solve()


def dic(n, arcs, kmax=8):
    tris = dir_triangles(n, arcs)
    for k in range(1, kmax + 1):
        if dicolorable(n, arcs, k, tris):
            return k
    return None


def lex_c3(n, arcs):
    """C3[H]: 3 blocks; inside block follow H, between blocks follow directed C3 0->1->2->0."""
    bo = beats(3, [(0, 1), (1, 2), (2, 0)])
    bi = beats(n, arcs)
    N = 3 * n
    out = []
    for o1 in range(3):
        for a1 in range(n):
            u = o1 * n + a1
            for o2 in range(3):
                for a2 in range(n):
                    v = o2 * n + a2
                    if u >= v:
                        continue
                    beat = bi[a1][a2] if o1 == o2 else bo[o1][o2]
                    out.append((u, v) if beat else (v, u))
    return N, out


def ceil_3k2(k):
    return (3 * k + 1) // 2


def main():
    ns = [int(x) for x in sys.argv[1:]] or [4, 5, 6, 7]
    grand_viol = 0
    for n in ns:
        cls = gentourng(n)
        hist = {}
        viol = []
        for arcs in cls:
            assert is_tournament(n, arcs)
            dH = dic(n, arcs, kmax=5)
            N, A = lex_c3(n, arcs)
            assert is_tournament(N, A)
            dC = dic(N, A, kmax=8)
            pred = ceil_3k2(dH)
            hist[(dH, dC)] = hist.get((dH, dC), 0) + 1
            if dC != pred:
                viol.append((arcs, dH, dC, pred))
        grand_viol += len(viol)
        print(f"n={n}: {len(cls)} iso, viol={len(viol)}, hist={dict(sorted(hist.items()))}", flush=True)
        if viol:
            for v in viol[:5]:
                print("  VIOLATION", v, flush=True)
    print("TOTAL VIOLATIONS:", grand_viol, flush=True)


if __name__ == '__main__':
    main()
