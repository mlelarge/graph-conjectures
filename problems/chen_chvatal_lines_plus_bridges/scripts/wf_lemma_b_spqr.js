// Historical snapshot for the repository's custom workflow runtime.
// This uses runtime-specific top-level constructs and is not standalone Node.js.
// Consult docs/STATUS.md and ledger D29-D30 before reusing any proposed target.

export const meta = {
  name: 'lemma-b-spqr',
  description: 'Attack Lemma B via the 2-cut/SPQR recursion: (1) 3-connected surplus lemma, (2) 2-cut inheritance lemma',
  phases: [
    { title: 'Recon' },
    { title: 'Prove' },
    { title: 'Verify' },
    { title: 'Synthesize' },
  ],
}

const DIR = 'problems/chen_chvatal_lines_plus_bridges'

const CONTEXT = `
GOAL: prove LEMMA B (the 2-connected core of Chen-Chvatal H5) via a 2-cut/SPQR
recursion. Work from ${DIR} (cd first). Oracle: .venv/bin/python with
  import sys; sys.path.insert(0,"scripts"); import core
geng + networkx available. Existing probes: scripts/lemma_b_spqr_probe.py,
two_connected_census.py; docs/H5_LEMMA_B_OBSTRUCTION.md.

LEMMA B:  G 2-connected + pendant-free + diam(G) >= 4  ==>  ell(G) >= |G| = n.
ell(G) = #distinct metric-betweenness lines; line(a,b) = {a,b} ∪ {x : [abx] or
[axb] or [xab]}, [uvw] iff d(u,v)+d(v,w)=d(u,w). Defined for ANY finite metric
(this matters below).

VERIFIED FACTS (scout, exact unless noted):
- Census min(ell-n): n=8->2, n=9->2, n=10->1, n=11->5 (all m<=22). Tight cases are
  small sporadic graphs near F_0. Margin does NOT shrink past n=10.
- **CORRECTION (D30):** the early sampling claim that there were zero
  3-connected diam>=4 graphs through n=12 was false. The exhaustive n=12 census
  over m=18..25 scanned 5,601,520 such graphs. It found no B1 failure and
  minimum D2-n=+6, but it also found G3 counterexamples. Do not infer rarity or
  a first occurrence at n=13 from the older samples.
- All near-floor witnesses are 2-separable: G?otQg(n8,[3,3]), HCQdarQ(n9,[4,3]),
  ICOeeOsk_(n10,[5,3]), JCOeeOskcs_(n11,[6,3]).
- **VIRTUAL-EDGE METRIC LEMMA (verified)**: if {a,b} is a 2-cut splitting G into
  side G1 = G[C1∪{a,b}] and the rest G2 = G[C2∪{a,b}] (C1,C2 the components of
  G-{a,b}), then for x,y in G1: d_G(x,y) = weighted shortest-path distance in
  (G1 with an added virtual edge ab of length w2 := d_{G2}(a,b)). I.e. the other
  side acts as a single weighted edge ab. (Confirmed on ICOeeOsk_, 0 mismatch.)
  So the 2-sum decomposition is metric-faithful onto WEIGHTED torsos, and lines on
  the weighted torso are well-defined finite-metric lines.

THE RECURSION (the proposed proof shape — your job is to make it rigorous):
- (Base) 3-CONNECTED SURPLUS LEMMA: a 3-connected graph (more precisely, a
  3-connected weighted torso) of diam>=4 has ell >= n with room to spare. Empirically
  3-connected diam>=4 has ell-n >> 0. Find a COARSE global-line argument (3-connectivity
  => 3 internally-disjoint paths between any pair (Menger) => many forced distinct
  lines). A clean Omega(n) or even >= n bound suffices.
- (Step) 2-CUT INHERITANCE LEMMA: if G has a 2-cut {a,b} with weighted sides
  G1*, G2* (each = its side + virtual edge ab of the OTHER side's a-b distance), relate
  ell(G) to ell(G1*), ell(G2*) (or to |G1*|,|G2*|) so the recursion yields ell(G)>=n.
  SUBTLETY (do not ignore): a side may have SMALL diameter, so the inductive
  hypothesis "diam>=4 => ell>=n" does NOT apply to the sides directly -- you need a
  stronger invariant (e.g. ell(torso) >= |torso| for the relevant weighted torsos,
  or a surplus that pays for the virtual edge), and the small sporadic 2-separable
  torsos must be handled separately (finite census).
Together (Base)+(Step)+(finite small-n census, N0=11) would prove Lemma B.

TOOLS (proved, reusable):
- L1: 2-connected => every interior BFS layer from any vertex has >=2 vertices =>
  n >= 2*diam.
- L2: for an edge {a,b}, line(a,b) = V \\ {z : d(a,z)=d(b,z)}; =V iff no equidistant z.
- ISO-MON: H=G[U] isometric induced subgraph => ell(H) <= ell(G).
- Virtual-edge metric lemma (above).
- Menger: 3-connected => 3 internally-disjoint paths between any two vertices.

DEAD ROUTES (do NOT revive): any short-line / bounded-index subset-of-lines charge
(D12 has ZERO asymptotic slack: even cycles give D12-n=1 forever while ell-n=Theta(n^2));
open-ear induction with invariant ell(G_i)>=|G_i| (a chord ear can DROP ell:
G?qadg, chord {0,7}, ell 22->13); ISO-MON on isometric cycles (max 3 in witnesses).

DISCIPLINE: prove for ALL n (with N0=11 finite base). Validate every sub-claim on
the oracle: 2-connected graphs via geng -C; weighted-torso distances via networkx
Dijkstra; lines on a weighted metric via the betweenness definition with weighted d.
A sub-claim failing one small graph is refuted -- say so. The deliverable is a
rigorous proof or a SOUND reduction with the precise remaining gap, NOT another
">=" gate. Beware the recurring overcount/collapse trap and the metric subtlety that
sides are not isometric in G (they are weighted-virtual-edge metrics).
`

