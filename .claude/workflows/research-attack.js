export const meta = {
  name: 'research-attack',
  description: 'Generic autonomous research engine: run propose->ground->skeptic->verify->synthesize->decide rounds against any problem ledger.json',
  whenToUse: 'Attack an open math conjecture that has a seeded ledger.json + a callable oracle. Pass args:{problem_dir, rounds?, proposers?, dry_limit?}. Problem-agnostic.',
  phases: [
    { title: 'Gate', detail: 'startup: refuse to re-run a ledger already handed back with nothing queued' },
    { title: 'Propose', detail: 'diverse-lens proposers read the ledger and propose next moves' },
    { title: 'Ground+Skeptic+Verify', detail: 'pipeline each proposal: oracle-check -> adversarial refute -> independent re-derive' },
    { title: 'Synthesize', detail: 'lead rewrites ledger.json: promote/graveyard, update crux, append decision, set needs_human' },
  ],
}

// ----------------------------------------------------------------------------
// Generic research engine.  NOTHING here is specific to any problem: all domain
// knowledge comes from <problem_dir>/ledger.json (read by agents) and the
// oracle it declares (called by agents via Bash).  Point it at any problem that
// satisfies engine/LEDGER_CONTRACT.md.
// ----------------------------------------------------------------------------

let A = args
if (typeof A === 'string') { try { A = JSON.parse(A) } catch (e) { A = {} } }
A = A || {}
const DIR = A.problem_dir
if (!DIR) throw new Error('args.problem_dir is required (absolute path to the problem folder containing ledger.json). Got args=' + JSON.stringify(args))
const ROUNDS = A.rounds || 1
const N_PROP = A.proposers || 3
const DRY_LIMIT = A.dry_limit || 2
const DROUGHT_LIMIT = A.drought_limit || 3   // hand back after this many rounds with no NEW frontier result
const LEDGER = `${DIR}/ledger.json`
// Model split: cheap idea-generation proposers on Fable 5; the schema-heavy,
// load-bearing slots (executor, ground, skeptic, verify, synthesize) on Opus.
// Fable churned on the strict StructuredOutput schemas, so keep it to proposers.
const MODEL_PROPOSE = A.model_propose || 'fable'
const MODEL_MAIN = A.model_main || 'opus'

// Generic research lenses, cycled across proposers. Domain-independent.
const LENSES = [
  { key: 'explicit-construction', brief: 'Construct or improve an EXPLICIT finite object that beats the current benchmark (push a bound). It must be groundable on the oracle.' },
  { key: 'asymptotic-argument', brief: 'Propose one concrete step of an ASYMPTOTIC / probabilistic / counting argument toward the open_crux. State the finite check that would FALSIFY it.' },
  { key: 'literature-reduction', brief: 'Reduce the open_crux to (or bound it by) a KNOWN theorem. Give the primary citation; flag it as needs-verification.' },
  { key: 'dual-attack', brief: 'Attack a DUAL / equivalent formulation named in the ledger and transfer the bound back.' },
]

