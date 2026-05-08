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

# Problem: Mapping planar graphs to odd cycles
Slug: mapping_planar_graphs_to_odd_cycles
Canonical URL: http://www.openproblemgarden.org/op/mapping_planar_graphs_to_odd_cycles
Posted: 2007-06-24
Subject path: Graph Theory » Coloring » Homomorphisms
Author(s): Jaeger, Francois
Keywords: girth, homomorphism, planar graph

## Statement(s)
**Conjecture.** Every planar graph of girth $ \ge 4k $ has a homomorphism to $ C_{2k+1} $ .

## Discussion (from OPG)
This conjecture is Jaeger's modular orientation conjecture restricted to planar graphs and then dualized. To see this duality, first note that circular coloring and circular flows are dual for planar graphs, and then observe that $ (2k+1) $ -orientations are equivalent to $ 2 + \frac{1}{k} $ -flows and $ 2 + \frac{1}{k} $ -colorings are equivalent to homomorphisms to $ C_{2k+1} $ . So if $ G $ and $ G^* $ are dual planar graphs, then we have the following equivalences. \item $ G $ has a $ (2k+1) $ -orientation. \item $ G $ has a $ 2 + \frac{1}{k} $ -flow. \item $ G^* $ has a $ 2 + \frac{1}{k} $ -coloring. \item $ G^* $ has a homomorphism to $ C_{2k+1} $ . There is an easy family of graphs which show that the above conjecture (if true) is best possible. Let $ H_k $ be the graph obtained from an odd circuit of length $ 4k-1 $ by adding a new vertex $ u $ joined to every existing vertex by a path of length $ 2k-1 $ . Now, $ H_k $ is a planar graph of girth $ 4k-1 $ , but there is no homomorphism from $ H_k $ to $ C_{2k+1} $ . To see the latter claim, suppose (for a contradiction) that such a homomorphsim $ f $ exists, let $ C $ be the unique circuit of $ H_k \setminus u $ and let $ a=f(u) $ . Now, no vertex in $ C $ can map to $ a $ since every such vertex is distance $ 2k-1 $ from $ u $ . However we must then have a homomorphism from $ C $ to $ C_{2k+1} \setminus a $ , which is impossible since $ C $ is an odd circuit and $ C_{2k+1} \setminus u $ is bipartite. The k=1 case of the above conjecture asserts that every (loopless) triangle free planar graph has a homomorphism to the triangle. In other words, every (loopless) triangle free planar graph is 3-colorable. This is a well known theorem of Grotszch. For every k>1, the above conjecture is still open. Actually, I think this conjecture is already quite interesting for k=2. One reason is that this case of the conjecture implies the 5-color theorem for planar graphs. To see this implication, suppose that the above conjecture is true for k=2, let G be a simple loopless planar graph, and let G' be the graph obtained from G by subdividing each edge two times. Now, G' has girth at least 9, so by our assumption there is a homomorphism from G' to C_5. It is easy to see that adjacent vertices of G must map to different vertices of C_5 under this homomorphism. Thus, we have a proper 5-coloring of G as desired. Let us call a homomorphism to $ C_{2k+1} $ a $ C_{2k+1} $ - coloring . It is quite easy to show that every planar graph of girth > 10k has a $ C_{2k+1} $ -coloring. This follows from a simple degeneracy argument: Every such (nonempty) graph must have a either a vertex of degree $ \le 1 $ , or a path $ P $ of length $ 2k-1 $ all of whose internal vertices have degree two. Both of these configurations are reducible, in the sense that we may delete either a vertex of degree $ \le 1 $ or the interior vertices of $ P $ and then extend any $ C_{2k+1} $ -coloring of the resulting graph to a $ C_{2k+1} $ -coloring of the original. By more complicated, but similar degeneracy arguments, we can approach this conjecture. To my knowledge, the best result to date is as follows. Theorem (Borodin, Kim, Kostochka, West) Every planar graph of girth $ \ge \frac{20k-2}{3} $ has a homomorphism to $ C_{2k+1} $ . For the special case of the conjecture when $ k=2 $ , Matt DeVos and Adam Deckelbaum have an unpublished improvement showing that every planar graph with odd girth $ \ge 11 $ has a homomorphism to $ C_5 $ .

## OPG bibliography (your starting point)
- [BKKW] O. V. Borodin, S. J. Kim, A. V. Kostochka, D. B. West, Homomorphisms from sparse graphs with large girth. Dedicated to Adrian Bondy and U. S. R. Murty. J. Combin. Theory Ser. B 90 (2004), no. 1, 147--159. MathSciNet
- [Ja] F. Jaeger, On circular flows in graphs in Finite and Infinite Sets, volume 37 of Colloquia Mathematica Societatis Janos Bolyai, edited by A. Hajnal, L. Lovasz, and V.T. Sos. North-Holland (1981) 391-402.
- [Zh] X. Zhu, Circular chromatic number of planar graphs of large odd girth, Electronic Journal of Combinatorics Vol. 8 no. 1 (2001).

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.