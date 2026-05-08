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

# Problem: Unfriendly partitions
Slug: unfriendly_partitions
Canonical URL: http://www.openproblemgarden.org/op/unfriendly_partitions
Posted: 2007-10-22
Subject path: Graph Theory » Infinite Graphs
Author(s): Cowan, Robert H., Emerson, William R.
Keywords: coloring, infinite graph, partition

## Statement(s)
**Problem.** Does every countably infinite graph have an unfriendly partition into two sets?

## Discussion (from OPG)
It is a simple property that every finite graph $ G $ has an unfriendly partition into two sets - just choose a partition of $ V(G) $ into two sets so that the number of edges with one end in each is maximum. Cowan and Emerson [CE] conjectured that the same property should hold true of infinite graphs. A counterexample to this was constructed by Milner and Shelah [MS], but their construction uses uncountably many vertices, leaving the countable case (highlighted above) still open. In the same article by Milner and Shelah [MS], they show that every graph does have an unfriendly partition into three sets. Curiously, it is quite easy to see that the answer to the above question is yes in the case when all vertices have finite degree, and also in the case when all vertices have infinite degree. The former follows from the unfriendly partition property for finite graphs together with a standard compactness argument. The latter can be achieved with a "back and forth" construction. Thus, the difficult case is the mixed one. Aharoni, Milner, and Prikry [AMP] showed that every graph with only finitely many vertices of infinite degree has an unfriendly partition into two sets, but this seems the extent of our knowledge. It does not appear that there is any consensus among experts as to whether this conjecture should be true or false.

## OPG bibliography (your starting point)
- *[CE] R. Cowan and W. Emerson, Proportional colorings of graphs, unpublished.
- [MS] E. C. Milner and S. Shelah, Graphs with no unfriendly partitions. A tribute to Paul Erdös, 373--384, Cambridge Univ. Press, Cambridge, 1990. MathSciNet .
- [AMP] R. Aharoni, E. C. Milner, K. Prikry, Unfriendly partitions of a graph. J. Combin. Theory Ser. B 50 (1990), no. 1, 1--10. MathSciNet

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.