# HPC / Reproducibility Memo for the Albertson Programme

Author: Role 6 (HPC / scientific software engineer)
Date: 2026-05-16
Plan reference: `docs/plan.md` v3 (2026-05-16)
Audience: the 9-person team; primary handoffs are to Roles 3, 4, 5, 9.

This memo answers the question every external referee will ask in 2031:
"Show me the bit-for-bit replay." Nothing in plan v3 is a theorem until
it survives that question. Plan v3 already killed several invalid
discard rules (F1b, F4, P3); the compute layer must not reintroduce
them.

---

## 1. Workload inventory

Each row maps a plan-v3 subtask (C1-C7, R1a-R1c, R2, R5) to solver
stack, scale, and parallelism model. "TBD-by-R4" means Role 4's
prototype is the blocker.

### 1.1 C1 - `cranston_residual.py` (residual spec)
- Plan: docs/plan.md C1, step 1 of the numbered plan.
- Solver: none (pure arithmetic + graph6 generator scaffold).
- Per-item runtime: seconds.
- Items: 3 (the three Cranston-residual triples).
- Peak RAM: < 1 GB.
- Parallelism: serial; this is a literature deliverable.
- Total CPU-hours: < 1.

### 1.2 C2 - SAT-encoded critical-graph search
- Plan: C2, R1a, steps 3, 5-6.
- Solvers (portfolio, Section 5): CaDiCaL, Kissat, Glucose,
  CryptoMiniSat; PySAT front-end.
- Per-item runtime: TBD-by-R4. CR-SAT at n~50, m~600 is beyond the
  Chimani-Mutzel published frontier (their benchmarks are an order of
  magnitude smaller). Realistic per-(kernel x solver) wall is 24-168 h
  with many TIMEOUTs.
- Items: 10^3-10^5 R1b sub-cases per Cranston triple, times >=3
  portfolio members.
- Peak RAM/worker: 8-32 GB (CDCL on ~10^6-clause instances; CEGAR
  with OGDF lemmas can push higher).
- Parallelism: embarrassingly parallel across (kernel, solver, seed);
  CEGAR refinement is sequential within an instance.
- Total CPU-hours: TBD-by-R4; plausible floor 10^4-10^5 per triple.

### 1.3 C3 - heuristic upper + certified lower crossing bounds
- Plan: C3, R1c. Owner: Role 3.
- Solvers: OGDF (upper), Buchheim-Chimani ILP via Gurobi/SCIP
  (lower), Chimani-Mutzel SAT (alternative lower).
- Per-item runtime: ILP at n=48, m~600 is research-grade (plan flags
  this as "at or beyond the current state of the art"). Per-graph
  budget 1-72 h; many will not close the gap.
- Items: 10^3-10^5 candidates per triple (R1b kernel x completion, or
  R1c sampling).
- Peak RAM/worker: 16-64 GB (Gurobi cut pool at 600 edges).
- Parallelism: embarrassingly parallel across candidates; in-solver
  threading useful to ~8 cores. Recommend 1 ILP per 8-core slot.
- Total CPU-hours: TBD-by-R3; plausible 10^4-10^6 per triple.

### 1.4 C4 - empirical Crossing Lemma sweep (Route R2)
- Solver: exact CR on t-critical graphs, t <= 20 (C3 stack, smaller).
- Items: O(10^3). Per-item minutes to hours. Peak RAM 4-16 GB.
- Total CPU-hours: 10^3-10^4. Owner: Role 3.

### 1.5 C5 - Mycielski / Kneser heuristic sweep
- Solver: OGDF heuristic; ILP on small members. Items O(10^2).
- Peak RAM 2-8 GB. Total CPU-hours: 10^2-10^3. Owner: Role 8.

### 1.6 C6 - cr(K_t) bounds bookkeeping
- Pure literature extraction + Python script. < 10 CPU-h. Owner: 1.

### 1.7 C7 - immersion-witness search
- Solver: ILP (edge-disjoint path packing) or bespoke flow code.
- Items O(10^2-10^3); per-item hours; RAM 8-32 GB.
- Parallelism: embarrassingly parallel. CPU-hours: 10^3-10^4.

### 1.8 SDP finite-L(t) extraction (highest leverage)
- Plan: F1b, C6, and the v3 transparency note. No finite certified
  L(25), L(26) currently exists.
