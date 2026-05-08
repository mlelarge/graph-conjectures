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

# Problem: Ryser's conjecture
Slug: rysers_conjecture
Canonical URL: http://www.openproblemgarden.org/op/rysers_conjecture
Posted: 2007-03-19
Subject path: Graph Theory » Hypergraphs
Author(s): Ryser, Herbert J.
Keywords: hypergraph, matching, packing

## Statement(s)
**Conjecture.** Let $ H $ be an $ r $ - uniform $ r $ -partite hypergraph. If $ \nu $ is the maximum number of pairwise disjoint edges in $ H $ , and $ \tau $ is the size of the smallest set of vertices which meets every edge, then $ \tau \le (r-1) \nu $ .

## Discussion (from OPG)
Definitions: A (vertex) cover is a set of vertices which meets (has nonempty intersection with) every edge, and we let $ \tau(H) $ denote the size of the smallest vertex cover of $ H $ . A matching is a collection of pairwise disjoint edges, and we let $ \nu(H) $ denote the size of the largest matching in $ H $ . When the hypergraph is clear from context, we just write $ \tau $ or $ \nu $ . It is immediate that $ \nu \le \tau $ , since every cover must contain at least one point from each edge in any matching. For $ r $ -uniform hypergraphs, $ \tau \le r \nu $ , since the union of the edges from any maximal matching is a set of at most $ r \nu $ vertices that which meets every edge. Ryser's conjecture is that this second bound can be improved if $ H $ is $ r $ -uniform and $ r $ -partite (the vertices may be partitioned into $ r $ sets $ V_1,V_2,\ldots,V_r $ so that every edge contains exactly one element of each $ V_i $ ). In the special case when $ r=2 $ our trivial inequality yields $ \nu \le \tau $ and the conjecture implies $ \tau \le \nu $ , so we should have $ \nu = \tau $ . In fact this is true, it is König's theorem on bipartite graphs [K]. Indeed, Ryser's conjecture is probably easiest to view as a high dimensional generalization of this early result of König. Recently, Aharoni [A] has applied the "Hall's theorem for hypergraphs" result of Aharoni and Haxell [AH] to prove this conjecture for $ r=3 $ . However the case $ r=4 $ is still wide open. Some other interesting work on this problem concerns fractional covers and fractional matchings. A fractional cover of $ H = (V,E) $ is a weighting $ a : V \rightarrow {\mathbb R}^+ $ so that $ \sum_{x \in S} a(x) \ge 1 $ for every $ S \in E $ , and the weight of this cover is $ \sum_{x \in V} a(x) $ . The fractional cover number , denoted $ \tau^* $ is the infimum of the set of weights of covers. Similarly, a fractional matching is an edge-weighting $ b : E \rightarrow {\mathbb R}^+ $ so that $ \sum_{S \ni x} b(S) \le 1 $ for every $ x \in V $ , and the weight of this matching is $ \sum_{S \in E} b(S) $ . The fractional matching number , denoted $ \nu^* $ is the supremum of the set of weights of fractional matchings. Fractional covers and matchings are the usual fractional relaxations, and by LP-duality, they satisfy $ \nu^* = \tau^* $ for every hypergraph. For $ r $ -regular $ r $ -partite hypergraphs, Füredi [F] has proved that $ \tau^* \le (r-1)\nu $ and Lovasz [L] has shown $ \tau \le \frac{1}{2} r \nu^* $ .

## OPG bibliography (your starting point)
- [A] R. Aharoni, Ryser's conjecture for tripartite 3-graphs. Combinatorica 21 (2001), no. 1, 1--4. MathSciNet
- [AH] R. Aharoni and P. Haxell, Hall's theorem for hypergraphs. J. Graph Theory 35 (2000), no. 2, 83--88. MathSciNet
- [F] Z. Füredi, Maximum degree and fractional matchings in uniform hypergraphs, Combinatorica 1 (1981), 155--162. MathSciNet
- [K] D. König, Theorie der endlichen und unendlichen Graphen, Leipzig, 1936.
- [L] L. Lovász, On minimax theorems of combinatorics, Ph.D thesis, Matemathikai Lapok 26 (1975), 209--264 (in Hungarian). MathSciNet

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.