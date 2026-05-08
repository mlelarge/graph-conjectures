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

# Problem: Minimal graphs with a prescribed number of spanning trees
Slug: minimal_graphs_with_a_prescribed_number_of_spanning_trees
Canonical URL: http://www.openproblemgarden.org/op/minimal_graphs_with_a_prescribed_number_of_spanning_trees
Posted: 2012-04-22
Subject path: Graph Theory
Author(s): Azarija, Jernej, Skrekovski, Riste
Keywords: number of spanning trees, asymptotics

## Statement(s)
**Conjecture.** Let $ n \geq 3 $ be an integer and let $ \alpha(n) $ denote the least integer $ k $ such that there exists a simple graph on $ k $ vertices having precisely $ n $ spanning trees. Then $ \alpha(n) = o(\log{n}). $

## Discussion (from OPG)
Observe that $ \alpha(n) $ is well defined for $ n \geq 3 $ since $ C_n $ has $ n $ spanning trees. The function was introduced by Sedlacek [S] who has shown that for large enough $ n $ $ \alpha(n) \leq \frac{n+6}{3} \mbox{if } n \equiv 0 \pmod{3} $ and $ \alpha(n) \leq \frac{n+4}{3} \mbox{if } n \equiv 2 \pmod{3}. $ Using the fact that almost all positive integers $ n $ are expressible as $ n = ab+ac+bc $ for integers $ 0 < a < b < c $ it can be shown [A] that for large enough $ n $ $ \alpha(n) \leq \frac{n+4}{3} \mbox{if } n \equiv 2 \pmod{3} $ and $ \alpha(n) \leq \frac{n+9}{4} $ otherwise. Moreover, the only fixed points of $ \alpha $ are 3, 4, 5, 6, 7, 10, 13 and 22. The conjecture is motivated by the following graph (ploted for a very small sample of vertices) The conjecture [C] is justifiable for highly composite numbers $ n $ since in this case one can construct the graph obtained after taking cycles $ C_{p_1}, \ldots,C_{p_k} $ for every odd prime factor $ p_i $ of $ n $ .

## OPG bibliography (your starting point)
- [S] J. Sedlacek, On the minimal graph with a given number of spanning trees, Canad. Math. Bull. 13 (1970) 515-517.
- [A] J. Azarija, R. Skrekovski, Euler's idoneal numbers and an inequality concerning minimal graphs with a prescribed number of spanning trees, IMFM preprints 49 (2011) Link to paper
- * [C] Minimal graphs with a prescribed number of spanning trees

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.