- Solver: SDPA-GMP (extended precision) and/or MOSEK on the
  Balogh-Lidicky-Salazar flag-algebra ancillary files.
- 2 instances; days each; RAM 64-256 GB; MPI within an instance.
- Total CPU-hours: 10^3-10^4. Owner: Role 9.
- **Single highest-leverage compute job in the plan.** Without
  finite L(t), Albertson falsification at R1c/C3/P3 is operationally
  undefined - only strong-form (Z(t)) falsification is testable.
  See Section 8.

### 1.9 R2 / R5 - pen-and-paper plus light numerics
- SymPy/NumPy. < 100 CPU-h.

### Workload summary

| Job  | Plan ref | Solver class    | Scale            | Honest CPU-h    | Owner role |
|------|----------|-----------------|------------------|-----------------|------------|
| C1   | C1       | none            | 3 items          | < 1             | 2          |
| C2   | C2, R1a  | SAT portfolio   | 10^3-10^5 items  | 10^4-10^6 TBD   | 4          |
| C3   | C3, R1c  | ILP + SAT       | 10^3-10^5 items  | 10^4-10^6 TBD   | 3          |
| C4   | C4, R2   | ILP + SAT       | 10^3 items       | 10^3-10^4       | 3          |
| C5   | C5, P2   | OGDF heuristic  | 10^2 items       | 10^2-10^3       | 8          |
| C6   | C6, F1b  | none            | 1 table          | < 10            | 1          |
| C7   | C7, R5   | ILP (flow)      | 10^2-10^3 items  | 10^3-10^4       | 7          |
| SDP  | F1b, C6  | SDP (high prec) | 2 instances      | 10^3-10^4       | 9          |
| R2/5 | step 8   | symbolic        | n/a              | < 100           | 1          |

Aggregate Track A (R1 + C1 + C3 + P1) realistic 12-month budget:
**5 x 10^5 to 2 x 10^6 core-hours**, dominated by C3 ILP and C2 SAT.

---

## 2. Cluster sizing

Three scenarios. The asymmetry is between "closes the K_{24}-extension
sub-family at (25, 48)" and "closes (25, 48) outright."

### (a) Single beefy node, 256-512 cores
- Capacity ~1.6-3.2 M core-hours/year at 0.7 utilisation.
- 12-month achievable: C1, C4, C5, C6, the 1.8 SDP run, part of C7.
  One Cranston triple in one structural restriction with one
  portfolio solver, inconclusive.
- Verdict: R2/R3 structural papers + P2 empirics. **Insufficient
  for any R1a verdict on the three Cranston pairs.**

### (b) University cluster, ~2000-4000 cores
- Capacity ~1.75 x 10^7 core-hours/year at 0.5 utilisation. Realistic
  effective: 30-50% of nominal allocation per project.
- 12-month achievable: all jobs 1.1-1.8; R1a+R1c on all three
  triples with full portfolio; R1b sub-families exhausted.
- This is the **target scenario for the plan as written**.

### (c) HPC partnership, 10k+ cores
- Capacity > 5 x 10^7 core-hours/year.
- 12-month: full portfolio + multi-seed ablations + R1c at
  non-restricted scale.
- Required only if R1a hits the bad case where most kernels TIMEOUT
  at 168 h and verdict-by-exhaustion needs 10x oversampling.
- **A positive R1a proof of Albertson at t=25, 26 in 12 months
  almost certainly needs (c)** if "positive proof" means closing
  every Cranston-residual graph, not just a structural sub-family.

### Cost
At cloud-spot equivalent $0.05-0.10/core-h and 1.5 M core-hours for
Track A: **$75k-150k at list price**. **The full Track A budget
plausibly exceeds $100k of cluster time at scenario (b) cloud-
equivalent pricing - this must be in the grant.** If the team
cannot secure (b) for 12 months, the headline claim must downscale
to "Albertson on the K_{24}-extension sub-family at (25, 48)."

---

## 3. Artifact storage and provenance

The 5-year-replay test is the spine. Anything that cannot be replayed
bit-for-bit in 2031 from a tagged commit + container image + hash-
pinned input is not theorem-grade.

### 3.1 Artifact classes

