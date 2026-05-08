# Plan: Graph-theory open problems site (OPG → erdosproblems-style)

Goal: scrape every problem under [openproblemgarden.org/category/graph_theory](http://www.openproblemgarden.org/category/graph_theory), normalise the data, and publish a browsable site in the spirit of [erdosproblems.com/tags/graph theory](https://www.erdosproblems.com/tags/graph%20theory).

## 1. What the source looks like

- **Listing URL**: `/category/graph_theory` — paginated via `?page=0..4` (5 pages, ~55 problem links each → on the order of 250 problems total).
- **Problem URL pattern**: `/op/<slug>` (e.g. [/op/seagull_problem](http://www.openproblemgarden.org/op/seagull_problem)).
- **Listing markup** (Drupal): `class="item-list"`, rows in a `<table>`, pager at `class="pager-list"`. Columns visible on the index: Title, Author(s), Importance, Recency, Topic » Subtopic, Posted by.
- **Problem page**: `<h1 class="title">`, structured field divs (`class="field…"`), a `<h2 class="OP">Bibliography</h2>` section, navigation/recent-activity sidebars to discard.
- **robots.txt**: allows scraping; `Crawl-Delay: 10` — must be honoured.
- **Licensing**: OPG content is user-contributed; check each page footer / site terms before redistributing. Plan attribution (link back to the canonical `/op/<slug>` on every detail page) regardless.

## 2. What the target should look like

Mirror the useful parts of erdosproblems.com:
- **Index page**: tag/subtopic chips, sortable table (Title, Authors, Importance, Recency, Subtopic), text search, status badge (open / partially solved / solved).
- **Detail page**: problem statement, posted-by, authors, references (with links), bibliography rendered like erdosproblems' bib boxes, link back to OPG canonical.
- **Cross-linking**: subtopic pages (Coloring, Digraphs, Extremal, Algebraic, …) and author pages.
- Out of scope (initial): user accounts, favourites, reactions, comments, dual-pane.

## 3. Architecture

```
┌─ scraper ─┐   ┌─ parser ─┐   ┌─ store ─┐   ┌─ generator ─┐
│ requests  │ → │ bs4/lxml │ → │  JSON   │ → │  static SSG │ → /site
│ + cache   │   │ field    │   │ + raw   │   │ list+detail │
│ (10s gap) │   │ extract  │   │ html    │   │ tag pages   │
└───────────┘   └──────────┘   └─────────┘   └─────────────┘
```

Keep the raw HTML cache and the parsed JSON as separate, committed artefacts so re-parsing never re-hits the source.

## 4. Phased work

### Phase 1 — Discovery & polite crawl
- Walk `?page=0..N` until pager-next disappears; collect `/op/<slug>` URLs into `urls.txt` (deduplicate).
- Fetch each problem page with `User-Agent: GraphConjectures-research/0.1 (mailto:marc.lelarge@gmail.com)` and a **≥10 s delay** between requests (sleep, not concurrent).
- Cache responses under `cache/op/<slug>.html`. Idempotent: skip if cached, support `--refresh`.
- Deliverable: `cache/` populated, `urls.txt`, a crawl log.

### Phase 2 — Parsing

Selectors and quirks live in [Appendix A](#appendix-a--parser-spec) — short version:

- Record shape (per page): `slug`, `node_id`, `canonical_url`, `title`, `subject_path[]` (hierarchical), `authors[]` (`{name, slug}`), `keywords[]`, `importance{label, stars}`, `accessible_to_undergrads` (bool), `posted_by{name, slug}`, `posted_at` (ISO date), `statements[]` (one per `div.envtheorem`: `{kind, html, text}`), `statement_html` / `statement_text` (whole `div.problem`), `discussion_html` / `discussion_text`, `references[]` (`{key, raw_html, raw_text, links[]}`), `categories[]` (union with provenance), `comments[]` (optional).
- Pre-processing: `html.unescape` everything; replace each `img.teximage` with its `$alt$` before extracting plain text (otherwise math vanishes — OPG renders LaTeX server-side as PNGs, no MathJax).
- Disambiguating `/category/<slug>` links: cannot be done from the slug alone — classify by which `div.authsubtable` block (label `Author(s):` / `Subject:` / `Keywords:`) the link sits in.
- Validate: title + at least one `envtheorem` + canonical_url required; log empty keywords / missing references as warnings, not errors.
- Deliverable: one JSON per slug under `data/problems/<slug>.json`, plus aggregated `data/problems.json`, `data/categories.json`, `data/authors.json`.

### Phase 2.5 — Intersection with erdosproblems.com

The new site should not duplicate problems that already live on erdosproblems.com. Detect overlap before generating pages.

- Build the reference set: parse `https://www.erdosproblems.com/tags/graph theory` once → `data/erdos_graph.json` (277 problems: 143 open, 134 solved, numbers 19–1216, each with statement, prize, tags, Erdős citation keys). Done by `scraper/erdos_index.py`.
- Match strategy (after Phase 2 produces parsed OPG records):
  1. **Citation filter**: shortlist OPG problems whose bibliography cites any Erdős paper key (`Er*`, `BoEr*`, `EFPS*`, etc. — pattern: any cite key that contains `Er` and a 2-digit year).
  2. **Statement fuzzy match**: for shortlisted candidates, normalise (lowercase, collapse whitespace, strip `$…$` delimiters but keep the LaTeX tokens) and score with `rapidfuzz.fuzz.token_set_ratio` against every erdos statement. Threshold ≥ 70 = candidate match; ≥ 85 = high-confidence.
  3. **Manual review**: write `data/intersection.tsv` (`opg_slug ↔ erdos_id ↔ score ↔ statement_excerpt`) and eyeball it — the count is small enough (probably < 30).
- Output: `data/intersection.json` mapping `opg_slug → {erdos_id, erdos_url, confidence}`. The site generator (Phase 3) uses this to either skip duplicates or render a "Also at erdosproblems.com #N" badge.

### Phase 3 — Site generation
- Pick one (recommend in §5):
  - **Astro** or **11ty**: static, fast, easy to mimic erdosproblems' layout.
  - **Hugo**: even faster builds, single binary.
  - **Flask + Frozen-Flask**: trivial Python integration with the parser.
- Pages:
  - `/` index — sortable/filterable table, search-as-you-type (client-side, e.g. MiniSearch).
  - `/op/<slug>` — problem detail, mirrors erdosproblems' look.
  - `/tag/<subtopic>` and `/author/<slug>` — filtered listings.
  - `/about` — sources, attribution, licence, last-crawl date.
- Deliverable: `site/` ready for GitHub Pages / Netlify.

### Phase 4 — Refresh & maintenance
- A `make refresh` target that re-crawls (respecting cache age, e.g. >30 days) and rebuilds.
- Optional: GitHub Action on a weekly cron, opening a PR with the diff so changes are reviewable.

## 5. Tech stack (decided)

Python end-to-end, no framework — the parser already produces JSON, so the "SSG" is one `build.py` rendering Jinja2 templates into static HTML.

- Language: **Python 3.11+**, deps: `requests`, `beautifulsoup4`, `lxml`, `jinja2`, `tenacity` (retry on transient HTTP errors).
- Storage: **JSON files in git** (one per slug + aggregates; ~250 records, diff-friendly, no DB).
- Templating: **Jinja2** → static HTML in `/site`. Math re-typeset client-side with **KaTeX** auto-render (loaded from a CDN) over the LaTeX strings preserved from `img.teximage` alts.
- Search: **MiniSearch** (single JS file, client-side index loaded from a generated `search-index.json`).
- Hosting: **local only** for now — `python -m http.server --directory site 8000`. Defer GitHub Pages until the site is good enough to share.

## 6. Repo layout (proposal)

```
Graph_conjectures/
├── GraphConj.md            # existing notes
├── PLAN.md                 # this file
├── scraper/
│   ├── crawl.py            # phase 1
│   ├── parse.py            # phase 2
│   └── requirements.txt
├── cache/op/<slug>.html    # raw HTML, gitignored or LFS
├── data/
│   ├── problems.json
│   ├── categories.json
│   └── authors.json
├── site/                   # SSG source
└── Makefile                # crawl / parse / build / serve
```

## 7. Decisions

1. **Licence**: OPG content is **GNU Free Documentation License** (verified by user). Full problem statements may be reproduced with attribution; the new site itself must therefore also be **GFDL** (each page links back to the OPG canonical URL and carries a GFDL notice in the footer).
2. **Scope**: graph theory only — `/category/graph_theory` and its descendants. No effort spent on cross-category normalisation.
3. **Relationship to [GraphConj.md](GraphConj.md)**: kept separate. The new site is a derived view of OPG, not a merge of personal notes.
4. **Stack**: see §5 — Python + Jinja2, no framework.
5. **Hosting**: local only initially (`python -m http.server`).

## 8. First concrete step

1. `scraper/crawl.py` walks the listing pages first (`?page=0..N` until the pager-next anchor disappears), then fetches each `/op/<slug>` with a 12 s sleep between requests, writing to `cache/op/<slug>.html`. Idempotent (skip if cached).
2. Smoke test: run with `--limit 5` so it stops after the first 5 problem pages (~1 minute with the delay) before committing to the full ~40-minute crawl.
3. Only after the cache is full do we write `scraper/parse.py` — that way reparsing never re-hits the source.

---

## Appendix A — Parser spec

Audited against 5 representative pages (`seagull_problem`, `reconstruction_conjecture`, `57_regular_moore_graph`, `strong_edge_colouring_conjecture`, `the_bermond_thomassen_conjecture`) plus the listing page. All five share one Drupal/`bluebreeze` template; differences are content-driven.

### Field selectors

| Field | Locator | Presence | Notes |
|---|---|---|---|
| `node_id` | numeric tail of `div.node[id="node-<nid>"]` (or `a[href^="/comment/reply/<nid>"]`) | always | stable |
| `canonical_url` | input URL; nid available from `link[rel="alternate"][type="application/rss+xml"]` (`/crss/node/<nid>`) | always | |
| `title` | `h1.title` (text, `.strip()`) | always | trailing whitespace; may end `?` |
| `breadcrumb` / `subject_path` | `div.breadcrumb a` minus the first two anchors (`Home`, `Subject`); also reachable as `div.authsubtable` whose label is `Subject:` (one row per level, `»`-separated) | ≥1 level always; 2nd/3rd optional | reconstruction has 1 level; seagull has 3 |
| `importance` | first `div.subtable` after label `Importance:` | always | categorical (`Medium`/`High`/`Outstanding`) + N×`✭` glyphs — store both `label` and `stars = text.count("✭")` |
| `accessible_to_undergrads` | `div.subtable` with label `Recomm. for undergrads:` | always | `yes`/`no` text on detail page; `0`/`1` on listing |
| `authors[]` | `div.authsubtable` with label `Author(s):` → all `td a[href^="/category/"]` | sometimes empty | `name` is link text (`"Kelly, Paul J."`); `slug` from href |
| `keywords[]` | `div.authsubtable` with label `Keywords:` → all `td a[href^="/category/"]` | sometimes empty (e.g. strong_edge_colouring) | tolerate empty `<tr>` |
| `posted_by` | last `div.subtable` → `a[href^="/user/"][href$="/track"]` | always | rare anonymous on comments only |
| `posted_at` | same row, `<td>` after `<span class="label">on:</span>` | always | format `"January 6th, 2008"` — strip ordinal suffix before `strptime("%B %d, %Y")` |
| `statement_html` | `div.problem` innerHTML | always | may interleave `<p>` and `<div class="envtheorem">` blocks |
| `statements[]` | every `div.envtheorem` inside `div.problem`; `kind` from leading `<b>` (`Conjecture`/`Question`/`Theorem`) | ≥1 always | bermond_thomassen has 2 |
| `statement_text` | `div.problem`.get_text after replacing each `img.teximage` with its `alt` | always | otherwise math drops out |
| `discussion_html` / `discussion_text` | `div.discussion` (same teximage substitution) | always (sometimes whitespace-only) | |
| `references[]` | each `<p>` inside `div.bibliography`; key via `re.match(r"\*?\s*\[([^\]]+)\]", text)` | sometimes absent | leading `*` marks original-source paper (legend in `div.teststyle`) — store as `is_original` flag |
| `categories[]` | union of all `a[href^="/category/"]` in `div.metatable` and `div.breadcrumb`, with provenance label (`author` / `subject` / `keyword`) — *never classify by slug alone* | always ≥1 | author slugs and topic slugs are not distinguishable in isolation |
| `comments[]` (optional) | `div.comment` siblings after `a#comment` | sometimes (reconstruction has 3) | poster may be unlinked |

### Watch-outs

- Run `html.unescape` on every extracted string (`&#039;`, `&amp;`, `&nbsp;` ubiquitous; `&nbsp;` survives as `\xa0` — strip it).
- Math is **PNGs at `/files/tex/<sha1>.png` with LaTeX in `alt`** (no MathJax). Before `get_text` on `div.problem` / `div.discussion` / bibliography, walk the tree and replace each `img.teximage` with its `alt`. Rendering on the new site can re-typeset from those LaTeX strings via KaTeX/MathJax.
- HTML entities appear *inside* alt strings — unescape after extraction.
- HTML is XHTML 1.0 Strict but contains uppercase `</LI>` tags — use `lxml` or `html.parser`; `html5lib` also fine.
- Listing column #5 (`view-field-node-data-field-top-sub-short`) is **always an empty `<a href="/">`** — useless; rely on per-page breadcrumb for topic.
- Listing has a data bug: at least one author cell links to `/kpz_equation_central_limit_theorem` (not a `/category/...` URL). Defensive parse: skip non-`/category/` hrefs.
- robots.txt is permissive but enforces `Crawl-Delay: 10` — sleep 10–12 s between requests, single-threaded, set a contact UA (`GraphConjectures-research/0.1 (mailto:marc.lelarge@gmail.com)`).

### Listing row schema (`/category/graph_theory`)

Single `<table>` in `div.view-content-OPview-area-new`; rows `tr.odd`/`tr.even` with six `<td>`:

1. `td.view-field-node-title > a` — slug + title (primary discovery target)
2. `td.view-field-node-data-field-last-names-...` — author last names, `; `-separated `<a>`
3. `td.view-field-node-data-field-stars1-...` — stars only (no word)
4. `td.view-field-node-data-field-accessible-...` — `0` / `1`
5. `td.view-field-node-data-field-top-sub-short-...` — empty (see watch-out)
6. `td.view-field-users-name > a[href^="/user/"]` — poster

Pagination via `?page=0..N`; walk until `pager-next` disappears.