const COMMON = `
You are one agent in an autonomous research engine attacking an open mathematical conjecture.
The single source of truth is the ledger at: ${LEDGER}
ALWAYS begin by reading it. Obey its discipline_gates exactly. The oracle (sound, exact,
computational ground truth) is described in ledger.benchmark.oracle_cmd / oracle_api; the
problem folder is ${DIR}. Call the oracle with that folder's venv, e.g.
  ${DIR}/.venv/bin/python ${DIR}/scripts/oracle.py ...
Never invent oracle output — run it. SCAN DISCIPLINE (a HARD gate — no exceptions, no clever workarounds):
every oracle/scan computation MUST be a SINGLE FOREGROUND command wrapped in \`timeout\` (e.g.
\`timeout 600 <one cmd>\`) that finishes inside THIS one turn. The following are ABSOLUTELY FORBIDDEN no
matter how you justify them, and any attempt to use them means you must instead report the experiment as
infeasible: \`run_in_background: true\` on the Bash tool; a trailing \`&\`; \`nohup\` / \`disown\` / \`setsid\`;
launching a task and then Read-polling or \`until\`-looping its \`.output\` file (busy-waiting); and chaining
multiple heavy scans in a \`for n in ...\` (or any) loop. Run exactly ONE scan per command, in the foreground,
timeout-capped. Choose n so a single scan completes within \`timeout 600\`; the COMBINATORIAL n-hunts at the
k>=6 frontier do NOT finish in any foreground budget, so if no feasible n exists, REPORT THE EXPERIMENT AS
INFEASIBLE (verdict=fail, killed_reason="scan infeasible in foreground budget; needs an analytic route, not
brute search") — do NOT background it, do NOT poll an output file, do NOT split it across turns. Nothing you
start may outlive the workflow; a computation must finish or be killed within YOUR turn.

UNIVERSAL-CLAIM DISCIPLINE (a hard gate, DISTINCT from empirical_not_proof). First classify every claim by
its LOGICAL FORM: EXISTENTIAL ("a witness exists"), UNIVERSAL ("for ALL X in class C, P(X)" — an
identity/inequality/property that must hold for every object), ASYMPTOTIC/family ("infinitely many ..."), or
STRUCTURAL. The verification bar depends on the form:
  • EXISTENTIAL  -> one oracle-verified construction settles it.
  • ASYMPTOTIC/family -> needs a SYMBOLIC proof; finite-n survival is not a theorem (empirical_not_proof).
  • UNIVERSAL  -> can NEVER be supported by examples drawn from a STRUCTURED sub-family (circulants, the
    specific construction, the family the conjecture came from): those are exactly the instances where special
    identities hold, so they are the WORST possible sample. Before a universal claim may be called "supported"
    (let alone proved), it MUST survive an EXHAUSTIVE census over GENERIC small members of the FULL class
    (e.g. nauty gentourng / all-objects enumeration), with the search aimed at the GENERIC part, NOT the
    structured sub-family. ONE counterexample kills it; any number of structured confirmations prove nothing.
Whenever you state, verify, or promote a claim, name its logical form and apply the matching bar.
Your final message is consumed as DATA, not shown to a human.`

const PROPOSAL_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['lens', 'idea', 'claim_form', 'falsifiable_prediction', 'ground_plan', 'beats_benchmark', 'novel_vs_graveyard'],
  properties: {
    lens: { type: 'string' },
    idea: { type: 'string', description: 'one concrete next move, specific enough to test' },
    claim_form: { type: 'string', enum: ['existential', 'universal', 'asymptotic', 'structural'], description: 'LOGICAL FORM of the claim this move makes. If UNIVERSAL ("for all X in class C ..."), its ground_plan MUST be (or include) an exhaustive census over GENERIC members of the full class, not the structured sub-family — else it cannot be supported.' },
    falsifiable_prediction: { type: 'string', description: 'what finite/oracle-checkable fact would CONFIRM or KILL it' },
    ground_plan: { type: 'string', description: 'exact oracle/bash command(s) or construction the grounder should run' },
    beats_benchmark: { type: 'string', description: 'how this advances open_crux or improves a proved bound' },
    novel_vs_graveyard: { type: 'boolean', description: 'true iff NOT already killed in ledger.graveyard' },
  },
}
const GROUND_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['verdict', 'evidence', 'killed_reason'],
  properties: {
    verdict: { type: 'string', enum: ['pass', 'fail', 'inconclusive'] },
    evidence: { type: 'string', description: 'commands actually run + their real output' },
    killed_reason: { type: 'string', description: 'empty unless verdict=fail' },
  },
}
const SKEPTIC_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['refuted', 'reason', 'attack_tried', 'generic_census'],
  properties: {
    refuted: { type: 'boolean' },
    reason: { type: 'string' },
    attack_tried: { type: 'string', description: 'scale-comparison vs benchmark / small-counterexample hunt / flaw in the argument / quantifier-trap check' },
    generic_census: { type: 'string', description: 'for a UNIVERSAL claim: the EXHAUSTIVE generic enumeration you ran over the full class (e.g. "gentourng all order<=7, 0 counterexamples" or "FOUND counterexample: <object>"). "n/a" only if the claim is not universal.' },
  },
}
const VERIFY_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['claim_type', 'claim_form', 'verified_scope', 'confirmed', 'can_enter_proved', 'notes'],
  properties: {
    claim_type: { type: 'string', enum: ['empirical', 'derivation', 'construction', 'citation'], description: 'kind of EVIDENCE' },
    claim_form: { type: 'string', enum: ['existential', 'universal', 'asymptotic', 'structural'], description: 'LOGICAL FORM (drives the bar)' },
    verified_scope: { type: 'string', description: 'the EXACT scope on which this is actually checked, e.g. "all tournaments to order 7 (gentourng), 0 counterexamples" vs "circulant/AC factors only". A universal claim verified only on a structured family must say so HERE and have confirmed=false.' },
    confirmed: { type: 'boolean', description: 'For a UNIVERSAL claim: FALSE unless an EXHAUSTIVE GENERIC census (not structured examples) found no counterexample.' },
    can_enter_proved: { type: 'boolean', description: 'FALSE for empirical-only claims (empirical_not_proof); FALSE for any universal claim lacking a symbolic proof OR a clean generic census (universal_needs_generic_census).' },
    notes: { type: 'string' },
  },
}
const SYNTH_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['ledger_advanced', 'frontier_advanced', 'decision_id', 'summary', 'promoted', 'graveyarded', 'next_action', 'needs_human', 'recommend_handback'],
  properties: {
    ledger_advanced: { type: 'boolean', description: 'true iff proved/open_crux/live_hypotheses changed at all this round' },
    frontier_advanced: { type: 'boolean', description: 'true iff this round produced a GENUINELY NEW result: a bound improved, a new structural barrier found, or a new survivor isolated -- NOT merely re-killing a variant of an already-dead family' },
    decision_id: { type: 'string', description: 'the new D-number appended to decision_log' },
    summary: { type: 'string' },
    promoted: { type: 'array', items: { type: 'string' } },
    graveyarded: { type: 'array', items: { type: 'string' } },
    next_action: { type: 'string' },
    needs_human: { type: ['string', 'null'], description: 'null unless a genuine human-decision gate was hit (quote it)' },
    recommend_handback: { type: ['string', 'null'], description: 'null to keep going; non-null = your judgment that the COMPUTATIONAL frontier is exhausted and real human math input is needed -- quote exactly what is needed (e.g. "a Bohman-Keevash concentration argument; the oracle cannot certify an asymptotic proof")' },
  },
}