| Class | Plan ref | Per-item size | Item count | Total | Retention |
|-------|----------|---------------|------------|-------|-----------|
| graph6 catalogues (R1b kernels, R1c samples) | R1b, R1c, C2 | 100 B - 10 KB | 10^6-10^8 | 10-1000 GB | permanent |
| SAT instance files (DIMACS, after CEGAR refinement) | C2 | 10 MB - 1 GB | 10^4-10^5 | 1-100 TB | permanent for closed instances; 1-year for timed-out |
| SAT proof logs (DRAT / LRAT) | C2 | 100 MB - 100 GB | 10^3-10^4 | 10-1000 TB | **permanent for any instance backing a published claim** |
| ILP solution + dual/cut logs | C3, C4, C7 | 10 MB - 10 GB | 10^4-10^5 | 1-100 TB | permanent for closed instances |
| Heuristic crossing-number drawings (OGDF) | C3, C5 | 10-100 KB | 10^5 | 10 GB | permanent (cheap) |
| SDP certificates (rational reconstruction) | 1.8 | 10 MB - 10 GB | O(10) | 10-100 GB | permanent |
| Run metadata (JSON: solver version, seed, wall) | all | 1-10 KB | one per worker invocation | 10 GB | permanent |

### 3.2 Hashing scheme
- Every artifact is named by SHA-256 of canonicalised content. graph6
  canonicalised via `nauty shortg`; DIMACS by sorted-clause +
  sorted-literal form; drawings by OGDF binary serialiser with
  canonical graph6 vertex order.
- Two-level layout `objects/aa/bbcc...` (git/IPFS convention).
- Metadata records carry: input hashes, output hash, solver
  name+version+commit, container digest, seed, wall, exit code,
  hostname, plan-version tag.

### 3.3 Provenance graph
Per-job append-only `provenance.jsonl`, one line per worker invocation,
recording (input_hashes, code_commit, container_digest, output_hash).
Mirrored cluster scratch + cold storage (Section 7 R3, R4).

### 3.4 Re-verifying a claim in 2031
1. Check out the tagged git commit from the published claim.
2. Pull container by digest (not tag) from the long-term registry mirror.
3. Resolve input hash to file via the content-addressable store.
4. Run the published replay script with published seed.
5. Compare output hash against the claimed value.
6. **Third-party check**: re-verify DRAT/LRAT with `drat-trim` AND
   `cake_lpr`; re-verify VIPR with the independent VIPR checker; for
   SDP re-check rational certificate. Steps 1-5 are bit-exact; step 6
   is what confers theorem status (Section 5).

---

## 4. Checkpointing and resumption

Each solver class has a different story; no uniform policy.

### 4.1 SAT (C2, R1a)
- **Inside a single invocation:** CaDiCaL/Kissat have no native
  mid-search checkpoint. Cap wall at the queue maximum (24-168 h);
  on timeout dump learnt-clauses for warm-start.
- **Across invocations:** every SAT call is idempotent, named by
  (instance-hash, solver+version, seed). Killed workers just retry.
- **CEGAR loop (C2):** persist the blocking-clause set as a DIMACS
  prefix between rounds. **This is the critical checkpoint**:
  losing 50 hours of refinement to a node failure is unacceptable.
- **Proof log retention:** DRAT/LRAT goes to the content store
  *before* solver exit. No DRAT, no closure.

### 4.2 ILP (C3, C4, C7)
- **Single solver:** Gurobi (MIP-start, node-file dumps), SCIP
  (`restart.dat`). Checkpoint hourly.
- **Across invocations:** persist (incumbent, dual_bound, cut_pool,
  node_file) and re-load. Cut-pool persistence matters most for the
  Buchheim-Chimani separation.
- **Hard rule:** any non-closed ILP exit must emit
  `(best_primal, best_dual, gap, certificate_status="partial")`.
  Records without explicit `certificate_status` are treated as if the
  run never happened (F4 operationalised).

### 4.3 SDP (1.8)
- SDPA-GMP checkpoints to `paramfile` per iteration. Bound swap and
  let OOM-kill trigger restart from the latest checkpoint.

### 4.4 OGDF + enumeration
- OGDF heuristic: stateless, re-run on failure. nauty/shortg/geng:
  chunk by canonical prefix, checkpoint at chunk boundary (standard
  nauty pattern).

