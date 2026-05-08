# Plan: Literature review of OPG problems via Claude

For each of the 227 problems in `data/problems.json`, ask Claude to assess its current status (still open / solved / disproved / partial / unclear), with cited evidence. Output is added to the static site as a per-problem "Status" section and an index-level filter.

## 1. Output schema (per problem)

```json
{
  "slug": "seagull_problem",
  "reviewed_at": "2026-05-07",
  "model": "claude-sonnet-4-6",
  "search_enabled": true,
  "status": "open",                          // open | solved | disproved | partial | unclear
  "confidence": "high",                      // high | medium | low
  "summary": "Still open as of 2024. Best partial results: …",
  "since_posted": [                          // results published AFTER OPG posting date
    {
      "title": "On the seagull problem and Hadwiger's conjecture",
      "authors": "Author A, Author B",
      "year": 2019,
      "venue": "J. Combin. Theory Ser. B",
      "url": "https://arxiv.org/abs/1907.12345",
      "doi": "10.1016/j.jctb.2019.…",
      "kind": "partial",                     // proof | counterexample | partial | survey | reduction
      "claim": "Proves the conjecture for graphs of bounded treewidth."
    }
  ],
  "search_queries": ["..."],
  "notes": "..."                             // caveats, open follow-ups, things Claude is unsure about
}
```

The schema is the contract. It is what `build.py` consumes and what we validate.

## 2. Architecture

```
data/problems.json
        │
        ▼
scraper/review.py ── (per slug) ──► Claude API
        │             system prompt (cached)
        │             user prompt = problem record
        │             tools: [web_search, web_fetch]
        │
        ▼
data/reviews/<slug>.json   (one file per problem; idempotent)
        │
        ▼
data/reviews.json          (aggregated)
        │
        ▼
scraper/build.py           (already exists; adds a Status section + index column)
```

Per-slug cache makes the run resumable, lets us re-review only stale entries (`--max-age 180d`), and lets us iterate the prompt without re-paying for unchanged problems.

## 3. Prompt strategy

- **System prompt (~1.5 K tokens)**, passed via `--append-system-prompt`: role (mathematical literature reviewer), task definition, output schema, citation standards (arXiv ID or DOI required for any post-OPG-posting claim, no fabrication, mark uncertainty with `confidence: low`), domain glossary, what to do when web search yields nothing useful (return `status: unclear`, not a guess).
- **User prompt (per problem, ~1 K tokens)**: title, statement(s) — both LaTeX and rendered text — authors, posted date (Claude should treat that as the "since when" anchor), keywords, OPG bibliography (the references we already extracted — *these are the starting point for backward search*), canonical URL.
- **Tool use**: `WebSearch` is the workhorse (arXiv, journal pages, MathSciNet abstracts, ResearchGate). `WebFetch` for following promising hits. Tools restricted via `--allowed-tools "WebSearch WebFetch"` so the agent can't write files or run shell commands. Cap at ~6 search calls per problem to bound runtime.
- **Prompt caching** is automatic on the Anthropic backend: identical `--append-system-prompt` text across the run is served from the prompt cache. No explicit cache-control plumbing needed.

## 4. Model & authentication

Authenticate via the **Max plan** through Claude Code's non-interactive mode (`claude -p`) — no API key, no per-token billing.

- **Invocation**: `claude -p "<user prompt>" --append-system-prompt "<system>" --allowed-tools "WebSearch WebFetch" --output-format json --model claude-sonnet-4-6`. The Python orchestrator (`scraper/review.py`) builds the prompts and shells out per problem.
- **Default model: Sonnet 4.6**. Strong on synthesis, web tool use, JSON; the right cost/quality point for routine reviews.
- **Escalate to Opus 4.7** (`--model claude-opus-4-7`) for: (a) any pilot problem whose output is messy, (b) the ~20–30 problems Sonnet returns as `confidence: low` or `status: unclear`. A small second pass.
- **Output parsing**: `--output-format json` returns the full session as JSON; we extract the assistant's final message and parse the embedded review JSON.