const PROOF_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['approach', 'verdict', 'confidence', 'summary', 'argument', 'key_lemmas', 'gaps', 'oracle_checks'],
  properties: {
    approach: { type: 'string' },
    verdict: { enum: ['proved', 'substantial_partial', 'stuck', 'refuted'] },
    confidence: { type: 'integer' },
    summary: { type: 'string' },
    argument: { type: 'string' },
    key_lemmas: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['statement', 'status'], properties: { statement: { type: 'string' }, status: { enum: ['proved', 'assumed', 'open', 'oracle-checked-only'] }, proof: { type: 'string' } } } },
    gaps: { type: 'array', items: { type: 'string' } },
    oracle_checks: { type: 'array', items: { type: 'string' } },
    refutation: { type: ['string', 'null'] },
  },
}
const VERIFY_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['verdict', 'found_gap', 'severity', 'details', 'small_checks'],
  properties: {
    verdict: { enum: ['sound', 'fixable', 'broken'] },
    found_gap: { type: 'boolean' },
    severity: { enum: ['none', 'minor', 'major', 'fatal'] },
    details: { type: 'string' },
    counterexample_g6: { type: ['string', 'null'] },
    small_checks: { type: 'array', items: { type: 'string' } },
    fix_suggestion: { type: ['string', 'null'] },
  },
}