---

## 5. Solver portfolios

For each problem class, three or more solvers, with explicit notes on
whether the solver's output can be checked by a third party. **A
solver whose proof log cannot be re-verified by an independent tool is
not theorem-grade.** This is the criterion that separates
"computational evidence" from "computer-assisted proof."

### 5.1 SAT (C2, R1a)
- **CaDiCaL** (Biere, MIT). Open-source, emits DRAT.
  **Theorem-grade** via `drat-trim` + `cake_lpr` (CakeML-verified).
  Reference solver.
- **Kissat** (Biere, MIT). Open-source, DRAT. Theorem-grade.
- **Glucose** (Audemard-Simon, MIT). Open-source, DRAT. Theorem-grade.
- **CryptoMiniSat** (Soos, MIT). DRAT for non-XOR; flag XOR usage
  in metadata.
- **MapleSAT** for additional diversity.
- **Recommendation:** CaDiCaL + Kissat + Glucose + CryptoMiniSat in
  parallel; first UNSAT wins; verify with `drat-trim` then
  `cake_lpr`. Theorem-grade only after `cake_lpr`.

### 5.2 ILP / MIP (C3, C4, C7)
- **Gurobi** (commercial). Strongest on Buchheim-Chimani CR-ILPs but
  **dual proof not third-party-checkable**. Evidence, not theorem.
- **SCIP** (ZIB Academic, source-available). Emits VIPR certificates
  (Cook-Koch-Steffy-Wolter 2014), checkable by an independent
  open-source verifier. **Theorem-grade**. Reference MIP solver.
- **HiGHS** (Apache 2.0). No VIPR yet; useful for LP-bound cross-
  checks and portfolio diversity.
- **CPLEX** (commercial). Diversity only; not theorem-grade.
- **Recommendation:** Gurobi + SCIP + HiGHS. Every closure claim
  needs a SCIP/VIPR certificate; Gurobi-only = evidence.
- **Honest caveat:** Buchheim-Chimani has exponentially many lazily
  separated constraints; VIPR certification at n=48 is **at or
  beyond current state of the art** (certificate size may itself be
  prohibitive). Expect SCIP/VIPR only on the closing arguments,
  Gurobi driving the search.

### 5.3 SDP (1.8)
- **SDPA-GMP** (open-source, extended-precision). Rational
  certificates. **Theorem-grade** via rational reconstruction +
  symbolic Cholesky.
- **MOSEK** (commercial, floating-point). Fastest production SDP;
  not theorem-grade alone.
- **CSDP** (open-source). Older, well-tested. Diversity.
- **Recommendation:** MOSEK finds the certificate, SDPA-GMP
  rationalises, third-party rational verifier closes. Standard
  flag-algebra workflow.

### 5.4 Heuristic CR upper bounds
- **OGDF planarisation** (GPL), **Sage** (GPL), bespoke Python.
  Drawings self-certify the upper bound (just count crossings).
  Trivially theorem-grade for upper bounds; **never theorem-grade
  for lower bounds** (F4). This is the invariant that keeps R1c
  honest.

### 5.5 Combined verdict
SAT, SDP, and heuristic upper bounds are theorem-grade with open-
source tooling. Only ILP/MIP forces compromise: SCIP+VIPR will not
scale cleanly to n=48, so the realistic published form will be
"Gurobi-closed; SCIP/VIPR-certified on the reduced post-preprocessing
instance." See the report-back.

---

## 6. Reproducibility contract

Every published numerical claim from this team must come with a
five-tuple `(commit, image, input_hash, output_hash, replay)`.
Without all five, the claim is not a theorem. The template below
goes in the supplementary materials of every paper, and a
machine-readable copy goes into `claims/<claim_id>.json` in the
repository.

### 6.1 Template

