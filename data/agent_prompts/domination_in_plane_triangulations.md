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

# Problem: Domination in plane triangulations
Slug: domination_in_plane_triangulations
Canonical URL: http://www.openproblemgarden.org/op/domination_in_plane_triangulations
Posted: 2009-05-04
Subject path: Graph Theory » Topological Graph Theory
Author(s): Matheson, Lesley R., Tarjan, Robert E.
Keywords: coloring, domination, multigrid, planar graph, triangulation

## Statement(s)
**Conjecture.** Every sufficiently large plane triangulation $ G $ has a dominating set of size $ \le \frac{1}{4} |V(G)| $ .

## Discussion (from OPG)
Motivated by some problems in multigrid computations, Matheson and Tarjan [MT] considered the problem of finding small dominating sets in plane triangulations. They proved that every such graph $ G $ has a dominating set of size $ \le \frac{1}{3} |V(G)| $ and posed the above question. The Octahedron is a triangulation with 6 vertices for which every dominating set has size $ \ge 2 $ , so no constant better than $ \frac{1}{3} $ can be achieved in general. However, it appears that one can do better for larger graphs. The most extreme examples here (also from [MT]) are constructed as follows: Start with $ n $ disjoint copies of $ K_4 $ embedded in the plane, and then add edges to complete this graph to a triangulation (with $ 4n $ vertices). Now each of the original copies of $ K_4 $ has an inner vertex which has degree 3 in the final graph, and in order to cover it, one must take at least one vertex from this $ K_4 $ . It follows that every dominating set has size $ \ge n $ . Since the Matheson-Tarjan proof is short and instructive, we sketch it here. In fact, we shall prove (as they did) the stronger statement that every near-triangulation (a graph embedded in the plane with all finite faces of size three) has a (possibly improper) 3-coloring so that each color class is a dominating set and so that the subgraph induced by those vertices incident with the infinite face is properly colored. This stronger fact we prove by induction. If the infinite face is not bounded by a cycle or the infinite face is bounded by a cycle which has a chord, then the graph may be written as the union of two near-triangulations $ G_1,G_2 $ where $ G_1 $ and $ G_2 $ either share one vertex or two adjacent vertices and one edge. In either case, the result follows by applying induction to $ G_1 $ and $ G_2 $ . Otherwise, choose a vertex $ v $ on the infinite face, delete $ v $ and apply induction. Since the neighbors of $ v $ are all on the infinite face, and do not form an independent set, there are at least two colors, say $ 1 $ and $ 2 $ , which appear on the neighbors of $ v $ . Now giving $ v $ the color $ 3 $ gives a solution.

## OPG bibliography (your starting point)
- [MT] L. R. Matheson, R. E. Tarjan, Dominating sets in planar graphs. European J. Combin. 17 (1996), no. 6, 565--568. MathSciNet

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.