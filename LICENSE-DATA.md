# Data licence (GFDL v1.2)

The data files in this repository derived from
[openproblemgarden.org](http://www.openproblemgarden.org/) — specifically:

- `data/problems.json` and the per-slug records inside it
- `data/agent_prompts/` (problem briefs that embed OPG statements and bibliographies)
- `data/reviews/*.json` insofar as their `summary`, `notes`, and any embedded
  problem-statement excerpts reproduce text from OPG

…are licensed under the **GNU Free Documentation License, Version 1.2**
(or any later version published by the Free Software Foundation),
with **attribution** to the contributors at openproblemgarden.org.

Each problem record carries a `canonical_url` field linking back to its
upstream Open Problem Garden page.

The full GFDL v1.2 text is available at:
<https://www.gnu.org/licenses/old-licenses/fdl-1.2.txt>

## What is and isn't covered

- The **code** that crawls, parses, and renders the data is under MIT
  (see `LICENSE`). Re-using the code without the data is unencumbered.
- The **review classifications** themselves (`status`, `confidence`,
  `since_posted` citation lists, `search_queries`, `verified_urls`) are the
  authors' independent assessments based on web research; they are not
  reproduced from OPG and are also offered under GFDL for licence symmetry.
- `data/erdos_graph.json` is derived from
  [erdosproblems.com](https://www.erdosproblems.com/), maintained by Thomas
  Bloom; the same GFDL terms apply with attribution to that site.