```
Claim ID: ALB-<plan-section>-<seq>
Plan reference: docs/plan.md v3, section <X>
Statement (informal): <one sentence>
Statement (formal): <inequality or set membership>

Reproducibility tuple:
1. Code commit: <40-char SHA, git tag>
   Repository: <URL + mirror URL>
2. Container image: <registry/image@sha256:digest>
   Build provenance: <SLSA attestation hash or Dockerfile hash>
3. Input artifact: <SHA-256 of canonicalised input>
   Stored at: objects/<aa>/<bbcc...> (mirrored to <URL1>, <URL2>)
4. Output artifact: <SHA-256 of output bundle>
   Contains: { proof-log, metadata.json, certificate.<ext> }
5. Replay script: scripts/replay/<claim_id>.sh
   Expected wall time: <h>
   Expected peak RAM: <GB>
   Expected exit code: 0
   Expected output hash: <SHA-256, must match item 4>

Third-party verifier:
- Tool: <drat-trim | cake_lpr | VIPR checker | rational-SDP>
- Version: <git tag>
- Expected verdict: VERIFIED

Theorem-grade: YES if and only if the third-party verifier ran
and emitted VERIFIED. Otherwise: COMPUTATIONAL EVIDENCE.
```

### 6.2 Enforcement
- Pre-publication hook: the manuscript LaTeX build refuses to
  compile if any `\claim{ALB-...}` macro references a `claim_id`
  whose JSON does not validate against the template schema and
  whose `theorem-grade` field is not `YES`.
- CI on the main branch re-runs the replay scripts for the
  cheapest-tier claims (< 1 core-h) on every PR. Mid-tier claims
  (1-1000 core-h) re-run nightly. Heavy claims (> 1000 core-h)
  re-run on demand and on every container image rebuild.

### 6.3 What is NOT acceptable
- "We ran the solver and it returned UNSAT." (no DRAT, no
  container, no replay.)
- "Gurobi closed the instance." (no third-party-checkable
  certificate; this is evidence not theorem.)
- "The heuristic upper bound was 4290." (F4: heuristic upper
  bounds do not eliminate.)
- "0.985 * Z(25) = 4290.66." (F1b: asymptotic constant applied
  as finite threshold; plan v3 already removed this misuse, the
  contract enforces that it does not creep back.)

---

## 7. Risks

Numbered, with mitigations. Each is anchored to a plan-v3 failure
mode (F1-F7) or to a known compute hazard.

1. **Silent solver bugs.** CaDiCaL/Kissat have shipped wrong-UNSAT
   bugs; Gurobi has shipped wrong-dual bugs; SDP solvers can be
   numerically unstable. **Mitigation:** portfolio + third-party
   proof checker (Section 5). Any UNSAT/closure not corroborated by
   a second-lineage solver AND a third-party checker is logged
   `UNCORROBORATED` and excluded from theorem claims.
2. **Container drift.** Same Dockerfile in 2027 produces a different
   image: apt mirrors rotate, pip yanks versions, base tags re-point.
   **Mitigation:** pin by digest not tag, every layer. Mirror the
   registry to two locations. Reproducible build (Nix / Bazel) for
   solver layers; archive build inputs alongside the digest.
3. **Long-term store rot.** Cluster scratch purges in 90 days; lab
   NAS dies in 2028; university object store is decommissioned.
   **Mitigation:** three-copy rule. Cluster scratch (working) + lab
   NAS (warm) + public permanent archive (Zenodo data + Software
   Heritage code). Every published claim's hashes resolve in all three.
4. **Provenance file corruption.** One bad `provenance.jsonl` line
   silently invalidates downstream claims. **Mitigation:** line-by-
   line hash-chain (SHA-256 of (prev + cur)) - a poor man's Merkle
   log. Periodic cross-mirror reconciliation.
5. **Closed-source solver lock-in.** Gurobi/MOSEK/CPLEX license terms
   change; in 2030 we cannot rebuild the Gurobi version that produced
   a 2026 closure. **Mitigation:** every Gurobi closure has a
   SCIP/VIPR cross-check as a deliverable. Gurobi is a search
   accelerator, not a proof oracle.
6. **F1b creep.** A team member uses `0.985 * Z(t)` as a finite
   threshold because it is the most recent number they read.
   **Mitigation:** lint `scripts/` for literal `0.985`, `0.98559895`,
   `0.83` not inside an `asymptotic_only` named constant. Contract
   (Section 6.3) restates the rule.
7. **F4 creep.** R1c emits 10^5 candidates; the natural reaction is
   to discard large heuristic upper bounds. Plan v3 forbids this.
   **Mitigation:** "candidate discarded" schema requires a
   `lower_bound_certificate` field. Records without one fail
   validation. Contract enforces at publication.
