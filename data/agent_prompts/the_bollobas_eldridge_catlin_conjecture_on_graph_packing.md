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

# Problem: The Bollobás-Eldridge-Catlin Conjecture on graph packing
Slug: the_bollobas_eldridge_catlin_conjecture_on_graph_packing
Canonical URL: http://www.openproblemgarden.org/op/the_bollobas_eldridge_catlin_conjecture_on_graph_packing
Posted: 2013-03-23
Subject path: Graph Theory » Extremal Graph Theory
Keywords: graph packing

## Statement(s)
**Conjecture (BEC-conjecture).** If $ G_1 $ and $ G_2 $ are $ n $ -vertex graphs and $ (\Delta(G_1) + 1) (\Delta(G_2) + 1) < n + 1 $ , then $ G_1 $ and $ G_2 $ pack.

## Discussion (from OPG)
A pair of $ n $ -vertex graphs $ G_1 $ and $ G_2 $ are said to $ {\it pack} $ if they are edge-disjoint subgraphs of the complete graph on $ n $ vertices. The main conjecture in the area of graph packing is the abovementioned conjecture by Bollobás, Eldridge [BE] and Catlin [C]. In support of the BEC-conjecture, Sauer and Spencer [SS] proved that if $ G_1 $ and $ G_2 $ are $ n $ -vertex graphs and $ 2 \Delta(G_1) \Delta(G_2) < n $ then $ G_1 $ and $ G_2 $ pack. Given a graph $ G $ , $ L(G) $ denotes the line graph of $ G $ and $ \Theta(G) $ denotes the number $ \Delta(L(G)) + 2 $ . Kostochka and Yu [KY1] proved that if $ G_1 $ and $ G_2 $ are two $ n $ -vertex graphs with $ \Theta(G_1) \Delta(G_2) \leq n $ , then $ G_1 $ and $ G_2 $ pack with the following exceptions: (1) $ G_1 $ is a perfect matching and $ G_2 $ is either $ K_{n/2,n/2} $ with $ n/2 $ odd or contains $ K_{n/2 + 1} $ or (2) $ G_2 $ is a perfect matching and $ G_1 $ is $ K_{r,n-r} $ with $ r $ odd or contains $ K_{n/2 + 1} $ . Kostachka and Yu [KY2] conjectured that if $ G_1 $ and $ G_2 $ are $ n $ -vertex graphs with $ \Theta(G_1) \Theta(G_2) < 2n $ then $ G_1 $ and $ G_2 $ pack.

## OPG bibliography (your starting point)
- *[BE] B. Bollabás and S. E. Eldridge, Maximal matchings in graphs with given maximal and minimal degrees, Congr. Numer. XV (1976), 165--168.
- *[C] P. A. Catlin, Embedding subgraphs and coloring graphs under extremal degree conditions, Ph. D. Thesis, Ohio State Univ., Columbus (1976).
- [KY1] A. V. Kostochka and G. Yu, An Ore-type analogue of the Sauer-Spencer Theorem, Graphs Combin. 23 (2007), 419--424.
- [KY2] A. V. Kostochka and G. Yu, An Ore-type graph packing problems, Combin. Probab. Comput. 16 (2007), 167--169.
- [SS] N. Sauer and J. Spencer, Edge disjoint placement of graphs, J. Combin. Theory Ser. B 25 (1978), 295--302.

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.