export const meta = {
  name: 'substrate-factory',
  description: 'Stage 1: triage each untried Aboulker conjecture for oracle-ability, then build + INDEPENDENTLY-VERIFY an oracle and seed a ledger for the oracle-able ones',
  whenToUse: 'Prepare problems for the research engine. Fans out over engine/aboulker_candidates.json; emits engine/manifest.json. Launch with args.root = absolute repo root (defaults to "." = cwd); runs with the repo root as cwd.',
  phases: [
    { title: 'Load', detail: 'read the candidate list' },
    { title: 'Triage', detail: 'per conjecture: is there a sound small-instance oracle?' },
    { title: 'Build', detail: 'oracle-able ones: scaffold + build oracle + seed ledger' },
    { title: 'Verify', detail: 'independent agent RUNS oracle + tests; readiness from measured facts, not self-report' },
    { title: 'Manifest', detail: 'aggregate engine/manifest.json from the verified set (content computed here, written verbatim)' },
  ],
}

// Repo root. Provided at launch (args.root, absolute) like research-attack.js's
// problem_dir; falls back to '.' since the workflow + its agents run with the
// repo root as cwd. No machine path is baked into the source.
const ROOT = (args && args.root) || '.'
const COMMON = `
You are an agent in the SUBSTRATE FACTORY that prepares open conjectures for an
autonomous research engine. Repo root = your current working directory; the
paths below resolve from it. Shared resources:
- Python: ${ROOT}/engine/.venv/bin/python (has networkx, python-sat, sympy, pytest)
- Reusable EXACT digraph-oracle lib: ${ROOT}/engine/lib/digraph_core.py
  (acyclic_number, dichromatic_number/is_k_dicolourable via SAT+lazy-cycle,
   is_triangle_free, is_oriented, geng triangle_free_graphs, all_orientations).
- nauty 'geng' is on PATH (enumerate small graphs/tournaments).
- The ledger contract: ${ROOT}/engine/LEDGER_CONTRACT.md
- A worked example (the pilot): ${ROOT}/problems/oriented_triangle_free_extremal/
  (ledger.json, scripts/{core,constructions,oracle}.py, tests/).
Never fabricate oracle output — RUN it. Your final message is consumed as DATA.`

const TRIAGE_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['arxiv', 'record', 'oracle_able', 'reason', 'proposed_slug', 'invariant', 'known_check'],
  properties: {
    arxiv: { type: 'string' }, record: { type: 'string' },
    oracle_able: { type: 'boolean', description: 'true iff there is a SOUND small-instance computation that can test/measure the conjecture (enumerable structures + exactly computable invariant). FALSE for purely asymptotic / complexity-class / extension-complexity / distributed-round claims with no finite handle.' },
    reason: { type: 'string', description: 'why oracle-able or not, concretely' },
    proposed_slug: { type: 'string', description: 'snake_case folder name under problems/' },
    invariant: { type: 'string', description: 'what the oracle would compute exactly on small instances' },
    known_check: { type: 'string', description: 'a SPECIFIC known small value from the paper the oracle must reproduce (the verification target); empty if none exists' },
  },
}
const BUILD_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['slug', 'built', 'oracle_verified', 'verified_against', 'ledger_path', 'notes'],
  properties: {
    slug: { type: 'string' },
    built: { type: 'boolean', description: 'true iff scripts/oracle.py + ledger.json were created' },
    oracle_verified: { type: 'boolean', description: 'the BUILDER\'s self-report that the oracle reproduced a known value. NOTE: this is NOT trusted for readiness — an independent Verify phase re-runs everything.' },
    verified_against: { type: 'string', description: 'the exact known value reproduced, with the command + output' },
    ledger_path: { type: 'string', description: 'path to the seeded ledger.json' },
    notes: { type: 'string' },
  },
}
// Independent verification — RAW MEASURED facts, not a self-graded readiness boolean.
const VERIFY_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['slug', 'ledger_ok', 'required_keys_ok', 'oracle_ran', 'landmark_reproduced', 'pytest_passed', 'evidence'],
  properties: {
    slug: { type: 'string' },
    ledger_ok: { type: 'boolean', description: 'ledger.json exists AND parses as valid JSON (you read + parsed it)' },
    required_keys_ok: { type: 'boolean', description: 'ledger has central_question, benchmark.oracle_cmd, benchmark.ground_truth_landmarks, decision_log' },
    oracle_ran: { type: 'boolean', description: 'the ledger\'s benchmark.oracle_cmd executed with exit code 0' },
    landmark_reproduced: { type: 'boolean', description: 'the oracle OUTPUT actually reproduced the claimed known value (you ran it and compared the numbers) — NOT asserted' },
    pytest_passed: { type: 'boolean', description: 'the problem test suite ran and ALL tests passed' },
    evidence: { type: 'string', description: 'exact commands run + their LITERAL output: the landmark value seen, the pytest summary line, any failure' },
  },
}

