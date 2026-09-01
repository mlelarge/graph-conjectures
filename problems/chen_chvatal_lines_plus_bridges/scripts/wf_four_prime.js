// Historical snapshot for the repository's custom workflow runtime.
// This uses runtime-specific top-level constructs and is not standalone Node.js.
// Consult docs/STATUS.md and ledger D29-D30 before reusing any proposed target.

export const meta = {
  name: 'four-prime-closer',
  description: 'Data-driven Hall/SDR attack on the block-local inequality (4) nSigma+Adist+D >= |S| (closes Lemma A easy branch)',
  phases: [
    { title: 'Map' },
    { title: 'Prove' },
    { title: 'Verify' },
    { title: 'Synthesize' },
  ],
}

const DIR = 'problems/chen_chvatal_lines_plus_bridges'

const CONTEXT = `
GOAL: prove ONE block-local inequality (4'); it is the last gap in Lemma A's easy
branch (the non-2-connected case of Chen-Chvatal H5). Everything around it is
already proved. Work from ${DIR} (cd there first). Oracle:
  .venv/bin/python  with  import sys; sys.path.insert(0,"scripts"); import core
geng (nauty) + networkx available. Enumerate 2-connected graphs with  geng -C -q <n>.
The repo gate that verifies (4') and its Hall form is scripts/c2_t1_hall_gate.py
(read it; run it; copy/modify it to probe). c2_tight.py dumps the fiber/apex/D'
structure of a named graph:  .venv/bin/python scripts/c2_tight.py <graph6>.

THE OBJECT. Let B be a 2-CONNECTED graph, |B| = n >= 3, with a marked vertex u.
Put S = V(B)\\{u} (|S| = n-1 >= 2). Let d = d_B be the graph metric of B. Define a
partial "rooted-at-u" order:  x <=_u y  iff  d(u,x)+d(x,y) = d(u,y)  (x lies on a
u--y geodesic). Say x,y are COMPARABLE iff x <=_u y or y <=_u x.

- Sigma_s = { x in S : x comparable to s }   (the comparability class of s in S).
  nSigma = # distinct sets Sigma_s over s in S.   [Members of a "fiber"
  {s : Sigma_s = C} are pairwise comparable, i.e. lie on a common u-geodesic chain.]
- A_s = line_B(u,s) cap S = Sigma_s ∪ { x in S : u is between x and s }
  ( = { x : d(x,u)+d(u,s)=d(x,s) } ).  Adist = # distinct A_s that are PROPER (!= S).
- D' = # distinct B-lines L_B(a,b) (a,b in B) with u NOT in L_B(a,b) and L_B(a,b) != S.
  (A u-avoiding B-line is automatically a subset of S.)

TARGET (4'):   nSigma + Adist + D'  >=  |S|  ( = n-1 ).

It is TRUE and TIGHT (min margin 0) over EVERY 2-connected marked graph through
n=9, and every H5 leaf block through n=10 (scripts/c2_t1_hall_gate.py [--all-marked]).
Prove it for ALL n.

THE INTENDED ROUTE (a Hall/SDR saturation, also verified):
  Choose ONE representative per Sigma-fiber (nSigma of them). Each of the remaining
  |S| - nSigma vertices s can be matched INJECTIVELY to either its own PROPER apex
  trace A_s (!= S) or to a D' line that CONTAINS s. A matching saturating these
  |S|-nSigma vertices gives  Adist + D' >= |S| - nSigma,  hence (4').
  Equivalently (Hall's condition): in the bipartite graph H with left = the
  non-representative S-vertices and right = {proper apex traces} ∪ {D' lines},
  edge s~A_s (if proper) and s~(each D' line containing s), EVERY left-subset W
  satisfies |N(W)| >= |W|. c2_t1_hall_gate.py already builds H and checks
  saturation (0 failures); the task is to PROVE Hall's condition holds, using
  2-CONNECTIVITY of B.

WHY 2-CONNECTIVITY MATTERS (leads, verify before using): B 2-connected => deg_B(u)>=2,
no cut vertex, every vertex lies on a cycle through u (two internally-disjoint u--x
paths), and B has an OPEN-EAR decomposition (C_0 a cycle through u, then ears). The
"second disjoint path" / ear is the natural source of the apex/D' witness for a
redundant (non-representative) chain vertex.

CONSTRAINTS: (4') is a STANDALONE statement about a 2-connected graph with a marked
vertex -- no R, no G, no H5 here. The deliverable is a RIGOROUS proof (or a proof of
the Hall condition), not another ">=" gate. n is small/structural -- the statement
is finite-verified for all 2-connected marked graphs n<=9, so a CORRECT structural
argument is what's needed. Validate every sub-claim by running the oracle on small
2-connected marked graphs (geng -C); a sub-claim that fails one graph is refuted --
say so. Beware the recurring trap: a count of distinct SUBSETS (apex traces, D'
lines) only lower-bounds anything if distinct subsets give distinct objects -- but
here the three families nSigma/Adist/D' are counted as distinct sets and the Hall
matching enforces injectivity, so focus on |N(W)| >= |W|.
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

// --------------------------- Map ---------------------------
phase('Map')
const MAPS = [
  `MAP the FIBER / CHAIN structure. Over all 2-connected marked graphs (geng -C) at