const GATE_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['ledger_handback_standing', 'has_unrun_experiment', 'status_md_hint', 'reason'],
  properties: {
    ledger_handback_standing: { type: 'boolean', description: 'AUTHORITATIVE — judged from ledger.json ONLY (never from STATUS.md). true iff the LEDGER\'s own current state is a standing hand-back: ledger.needs_human is non-null/non-empty, OR the ledger\'s LATEST decision_log entry records a recommend_handback / "frontier exhausted" / "hand back to human" not superseded by a later entry. A cleared (null/absent) needs_human with no such current decision_log record = NOT standing (false).' },
    has_unrun_experiment: { type: 'boolean', description: 'AUTHORITATIVE — from ledger.next_action / live_hypotheses ONLY. true iff a CONCRETE computational experiment is queued and not yet run.' },
    status_md_hint: { type: 'string', description: 'What docs/STATUS.md (a MIRROR that may be STALE) says about handback/exhaustion. A HINT to help you notice exhaustion in the ledger — it must NOT by itself set ledger_handback_standing and must NOT override the ledger. "n/a" if absent or silent.' },
    reason: { type: 'string', description: 'one line: quote the LEDGER-authoritative standing hand-back, or "no hand-back standing in ledger".' },
  },
}

// --- STARTUP GUARD: don't burn a round re-concluding a hand-back ---------------
// ledger.json is AUTHORITATIVE; docs/STATUS.md is only a (possibly stale) mirror
// that HELPS the gate notice exhaustion but never blocks on its own. A previously-
// attempted ledger may already record a standing hand-back (needs_human, or a
// recommend_handback in its latest decision_log) with no fresh experiment queued;
// re-running then just spends a round to re-derive it. Read the gate via one cheap
// agent (workflow scripts have no fs access) and refuse ONLY when the LEDGER itself
// is standing-handback AND has no concrete next_action. The override is semantic
// and auditable: QUEUE a concrete next_action (or clear needs_human) in the ledger
// — the ledger then records WHY the re-run is warranted, and the EXECUTOR consumes it.
phase('Gate')
const gate = await agent(
  `${COMMON}\n\nYou are the STARTUP GATE. Do NOT run any experiment or call the oracle. ledger.json is the AUTHORITATIVE source; docs/STATUS.md is only a mirror that MAY BE STALE. Read ${LEDGER} (authoritative) and ${DIR}/docs/STATUS.md (hint only, if it exists).\n- ledger_handback_standing: judge from the LEDGER ALONE — true iff ledger.needs_human is non-null/non-empty, OR the ledger's LATEST decision_log entry records a recommend_handback / "frontier exhausted" / "hand back to human" not superseded by a later entry. A cleared/absent needs_human with no current decision_log handback record = false. Do NOT set this true merely because STATUS.md says so.\n- has_unrun_experiment: true iff ledger.next_action (or a live_hypothesis) names a CONCRETE un-run computational experiment.\n- status_md_hint: what STATUS.md claims about handback/exhaustion (hint only).\n- reason: quote the ledger-authoritative standing hand-back, or "no hand-back standing in ledger".\nReport the fields; nothing else.`,
  { label: 'startup-gate', phase: 'Gate', schema: GATE_SCHEMA, model: MODEL_MAIN }
)
if (gate && gate.ledger_handback_standing && !gate.has_unrun_experiment) {
  log(`Startup gate: the LEDGER records a standing hand-back and nothing fresh queued — NOT running. Queue a concrete next_action (or clear needs_human) in the ledger to direct another round.`)
  return {
    problem_dir: DIR,
    rounds_run: 0,
    stopped_for: `startup_gate: ledger records a standing hand-back — ${gate.reason}. No un-run experiment queued; add a concrete next_action to the ledger (the EXECUTOR will consume it) to run another round.`,
    gate,
    ledger: LEDGER,
    status_md: `${DIR}/docs/STATUS.md`,
  }
}
log(`Startup gate: clear — ${gate ? (gate.has_unrun_experiment ? 'fresh next_action queued' : 'no hand-back standing in ledger') : 'gate unavailable, proceeding'}`)