8. **Queue-policy change.** Cluster wall drops from 168 h to 24 h,
   killing in-flight SAT jobs. **Mitigation:** CEGAR checkpoint
   (Section 4.1) is designed so a 168-h job replays as seven 24-h
   jobs with no loss. End-to-end test in first 30 days.
9. **Silent bit-flip at 10^6 core-hours.** A flipped bit in a CDCL
   learnt-clause can produce false UNSAT. **Mitigation:** third-party
   DRAT verification (Section 5.1). No DRAT, no UNSAT claim.
10. **Bad input graphs.** R1b/R1c emits a graph claimed 25-critical
    that is actually 24-critical; the SAT closure is trivially
    vacuous. **Mitigation:** every input independently verified
    (delta >= t-1, chi >= t via an independent chromatic check,
    edge-connectivity via independent max-flow). Verification is
    itself a tracked artifact with its own reproducibility tuple.

---

## 8. Dependencies on other roles

Specific asks, not vague coordination.

### Role 3 (exact crossing)
- **Deliver** by month 4: a working OGDF + Gurobi + SCIP pipeline
  for the Buchheim-Chimani ILP producing VIPR certificates on at
  least one n=48 instance. Load-bearing for Sections 1.3 and 5.2.
- **Decide:** which formulation (Buchheim-Chimani ILP vs
  Chimani-Mutzel SAT) we standardise on.
- **Provide:** per-instance memory profile to right-size worker slots.

### Role 4 (SAT/CEGAR)
- **Deliver** by month 3: a CaDiCaL + DRAT pipeline for C2 on at
  least one R1b sub-case of (25, 48).
- **Decide:** the CEGAR refinement protocol (blocking-clause
  injection, OGDF lemma integration). Determines Section 4.1
  checkpoint format.
- **Provide:** an honest single-instance wall-time estimate. Section
  1.2 is TBD-by-R4 and Section 2 sizing hinges on it.

### Role 5 (enumeration)
- **Deliver** by month 2: R1b kernel generator (graphs with a fixed
  K_{24} subgraph at a fixed position) emitting canonical graph6,
  hash-named.
- **Provide:** count estimates per R1b restriction to budget C2/C3
  input volume.

### Role 9 (SDP)
- **Deliver:** a finite certified lower bound L(25), L(26) on
  cr(K_25), cr(K_26) extracted from the Balogh-Lidicky-Salazar
  flag-algebra ancillary computations - or a definite verdict that
  no such extraction is feasible.
- **The single highest-leverage deliverable in the programme**
  (Section 1.8). Without it, Albertson falsification at finite t is
  operationally undefined: R1c/C3/P3 can only test the strong form.
- **Decide:** SDPA-GMP vs MOSEK + rational reconstruction.
  Determines container image content.

---

## 9. First 30-day deliverables

Concrete, finishable, no TBDs.

1. **Reproducibility contract template** (Section 6) at
   `work/06_hpc/contract_template.md` plus `claims/schema.json`.
   Month-1 floor: template exists and Roles 1-9 have adopted it.
   CI integration is a stretch goal.
2. **Content-addressable artifact store skeleton**: directory
   layout, three-mirror config (cluster scratch + lab NAS + Zenodo),
   `objects/aa/bbcc...` reader/writer, `provenance.jsonl` hash-
   chain. End-to-end round-trip test on a dummy artifact.
3. **Container baseline image**: digest-pinned, contains CaDiCaL,
   Kissat, Glucose, CryptoMiniSat, SCIP, HiGHS, OGDF, Sage,
   SDPA-GMP, drat-trim, cake_lpr, VIPR checker. Reproducibly built
   under Nix. Digest committed.
4. **CEGAR checkpoint end-to-end test** (Risk 8 mitigation): run a
   tiny SAT/CEGAR instance 60 min, kill at 30, restart from
   checkpoint, verify identical final state. Proves Section 4.1
   policy before we trust it at scale.
5. **L(t) extraction blocker formally filed with Role 9** (Section
   8). Without a Role-9 verdict on finite L(25), L(26) extraction
   within 6 months, the falsification half of Track A cannot be
   planned. Coordination deliverable, on the 30-day critical path.

End of memo.
