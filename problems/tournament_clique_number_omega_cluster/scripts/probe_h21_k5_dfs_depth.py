"""Feasibility probe: how far does attack_class's optimal-sigma DFS get on the
49-vertex inner X=AC_7[AC_7] (clique==5 orders) within a fixed wall budget?
Reports max prefix depth reached and number of COMPLETE sigmas (leaves) found.
If leaves==0 the H21 mechanism cannot evaluate even ONE merged order -> the
ground_plan is infeasible in any foreground budget."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ground_potential_sum_c3 import lex_compose, beats_masks, max_clique_mask
from lexlib import AC, is_tournament

SECS = float(sys.argv[1]) if len(sys.argv) > 1 else 170.0

n1, a1 = AC(7, [1, 2, 4])
nX, arcsX = lex_compose(n1, a1, n1, a1)
print("X order", nX, "tourn", is_tournament(nX, arcsX), flush=True)
beatsH = beats_masks(nX, arcsX)
full = (1 << nX) - 1
badj = [0] * nX
order = []
k = 5
maxdepth = [0]
leaves = [0]
t0 = time.time()
deadline = t0 + SECS


def dfs(placed):
    if time.time() > deadline:
        return True
    d = len(order)
    if d > maxdepth[0]:
        maxdepth[0] = d
    if placed == full:
        leaves[0] += 1
        return False
    rest = full & ~placed
    c = rest
    while c:
        v = (c & -c).bit_length() - 1
        c &= c - 1
        nb = beatsH[v] & placed
        dv = 1 + max_clique_mask(badj, nb) if nb else 1
        if dv > k:
            continue
        badj[v] = nb
        undo = []
        m = nb
        while m:
            u = (m & -m).bit_length() - 1
            m &= m - 1
            badj[u] |= 1 << v
            undo.append(u)
        order.append(v)
        if dfs(placed | (1 << v)):
            return True
        order.pop()
        badj[v] = 0
        for u in undo:
            badj[u] &= ~(1 << v)
    return False


dfs(0)
print("elapsed", round(time.time() - t0, 1),
      "max prefix depth reached", maxdepth[0], "/", nX,
      "complete sigmas (leaves):", leaves[0], flush=True)