const report = []
let dry = 0, drought = 0, handback = null

for (let r = 1; r <= ROUNDS; r++) {
  log(`Round ${r}/${ROUNDS} — proposing (${N_PROP} lenses)`)
  const PH_P = `R${r}:Propose`, PH_G = `R${r}:Ground+Skeptic+Verify`, PH_S = `R${r}:Synthesize`

  // --- DIRECTED EXECUTION + PROPOSE (parallel) ---
  // A first-class EXECUTOR runs whatever concrete experiment the last round queued
  // (ledger.next_action / an UN-RUN hypothesis) so the engine's own priority can
  // never sit idle while free-lance proposers chase peripheral ideas.
  const thunks = []
  thunks.push(() => agent(
    `${COMMON}\n\nYou are the EXECUTOR — the highest-priority slot. Read ${LEDGER}. If ledger.next_action, or any live_hypothesis whose status/idea is marked UN-RUN / "run this" / "the only un-run experiment", names a CONCRETE computational experiment that has NOT yet been run, then ACTUALLY DO IT NOW: implement the script under ${DIR}/scripts/, RUN it with ${DIR}/.venv/bin/python, and capture the REAL output. Return it as a proposal whose ground_plan is the exact command you ran (so it re-grounds), idea names the experiment, and falsifiable_prediction is its beat/floor signature with the measured numbers. If and only if there is NO concrete un-run experiment queued, return idea="(none queued)" and novel_vs_graveyard=false to be skipped.`,
    { label: `execute:next_action`, phase: PH_P, schema: PROPOSAL_SCHEMA, model: MODEL_MAIN }
  ))
  for (let i = 0; i < N_PROP; i++) {
    const lens = LENSES[i % LENSES.length]
    thunks.push(() => agent(
      `${COMMON}\n\nLENS = ${lens.key}: ${lens.brief}\n\nRead ${LEDGER}. Propose exactly ONE move under your lens that attacks ledger.open_crux or improves a proved bound. It must be concrete enough that the grounder can test it with the oracle. Do NOT repeat anything in ledger.graveyard, and do NOT duplicate the queued next_action (the executor owns that). Return the proposal.`,
      { label: `propose:${lens.key}`, phase: PH_P, schema: PROPOSAL_SCHEMA, model: MODEL_PROPOSE }
    ))
  }
  const proposals = (await parallel(thunks)).filter(Boolean).filter(p => p.novel_vs_graveyard !== false)

  log(`Round ${r} — ${proposals.length} proposals; grounding -> skeptic -> verify`)

  // --- GROUND -> SKEPTIC -> VERIFY (pipeline; each proposal flows independently) ---
  const outcomes = await pipeline(
    proposals,
    // stage 1: ground on the oracle
    (p) => agent(
      `${COMMON}\n\nGROUND this proposal by actually RUNNING the oracle. Proposal:\n${JSON.stringify(p, null, 2)}\n\nExecute its ground_plan (run the commands; if a construction is described, build it and feed it to the oracle). Report the REAL output. verdict=fail only if the oracle contradicts the proposal's falsifiable_prediction.`,
      { label: `ground`, phase: PH_G, schema: GROUND_SCHEMA, model: MODEL_MAIN }
    ).then(g => ({ p, g })),
    // stage 2: adversarial skeptic (kill-by-default) — only if not already killed
    (x) => (x.g.verdict === 'fail')
      ? { ...x, s: { refuted: true, reason: x.g.killed_reason || 'failed grounding', attack_tried: 'oracle', generic_census: 'n/a (failed grounding)' } }
      : agent(
          `${COMMON}\n\nYou are the SKEPTIC. Try to REFUTE this proposal (default to refuted=true if unconvinced). Proposal:\n${JSON.stringify(x.p, null, 2)}\nGrounding evidence:\n${JSON.stringify(x.g, null, 2)}\nAttack it: compare its claimed gain against ledger.benchmark scales; hunt a small counterexample with the oracle; find the flaw in any asymptotic step.\nIf the proposal asserts a UNIVERSAL claim (claim_form="universal", or it states an identity/inequality/property "for all X"), your FIRST and PRIMARY move is the smallest-counterexample EXHAUSTIVE hunt over the FULL class — run nauty gentourng / all-objects enumeration aimed at the GENERIC part of the class, NOT a re-test of the structured family the claim came from; one counterexample sets refuted=true. Record exactly what census you ran in generic_census. A universal claim supported ONLY by structured/circulant examples is NOT verified — refute it as "biased sample; generic census not done/failed".\nALSO run the QUANTIFIER-TRAP check on any argument: does it give an INDUCED sub-object its OPTIMAL / minimum-over-orders invariant when that sub-object actually inherits an ARBITRARY induced one? (canonical warning: a transitive triple has tournament-clique-number 1, but its REVERSE order has a 3-clique — so an arbitrary induced order's clique number is NOT bounded by the min-over-orders value.) If the argument confuses "for all orders" with "for the optimal order", refute it.`,
          { label: `skeptic`, phase: PH_G, schema: SKEPTIC_SCHEMA, model: MODEL_MAIN }
        ).then(s => ({ ...x, s })),
    // stage 3: independent re-verification of survivors
    (x) => (x.s.refuted)
      ? { ...x, v: { claim_type: 'derivation', claim_form: x.p.claim_form || 'structural', verified_scope: 'n/a (refuted)', confirmed: false, can_enter_proved: false, notes: 'refuted by skeptic' } }
      : agent(
          `${COMMON}\n\nINDEPENDENTLY re-verify this surviving result from scratch (do not trust the prior agents). Proposal:\n${JSON.stringify(x.p, null, 2)}\nGrounding:\n${JSON.stringify(x.g, null, 2)}\nApply BOTH discipline gates:\n  (empirical_not_proof) if the support is only finite-n oracle evidence, set can_enter_proved=false.\n  (universal_needs_generic_census) if claim_form is UNIVERSAL, set confirmed=true ONLY if an EXHAUSTIVE GENERIC census over the full class (gentourng / all-objects, generic part — NOT the structured family) found no counterexample; otherwise confirmed=false. NEVER let structured/circulant confirmations stand in for a generic census.\nRecord in verified_scope the EXACT scope you actually checked (state the family explicitly if it is not the full class), and set claim_form.`,
          { label: `verify`, phase: PH_G, schema: VERIFY_SCHEMA, model: MODEL_MAIN }
        ).then(v => ({ ...x, v })),
  )

  const valid = outcomes.filter(Boolean)
  log(`Round ${r} — synthesizing (${valid.filter(o => !o.s.refuted && o.v.confirmed).length} survivors)`)

  // --- SYNTHESIZE (single writer: rewrites ledger.json) ---
  const synth = await agent(
    `${COMMON}\n\nYou are the LEAD. Read the current ${LEDGER}, then REWRITE it (Edit/Write) integrating this round's outcomes:\n${JSON.stringify(valid.map(o => ({ proposal: o.p, ground: o.g, skeptic: o.s, verify: o.v })), null, 2)}\n\nRules:\n- Move every refuted/failed idea to graveyard with a one-line kill reason (so it is never re-proposed).\n- Promote to "proved" ONLY claims with verify.can_enter_proved=true (NEVER empirical-only — discipline gate).\n- AUTO-SCOPING (discipline gate universal_needs_generic_census): record every claim at the SCOPE on which verify.verified_scope says it was actually checked. If a claim's only support is from ONE structured construction family (circulants / a specific construction), state it AT FAMILY SCOPE ("holds for circulant/AC factors"), NEVER as universal; a UNIVERSAL phrasing with only structured support must NOT be recorded as universal (graveyard the universal phrasing, keep the family-scoped fact). Widen a claim from family scope to universal ONLY when verify reports a clean EXHAUSTIVE GENERIC census. Tag each proved/hypothesis entry with its claim_form.\n- THREAD-KEEPER: if this round narrowed the frontier (a route closed, a barrier found, a survivor isolated), REWRITE the open_crux TEXT ITSELF so it states the current frontier — not just a note. The open_crux field must always read as the live problem, e.g. fold in "static first-moment counts are now closed; only the dynamic-concentration route survives".\n- Update live_hypotheses to reflect what moved; you MAY refine statuses and add new hypotheses with fresh H-numbers (e.g. the specific next mechanism the round pointed to).\n- Append ONE decision_log entry with the next D-number; for its date reuse the value already in the ledger's updated_at field (do not fabricate a clock).\n- Set next_action and needs_human (null unless a genuine human-decision gate was hit — quote it).\n- Set frontier_advanced HONESTLY: true ONLY if a bound improved / a new structural barrier was found / a new survivor isolated; FALSE if the round merely re-killed a variant of an already-dead family. Set recommend_handback to a quoted description of the needed human math input if (and only if) the computational frontier is exhausted on all live levers.\n- ALSO rewrite ${DIR}/docs/STATUS.md as a concise human-readable mirror of the NEW ledger: central_question, where each side of open_crux now stands, live_hypotheses with status, the last 2 decision_log notes, and needs_human/recommend_handback. Keep it under ~40 lines.\n- Preserve all prior history; only append / append-to-graveyard / rewrite-crux / refine-hypotheses. Keep the JSON valid.\nThen return the synthesis summary.`,
    { label: `synthesize`, phase: PH_S, schema: SYNTH_SCHEMA, model: MODEL_MAIN }
  )

  report.push({ round: r, proposals: proposals.length, synth })
  if (!synth.ledger_advanced) { dry++; log(`Round ${r} — DRY (${dry}/${DRY_LIMIT})`) } else dry = 0
  if (!synth.frontier_advanced) { drought++; log(`Round ${r} — no new frontier result (drought ${drought}/${DROUGHT_LIMIT})`) } else drought = 0
  log(`Round ${r} — ${synth.decision_id}: promoted=${(synth.promoted || []).length} graveyarded=${(synth.graveyarded || []).length} frontier_advanced=${synth.frontier_advanced}`)
  if (synth.needs_human) { handback = `needs_human: ${synth.needs_human}`; log(`Round ${r} — ${handback}`); break }
  if (synth.recommend_handback) { handback = `frontier exhausted: ${synth.recommend_handback}`; log(`Round ${r} — synthesis recommends handback: ${synth.recommend_handback}`); break }
  if (dry >= DRY_LIMIT) { handback = `${DRY_LIMIT} dry rounds (ledger unchanged)`; log(`Stopping: ${handback}`); break }
  if (drought >= DROUGHT_LIMIT) { handback = `${DROUGHT_LIMIT} rounds with no new frontier result (only re-killing dead families) — time for a genuinely new idea`; log(`Stopping: ${handback}`); break }
}

return {
  problem_dir: DIR,
  rounds_run: report.length,
  stopped_for: handback || 'rounds_complete',
  promotions_total: report.reduce((s, x) => s + (x.synth.promoted || []).length, 0),
  graveyarded_total: report.reduce((s, x) => s + (x.synth.graveyarded || []).length, 0),
  ledger: LEDGER,
  status_md: `${DIR}/docs/STATUS.md`,
  rounds: report,
}