// --------------------------- Recon ---------------------------
phase('Recon')
const MAPS = [
  `MAP the 3-CONNECTED surplus. Sample/enumerate 3-connected graphs with diam>=4
(they start at n=13; also include 3-connected WEIGHTED torsos that arise from SPQR
splits of the small witnesses). Measure ell-n and, more usefully, find a COARSE
provable lower bound: e.g. count lines forced by Menger's 3 disjoint paths, or by
pairs at distance 2/3 whose lines are locally determined and distinct. Report which
coarse functional is >= n on all 3-connected diam>=4 cases, and WHY it does not
collapse (contrast with the dead short-line route). Aim to identify a provable
'3-connected => ell >= n (with slack)' mechanism.`,
  `MAP the 2-CUT line split. For the witnesses (G?otQg, HCQdarQ, ICOeeOsk_,
JCOeeOskcs_) and random 2-separable diam>=4 graphs, take the best 2-cut {a,b} and
the weighted sides G1*, G2*. Classify every line of G by how it meets the sides
(internal to C1, internal to C2, crossing). Tabulate ell(G) vs ell(G1*), ell(G2*),
|G1*|, |G2*|, and the virtual-edge weights. Find the cleanest INHERITANCE
relationship (an inequality ell(G) >= something(sides)). Check whether lines
internal to one side inject into ell(G) (is the side isometric-with-virtual-edge, so
its lines lift?). This is the foundation of route 2 -- report the exact bookkeeping.`,
  `MAP the RECURSION base/leaves. Enumerate the small 2-separable torsos that appear
as leaves of the 2-cut decomposition of the tight witnesses (cycles=S-nodes,
bonds=P-nodes, small 3-connected=R-nodes, with weighted virtual edges). Verify the
virtual-edge metric lemma broadly (random 2-separable diam>=4 graphs, all 2-cuts).
Determine what inductive invariant could close: is ell(torso) >= |torso| for ALL the
weighted torsos that arise (including small-diam ones)? Find counterexamples to
naive invariants. Pin down which torsos need separate finite handling.`,
]
const maps = await parallel(MAPS.map((p, i) => () =>
  agent(`${CONTEXT}\n\nMAP TASK ${i + 1}. ${p}\nMeasurement to enable a proof; return concrete tables + the structural reason in 'argument'. verdict='substantial_partial'.`,
    { label: `map:${['3conn-surplus', '2cut-split', 'recursion-base'][i]}`, phase: 'Recon', schema: PROOF_SCHEMA })))

const MAPCTX = `${CONTEXT}\n\nEMPIRICAL MAPS (from Recon; re-verify load-bearing claims):\n${(maps || []).filter(Boolean).map((m, i) => `--- MAP ${i + 1} (${['3conn-surplus', '2cut-split', 'recursion-base'][i]}) ---\n${m.summary}\n${m.argument}`).join('\n\n')}`

// --------------------------- Prove ---------------------------
phase('Prove')
const PROVES = [
  { key: 'route1-3conn-surplus', prompt: `Prove ROUTE 1 (3-connected surplus lemma): a 3-connected graph (or weighted torso) of diam>=4 has ell >= n (ideally with growing slack). Use Menger (3 internally-disjoint paths) to force distinct lines; or a coarse global-line count that provably does not collapse. A clean ell>=n (even non-tight) suffices for the base case. State exactly what class it covers (unweighted 3-connected? weighted torsos?).` },
  { key: 'route2-2cut-inherit', prompt: `Prove ROUTE 2 (2-cut inheritance): for a 2-connected diam>=4 G with 2-cut {a,b} and weighted sides G1*, G2*, establish an inheritance inequality (e.g. ell(G) >= ell(G1*) + ell(G2*) - O(1), or ell(G) >= |G1*| + |G2*| - 2 = n) so the recursion closes. Use the virtual-edge metric lemma to lift side-lines into ell(G). Address the metric subtlety (sides not isometric in G; weighted virtual edges) and the small-diam side case head-on.` },
  { key: 'recursion-closes', prompt: `Assume plausible forms of Route 1 + Route 2 and show the FULL RECURSION CLOSES to ell(G) >= n for all 2-connected diam>=4 G with n >= N0=11 (small n by census). Determine the exact inductive invariant needed (it is probably NOT 'diam>=4 => ell>=n' since sides can have small diam -- find the right invariant, e.g. on weighted torsos). Identify precisely which of Route 1 / Route 2 is the true bottleneck and what minimal statement each must deliver for the recursion to work.` },
]
const proofs = await parallel(PROVES.map(spec => () =>
  agent(`${MAPCTX}\n\nPROOF TASK. ${spec.prompt}\nRun oracle checks (geng -C, networkx Dijkstra for weighted torsos, the line definition on weighted metrics) and report exactly. Be honest about gaps; verdict='proved' only for a complete rigorous argument.`,
    { label: `prove:${spec.key}`, phase: 'Prove', schema: PROOF_SCHEMA }).then(a => ({ spec, attempt: a }))))

