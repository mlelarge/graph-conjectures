// Historical snapshot for the repository's custom workflow runtime.
// This uses runtime-specific top-level constructs and is not standalone Node.js.
// Consult docs/STATUS.md and ledger D29-D30 before reusing any proposed target.

export const meta = {
  name: 'c2-hall-closer',
  description: 'Data-driven Hall/SDR attack on the single open inequality C2 that closes Lemma A (non-2-connected case of H5)',
  phases: [
    { title: 'Map' },
    { title: 'Prove' },
    { title: 'Verify' },
    { title: 'Synthesize' },
  ],
}

const DIR = 'problems/chen_chvatal_lines_plus_bridges'

const CONTEXT = `
GOAL: close ONE inequality (C2) and thereby PROVE the non-2-connected case of the
Chen-Chvatal H5 lemma. Everything around C2 is already rigorously PROVED and
adversarially verified. Work from ${DIR} (cd there first). Oracle:
  .venv/bin/python with  import sys; sys.path.insert(0,"scripts"); import core
geng (nauty), networkx available. Read docs/H5_LEMMA_A_REDUCTION.md for the full
proved scaffold; gate: scripts/lemma_a_reduction_gate.py.

SETUP. G connected, pendant-free, NOT 2-connected. B = a non-bridge leaf block,
u = its unique cut vertex, S = V(B)\\{u} (|S|>=2), R = G - S (connected, u in R).
G = 1-sum of R and B at the single vertex u. Each line L ↦ trace (L∩S, L∩R).
Definitions: Z = #{lines with L∩S ∈ {∅,S}};  P = #{lines with ∅ ⊊ L∩S ⊊ S}.

PROVED (do not re-derive; rely on these):
- (M) R and B are isometric in G; d_G(r,s) = d_R(r,u)+d_B(u,s) for r∈R, s∈S.
- (RR) for a,b∈R: line_G(a,b)∩R = line_R(a,b); so Lines(R) injects into the
  Z-class ⇒ Z ≥ ell(R).
- (CROSS) for s∈S, p∈R\\{u}: line_G(s,p) = Σ_s ⊔ T_p, a genuine PRODUCT — Σ_s=line∩S
  depends only on s, T_p=line∩R depends only on p, no collapse (strict triangle
  inequality). So distinct mixed-pair lines = |{Σ_s : s∈S}| · |{T_p : p∈R\\{u}}|.
- (THM) ell(G) = Z + P, hence ell(G) ≥ ell(R) + P.

THE TARGET (Lemma A): ell(G) ≥ |S| + max(ell(R), |R|). Setting Q := Z − ell(R) ≥ 0,
this is EXACTLY:
  (C2)   P + Q  ≥  |S| + max(0, |R| − ell(R)).
- EASY branch (ell(R) ≥ |R|): suffices to show P ≥ |S|. (Oracle: P − |S| ≥ 1 on n≤10.)
- DEFICIT branch (ell(R) < |R|, LIVE in ~half of cases): need the extra |R|−ell(R);
  the block's mixed/Σ=S lines must REPAIR R's line-deficit.
C2 holds with min margin 1 over every leaf block n=8,9,10 (verified). It is the
ENTIRE remaining content of Lemma A.

INTENDED MECHANISM: a Hall/SDR (systems-of-distinct-representatives) argument.
Build the bipartite "incidence" between S (or V\\{u}) and the proper-S-trace
lines (P-class) plus the deficit-repair lines (in Q), and show a matching
saturates the required side, using 2-connectivity of B (which guarantees ≥2
internally-disjoint u–s paths for every s, hence a richer Σ-ray / line supply
than R has). The PRODUCT structure P ≥ |{Σ_s}|·|{T_p}| is the key lever.

HARD CONSTRAINTS — these routes are REFUTED, do NOT use them:
- signature split (A') nS≥|S| ∧ (C') excessS≥max(ell(R),|R|): (C') FALSE at n=10.
- R-mirror Hall Q_rmirror=#{∅⊊L∩R⊊R} ≥ |R|: FALSE at n=10 (I?AB?rCM?).
- any closed form for C2 in (ell(B),|R|,deficit): all fail (block can be C4, ell(B)=1).
- any global subset-of-short-lines / bounded-index charge (the exhausted axis).
The deliverable is a RIGOROUS proof of C2 (or of the easy branch P≥|S| plus an
explicit deficit-repair lemma), NOT another empirical ">=" gate. Validate every
sub-claim on small graphs with the oracle (geng -c -d2, filter non-biconnected
pendant-free diam>=4); a sub-claim failing one graph is refuted — say so.
`

