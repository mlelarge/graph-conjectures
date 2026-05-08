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

# Problem: Linear Hypergraphs with Dimension 3
Slug: linear_hypergraphs_with_dimension_3
Canonical URL: http://www.openproblemgarden.org/op/linear_hypergraphs_with_dimension_3
Posted: 2007-09-26
Subject path: Graph Theory » Topological Graph Theory » Drawings
Author(s): de Fraysseix, Hubert, Ossona de Mendez, Patrice, Rosenstiehl, Pierre
Keywords: Hypergraphs

## Statement(s)
**Conjecture.** Any linear hypergraph with incidence poset of dimension at most 3 is the intersection hypergraph of a family of triangles and segments in the plane.

## Discussion (from OPG)
A hypergraph is linear if any two edges may share at most one vertex. The incidence poset of a hypergraph is the vertex-edge inclusion poset. The dimension of a poset $ P $ is the minimum number of linear extentions of $ P $ , whose intersection is $ P $ [DM]. Schnyder proved that the incidence poset of a graph $ G $ has dimension at most $ 3 $ if and only if $ G $ is planar [S89]. Fraysseix, Rosenstiehl and Ossona de Mendez proved that every planar graph has a representation by contacts of triangles [FOR94] and Scheinerman conjectured that every planar graph has a representation by intersection of segments [S84] (claimed to be proved by Gonçalves et al.). A hypergraph is planar if its vertex-edge incidence graph is planar [W]. Fraysseix, Rosenstiehl and Ossona de Mendez proved that every planar linear hypergraph has a representation by contacts of triangles [FOR07] and it has been conjectured that they have a representation by intersection of straight line segments [FO07] (cf Straight line representation of planar linear hypergraphs ). Although the incidence poset of a simple planar hypergraph has dimension at most $ 3 $ (what follows from [BT]), the converse is false: The linear hypergraph with vertices $ 1,\dots,5 $ and edge set $ \{\{1,2\},\{2,3\},\{3,4\},\{1,4\},\{1,3,5\},\{2,4,5\}\} $ has incidence dimension $ 3 $ but is not planar (its vertex-edge incidence graph is a subdivision of $ K_{3,3} $ ). It follows from [O] that the vertices of simple hypergraphs with incidence posets of dimensions $ d $ can be represented by convex sets of the Euclidean space of dimension $ d-1 $ , in such a way that the edges of the hypergraph are exactly the maximal subsets of vertices, such that the corresponding subset of convexes has a non-empty intersection.

## OPG bibliography (your starting point)
- [BT] G.~Brightwell and W.T. Trotter, The order dimension of planar maps, SIAM journal on Discrete Mathematics 10 (1997), no.~4, 515--528.
- [DM] B.~Dushnik and E.W. Miller, Partially ordered sets, Amer. J. Math. 63 (1941), 600--610.
- [FO07] Hubert de Fraysseix, Patrice Ossona de Mendez: Stretching of Jordan arc contact systems, Discrete Applied Mathematics 155 (2007), no. 9, 1079--1095.
- [FOR94] H.~de Fraysseix, P.~Ossona~de Mendez, and P.~Rosenstiehl, On triangle contact graphs, Combinatorics, Probability and Computing 3 (1994), 233--246.
- *[FOR07] H.~de Fraysseix, P.~Ossona~de Mendez, and P.~Rosenstiehl, Representation of Planar Hypergraphs by Contacts of Triangles, Proc. of Graph Drawing '07, to appear.
- [O] P.~Ossona~de Mendez, Realization of posets, Journal of Graph Algorithms and Applications 6 (2002), no.~1, 149--153.
- [S84] E.R. Scheinerman, Intersection classes and multiple intersection parameters of graphs, Ph.D. thesis, Princeton University, 1984.
- [S89] W.~Schnyder, Planar graphs and poset dimension, Order 5 (1989), 323--343.
- [W] T.R.S. Walsh, Hypermaps versus bipartite maps, J. Combinatorial Theory 18(B) (1975), 155--163.

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.