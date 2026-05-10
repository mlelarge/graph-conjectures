# Earth–Moon problem

Self-contained workstream attacking Ringel's Earth–Moon problem:

> What is the maximum chromatic number $\chi_{\rm EM}$ of a biplanar graph
> (a graph whose edge set can be partitioned into two planar subgraphs)?

Current bracket: $9 \le \chi_{\rm EM} \le 12$
(Sulanke / Gardner 1980 below, Heawood 1890 above).

## Goal

Two complementary targets — both reuse the same tooling:

- **Disproof of folklore $\chi_{\rm EM} = 9$**: exhibit a biplanar graph with $\chi \ge 10$.
  Headline candidate: $C_7 \boxtimes K_4$ on 28 vertices ($\chi = 10$, $\omega = 8$, $K_9$-free).
- **Upper bound $\chi_{\rm EM} \le 11$** via a density theorem on 12-critical $K_9$-free graphs,
  combining Kostochka–Yancey (2014) with the biplanar edge bound $|E| \le 6n - 12$.

## Status

Plan stage. Tooling not yet built. See [docs/plan.md](docs/plan.md).

## Layout

```
docs/                 plan, literature notes, upper-bound working file
scripts/              biplanarity oracle, chromatic solver, miners (to come)
data/                 known examples, candidate stream, certificates
tests/                regression suite that gates the oracle
```

## References (starting point)

- M. Kirchweger, M. Scheucher, S. Szeider, *SAT-Based Generation of Planar Graphs*,
  SAT 2023 — directly relevant SMS framework, used as the implementation baseline.
  Ships `--earthmoon_candidate1` ($C_5[4,4,4,4,3]$, 19 vertices, ruled out) and
  `--earthmoon_candidate2` ($C_7[K_4]$, 28 vertices, target).
- D. Boutin, E. Gethner, T. Sulanke, *Thickness-two graphs of order ≤ 12: 9-colorable
  examples*, 2008.
- E. Gethner, T. Sulanke, infinite family of 9-critical thickness-2 graphs, 2009.
- A. Kostochka, M. Yancey, *Ore's conjecture for $k = 4$ and Grötzsch's theorem*, 2014.
- L. Mansfield, *Determining the thickness of graphs is NP-hard*, 1983.
- J. P. Hutchinson, *Coloring ordinary maps, maps of empires and maps of the moon*, 1993.

Original problem record: <http://www.openproblemgarden.org/op/earth_moon_problem>.