n=4..8, characterize: (a) a Sigma-fiber {s: Sigma_s=C} -- confirm its members are
pairwise comparable (a chain on a u-geodesic), and tabulate fiber-size distribution;
(b) for a NON-representative chain vertex s (not the deepest? not the shallowest?),
is A_s proper (!= S), and if so what is A_s \\ (apex of the rep)? (c) exactly when is
A_s = S (apex improper) -- characterize it metrically. Report the structural picture
that a proof can use to assign a witness to each non-representative vertex.`,
  `PROBE the HALL deficiency directly. Copy/modify c2_t1_hall_gate.py to, for every
2-connected marked graph n=4..8, compute min over nonempty left-subsets W of
(|N(W)| - |W|) (the Hall slack), and DUMP the binding (tight, slack 0) W's and their
neighbourhoods. Questions: are the tight W's always whole Sigma-fibers (minus rep)?
single chains? What apex/D' resources are the *only* ones available to a tight W?
Identify the precise 2-connectivity fact that prevents |N(W)| < |W|. Give the
smallest tight examples (graph6 + the W).`,
  `MAP the WITNESS supply from 2-CONNECTIVITY. For a redundant (non-representative)
vertex s on a u-geodesic chain, 2-connectivity gives a second internally-disjoint
u--s path / an ear avoiding the chain. Empirically: does that second path/ear always
produce EITHER a proper apex trace A_s (a vertex off the chain that is not comparable
to s and not separated by u) OR a u-avoiding line D' containing s? Trace this on
several small 2-connected marked graphs (dump with c2_tight.py). Produce a concrete,
checked rule "non-rep s |-> witness(s)" and report where it is canonical vs ambiguous.`,
]
const maps = await parallel(MAPS.map((p, i) => () =>
  agent(`${CONTEXT}\n\nMAP TASK ${i + 1}. ${p}\nMeasurement to enable a proof; return concrete tables + the structural reason in 'argument'. verdict='substantial_partial'.`,
    { label: `map:${['fibers', 'hall-deficiency', 'witnesses'][i]}`, phase: 'Map', schema: PROOF_SCHEMA })))

const MAPCTX = `${CONTEXT}\n\nEMPIRICAL MAPS (from the Map phase; re-verify anything load-bearing):\n${(maps || []).filter(Boolean).map((m, i) => `--- MAP ${i + 1} (${['fibers', 'hall-deficiency', 'witnesses'][i]}) ---\n${m.summary}\n${m.argument}`).join('\n\n')}`

// --------------------------- Prove ---------------------------
phase('Prove')
const PROVES = [
  { key: 'hall-defect', prompt: `Prove (4') via HALL'S CONDITION on the bipartite graph H (non-rep S-vertices -> {proper apex traces} ∪ {D' lines}). Assume a Hall-violating set W (|N(W)| < |W|) and derive a contradiction from 2-connectivity of B (e.g. W's vertices would force a cut vertex, or a vertex with no second disjoint u-path). Make the deficiency-set argument rigorous.` },
  { key: 'ear-induction', prompt: `Prove (4') by INDUCTION on an open-ear decomposition of B (B_0 = cycle through u; B_{i+1} = B_i + ear). Track nSigma, Adist, D', |S| as each ear is added; show the inequality is preserved (base: a single cycle through u). Identify exactly how an ear of length L contributes (it adds L-1 new S-vertices and must supply >= that many new nSigma/Adist/D' units).` },
  { key: 'explicit-injection', prompt: `Prove (4') by an EXPLICIT INJECTION phi from S into {Sigma-fibers} ⊔ {proper apex traces} ⊔ {D' lines}: send the representative of each fiber to its fiber, and each non-representative s to a canonically chosen proper A_s or D' line (from the Map-phase witness rule), and prove phi is injective using 2-connectivity. This is the most direct route if the witness rule is canonical.` },
  { key: 'chain-transversal', prompt: `Prove (4') by a POSET/CHAIN argument. The comparability relation <=_u makes S a graded poset (by distance from u); Sigma-fibers are chains. |S| - nSigma = sum over fibers of (size-1) = the number of "covered" pairs. Show each redundant chain element s (with a predecessor in its fiber) yields a distinct proper apex trace or D' line via the second u-path guaranteed by 2-connectivity (Menger). Relate to a Dilworth/Mirsky-style transversal count.` },
]
const proofs = await parallel(PROVES.map(spec => () =>
  agent(`${MAPCTX}\n\nPROOF TASK. ${spec.prompt}\nRun oracle checks (geng -C, c2_t1_hall_gate.py) and report exactly. Be honest about gaps; set verdict='proved' only for a complete rigorous argument.`,
    { label: `prove:${spec.key}`, phase: 'Prove', schema: PROOF_SCHEMA }).then(a => ({ spec, attempt: a }))))

// --------------------------- Verify ---------------------------
phase('Verify')
const verified = await parallel((proofs || []).filter(r => r && r.attempt).map(r => () =>
  parallel([
    () => agent(`${CONTEXT}\n\nADVERSARIAL VERIFICATION of a (4') proof attempt (${r.spec.key}). Default to skepticism.\nARGUMENT:\n${r.attempt.argument}\nKEY LEMMAS:\n${(r.attempt.key_lemmas || []).map(l => `[${l.status}] ${l.statement}`).join('\n')}\nGAPS: ${(r.attempt.gaps || []).join(' | ')}\nBreak any 'proved' step: find a logical gap OR a small 2-connected marked graph (geng -C) where a claimed sub-lemma fails (especially the Hall condition |N(W)|>=|W|, the witness-injectivity, or an ear-induction step). RUN the oracle. Only 'sound' if nothing breaks after genuine attempts.`,
      { label: `verify:${r.spec.key}:A`, phase: 'Verify', schema: VERIFY_SCHEMA }),
    () => agent(`${CONTEXT}\n\nADVERSARIAL VERIFICATION (2nd reviewer) of (4') attempt (${r.spec.key}). Focus on DISTINCTNESS / INJECTIVITY: are the witnesses the proof assigns to distinct non-rep vertices actually DISTINCT objects (apex traces / D' lines that don't collide)? Is the use of 2-connectivity essential and correct (would the step fail on a graph that is only 1-connected)? Test the assignment exhaustively on n=5,6,7 2-connected marked graphs with the oracle. Report concretely with code.`,
      { label: `verify:${r.spec.key}:B`, phase: 'Verify', schema: VERIFY_SCHEMA }),
  ]).then(vs => ({ ...r, verifications: (vs || []).filter(Boolean) }))))

// --------------------------- Synthesis ---------------------------
phase('Synthesize')
const pack = (verified || []).filter(Boolean).map(r => {
  const a = r.attempt
  const vs = (r.verifications || []).map(v => `  [${v.verdict}/${v.severity}] ${v.details}${v.counterexample_g6 ? ' CE:' + v.counterexample_g6 : ''}`).join('\n')
  return `### ${r.spec.key} -> ${a.verdict} (conf ${a.confidence})\n${a.summary}\nGAPS: ${(a.gaps || []).join(' | ')}\nVERIFY:\n${vs}`
}).join('\n\n')

const synth = await agent(`${CONTEXT}\n\nSYNTHESIS. All (4') proof attempts + adversarial verification:\n\n${pack}\n\nDELIVERABLE in 'argument' (clean markdown): (1) Is (4') PROVED end-to-end with no surviving verifier objection? If yes, write the cleanest complete proof. (2) If not, the precise remaining gap and the most promising partial. (3) Did any verifier find a counterexample to (4') itself (vs a proof step)? Flag loudly if so. (4) Honest verdict: 'proved' only if a complete, verification-surviving proof exists; else 'substantial_partial'. Be ruthless: oracle-checked-only != proved.`,
  { label: 'synthesis', phase: 'Synthesize', schema: PROOF_SCHEMA })

return {
  map_summaries: (maps || []).filter(Boolean).map(m => m.summary),
  attempts: (verified || []).filter(Boolean).map(r => ({ key: r.spec.key, verdict: r.attempt.verdict, confidence: r.attempt.confidence, verifier_verdicts: (r.verifications || []).map(v => v.verdict) })),
  synthesis_verdict: synth ? synth.verdict : null,
  synthesis_report: synth ? synth.argument : null,
}