// --------------------------- Verify ---------------------------
phase('Verify')
const verified = await parallel((proofs || []).filter(r => r && r.attempt).map(r => () =>
  parallel([
    () => agent(`${CONTEXT}\n\nADVERSARIAL VERIFICATION of a Lemma B SPQR attempt (${r.spec.key}). Default to skepticism.\nARGUMENT:\n${r.attempt.argument}\nKEY LEMMAS:\n${(r.attempt.key_lemmas || []).map(l => `[${l.status}] ${l.statement}`).join('\n')}\nGAPS: ${(r.attempt.gaps || []).join(' | ')}\nBreak any 'proved' step: find a logical gap OR a small graph where a claimed sub-lemma fails (geng -C diam>=4; for route 2, build the weighted sides and test the inheritance inequality with networkx Dijkstra + the weighted line definition). Pay special attention to: lines that DON'T lift across the 2-cut, the small-diam side case, and any overcount. RUN code. Only 'sound' if nothing breaks.`,
      { label: `verify:${r.spec.key}:A`, phase: 'Verify', schema: VERIFY_SCHEMA }),
    () => agent(`${CONTEXT}\n\nADVERSARIAL VERIFICATION (2nd reviewer) of ${r.spec.key}. Focus on the METRIC FAITHFULNESS and DISTINCTNESS: does the virtual-edge reduction hold where the proof uses it (test on random 2-separable diam>=4 graphs)? Are the lines claimed distinct / claimed to lift actually distinct in ell(G) (no collapse, no overcount)? Is the inductive invariant actually preserved by the recursion step? Test exhaustively on small cases with the oracle. Report concretely with code.`,
      { label: `verify:${r.spec.key}:B`, phase: 'Verify', schema: VERIFY_SCHEMA }),
  ]).then(vs => ({ ...r, verifications: (vs || []).filter(Boolean) }))))

// --------------------------- Synthesis ---------------------------
phase('Synthesize')
const pack = (verified || []).filter(Boolean).map(r => {
  const a = r.attempt
  const vs = (r.verifications || []).map(v => `  [${v.verdict}/${v.severity}] ${v.details}${v.counterexample_g6 ? ' CE:' + v.counterexample_g6 : ''}`).join('\n')
  return `### ${r.spec.key} -> ${a.verdict} (conf ${a.confidence})\n${a.summary}\nGAPS: ${(a.gaps || []).join(' | ')}\nVERIFY:\n${vs}`
}).join('\n\n')

const synth = await agent(`${CONTEXT}\n\nSYNTHESIS. All Lemma B SPQR attempts + adversarial verification:\n\n${pack}\n\nDELIVERABLE in 'argument' (clean markdown): (1) Is Lemma B proved end-to-end? If yes, the cleanest complete proof. (2) If not (likely), state EXACTLY what each route delivers and the precise remaining gap; is Route 1 (3-conn surplus) closable? is Route 2 (2-cut inheritance) the bottleneck and why? what is the right inductive invariant? (3) Did any verifier find a counterexample to Lemma B itself or to the virtual-edge lemma? Flag loudly. (4) Honest verdict: 'proved' only if complete & verification-surviving; else 'substantial_partial'. Be ruthless: oracle-checked-only != proved; watch for the metric-faithfulness and overcount traps.`,
  { label: 'synthesis', phase: 'Synthesize', schema: PROOF_SCHEMA })

return {
  map_summaries: (maps || []).filter(Boolean).map(m => m.summary),
  attempts: (verified || []).filter(Boolean).map(r => ({ key: r.spec.key, verdict: r.attempt.verdict, confidence: r.attempt.confidence, verifier_verdicts: (r.verifications || []).map(v => v.verdict) })),
  synthesis_verdict: synth ? synth.verdict : null,
  synthesis_report: synth ? synth.argument : null,
}
