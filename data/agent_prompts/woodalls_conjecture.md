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

# Problem: Woodall's Conjecture
Slug: woodalls_conjecture
Canonical URL: http://www.openproblemgarden.org/op/woodalls_conjecture
Posted: 2007-04-05
Subject path: Graph Theory » Directed Graphs
Author(s): Woodall, Douglas R.
Keywords: digraph, packing

## Statement(s)
**Conjecture.** If $ G $ is a directed graph with smallest directed cut of size $ k $ , then $ G $ has $ k $ disjoint dijoins.

## Discussion (from OPG)
Definitions: Let $ G $ be a directed graph. A directed cut of $ G $ is an edge-cut in which all edges are directed the same way. A dijoin is a set of edges which intersect every directed cut. There is an important theorem of Lucchesi and Younger [LY] which asserts that the dual problem has an optimum integer packing. That is, for every digraph $ G $ in which the smallest dijoin has size $ k $ , there exist $ k $ pairwise disjoint directed cuts. This result implies more generally (in the terminology of Corneujols [C]) that the clutter of (minimal) directed cuts has the max-flow min-cut property (MFMC). It follows from this and Lehman's theorem [L] that the clutter of (minimal) dijoins is ideal. Therefore, if the smallest directed cut of $ G $ has size $ k $ , then there exist nonnegative rational numbers $ x_1,x_2,\ldots,x_m $ summing to $ k $ and dijoins $ J_1,J_2,\ldots,J_m $ so that if each dijoin $ J_i $ is taken with weight $ x_i $ , the total weight of the dijoins containing any edge is at most 1. The above conjecture asserts that such a combination exists with $ x_1,x_2,\ldots,x_m $ integral. Schrijver [Sc80] has found a digraph in which the clutter of (minimal) dijoins does not have the MFMC property. Thus, the weighted version of Woodall's conjecture is not true in general. However, this clutter does have the MFMC property in a number of interesting special cases. One such example (due to Schrijver [Sc82] and Feofiloff, Younger [FY]) is when the digraph is acyclic and every source is joined to every sink by a directed path. Since every such digraph has the MFMC property, every such digraph must satisfy Woodall's conjecture. There seem to be few positive results towards Woodall's conjecture for general digraphs. Although this was probably already known, Seymour and I (M. DeVos) observed that the conjecture is true for $ k=2 $ . To see this, note that the underlying graph is 2-edge-connected, so it may be oriented to give a strongly connected digraph, call it $ H $ . Now partition the edges into two sets $ \{X,Y\} $ where $ X $ consists of those edges which have the same orientation in both $ H $ and $ G $ , and $ Y $ consists of those edges with different orientations in the two graphs. It is immediate that both $ X $ and $ Y $ meet every directed cut, so each is a dijoin. Extending this to $ k=3 $ appears difficult. Indeed, I believe the following weak version of this is still open. Conjecture Prove that there exists a fixed integer $ k $ so that every digraph with all directed cuts of size $ \ge k $ contains three pairwise disjoint dijoins. The restriction of this conjecture to the special case of planar graphs is also open. Here we can use duality to restate the conjecture. Call a set of edges $ A $ a feedback arc-set if $ A $ intersects every directed cycle (or equivalently, $ G-A $ is acyclic). Conjecture If $ G $ is a planar digraph with all directed cycles of length $ \ge k $ , then $ G $ contains $ k $ pairwise disjoint feedback arc-sets. The above conjecture is known to fail when the assumption of planarity is removed. On the other hand, it does hold for digraphs which are orientations of series-parallel graphs [LW]. It is also still open for $ k=3 $ .

## OPG bibliography (your starting point)
- [C] G. Cornuejols, Combinatorial Optimization, Packing and Covering SIAM, Philadelphia (2001). MathSciNet
- [FY] P. Feofiloff and D. H. Younger, Directed cut transversal packing for source-sink connected graphs. Combinatorica 7 (1987), no. 3, 255--263. MathSciNet
- [LW] O. Lee, Y. Wakabayashi, Note on a min-max conjecture of Woodall. J. Graph Theory 38 (2001), no. 1, 36--41. MathSciNet
- [LY] C.L. Lucchesi and D. H. Younger A minimax theorem for directed graphs, Journal of the London Math. Soc. (2) 17 (1978) 369-374. MathSciNet
- [Sc80] A. Schrijver, A counterexample to a conjecture of Edmonds and Giles , Discrete Math. 32 (1980) 213-214. MathSciNet
- [Sc82] A. Schrijver, Min-max relations for directed graphs, Annals of Discrete Math. 16 (1982) 261-280. MathSciNet
- [W] D. R. Woodall, Menger and König systems. Theory and applications of graphs (Proc. Internat. Conf., Western Mich. Univ., Kalamazoo, Mich., 1976), pp. 620--635, Lecture Notes in Math., 642, Springer, Berlin, 1978. MathSciNet

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.