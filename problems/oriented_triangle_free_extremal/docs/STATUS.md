# STATUS — oriented_triangle_free_extremal (as of D10, 2026-06-05)

Paper: arXiv:2403.02298 (Aboulker, Havet, Pirot, Schabanel, 2024).

## Central question
Asymptotic order of two extremal functions over oriented triangle-free graphs of order n:
a_vec(n) = min acyclic number, t_vec(n) = max dichromatic number.
Conj 3: a_vec(n) = Theta(sqrt(n log n)). Conj 4: t_vec(n) = Theta(sqrt(n/log n)). Conj 3 => Conj 4.
Open gap: a factor sqrt(log n) on each (a_vec upper / t_vec lower).

## open_crux — COMPUTATIONAL FRONTIER NOW EXHAUSTED

### a_vec UPPER bound (target sqrt(n log n); proved (107/8) sqrt(n) log n)
Every orientation-RULE family is DEAD, all re-flooring at a*/(sqrt n log n) ~ 1.07:
static (G2/G3), uniform random (G4), online topological (G8), online class-balancing (G11),
offline Paley label-tournament (G14), and — as of D10 — **direct-a*-greedy (G25/H5)**, the strongest
per-arc rule (orient each arriving edge to MINIMIZE the exact acyclic number). H5 result: n=20 a*=14 R=1.045,
n=30 a*=19 R=1.020, = best-of-~6-random; n=40 infeasible. The ENTIRE online per-arc sub-route is exhausted.
The alpha-route is now QUADRUPLY closed: wrong scale (D7), wrong inequality a_vec>=alpha (D8),
matched-density vacuous (D9), maximal-density a_vec does NOT track alpha (D10/G27, diverge by sqrt(log n)).
SOLE surviving route: self-correcting concentration on a* DIRECTLY (H1/H4, Bohman-Keevash) — NON-computational.

### t_vec LOWER bound (dual): chi=3 ceiling / m(3), m(4)
chi=3 ceiling survives NINE construction families (G1,G5,G6,G7,G9,G10, malformed G16, chromatic-base G22,
and D10's G26 Pent5(D25) = full chi=3 second factor across an outer C5 → chi_vec=3). m(4)<=209 rigid.
No construction lever survives.
H3 (18<=m(3)<=25): UPPER lever dead in both formulations (annealing G13, complete-SAT G19); LOWER lever
attempted (G24) and STUCK behind the paper's own n=17 brute-force wall (AES pruning empty; 14.4M-graph
enumeration not done). Needs a new SYMBOLIC reduction, not enumeration.

## live_hypotheses
- H1 open-sole-survivor — dynamic Bohman-Keevash concentration on a* directly; NON-computational.
- H2 exhausted-all-product-and-chromatic-base-families — 9 chi=3-ceiling families, incl. G26 Pent5.
- H3 both-levers-stuck-needs-symbolic — UPPER dead (G13+G19); LOWER behind the n=17 wall (G24).
- H4 online-sub-route-DEAD — G8/G11/G14/G25 all re-floor; only graph-structure concentration survives.
- H5 DEAD — direct-a*-greedy run (G25); no beat-the-floor signal; closes the online sub-route.

## last 2 decision_log notes
- D9: G22/G23/G24 refuted; frontier NOT advanced. Chromatic-base m(4) caps at chi=3 (G22); matched-density alpha vacuous (G23); H3 LOWER attempted-and-stuck behind the n=17 wall (G24).
- D10: G25/G26/G27 refuted; frontier NOT advanced — BUT the last un-run experiment H5 was RUN (G25) and re-floors, closing the online sub-route. 9th chi=3-ceiling family (G26 Pent5); alpha-route quadruply closed (G27). COMPUTATIONAL FRONTIER EXHAUSTED.

## needs_human / recommend_handback
needs_human: null (no decision gate hit).
recommend_handback: **YES.** No purely-computational lever remains (G2–G27 all dead). Two NON-computational
human-math inputs are needed, neither certifiable by the oracle: (A) a_vec UPPER — a Bohman-Keevash-style
dynamic-concentration argument controlling the max acyclic INDUCED set a*(D) DIRECTLY (O(1)-step martingale tied
to the GRAPH structure) to beat the empirically rock-solid sqrt(n) log n random floor; (B) t_vec/m(3) — a new
SYMBOLIC 2-dicolourability reduction lifting m(3)>=18 above n=17 WITHOUT enumerating the 14.4M-graph slice
(graph-level enumeration provably inherits the paper's n=17 wall, AES pruning empty).

## Next action
HANDBACK to human for routes (A)/(B) above. If forced to continue computationally, only non-promotable
re-confirmations remain; do NOT re-propose any dead pattern (orientation rule, alpha relocation,
chi=3-seed construction, sub-25 chi=3 search, or m(3) graph-enumeration).
