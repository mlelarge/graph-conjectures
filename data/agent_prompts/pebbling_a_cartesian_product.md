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

# Problem: Pebbling a cartesian product
Slug: pebbling_a_cartesian_product
Canonical URL: http://www.openproblemgarden.org/op/pebbling_a_cartesian_product
Posted: 2007-09-24
Subject path: Graph Theory
Author(s): Graham, Ronald L.
Keywords: pebbling, zero sum

## Statement(s)
**Conjecture.** $ p(G_1 \Box G_2) \le p(G_1) p(G_2) $ .

## Discussion (from OPG)
The pebbling number of a graph $ G $ , denoted $ p(G) $ , is the smallest integer $ k $ so that however $ k $ pebbles are distributed onto the vertices of $ G $ , it is possible to move a pebble to any vertex by a sequence of steps, where in each step we remove two pebbles from one vertex, and then place one on an adjacent vertex. The cartesian product of two graphs $ G_1 $ and $ G_2 $ , denoted $ G_1 \Box G_2 $ , is the graph with vertex set $ V(G_1) \times V(G_2) $ and an edge from $ (v,w) $ to $ (v',w') $ if either $ v=v' $ and $ w \sim w' $ (in $ G_2 $ ) or $ w=w' $ and $ v \sim v' $ (in $ G_1 $ ). Graph Pebbling arose out of the study of zero-sum subsequences in groups, but has proved to be a rich and interesting topic in graph theory. See Glenn Hurlbert's wonderful graph pebbling page for much more on this topic (and this problem in particular). Graham's conjecture was stated in one of the first papers on this subject by Fan Chung [C], and has since generated considerable interest. There are a number of partial results toward this conjecture. Chung [C] proved that $ p(P_{d_1+1} \Box P_{d_2+1} \ldots \Box P_{d_{\ell}+1}) = 2^{d_1 + d_2 \ldots + d_{\ell}} $ , thus settling the conjecture for products of paths (here $ P_n $ denotes a path with $ n $ vertices). It is also known when $ G_1,G_2 $ are both trees, both cycles, and for graphs with high minimum degree. Again, we encourage the interested reader to see the graph pebbling page for more details.

## OPG bibliography (your starting point)
- *[C] F. Chung, Pebbling in hypercubes SIAM J. Disc. Math. 2 (1989), 467--472.

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.