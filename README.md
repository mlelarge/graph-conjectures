# graph-conjectures

A browseable, status-annotated mirror of the **graph-theory category** of
[openproblemgarden.org](http://www.openproblemgarden.org/category/graph_theory),
with an automated **literature-review pass** classifying each problem as
`open`, `partial`, `solved`, `disproved`, or `unclear` — every cited paper
verified by `WebFetch` before inclusion.

**Coverage as of last build: 227 / 227 problems (100%)**.

| status    | count | meaning                                                                     |
|-----------|-----:|-----------------------------------------------------------------------------|
| partial   |  137 | progress since posting (special cases, weakened versions, asymptotic)       |
| open      |   57 | no significant progress found in literature search                          |
| solved    |   19 | proved since posting                                                        |
| disproved |   13 | counterexample found since posting                                          |
| unclear   |    1 | insufficient information to decide                                          |

Confidence: 151 high · 68 medium · 8 low. **459 verified citations** in total
(avg 2.0 per problem, max 8).

The output site is inspired by
[erdosproblems.com](https://www.erdosproblems.com/), which itself is an
excellent companion source.

## Quick start

```bash
# 1) install deps (uv recommended)
uv venv
uv pip install -r scraper/requirements.txt

# 2) the data is already in data/; render the static site
.venv/bin/python scraper/build.py
python -m http.server --directory site 8000
# open http://localhost:8000
```

To regenerate from scratch, the pipeline runs in this order:

```bash
# Crawl OPG (idempotent, caches HTML; honours robots.txt 10s crawl-delay)
.venv/bin/python scraper/crawl.py

# Parse cached HTML into per-slug JSON
.venv/bin/python scraper/parse.py

# Build the erdosproblems.com cross-reference index
.venv/bin/python scraper/erdos_index.py
.venv/bin/python scraper/intersect.py

# (Optional) literature-review pass — see scripts/ for the parallel-worker layout
python scripts/partition.py --workers 8
# then in 8 terminals: PER_SLUG_TIMEOUT=900 WORKER=NN bash scripts/run_worker.sh

# Render
.venv/bin/python scraper/build.py
```

## Architecture

```
crawl.py     →  cache/op/<slug>.html       (raw OPG pages, 12s/req polite crawl)
parse.py     →  data/problems.json         (selectors documented in PLAN.md §A)
erdos_index  →  data/erdos_graph.json      (reference set from erdosproblems.com)
intersect    →  data/intersection.json     (cross-references; only confirmed ones surfaced)
review run   →  data/reviews/<slug>.json   (per-slug literature reviews)
build.py     →  site/                      (Jinja2 → static HTML, KaTeX for math)
```

The literature-review run uses a **terminal-per-bucket worker pattern**
(`scripts/`) rather than in-process parallelism: each terminal runs `claude -p`
sequentially for its bucket of slugs, with an `os.killpg`-based hard timeout
per slug to recover from the occasional infrastructure stall. See `LIT_REVIEW.md`
for the full design rationale; the worker pattern was the only one that survived
contact with infrastructure stalls at scale.

## Repository layout

```
graph-conjectures/
├── scraper/                # Python pipeline + Jinja2 templates + CSS
│   ├── crawl.py            # polite OPG crawler (12s/req, idempotent cache)
│   ├── parse.py            # HTML → JSON (selectors per PLAN.md Appendix A)
│   ├── erdos_index.py      # erdosproblems.com index for cross-referencing
│   ├── intersect.py        # fuzzy match to find shared problems
│   ├── review.py           # legacy single-process review orchestrator (superseded)
│   ├── review_system_prompt.md   # prompt used for `claude -p` reviews
│   ├── build.py            # site generator
│   ├── templates/          # Jinja2 templates
│   ├── static/style.css    # site styling
│   └── requirements.txt
├── scripts/                # parallel-worker pattern for the review run
│   ├── partition.py        # split unreviewed slugs into N buckets
│   ├── run_worker.sh       # one bucket per terminal, claude -p per slug
│   ├── status.sh           # snapshot all workers (done/fail/age/current slug)
│   └── timeout_claude.py   # process-group SIGKILL wrapper for `claude -p`
├── data/
│   ├── problems.json       # 227 OPG problems (parsed)
│   ├── reviews/            # 227 per-slug review JSONs
│   ├── erdos_graph.json    # erdosproblems graph-theory tag, 277 problems
│   ├── intersection.json   # fuzzy cross-references (manually curated)
│   ├── categories.json     # subjects / keywords / authors aggregated
│   ├── authors.json
│   └── agent_prompts/      # 227 derived per-problem briefs (input to claude -p)
├── problems/               # self-contained research workstreams
│   ├── directed_path_minimum_outdegree/
│   └── pebbling_cartesian_product/
├── PLAN.md                 # crawler / parser / site design + parser-selector spec
├── LIT_REVIEW.md           # literature-review pipeline design
├── LICENSE                 # MIT for code
└── LICENSE-DATA.md         # GFDL for data derived from OPG
```

## Featured: directed-path conjecture (Cheng--Keevash Conjecture 1)

A separate workstream attacks Thomasse's directed-path conjecture
(every oriented graph with minimum out-degree $\delta$ contains a
directed simple path of length $2\delta$), via Cheng--Keevash Lemma 7
and computer-aided enumeration.

The workstream now lives under
[`problems/directed_path_minimum_outdegree/`](problems/directed_path_minimum_outdegree/).
Its current packaged status closes $\delta \leq 3$, and closes
$\delta = 4$ at $n = 9, 10, 11$; the first open local target is
$\delta = 4, n \geq 12$.

## Licensing summary

- **Code**: MIT (see `LICENSE`).
- **Data derived from openproblemgarden.org**: GFDL v1.2 with attribution
  (see `LICENSE-DATA.md`). Each problem record carries a `canonical_url`
  field linking back upstream.

## Acknowledgments

- The **Open Problem Garden** community for their decade+ of curating these
  problems.
- **Thomas Bloom** for [erdosproblems.com](https://www.erdosproblems.com/),
  which directly inspired the layout and which we cross-reference.
- The reviews were generated with **Claude** (Sonnet) via `claude -p`, with
  every cited URL verified by `WebFetch` before inclusion. Reviews are
  advisory and should be spot-checked before being relied upon for research
  decisions.
