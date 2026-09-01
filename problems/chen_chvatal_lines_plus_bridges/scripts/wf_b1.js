// Historical snapshot for the repository's custom workflow runtime.
// This uses runtime-specific top-level constructs and is not standalone Node.js.
// Consult docs/STATUS.md and ledger D29-D30 before reusing any proposed target.

export const meta = {
  name: 'lemma-b1-d2',
  description: 'Prove (B1): 3-connected + diam>=4 => D2 >= n (#distance-exactly-2 lines >= n)',
  phases: [
    { title: 'Recon' },
    { title: 'Prove' },
    { title: 'Verify' },
    { title: 'Synthesize' },
  ],
}

const DIR = 'problems/chen_chvatal_lines_plus_bridges'

const CONTEXT = `
GOAL: prove (B1), the cleaner of the two Lemma B sub-lemmas. Work from ${DIR}
(cd first). Oracle: .venv/bin/python with import sys; sys.path.insert(0,"scripts");
import core. geng + networkx available. Enumerate 3-connected graphs by filtering
geng -C output (or random gnp + biconnectivity + a brute 2-cut check).

(B1):  G 3-connected + diam(G) >= 4  ==>  D2(G) >= n,
where D2(G) = #distinct lines from pairs at distance EXACTLY 2.
line(a,b) = {a,b} ∪ {x : [abx] or [axb] or [xab]}, [uvw] iff d(u,v)+d(v,w)=d(u,w).
Proving (B1) + the (separately open) (B2) proves Lemma B (the 2-connected core of
Chen-Chvatal H5): ell(G) >= max(D2, BIGTORSO) >= n. (B1) handles the 3-connected
case where D2 wins; do NOT worry about BIGTORSO/2-cuts here.

STRUCTURE OF A DISTANCE-2 LINE. For a pair {a,b} with d(a,b)=2:
- the "interior" {x : [axb]} (x strictly between a,b) = N(a) ∩ N(b) (common
  neighbours): [axb] needs d(a,x)+d(x,b)=2 with both >=1, so both =1.
- plus far extensions {x : [abx]} (b between a,x; d(a,x)=2+d(b,x)) and {x : [xab]}.
So line(a,b) = {a,b} ∪ (N(a)∩N(b)) ∪ {far extensions}.

PROVED FLOOR (CLAIM A, verified universally): in any 2-connected diam>=4 graph
every vertex has >= 2 vertices at distance exactly 2. So the DISTANCE-2 GRAPH
G2 (vertices V, edges = pairs at distance exactly 2) has min-degree >= 2, hence
|E(G2)| >= n and (min-deg>=2 => every component has a cycle) there is an INJECTION
phi: V -> E(G2), v |-> an incident distance-2 edge, all distinct.
D2 = #distinct images of the line map  E(G2) -> lines, e=(a,b) |-> line(a,b).
Therefore: **D2 >= n  <=>  the bipartite graph H = (V, {distance-2 lines}),
v ~ L iff some distance-2 edge incident to v has line L, has a V-SATURATING
MATCHING (Hall)** -- equivalently the injection phi survives the collapse
e |-> line(e). So (B1) is a HALL/EXPANSION statement: every S ⊆ V has at least
|S| distinct distance-2 lines incident to S, forced by 3-CONNECTIVITY.

VERIFIED FACTS (scout):
- (B1) holds with LARGE slack: D2-n ranges +11..+31 on 3-connected diam>=4 graphs
  n=11..14 (tightest known +11). All have diam=4. Hall (V-saturating matching into
  distinct distance-2 lines) holds on every one.
- Max collision multiplicity (distance-2 pairs sharing a line) is SMALL: <= 3.
- 3-CONNECTIVITY IS ESSENTIAL: D2 < n on 2-separable diam>=4 graphs (e.g. HCQdarQ).
- Refuted shortcut: "all distance-2 collisions are LOCAL (colliding pairs share a
  vertex)" is FALSE -- diffuse/antipodal collisions exist (e.g. the tight witness
  J~aK]Qc[?[?, the two diameter-endpoints' pairs collide). So 3-connectivity bounds
  collision COUNT, not collision LOCALITY.

TOOLS: L2 (for an EDGE {a,b}: line(a,b)=V\\{z:d(a,z)=d(b,z)}); Menger (3-connected =>
3 internally-disjoint paths between any two vertices, and G-{any 2 vertices} is
connected); CLAIM A; the distance-2 line structure above.

PROMISING ANGLE (large slack suggests a COARSE argument may suffice): D2 = |E(G2)| -
#collisions, where #collisions = sum over lines of (multiplicity-1). With |E(G2)| >=
n (and often >= 3n/2 when min-deg(G2)>=3), it suffices to bound #collisions <=
|E(G2)| - n using 3-connectivity (max multiplicity <= 3 is already verified; bound
the NUMBER of collided lines). A non-tight bound is fine.

DISCIPLINE: prove for ALL n. Validate every sub-claim on the oracle (3-connected
diam>=4 graphs via geng -C + a 2-cut filter, or random gnp). A sub-claim failing one
graph is refuted -- say so. Deliverable: a rigorous proof of (B1) or a sound
reduction with the precise gap. Beware the recurring collapse/overcount trap and that
distance-2 collisions are NOT local.
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

phase('Recon')
const MAPS = [
  `MAP the COLLISION structure. Over many 3-connected diam>=4 graphs (random gnp +
brute 3-conn check; n=11..16), enumerate every line shared by >=2 distance-2 pairs.
For each collided line L: how many distance-2 pairs map to it (multiplicity), and
WHAT is the structural relationship of those pairs (share a vertex? antipodal?
same common-neighbour set?). Tabulate the multiplicity distribution and the total
#collisions vs |E(G2)|-n (the surplus). Goal: find what 3-connectivity forbids that
keeps #collisions < surplus. Report the tightest cases (smallest D2-n).`,
  `MAP the HALL deficiency directly. Build H = (V, distance-2 lines) and, via the
alternating-closure / Dulmage-Mendelsohn method, find min over S of (|N_H(S)|-|S|)
and the binding (tight) S. Are tight S small or large? singletons? What distance-2
lines are the ONLY ones available to a tight S, and which 3-connectivity property
prevents |N_H(S)| < |S|? Compare to 2-separable graphs where Hall FAILS (D2<n) to
isolate exactly what 3-connectivity adds. Report smallest tight S + their neighbourhoods.`,
  `MAP what 3-CONNECTIVITY gives at the distance-2 level. For a pair {a,b} at distance
2, the interior is N(a)∩N(b). Menger gives 3 internally-disjoint a-b paths; a
diam>=4 vertex has far structure. Empirically: does 3-connectivity force each vertex
v to have distance-2 neighbours whose lines are distinct (an owner-like assignment
that, unlike the refuted simple owner-rule, survives)? Test candidate injections
V -> distinct distance-2 lines (e.g. v -> line(v, w) for w a distance-2 vertex chosen
by a Menger/degree rule) and report which survive on all samples and which break.`,
]
const maps = await parallel(MAPS.map((p, i) => () =>
  agent(`${CONTEXT}\n\nMAP TASK ${i + 1}. ${p}\nMeasurement to enable a proof; concrete tables + structural reason in 'argument'. verdict='substantial_partial'.`,
    { label: `map:${['collisions', 'hall', '3conn-leverage'][i]}`, phase: 'Recon', schema: PROOF_SCHEMA })))