const PROOF_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['approach', 'verdict', 'confidence', 'summary', 'argument', 'key_lemmas', 'gaps', 'oracle_checks'],
  properties: {
    approach: { type: 'string' },
    verdict: { enum: ['c2_proved', 'easy_branch_proved', 'substantial_partial', 'stuck', 'refuted'] },
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

// ---- Map phase: characterize the incidence/product structure empirically ----
phase('Map')
const MAPS = [
  `MAP THE EASY BRANCH. Over all non-2-connected pendant-free diam>=4 graphs at n=8,9
(and spot n=10), for every leaf block compute |{Σ_s : s∈S}| (distinct B-side rays
from u among mixed lines), |{T_p : p∈R\\{u}}| (distinct R-side rays), and P. Tabulate
P vs |{Σ_s}|·|{T_p}| vs |S|. QUESTIONS: is P ≥ |{Σ_s}|·|{T_p}| always (the product
lower bound)? Is |{Σ_s}|·|{T_p}| ≥ |S| always in the no-deficit branch? When |{Σ_s}|
is small, is |{T_p}| correspondingly large? Find the exact combinatorial reason
(tie it to 2-connectivity of B / structure of R). Report tables + the tightest cases.`,
  `MAP THE DEFICIT BRANCH. Restrict to leaf blocks with ell(R) < |R| (the deficit
cases). For each, identify EXACTLY which lines supply the extra |R|−ell(R) beyond
ell(R)+|S|: are they Σ=S lines (Q), specific mixed lines, or B-internal? Characterize
the deficit of R structurally (which pairs of R-vertices share a line in R but get
SEPARATED in G, and by which G-line). Produce a candidate identity/bijection
"deficit of R ↦ distinct extra G-lines". Use the oracle heavily; report the mechanism.`,
  `MAP THE HALL STRUCTURE. Construct the explicit bipartite graph H: left = S (or the
|S| fresh-line slots), right = P-class lines; s ~ L iff s is "represented" by L (define
a natural incidence, e.g. s ∈ Σ-support of L, or the line line_G(s, p*) for a fixed
p*). Empirically test Hall's condition: for every W ⊆ S, is |N(W)| ≥ |W|? Find the
minimal-|N(W)|/|W| ratios across the census and whether 2-connectivity of B forces
|N(W)| ≥ |W|. If a clean incidence with provable Hall condition exists, state it; if
the naive incidence fails Hall, report the failing W and refine the incidence.`,
]
const maps = await parallel(MAPS.map((p, i) => () =>
  agent(`${CONTEXT}\n\nRECON/MAP TASK ${i + 1}. ${p}\nThis is measurement to enable a proof; return concrete tables and the structural reason in 'argument'. verdict='substantial_partial'.`,
    { label: `map:${['easy', 'deficit', 'hall'][i]}`, phase: 'Map', schema: PROOF_SCHEMA })))

const MAPCTX = `${CONTEXT}\n\nEMPIRICAL MAPS (from the Map phase — use, but re-verify load-bearing claims):\n${(maps || []).filter(Boolean).map((m, i) => `--- MAP ${i + 1} (${['easy', 'deficit', 'hall'][i]}) ---\n${m.summary}\n${m.argument}`).join('\n\n')}`

// ---- Prove phase ----
phase('Prove')
const PROVES = [
  { key: 'hall-easy', prompt: `Prove the EASY branch P ≥ |S| (ell(R) ≥ |R|) rigorously via the product bound and a Hall/SDR or counting argument, using the mapped incidence and 2-connectivity of B. Then state precisely what extra is needed for the deficit branch. A complete easy-branch proof is itself valuable (verdict='easy_branch_proved').` },
  { key: 'deficit-repair', prompt: `Prove the DEFICIT branch: when ell(R) < |R|, exhibit ≥ |S| + (|R|−ell(R)) distinct lines among the P-class and Q-class, via an explicit injection that (a) gives |S| fresh block lines and (b) gives |R|−ell(R) deficit-repair lines from the mapped "deficit ↦ extra G-line" mechanism. Combine with the easy-branch idea to get full C2.` },
  { key: 'full-c2-hall', prompt: `Prove the FULL C2 = P + Q ≥ |S| + max(0,|R|−ell(R)) in one shot via a single Hall/SDR system on V\\{u} → distinct G-lines (each vertex of S and each "deficient" R-vertex claims a distinct proper-or-Q line), with Hall's condition discharged by 2-connectivity of B and the product structure. This is the cleanest possible closing.` },
]
const proofs = await parallel(PROVES.map(spec => () =>
  agent(`${MAPCTX}\n\nPROOF TASK. ${spec.prompt}\nRun oracle checks; report exactly. Be honest about gaps.`,
    { label: `prove:${spec.key}`, phase: 'Prove', schema: PROOF_SCHEMA }).then(a => ({ spec, attempt: a }))))

// ---- Verify phase ----
phase('Verify')
const verified = await parallel((proofs || []).filter(r => r && r.attempt).map(r => () =>
  parallel([
    () => agent(`${CONTEXT}\n\nADVERSARIAL VERIFICATION of a C2 proof attempt (${r.spec.key}). Default to skepticism.\nARGUMENT:\n${r.attempt.argument}\nKEY LEMMAS:\n${(r.attempt.key_lemmas || []).map(l => `[${l.status}] ${l.statement}`).join('\n')}\nGAPS: ${(r.attempt.gaps || []).join(' | ')}\nBreak any 'proved' step: find a logical gap OR a small graph (geng -c -d2, non-biconnected pendant-free diam>=4) where a claimed sub-lemma (especially Hall's condition |N(W)|≥|W|, or the deficit-repair injection) FAILS. Run the oracle. Only 'sound' if nothing breaks.`,
      { label: `verify:${r.spec.key}:A`, phase: 'Verify', schema: VERIFY_SCHEMA }),
    () => agent(`${CONTEXT}\n\nADVERSARIAL VERIFICATION (2nd reviewer) of C2 attempt (${r.spec.key}). Focus on DISTINCTNESS / double-counting: are the lines the proof claims distinct actually distinct (run the oracle on n=8,9,10)? Is the Hall incidence well-defined (single-valued)? Is the deficit-repair injection truly injective and disjoint from the |S| fresh lines? Report concretely with code.`,
      { label: `verify:${r.spec.key}:B`, phase: 'Verify', schema: VERIFY_SCHEMA }),
  ]).then(vs => ({ ...r, verifications: (vs || []).filter(Boolean) }))))

// ---- Synthesis ----
phase('Synthesize')
const pack = (verified || []).filter(Boolean).map(r => {
  const a = r.attempt
  const vs = (r.verifications || []).map(v => `  [${v.verdict}/${v.severity}] ${v.details}${v.counterexample_g6 ? ' CE:' + v.counterexample_g6 : ''}`).join('\n')
  return `### ${r.spec.key} → ${a.verdict} (conf ${a.confidence})\n${a.summary}\nGAPS: ${(a.gaps || []).join(' | ')}\nVERIFY:\n${vs}`
}).join('\n\n')

const synth = await agent(`${CONTEXT}\n\nSYNTHESIS. All C2 proof attempts + adversarial verification:\n\n${pack}\n\nDELIVERABLE in 'argument' (clean markdown): (1) Is C2 (or the easy branch P≥|S|) now PROVED end-to-end with no surviving verifier objection? If yes, write the cleanest complete proof. (2) If not, the precise remaining gap and the most promising partial. (3) Did any verifier counterexample refute C2 itself (vs a step)? Flag loudly if so. (4) Honest verdict: 'c2_proved' only if a complete, verification-surviving proof of C2 exists; 'easy_branch_proved' if only the easy branch is closed; else 'substantial_partial'. Be ruthless: oracle-checked-only ≠ proved.`,
  { label: 'synthesis', phase: 'Synthesize', schema: PROOF_SCHEMA })

return {
  map_summaries: (maps || []).filter(Boolean).map(m => m.summary),
  attempts: (verified || []).filter(Boolean).map(r => ({ key: r.spec.key, verdict: r.attempt.verdict, confidence: r.attempt.confidence, verifier_verdicts: (r.verifications || []).map(v => v.verdict) })),
  synthesis_verdict: synth ? synth.verdict : null,
  synthesis_report: synth ? synth.argument : null,
}
