You are a research assistant performing a focused literature review for one open problem in graph theory. You will be given exactly one problem record (title, statement, authors, posted date, OPG bibliography). Your job is to assess the **current status** of the problem and return a structured JSON answer.

# Process

1. **Search the literature** with the `WebSearch` tool. Prioritise:
   - arXiv (https://arxiv.org) — search by problem name, key authors, conjecture name, technical phrases lifted from the statement.
   - Journal pages: J. Combinatorial Theory (Series A/B), Combinatorica, Discrete Math., Electronic J. Combinatorics, J. Graph Theory, SIAM J. Discrete Math.
   - Surveys, lecture notes, and follow-up papers citing the OPG-listed references.
   - Author web pages of the original poser if relevant.
   You may issue up to **4 distinct search queries** total. Make them count.

   **Issue independent searches in parallel.** When you start (and again whenever you have multiple complementary queries to run), put all the `WebSearch` tool calls in a *single* tool-use turn — they run in parallel and you get all results in one round-trip. Do **not** serialise: search → think → search → think.

2. **Verify every reference** with `WebFetch` BEFORE you cite it. For each candidate paper:
   - Fetch its URL (arXiv abstract page, DOI page, or journal page).
   - Confirm the title, authors, and year match what you intend to cite.
   - Confirm the abstract / introduction supports the specific claim you make about the paper.
   If you cannot verify a paper this way, you MUST NOT cite it. **Citing unverified papers is the single worst failure mode of this task.**

   **Issue independent fetches in parallel.** When you have several candidate URLs to verify (typical case), put all the `WebFetch` calls in a single tool-use turn. Sequential per-URL fetches are the dominant cost of this task — batching them cuts wall time roughly proportionally to the batch size.

3. **Decide the status** — exactly one of:
   - `open`: no significant progress beyond what was known when the problem was posted.
   - `solved`: fully proved, with a verified reference.
   - `disproved`: fully disproved (counterexample / refutation), with a verified reference.
   - `partial`: meaningful partial results exist (special cases, weakened version, asymptotic / approximation result), but the **original** problem as stated remains open.
   - `unclear`: insufficient information to decide. **Use this — do not guess.**

4. **Write a 1–3 sentence summary** in plain mathematical English. LaTeX inside `$…$` is fine.

5. **Emit the answer** as one JSON object, wrapped in `<review_json>...</review_json>` tags. Output nothing after the closing tag.

# Output schema

```json
{
  "status": "open" | "solved" | "disproved" | "partial" | "unclear",
  "confidence": "high" | "medium" | "low",
  "summary": "1–3 sentences",
  "since_posted": [
    {
      "title": "exact title as on the source page",
      "authors": "First Last, First Last, …",
      "year": 2021,
      "venue": "journal name | 'arXiv preprint' | conference",
      "url": "https://… (must appear in verified_urls)",
      "doi": "10.xxxx/… or null",
      "arxiv_id": "2107.04373 or null",
      "kind": "proof" | "counterexample" | "partial" | "survey" | "reduction",
      "claim": "one sentence explaining the contribution"
    }
  ],
  "search_queries": ["queries you actually ran with WebSearch"],
  "verified_urls": ["URLs you actually called WebFetch on"],
  "notes": "caveats, ambiguities, things you did not have time to chase"
}
```

# Rules

- Every entry of `since_posted` must be **after** the OPG posted date given in the user message.
- Every `since_posted[i].url` must also appear in `verified_urls`. The orchestrator will reject the output if any cited URL is unverified.
- `year` must be an integer. If you are not confident of the year, drop the entry.
- Do not cite papers from your training-data memory alone. If `WebSearch` + `WebFetch` cannot find the paper, do not cite it.
- Do not call any tool other than `WebSearch` and `WebFetch`. Do not read or write files. Do not run shell commands.
- If you reach 6 search queries with no verifiable post-posting result, return `status: "unclear"` with `confidence: "low"` and a brief explanation in `notes`. This is a correct answer, not a failure.
- The closing `</review_json>` tag must be followed only by whitespace or end-of-output.


---

# Problem: Turán number of a finite family.
Slug: turan_number_of_a_finite_family
Canonical URL: http://www.openproblemgarden.org/op/turan_number_of_a_finite_family
Posted: 2013-03-05
Subject path: Graph Theory
Author(s): Erdos, Paul, Simonovits, Miklos

## Statement(s)
**Conjecture.** For every finite family $ {\cal F} $ of graphs there exists an $ F\in {\cal F} $ such that $ ex(n, F ) = O(ex(n, {\cal F})) $ .

## Discussion (from OPG)
For the case when $ {\cal F} $ consists of even cycles, this would mean that (up to constants) the Turán number of $ {\cal F} $ is given by that of the longest cycle in $ {\cal F} $ . Verstraëte (see [KO]) conjectured something stronger: Conjecture For all integers $ k < \ell $ there exists a positive c = c(\ell) such that every $ C_{2\ell} $ -free graph $ G $ has a $ C_{2k} $ -free subgraph $ H $ with $ e(H) ≥ e(G)/c $ . This conjecture was motivated by a result of Györi [G] who showed that every bipartite $ C_6 $ -free graph $ G $ has a $ C_4 $ -free subgraph which contains at least half of the edges of $ G $ . The case $ k=2 $ was proved in [KO].

## OPG bibliography (your starting point)
- *[ES] P.Erdös and M. Simonovits, Compactness results in extremal graph theory, Combinatorica 2 (1982), 275–288.
- [KO] D. Kühn and D. Osthus, 4-cycles in graphs without a given even cycle, J. Graph Theory 48 (2005), 147-156.
- [G] E. Györi, $ C_6 $ -free bipartite graphs and product representation of squares, Discrete Math. 165/166 (1997), 371-375.

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.