const MAPCTX = `${CONTEXT}\n\nEMPIRICAL MAPS (re-verify load-bearing claims):\n${(maps || []).filter(Boolean).map((m, i) => `--- MAP ${i + 1} (${['collisions', 'hall', '3conn-leverage'][i]}) ---\n${m.summary}\n${m.argument}`).join('\n\n')}`

phase('Prove')
const PROVES = [
  { key: 'coarse-collision-bound', prompt: `Prove (B1) by COARSE COUNTING: D2 = |E(G2)| - #collisions. Lower-bound |E(G2)| (>= n from CLAIM A; better via min-deg of G2) and upper-bound #collisions using 3-connectivity, to get D2 >= n. A non-tight bound suffices given the +11..+31 slack. Pin down exactly what bounds the number of collided lines (e.g. each collision forces a local configuration that 3-connectivity limits).` },
  { key: 'hall-defect', prompt: `Prove (B1) via HALL on H=(V, distance-2 lines): assume a deficient set S (|N_H(S)| < |S|) and derive a contradiction from 3-connectivity (the distance-2 lines incident to S being too few would force a 2-cut or a vertex without enough distinct distance-2 structure). Use the alternating/defect characterization and Menger.` },
  { key: 'menger-injection', prompt: `Prove (B1) by an explicit INJECTION V -> distinct distance-2 lines built from Menger's 3 internally-disjoint paths / the distance-2 neighbourhood structure (interior = common neighbours). Define a canonical witness line for each vertex and prove distinctness using 3-connectivity. (The naive single owner-rule is refuted; find a rule that survives diffuse collisions.)` },
]
const proofs = await parallel(PROVES.map(spec => () =>
  agent(`${MAPCTX}\n\nPROOF TASK. ${spec.prompt}\nRun oracle checks (3-connected diam>=4 graphs; distance-2 lines) and report exactly. verdict='proved' only for a complete rigorous argument; be honest about gaps.`,
    { label: `prove:${spec.key}`, phase: 'Prove', schema: PROOF_SCHEMA }).then(a => ({ spec, attempt: a }))))

