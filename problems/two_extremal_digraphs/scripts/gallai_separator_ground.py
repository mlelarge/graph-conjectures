#!/usr/bin/env python3
import sys, json, itertools, signal
sys.path.insert(0, 'scripts')
import h2_oracle as H

signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(TimeoutError()))
signal.alarm(580)

def underlying_edges(n, arcs):
    es = set()
    for (u, v) in arcs:
        es.add((min(u, v), max(u, v)))
    return es

def digon_vertices(n, arcs):
    aset = set((u, v) for (u, v) in arcs)
    dv = set()
    for (u, v) in arcs:
        if (v, u) in aset:
            dv.add(u); dv.add(v)
    return dv

def digon_components(n, arcs):
    # forest F_D: edges that are digons
    aset = set((u, v) for (u, v) in arcs)
    adj = {i: set() for i in range(n)}
    dv = set()
    for (u, v) in arcs:
        if (v, u) in aset and u < v:
            adj[u].add(v); adj[v].add(u)
            dv.add(u); dv.add(v)
    # components among digon vertices only
    seen = set()
    comps = []
    for s in dv:
        if s in seen:
            continue
        stack = [s]; comp = set()
        while stack:
            x = stack.pop()
            if x in seen: continue
            seen.add(x); comp.add(x)
            for y in adj[x]:
                if y not in seen: stack.append(y)
        comps.append(comp)
    return comps, dv

def underlying_connected_after_remove(n, edges, removed):
    verts = [v for v in range(n) if v not in removed]
    if not verts:
        return True
    adj = {v: set() for v in verts}
    rs = set(removed)
    for (a, b) in edges:
        if a in rs or b in rs: continue
        adj[a].add(b); adj[b].add(a)
    start = verts[0]
    seen = {start}; stack = [start]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y); stack.append(y)
    return len(seen) == len(verts)

def node_connectivity(n, edges):
    # underlying simple graph vertex connectivity (small n brute force)
    # kappa = min size of vertex set whose removal disconnects (or n-1 for complete)
    # check k=0 (already connected assumed), then 1,2,3,...
    for k in range(0, n):
        # if removing any k vertices disconnects -> kappa = k
        if k == 0:
            if not underlying_connected_after_remove(n, edges, set()):
                return 0
            continue
        for combo in itertools.combinations(range(n), k):
            if not underlying_connected_after_remove(n, edges, set(combo)):
                return k
        # also: if n-k <= 1 the graph is "complete-ish"
    return n - 1

def size2_separators(n, edges, dv):
    seps = []
    for combo in itertools.combinations(range(n), 2):
        if not underlying_connected_after_remove(n, edges, set(combo)):
            digon_inc = [c in dv for c in combo]
            seps.append((combo, digon_inc))
    return seps

def analyze(member, label):
    n = member['n']; arcs = [tuple(a) for a in member['arcs']]
    edges = underlying_edges(n, arcs)
    comps, dv = digon_components(n, arcs)
    k_fd = len(comps)
    kappa = node_connectivity(n, edges)
    chi = H.chi_vec(n, arcs)
    lam = H.lambda_D(n, arcs)
    is2e = H.is_2extremal(n, arcs)
    res = {
        'label': label, 'n': n, 'k_fd': k_fd, 'kappa': kappa,
        'chi_vec': chi, 'lambda_D': lam, 'is_2extremal': is2e,
        'digon_vertices': sorted(dv),
    }
    if k_fd >= 2:
        seps = size2_separators(n, edges, dv)
        res['has_size2_sep'] = len(seps) > 0
        # a sep with >=1 digon-incident cut vertex (MC=1 shadow)
        res['sep_with_digon_incident'] = any(any(fl) for (_, fl) in seps)
        res['size2_seps'] = [{'cut': list(c), 'digon_inc': fl} for (c, fl) in seps]
    return res

def main():
    truth = []
    for nn in range(3, 8):
        data = json.load(open(f'data/L_{nn}.json'))
        for idx, m in enumerate(data):
            truth.append(analyze(m, f'L{nn}.{idx}'))

    # Falsifiable prediction checks
    kfd2 = [r for r in truth if r['k_fd'] >= 2]
    print(f"Total truth-set members L3..L7: {len(truth)}")
    print(f"Members with k_fd>=2: {len(kfd2)}")

    # PREDICTION 1: every k_fd>=2 member has kappa==2 (none 3-connected)
    not_kappa2 = [r for r in kfd2 if r['kappa'] != 2]
    print(f"\n[PRED1] k_fd>=2 with kappa != 2 (KILL if any 3-connected): {len(not_kappa2)}")
    for r in not_kappa2:
        print("   ", r['label'], "kappa=", r['kappa'], "chi=", r['chi_vec'], "lam=", r['lambda_D'])

    # KILL CANDIDATE: 3-connected (kappa>=3) AND k_fd>=2 AND chi==3 AND 2-extremal
    kills = [r for r in kfd2 if r['kappa'] >= 3 and r['chi_vec'] == 3 and r['is_2extremal']]
    print(f"\n[KILL] 3-connected & k_fd>=2 & chi=3 & 2-extremal (Conj-9.2 counterexample candidate): {len(kills)}")
    for r in kills:
        print("   KILL:", r['label'], r)

    # PREDICTION 2: every k_fd>=2 member has a size-2 sep with >=1 digon-incident cut vertex (MC=1)
    no_digon_sep = [r for r in kfd2 if not r.get('sep_with_digon_incident', False)]
    print(f"\n[PRED2] k_fd>=2 lacking a size-2 sep w/ >=1 digon-incident cut vtx: {len(no_digon_sep)}")
    for r in no_digon_sep:
        print("   ", r['label'], "seps=", r.get('size2_seps'))

    # Detailed breakdown
    print("\n--- k_fd>=2 member detail ---")
    n_all_digon_sep = 0
    n_mixed_sep = 0
    for r in kfd2:
        seps = r.get('size2_seps', [])
        # classify: at least one sep entirely on F_D vs only mixed
        entirely = any(all(s['digon_inc']) for s in seps)
        mixed = any((any(s['digon_inc']) and not all(s['digon_inc'])) for s in seps)
        tag = 'BOTH-on-FD' if entirely else ('MIXED-only' if mixed else 'NO-digon-sep')
        if entirely: n_all_digon_sep += 1
        elif mixed: n_mixed_sep += 1
        print(f"  {r['label']:8s} n={r['n']} kappa={r['kappa']} chi={r['chi_vec']} lam={r['lambda_D']} k_fd={r['k_fd']} -> {tag}; seps={seps}")
    print(f"\nSummary: {n_all_digon_sep} have a 2-cut entirely on F_D; {n_mixed_sep} mixed-only (still MC=1).")

    verdict_pred1 = (len(not_kappa2) == 0)
    verdict_pred2 = (len(no_digon_sep) == 0)
    verdict_kill = (len(kills) == 0)
    print(f"\nPRED1 (all k_fd>=2 kappa==2): {verdict_pred1}")
    print(f"PRED2 (all k_fd>=2 have MC=1 size-2 sep): {verdict_pred2}")
    print(f"NO KILL counterexample present: {verdict_kill}")
    print(f"OVERALL CONFIRM: {verdict_pred1 and verdict_pred2 and verdict_kill}")

main()