## 5. Throughput & rate limits

Max plan rate limits apply per 5-hour rolling window — the exact ceiling depends on your tier. For 227 problems:

- **Concurrency**: 1–2 parallel calls only (don't burn the window with simultaneous bursts).
- **Resume on rate-limit**: `review.py` catches `claude -p`'s rate-limit error, sleeps until the window reset is reported, continues. Per-slug JSON cache makes restart cheap and idempotent.
- **Pacing knob**: `--rpm` flag in the orchestrator (default ≤ 12 req/min) so the run self-throttles even before hitting a hard limit.
- **Realistic wall clock**: 1 day at safe pacing on Max 5×; well under that on higher tiers. The full run does not need to finish in one sitting.

No per-token cost. The only "cost" is the share of the 5-hour Max window consumed.

## 6. Quality safeguards

- **Schema validation**: every output goes through `jsonschema`. Anything malformed is retried once with a stricter reminder, then logged for manual review.
- **Hallucination spot-check**: pick a random 10% of `since_posted` entries and verify the URL resolves and the title matches. If the rate of bad cites > 5%, switch to mandatory `web_fetch` verification (doubles cost).
- **Confidence floor**: any review where Claude cites zero post-posting papers and the OPG posting date is > 10 years old gets re-run with Opus.
- **Mandatory diff log**: each review records the exact search queries and tool calls. Re-running on the same problem must produce a comparable trace (we can `git diff` the JSONs).
- **Disagreement check** (optional, +50% cost): for ~20 randomly selected `solved` / `disproved` outputs, run a second independent Sonnet review and flag any disagreement.

## 7. Integration with the site

- `build.py` reads `data/reviews.json` if present and decorates each problem record with `_review`.
- New section on `templates/problem.html` titled **"Status (literature review)"** with a coloured badge (`open` grey, `partial` orange, `solved`/`disproved` green/red, `unclear` muted), summary, and a list of `since_posted` references with deep links.
- New column on `templates/index.html` showing the status badge; new filter chip ("show only open").
- `templates/about.html` gains a paragraph explaining the auto-review is advisory and lists model + date.

## 8. Phasing

1. **Pilot (10 problems)** — pick a deliberate mix: 3 famous (`seagull_problem`, `the_erdos_hajnal_conjecture`, `reconstruction_conjecture`), 3 obscure, 3 known-recently-solved (e.g. `erdos_faber_lovasz_conjecture` — proved in 2021, expect `status: solved`), 1 with no bibliography. Inspect every output by hand. Iterate the prompt until the schema and tone are right.
2. **Full run (217 remaining)** — `review.py --concurrency 4`. Saves per-slug JSON; resumable. Logs everything.
3. **Validation pass** — spot-check 10% manually; re-run any flagged outputs through Opus.
4. **Site integration** — extend `build.py` + templates + CSS. One commit.
5. **Refresh cadence** — quarterly cron (or just rerun before each site rebuild). `--max-age 90d` skips fresh entries.

## 9. Decisions

1. **Max plan tier**: Max 20× — supports higher concurrency (still cap at 2–3 parallel for politeness).
2. **Web search**: enabled.
3. **Hallucination tolerance**: **mandatory** — every cited reference must be verified by `WebFetch` before it is allowed in the output. This roughly doubles the per-problem turn count but eliminates fabricated citations.
4. **Status taxonomy**: the five buckets `open / solved / disproved / partial / unclear` are confirmed.
5. **Restart cadence**: run may span multiple sittings, resuming on rate-limit errors. Per-slug JSON cache is the resume key.

## 10. First concrete step

Once §9 is answered: write `scraper/review.py` (Python orchestrator that shells out to `claude -p` per problem, with `--allowed-tools "WebSearch WebFetch"` and `--output-format json`), run on one problem, eyeball the parsed JSON, then expand to the 10-problem pilot before the full 227-problem run.
