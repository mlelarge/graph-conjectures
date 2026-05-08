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

# Problem: Decomposing eulerian graphs
Slug: decomposing_eulerian_graphs
Canonical URL: http://www.openproblemgarden.org/op/decomposing_eulerian_graphs
Posted: 2007-03-07
Subject path: Graph Theory » Basic Graph Theory » Cycles
Keywords: cover, cycle, Eulerian

## Statement(s)
**Conjecture.** If $ G $ is a 6- edge-connected Eulerian graph and $ P $ is a 2-transition system for $ G $ , then $ (G,P) $ has a compaible decomposition.

## Discussion (from OPG)
Definition: Let $ G $ be an Eulerian graph and for every vertex $ v $ , let $ P(v) $ be a partition of the edges incident with $ v $ . We call $ P $ a transition system . If every member of $ P(v) $ has size at most $ k $ (for every $ v $ ), then we call $ P $ a $ k $ - transition sytem . A compatible decomposition of $ (G,P) $ is a list of edge-disjoint cycles $ C_1,\ldots,C_n $ with union $ G $ so that every $ C_i $ contains at most one edge from every member of $ P(v) $ . Let $ G $ be a graph and let $ G' $ be the graph obtained from $ G $ by replacing each edge $ e $ of G by two edges $ e',e'' $ in parallel. Let $ P $ be the 2-transition system of $ G $ with $ {e',e''} \in P(v) $ whenever $ e' $ and $ e'' $ are incident with $ v $ . Now, $ G' $ is an Eulerian graph and every compatible decomposition of $ (G',P) $ gives a cycle double cover of $ G $ . Since the cycle double cover conjecture can be reduced to graphs which are 3-edge-connected, the above conjecture would imply the cycle double cover conjecture. We define a transition system $ P $ to be admissable if every member of $ P(v) $ contains no more than half of the edges in any edge-cut. It is easy to see that if there is a compatible decomposition of $ (G,P) $ , then $ P $ must be admissable. The converse of this is not true; There is an admissable 2-transition system of the graph $ K_5 $ which does not admit a compatible decomposition. Recently, G. Fan and C.Q. Zhang [FZ] have proved that $ (G,P) $ does have a compatible decomposition whenever $ P $ is admissable and $ G $ has no $ K_5 $ minor. This result imporoved upon an earlier theorem of Fleischner and Frank [FF]. Very recently, I have proved a weak version of the above conjecture, by showing that $ (G,P) $ also has a compatible decomposition when P is a 2-transition system and G is 80-edge-connected. I'd quite like to see an improvement on this bound. Here is a related conjecture. Conjecture (Sabidussi) Let $ W $ be an Euler tour of the graph $ G $ . If $ G $ has no vertex of degree two, then there is a cycle decomposition of $ G $ , say $ F $ , so that no two consecutive edges of $ W $ are in a common circuit of $ F $ . If $ W $ is given by $ v_1,e_1,v_2,e_2,...,e_{m-1},v_m $ then we may form a 2-transition system $ P $ by putting $ \{e_{i-1},e_i\} $ in $ P(v_i) $ for every $ i $ (working modulo $ m $ ). Now a compatible decomposition of $ (G,P) $ is precisely a cycle decomposition of $ G $ satisfying the above conjecture. Thus, Sabidussi's conjecture is equivalent to the assertion that $ (G,P) $ has a compatible decomposition whenever $ G $ has no vertex of degree two and $ P $ is a 2-transition system which comes from an Euler tour. Let $ G $ be a directed Eulerian graph and for every vertex $ v $ , let $ P(v) $ be a partition of the edges incident with $ v $ into pairs so that every in-edge is paired with an out-edge. We define a compatible decomposition to be a decomposition of $ G $ into directed circuits so that every directed circuit contains at most one edge from every member of $ P(v) $ . Our current techniques don't seem to shed any light on the problem of finding compatible decompositions for Eulerian digraphs. Next I pose a very basic question which is still open. Problem (DeVos) Does there exist a fixed integer $ k $ such that $ (G,P) $ has a compatible decomposition whenever $ G $ is a $ k $ -edge-connected directed Eulerian graph and $ P $ is a 2-transition system?

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.