phase('Load')
const candidates = await agent(
  `${COMMON}\n\nRead ${ROOT}/engine/aboulker_candidates.json and return its array verbatim as {items:[...]}.`,
  { label: 'load-candidates', phase: 'Load', schema: {
    type: 'object', additionalProperties: false, required: ['items'],
    properties: { items: { type: 'array', items: { type: 'object' } } } } }
)
const items = (candidates && candidates.items) || []
log(`Loaded ${items.length} untried Aboulker conjectures`)

// pipeline: triage -> (if oracle-able) build+seed. No barrier; each flows independently.
const rows = await pipeline(
  items,
  // stage 1: triage oracle-ability
  (c) => agent(
    `${COMMON}\n\nTRIAGE this conjecture for ORACLE-ABILITY.\n${JSON.stringify(c, null, 2)}\nFetch the paper (WebFetch https://arxiv.org/abs/${c.arxiv}, or pdftotext the PDF) only as needed to judge. Decide HONESTLY: can a sound program enumerate small instances and EXACTLY compute the relevant invariant to test or measure this conjecture? Most asymptotic χ-boundedness / maderian / extension-complexity / distributed-complexity claims are NOT oracle-able — say so. Identify a SPECIFIC known small value from the paper the oracle must reproduce.`,
    { label: `triage:${c.arxiv}#${c.id}`, phase: 'Triage', schema: TRIAGE_SCHEMA }
  ),
  // stage 2: build + seed (oracle-able only). Verification happens in a separate phase.
  (t) => (!t.oracle_able)
    ? { slug: t.proposed_slug, built: false, oracle_verified: false, verified_against: '', ledger_path: '', notes: `PARKED (no oracle): ${t.reason}`, triage: t }
    : agent(
        `${COMMON}\n\nBUILD SUBSTRATE for this oracle-able conjecture:\n${JSON.stringify(t, null, 2)}\n\nSteps (model on the pilot):\n1. Scaffold ${ROOT}/problems/${t.proposed_slug}/{scripts,data,tests,docs,Refs}.\n2. Symlink the shared venv: ln -s ${ROOT}/engine/.venv ${ROOT}/problems/${t.proposed_slug}/.venv\n3. Build scripts/oracle.py (+ scripts/core.py or import ${ROOT}/engine/lib/digraph_core.py via sys.path, deriving the path from __file__ so it stays portable). Compute the invariant EXACTLY. Add a check_construction-style entrypoint + a small CLI.\n4. RUN the oracle and reproduce the known value "${t.known_check}". Set built/oracle_verified/verified_against to what actually ran (an independent agent will re-run this — do not overclaim).\n5. Add tests/ with a real pytest suite that asserts the landmark.\n6. Seed ledger.json per the contract: central_question, benchmark (incl oracle_cmd = "${ROOT}/problems/${t.proposed_slug}/.venv/bin/python scripts/oracle.py ..." and ground_truth_landmarks), proved[], open_crux, live_hypotheses[], empty graveyard[], decision_log=[D1 setup], discipline_gates (empirical≠proof, audit≠redteam, citations-verified), needs_human=null.\n7. Write a one-screen docs/STATUS.md + README.md.\nReturn the build result.`,
        { label: `build:${t.proposed_slug}`, phase: 'Build', schema: BUILD_SCHEMA }
      ).then(b => ({ ...b, triage: t })),
)

const valid = rows.filter(Boolean)

