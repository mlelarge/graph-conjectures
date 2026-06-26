"""Red-team for Conjecture 6.2 over the FULL class Forb_ind(K2_digon, ->C3, S2+),
NOT restricted to triangle-free underlying graphs.

Orientations of simple graphs are automatically digon-free (K2_digon-free).
We filter for induced ->C3-free and S2+-free, then hunt chi_d >= 3.

Modes:
  exhaustive <n>            : all simple graphs (geng) x all orientations, filtered.
  structured                : the C_k(arc) tournament-slot family, k=4..12.
  random <n> <trials>       : random orientations of random simple graphs on n vtx.
"""
import sys, json, random, itertools
sys.path.insert(0, "scripts")
import core

C3 = core.C3()
S2P = core.S2_plus()

def in_class(D):
    # digon-free automatic for orientations; just need ->C3-free and S2+-free
    return not (core.contains_induced(D, C3) or core.contains_induced(D, S2P))

def report(found, maxchi, count, label):
    return {"label": label, "members_checked": count, "max_chi_d": maxchi,
            "violation": found}

def exhaustive(n):
    maxchi = 0; cnt = 0; viol = None
    for (gn, edges) in core.dc._all_simple_graphs(n) if hasattr(core.dc, "_all_simple_graphs") else all_simple_graphs(n):
        for arcs in core.all_orientations(edges):
            D = (n, arcs)
            if not in_class(D):
                continue
            cnt += 1
            chi = core.dichromatic_number(n, arcs)
            if chi > maxchi:
                maxchi = chi
            if chi >= 3 and viol is None:
                viol = {"n": n, "arcs": arcs, "chi_d": chi}
                return report(viol, maxchi, cnt, f"exhaustive n={n}")
    return report(viol, maxchi, cnt, f"exhaustive n={n}")

def all_simple_graphs(n):
    import subprocess
    gp = core.dc._geng_path()
    proc = subprocess.run([gp, "-q", str(n)], capture_output=True, text=True)
    for line in proc.stdout.splitlines():
        if line.strip():
            yield core.dc._graph6_to_edges(line)

def structured():
    arc = (2, [(0, 1)])
    out = []
    maxchi = 0; viol = None
    for k in range(4, 13):
        D = core.substitute_into_cycle([arc] * k)
        n, arcs = D
        if not in_class(D):
            out.append({"k": k, "n": n, "in_class": False})
            continue
        chi = core.dichromatic_number(n, arcs)
        maxchi = max(maxchi, chi)
        if chi >= 3 and viol is None:
            viol = {"k": k, "n": n, "arcs": arcs, "chi_d": chi}
        out.append({"k": k, "n": n, "in_class": True, "chi_d": chi})
    return {"label": "structured C_k(arc)", "per_k": out,
            "max_chi_d": maxchi, "violation": viol}

def random_scan(n, trials, seed=0):
    rng = random.Random(seed)
    maxchi = 0; cnt = 0; viol = None
    verts = list(range(n))
    pairs = list(itertools.combinations(verts, 2))
    for _ in range(trials):
        # random simple graph (each edge present w.p. p), then random orientation
        p = rng.uniform(0.3, 0.85)
        arcs = []
        for (u, v) in pairs:
            if rng.random() < p:
                arcs.append((u, v) if rng.random() < 0.5 else (v, u))
        D = (n, arcs)
        if not in_class(D):
            continue
        cnt += 1
        chi = core.dichromatic_number(n, arcs)
        if chi > maxchi:
            maxchi = chi
        if chi >= 3 and viol is None:
            viol = {"n": n, "arcs": arcs, "chi_d": chi}
            break
    return report(viol, maxchi, cnt, f"random n={n} trials={trials}")

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "exhaustive":
        print(json.dumps(exhaustive(int(sys.argv[2])), indent=2))
    elif mode == "structured":
        print(json.dumps(structured(), indent=2))
    elif mode == "random":
        n = int(sys.argv[2]); trials = int(sys.argv[3])
        seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        print(json.dumps(random_scan(n, trials, seed), indent=2))
