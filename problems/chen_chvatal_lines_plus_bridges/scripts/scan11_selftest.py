"""Validate scan11_worker invariants against core.py on all connected
pendant-free graphs up to n=8 (covers the full known bad set n in {4,5,6,8}).
Asserts ell, br, and bad-classification match exactly."""
import subprocess
import sys

import core
import scan11_worker as W


def main():
    n_checked = 0
    n_bad_core = 0
    n_bad_worker = 0
    mismatches = []
    for n in range(4, 9):
        proc = subprocess.run(["geng", "-c", "-d2", "-q", str(n)],
                              capture_output=True, text=True)
        for g6 in proc.stdout.split():
            nn, edges = core.graph6_to_edges(g6)
            if core.has_pendant_edge(nn, edges):
                continue
            n_checked += 1
            # core
            ell_c = core.ell(nn, edges)
            br_c = core.bridges_count(nn, edges)
            bad_c = (ell_c + br_c < nn)
            # worker
            res = W.classify(g6)
            adj = W.adj_of(nn, edges)
            dist = W.all_pairs(nn, adj)
            ell_w, _ = W.count_lines_and_diam(nn, dist)
            br_w = W.bridges_count(nn, adj)
            bad_w = (res is not None)
            if bad_c:
                n_bad_core += 1
            if bad_w:
                n_bad_worker += 1
            if ell_w != ell_c or br_w != br_c or bad_w != bad_c:
                mismatches.append((g6, nn, ell_c, ell_w, br_c, br_w,
                                   bad_c, bad_w))
    print(f"checked={n_checked} bad_core={n_bad_core} bad_worker={n_bad_worker} "
          f"mismatches={len(mismatches)}")
    for m in mismatches[:20]:
        print("MISMATCH", m)
    sys.exit(0 if not mismatches and n_bad_core == 8 else 1)


if __name__ == "__main__":
    main()
