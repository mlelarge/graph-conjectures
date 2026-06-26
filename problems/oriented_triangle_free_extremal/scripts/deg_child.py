"""Child: compute acyclic_number witness for one (n,c,seed) and print JSON.
Run as: python deg_child.py n c seed
Prints one JSON line {"a":..,"S":[..],"edges":[[u,v],..]} or nothing on kill.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from lit_reduction_test import triangle_free_process, random_orientation
from lit_reduction_degeneracy import acyclic_number_witness

n = int(sys.argv[1]); c = float(sys.argv[2]); s = int(sys.argv[3])
p = c / math.sqrt(n)
m_cap = int(p * n * (n - 1) / 2)
n2, edges = triangle_free_process(n, m_cap, seed=1000 * int(c * 10) + s + n)
assert core.is_triangle_free(n2, edges)
arcs = random_orientation(edges, seed=7 * s + 3)
assert core.is_oriented(arcs)
a, S = acyclic_number_witness(n2, arcs)
assert len(S) == a
sub_arcs = [(u, v) for (u, v) in arcs if u in set(S) and v in set(S)]
assert core.is_acyclic(n2, sub_arcs), "witness not acyclic!"
print(json.dumps({"a": a, "S": list(S), "edges": [list(e) for e in edges]}),
      flush=True)