// --- Verify: an INDEPENDENT agent re-runs the oracle + tests. Readiness is
//     computed from MEASURED facts here, never from the builder's self-report. ---
phase('Verify')
const built = valid.filter(r => r.built && r.ledger_path)
const checks = (await parallel(built.map(r => () =>
  agent(
    `${COMMON}\n\nINDEPENDENTLY VERIFY this prepared problem. Do NOT trust any prior agent's claims — RUN everything yourself and report only what you actually observed.\nslug: ${r.slug}\nledger_path: ${r.ledger_path}\nbuilder's claimed known value (verified_against): ${JSON.stringify(r.verified_against)}\n\nSteps:\n1. Read the ledger at ${r.ledger_path}; confirm it parses as JSON and has keys central_question, benchmark.oracle_cmd, benchmark.ground_truth_landmarks, decision_log.\n2. Run the ledger's benchmark.oracle_cmd. Capture exit code + stdout.\n3. Confirm the output ACTUALLY reproduces the claimed known value (the landmark). Quote the matching number/string from the output.\n4. Run the test suite: (cd ${ROOT}/problems/${r.slug} && .venv/bin/python -m pytest tests/ -q). Capture the summary line.\nReturn the measured booleans + evidence (commands + literal output). Set a boolean FALSE if you could not make it pass — never paper over a failure.`,
    { label: `verify:${r.slug}`, phase: 'Verify', schema: VERIFY_SCHEMA }
  ).then(v => ({ ...(v || {}), slug: r.slug }))
))).filter(Boolean)

const measured = {}
for (const c of checks) measured[c.slug] = c
const isReady = (r) => {
  const c = measured[r.slug]
  return !!(r.built && r.ledger_path && c &&
    c.ledger_ok && c.required_keys_ok && c.oracle_ran && c.landmark_reproduced && c.pytest_passed)
}
const ready = valid.filter(isReady)
const parked = valid.filter(r => !isReady(r))
const parkReason = (r) => {
  if (!(r.built && r.ledger_path)) return r.notes        // builder parked (no oracle)
  const c = measured[r.slug]
  if (!c) return 'VERIFY FAILED: verifier agent returned no result'
  if (!c.ledger_ok) return 'VERIFY FAILED: ledger.json missing or invalid JSON'
  if (!c.required_keys_ok) return 'VERIFY FAILED: ledger missing required keys'
  if (!c.oracle_ran) return 'VERIFY FAILED: oracle_cmd did not run (exit != 0)'
  if (!c.landmark_reproduced) return 'VERIFY FAILED: oracle did not reproduce the claimed landmark'
  if (!c.pytest_passed) return 'VERIFY FAILED: test suite did not pass'
  return r.notes
}
log(`Substrate: ${ready.length} engine-ready (independently verified), ${parked.length} parked`)

// --- Manifest: content computed HERE in JS from the verified set, then written
//     VERBATIM by an agent (it cannot re-derive or drift). Paths are repo-relative. ---
phase('Manifest')
const manifest = {
  generated_from: 'engine/aboulker_candidates.json',
  engine_ready: ready.map(r => ({
    slug: r.slug,
    arxiv: r.triage && r.triage.arxiv,
    record: r.triage && r.triage.record,
    oracle_able: r.triage && r.triage.oracle_able,
    built: r.built,
    oracle_verified: true,                       // independently re-verified in the Verify phase
    verified_against: r.verified_against,
    verify_evidence: (measured[r.slug] || {}).evidence || '',
    ledger_path: `problems/${r.slug}/ledger.json`,
    notes: r.notes,
  })),
  parked: parked.map(r => ({
    slug: r.slug,
    arxiv: r.triage && r.triage.arxiv,
    record: r.triage && r.triage.record,
    oracle_able: r.triage && r.triage.oracle_able,
    built: r.built,
    oracle_verified: false,
    verified_against: r.verified_against,
    ledger_path: r.ledger_path ? `problems/${r.slug}/ledger.json` : '',
    notes: parkReason(r),
  })),
}
const manifestJSON = JSON.stringify(manifest, null, 2)
await agent(
  `${COMMON}\n\nWrite the EXACT bytes between the markers below to ${ROOT}/engine/manifest.json — do not reformat, re-derive, add, or remove anything. Then read it back and confirm it is byte-identical, and return the one-line summary "wrote ${manifest.engine_ready.length} engine_ready, ${manifest.parked.length} parked".\n\n<<<MANIFEST_JSON\n${manifestJSON}\nMANIFEST_JSON`,
  { label: 'write-manifest', phase: 'Manifest' }
)

return {
  total: items.length,
  engine_ready: ready.map(r => ({ slug: r.slug, arxiv: r.triage && r.triage.arxiv, verified: r.verified_against, ledger: `problems/${r.slug}/ledger.json` })),
  parked: parked.map(r => ({ slug: r.slug, arxiv: r.triage && r.triage.arxiv, notes: parkReason(r) })),
  manifest: 'engine/manifest.json',
}