phase('Verify')
const verified = await parallel((proofs || []).filter(r => r && r.attempt).map(r => () =>
  parallel([
    () => agent(`${CONTEXT}\n\nADVERSARIAL VERIFICATION of a (B1) proof attempt (${r.spec.key}). Default to skepticism.\nARGUMENT:\n${r.attempt.argument}\nKEY LEMMAS:\n${(r.attempt.key_lemmas || []).map(l => `[${l.status}] ${l.statement}`).join('\n')}\nGAPS: ${(r.attempt.gaps || []).join(' | ')}\nBreak any 'proved' step: a logical gap OR a 3-connected diam>=4 graph where a claimed sub-lemma fails (build random 3-connected diam>=4 graphs and test with the oracle). Check the collision-bound / Hall-condition / injection-distinctness exhaustively. RUN code. Only 'sound' if nothing breaks.`,
      { label: `verify:${r.spec.key}:A`, phase: 'Verify', schema: VERIFY_SCHEMA }),
    () => agent(`${CONTEXT}\n\nADVERSARIAL VERIFICATION (2nd reviewer) of ${r.spec.key}. Focus on DISTINCTNESS/COLLISION claims and the essential use of 3-connectivity: would the step also (wrongly) prove D2>=n for a 2-separable graph where it is FALSE? If so the argument doesn't really use 3-connectivity and is broken. Test the claimed bound on 2-separable diam>=4 graphs (must FAIL there) and on 3-connected ones (must hold). Report concretely with code.`,
      { label: `verify:${r.spec.key}:B`, phase: 'Verify', schema: VERIFY_SCHEMA }),
  ]).then(vs => ({ ...r, verifications: (vs || []).filter(Boolean) }))))

phase('Synthesize')
const pack = (verified || []).filter(Boolean).map(r => {
  const a = r.attempt
  const vs = (r.verifications || []).map(v => `  [${v.verdict}/${v.severity}] ${v.details}${v.counterexample_g6 ? ' CE:' + v.counterexample_g6 : ''}`).join('\n')
  return `### ${r.spec.key} -> ${a.verdict} (conf ${a.confidence})\n${a.summary}\nGAPS: ${(a.gaps || []).join(' | ')}\nVERIFY:\n${vs}`
}).join('\n\n')

const synth = await agent(`${CONTEXT}\n\nSYNTHESIS. All (B1) proof attempts + adversarial verification:\n\n${pack}\n\nDELIVERABLE in 'argument' (clean markdown): (1) Is (B1) proved end-to-end with no surviving objection? If yes, the cleanest complete proof. (2) If not, the precise remaining gap + most promising partial. (3) Did any verifier find a counterexample to (B1) or a step that wrongly ignores 3-connectivity? Flag loudly. (4) Honest verdict: 'proved' only if complete & verification-surviving (and it genuinely uses 3-connectivity); else 'substantial_partial'. Be ruthless: oracle-checked-only != proved.`,
  { label: 'synthesis', phase: 'Synthesize', schema: PROOF_SCHEMA })

return {
  map_summaries: (maps || []).filter(Boolean).map(m => m.summary),
  attempts: (verified || []).filter(Boolean).map(r => ({ key: r.spec.key, verdict: r.attempt.verdict, confidence: r.attempt.confidence, verifier_verdicts: (r.verifications || []).map(v => v.verdict) })),
  synthesis_verdict: synth ? synth.verdict : null,
  synthesis_report: synth ? synth.argument : null,
}
