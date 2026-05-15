# graph-conjectures

A browseable, status-annotated mirror of the **graph-theory category** of
[openproblemgarden.org](http://www.openproblemgarden.org/category/graph_theory),
extended with **new conjectures mined from recent arXiv papers** by 12 curated
graph-theorists. Every problem and conjecture is classified as `open`,
`partial`, `solved`, `disproved`, or `unclear` via an automated literature-
review pass, with every cited paper verified by `WebFetch` before inclusion.

**Two corpora, one merged index:**

| corpus | count | scope |
|---|---:|---|
| **OPG**    |  227 | full graph-theory tag of openproblemgarden.org |
| **arXiv**  |  762 | new conjectures from 857 arxiv papers (2016–2026) by 12 curated authors |

Reviewed status counts:

| status    | OPG  | arXiv | meaning                                                   |
|-----------|-----:|------:|------------------------------------------------------------|
| open      |   57 |   554 | no significant progress found in literature search         |
| partial   |  137 |   132 | progress since posting (special cases, weakened version)   |
| solved    |   19 |    58 | fully proved by a follow-up paper                          |
| disproved |   13 |    13 | counterexample found                                       |
| unclear   |    1 |     5 | insufficient information to decide                         |

**44 of the arXiv-extracted records** were also identified as direct progress
on existing OPG problems and attached as citations on those OPG pages (e.g. on
`/op/caccetta_haggkvist_conjecture/` and 20 other pages).

The output site is inspired by
[erdosproblems.com](https://www.erdosproblems.com/), which itself is an
excellent companion source.

## Quick start

```bash
# 1) install deps (uv recommended)
uv venv
uv pip install -r scraper/requirements.txt

# 2) the data is already in data/; render the static site
.venv/bin/python scraper/build.py --confirmed-only
python -m http.server --directory site 8000
# open http://localhost:8000
```

## Curated arXiv authors

`data/arxiv_authors.json` lists the 12 authors whose recent (since 2016) work
on `math.CO`, `cs.DM`, and `math.GT` is mined for new conjectures:

```
Paul Seymour · Sophie Spirkl · Stéphan Thomassé · Pierre Aboulker
Alex Scott · Zdeněk Dvořák · Jacob Fox · Noga Alon
Gwenaël Joret · Raphael Mario Steiner · Bojan Mohar · Marthe Bonamy
```

Edit that file to grow or shrink the curated set; the rest of the pipeline
re-runs idempotently.

## Pipelines

### A. OPG mirror (227 problems)

```bash
.venv/bin/python scraper/crawl.py          # polite OPG crawler, 12s/req
.venv/bin/python scraper/parse.py          # HTML → data/problems.json
.venv/bin/python scraper/erdos_index.py    # erdosproblems.com index
.venv/bin/python scraper/intersect.py      # OPG ↔ erdosproblems cross-ref
# Literature review (8-terminal worker pattern):
.venv/bin/python scripts/partition.py --workers 8
# In 8 terminals: PER_SLUG_TIMEOUT=900 WORKER=NN bash scripts/run_worker.sh
```

### B. arXiv mining (762 new conjectures)

```bash
# (1) Metadata harvest via OAI-PMH — fast, polite, ~7 min for the 3 sets
.venv/bin/python scripts/arxiv_oai_fetch.py --set math.CO,cs.DM,math.GT --from 2016-01-01

# (2) Download paper content (HTML, PDF fallback) — ~2h for 857 unique papers
.venv/bin/python scripts/arxiv_download_content.py

# (3) Partition + 8-worker extraction via `claude -p` — ~2h on Max plan
.venv/bin/python scripts/arxiv_partition.py --workers 8
# In 8 terminals: PER_PAPER_TIMEOUT=900 WORKER=NN bash scripts/arxiv_run_worker.sh

# (4) Aggregate: dedup states + fuzzy-match studies → OPG
.venv/bin/python scripts/arxiv_aggregate.py
# (review data/arxiv_opg_matches.tsv, set manual_confirmed flags as desired)

# (5) Phase 1 internal cross-reference (free, no claude calls, ~1s)
.venv/bin/python scripts/arxiv_internal_refs.py

# (6) Phase 2 web-search status review — ~5h on Max plan
.venv/bin/python scripts/arxiv_review_partition.py --workers 8
# In 8 terminals: PER_REVIEW_TIMEOUT=900 WORKER=NN bash scripts/arxiv_review_run_worker.sh
```

### C. Site build

```bash
.venv/bin/python scraper/build.py --confirmed-only
```

`--confirmed-only` attaches only `arxiv_opg_matches.json` entries flagged
`manual_confirmed: true`. Without the flag, auto-high (score ≥ 92) matches
are also attached.

## Architecture

```
OPG branch:
  crawl.py        →  cache/op/<slug>.html     polite crawl, 12s/req
  parse.py        →  data/problems.json       227 OPG problems
  erdos_index.py  →  data/erdos_graph.json    277 erdosproblems records
  intersect.py    →  data/intersection.json   confirmed OPG ↔ erdos crosslinks
  review run      →  data/reviews/<slug>.json 227 status reviews

arXiv branch:
  arxiv_oai_fetch.py      → cache/arxiv/<slug>/papers.json   12 author manifests
  arxiv_download_content  → cache/arxiv/<slug>/*.html|*.pdf  857 unique papers
  arxiv_run_worker.sh     → data/arxiv_extracted/*.json      1,565 raw records
  arxiv_aggregate.py      → data/arxiv_conjectures.json      762 deduped conjectures
                          → data/arxiv_opg_matches.{json,tsv} 44 confirmed citations
  arxiv_internal_refs.py  → data/arxiv_internal_refs.json    148 cross-corpus refs
  arxiv_review_*          → data/arxiv_reviews/<id>.json     762 status reviews

Site:
  build.py        →  site/                    Jinja2 → static HTML, KaTeX
                     /                        merged index (989 rows, filter by source/status)
                     /op/<slug>/              227 OPG problem pages
                     /arxiv/<id>/             762 arxiv conjecture pages
                     /author/<slug>/          218 author landing pages
                     /tag/<slug>/             227 subject pages
```

Both review runs use a **terminal-per-bucket worker pattern** (`scripts/*_run_worker.sh`)
rather than in-process parallelism. Each terminal runs `claude -p` sequentially
for its bucket, with an `os.killpg`-based hard timeout per item to recover from
infrastructure stalls. See `LIT_REVIEW.md` for the design rationale.

## Repository layout

```
graph-conjectures/
├── scraper/                          # Python pipeline + Jinja2 templates + CSS
│   ├── crawl.py / parse.py           # OPG crawler + parser
│   ├── erdos_index.py / intersect.py # OPG ↔ erdosproblems cross-reference
│   ├── arxiv_fetch.py                # legacy /api/query author search (kept for reference)
│   ├── arxiv_extract.py              # claude -p extraction of one paper
│   ├── arxiv_review.py               # claude -p status review of one conjecture
│   ├── arxiv_system_prompt.md        # extraction prompt
│   ├── arxiv_review_system_prompt.md # review prompt
│   ├── review_system_prompt.md       # OPG-review prompt
│   ├── build.py                      # site generator
│   ├── templates/                    # Jinja2 templates
│   ├── static/style.css
│   └── requirements.txt
├── scripts/                          # worker-pattern harness
│   ├── partition.py / run_worker.sh  # OPG-review workers
│   ├── arxiv_oai_fetch.py            # OAI-PMH metadata harvest
│   ├── arxiv_download_content.py     # polite HTML/PDF download
│   ├── arxiv_partition.py            # extraction-bucket partition
│   ├── arxiv_run_worker.sh           # extraction worker
│   ├── arxiv_aggregate.py            # dedup + OPG-match aggregator
│   ├── arxiv_internal_refs.py        # intra-corpus cross-reference
│   ├── arxiv_review_partition.py     # review-bucket partition
│   ├── arxiv_review_run_worker.sh    # review worker
│   ├── arxiv_fetch_all.py            # legacy /api/query driver (kept for reference)
│   ├── arxiv_disambig.py             # legacy disambiguation gate
│   ├── status.sh                     # snapshot all OPG workers
│   └── timeout_claude.py             # process-group SIGKILL wrapper for `claude -p`
├── data/
│   ├── problems.json                 # 227 OPG problems
│   ├── reviews/                      # 227 per-slug OPG review JSONs
│   ├── erdos_graph.json              # erdosproblems.com index, 277 problems
│   ├── intersection.json             # confirmed OPG↔erdos cross-refs
│   ├── arxiv_authors.json            # the 12 curated arxiv authors
│   ├── arxiv_conjectures.json        # 762 deduped new conjectures
│   ├── arxiv_extracted/              # 857 raw per-paper extraction outputs
│   ├── arxiv_reviews/                # 762 per-conjecture review JSONs
│   ├── arxiv_opg_matches.{json,tsv}  # arxiv → OPG citation matches (manually triaged)
│   ├── arxiv_internal_refs.{json,tsv} # intra-corpus cross-refs (Phase 1)
│   ├── categories.json
│   └── authors.json
├── problems/                         # self-contained research workstreams
│   ├── directed_path_minimum_outdegree/
│   ├── earth_moon_problem/
│   ├── 3_decomposition_conjecture/
│   ├── pebbling_cartesian_product/
│   └── unit_vector_flows/
├── PLAN.md                           # OPG crawler / parser / site design
├── LIT_REVIEW.md                     # OPG literature-review design
├── LICENSE                           # MIT for code
└── LICENSE-DATA.md                   # GFDL for data derived from OPG
```

## Featured: directed-path conjecture (Cheng--Keevash Conjecture 1)

A separate workstream attacks Thomassé's directed-path conjecture
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
- **Data derived from arxiv.org**: arXiv allows bulk metadata access via
  OAI-PMH and free distribution under terms documented at
  [info.arxiv.org/help/api/tou.html](https://info.arxiv.org/help/api/tou.html).
  Each conjecture record carries the source `arxiv_id` and `abs_url`.

## Acknowledgments

- The **Open Problem Garden** community for their decade+ of curating these
  problems.
- **Thomas Bloom** for [erdosproblems.com](https://www.erdosproblems.com/),
  which directly inspired the layout and which we cross-reference.
- The 12 curated arXiv authors whose recent work is mined here.
- Reviews and extraction were generated with **Claude** (Sonnet 4.6) via
  `claude -p`, with every cited URL verified by `WebFetch` before inclusion.
  Reviews are advisory and should be spot-checked before being relied upon
  for research decisions.
