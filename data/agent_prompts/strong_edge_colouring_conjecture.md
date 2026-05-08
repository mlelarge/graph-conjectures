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

# Problem: Strong edge colouring conjecture
Slug: strong_edge_colouring_conjecture
Canonical URL: http://www.openproblemgarden.org/op/strong_edge_colouring_conjecture
Posted: 2013-03-01
Subject path: Graph Theory » Coloring » Edge coloring
Author(s): Erdos, Paul, Nesetril, Jaroslav

## Statement(s)
**Conjecture.** $$s\chi'(G) \leq \frac{5\Delta^2}{4}, \text{if $\Delta$ is even,}$$ $$s\chi'(G) \leq \frac{5\Delta^2-2\Delta +1}{4},&\text{if $\Delta$ is odd.}$$

## Discussion (from OPG)
The conjectured bounds would be sharp. When $ D $ is even, expanding each vertex of a $ 5 $ -cycle into a stable set of size $ \Delta/2 $ yields such a graph with $ 5\Delta^2/4 $ edges in which the largest induced matching has size $ 1 $ . A similar construction achieves the bound when $ \Delta $ is odd. Greedy colouring the edges yields $ s\chi'(G) \leq 2\Delta(\Delta-1)+1 $ . Using probabilistic methods, Molloy and Reed~[MoRe97] proved that there is a positive constant $ \epsilon $ such that, for sufficiently large $ \Delta $ , every graph with maximum degree $ \Delta $ has strong chromatic index at most $ (2-\epsilon)\Delta^2 $ . The greedy bound proves the conjecture for $ \Delta \leq 2 $ . For $ \Delta =3 $ , the conjectured bound of 10 was proved independently by Hor\'ak, He, and Trotter[HHT] and by Andersen [A]. For $ \Delta=4 $ , the conjectured bound is 20, and Cranston [C] proved that 22 colours suffice. For a bipartite graph $ G $ , Faudree et al. [FGST] conjectured that $ s\chi'(G)\leq \Delta^2(G) $ . This is implied by the stronger conjecture due to Kaiser. Conjecture Let $ G=((A_1,A_2),E) $ be a bipartite graph such that every vertex in $ A_1 $ has degree at most $ \Delta_1 $ and every vertex in $ A_2 $ has degree at most $ \Delta_2 $ . Then $ s\chi'(G)\leq \Delta_1\Delta_2 $ .

## OPG bibliography (your starting point)
- [A] L. D. Andersen. The strong chromatic index of a cubic graph is at most 10. Discrete Math., 108(1-3):231--252, 1992.
- [C] D. W. Cranston. Strong edge-coloring of graphs with maximum degree 4 using 22 colors. Discrete Math., 306(21):2772--2778, 2006.
- [FGST] R. J. Faudree, A. Gyárfás, R. H. Schelp, and Zs. Tuza. Induced matchings in bipartite graphs. Discrete Math., 78(1-2):83--87, 1989.
- [HHT] P. Horák, Q. He, and W. T. Trotter. Induced matchings in cubic graphs. J. Graph Theory, 17(2):151--160, 1993.

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.