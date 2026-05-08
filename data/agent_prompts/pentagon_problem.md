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

# Problem: Pentagon problem
Slug: pentagon_problem
Canonical URL: http://www.openproblemgarden.org/op/pentagon_problem
Posted: 2007-03-24
Subject path: Graph Theory » Coloring » Homomorphisms
Author(s): Nesetril, Jaroslav
Keywords: cubic, homomorphism

## Statement(s)
**Question.** Let $ G $ be a 3-regular graph that contains no cycle of length shorter than $ g $ . Is it true that for large enough~ $ g $ there is a homomorphism $ G \to C_5 $ ?

## Discussion (from OPG)
This question was asked by Nesetril at numerous problem sessions (and also appears as [N]). By Brook's theorem any triangle-free cubic graph is 3-colorable. Does a stronger assumption on girth of the graph imply stronger coloring properties? This problem is motivated by complexity considerations [GHN] and also by exploration of density of the homomorphism order: We write $ G \prec H $ if there is a homomorphism $ G \to H $ but there is no homomorphism $ H \to G $ . It is known that whenever $ G \prec H $ holds and $ H $ ~is not bipartite, there is a graph~ $ K $ satisfying $ G \prec K \prec H $ . A negative solution to the Pentagon problem would have the following density consequence: for each cubic graph~ $ H $ for which~ $ C_5 \prec H $ holds, there exists a cubic graph~ $ K $ satisfying $ C_5 \prec K \prec H $ (see [N]). If we replaced $ C_5 $ in the statement of the problem by a longer odd cycle, we would get a stronger statement. It is known that no such strenghthening is true. This was proved by Kostochka, Nesetril, and Smolikova [KNS] for $ C_{11} $ (hence for all $ C_l $ with $ l \ge 11 $ ), by Wanless and Wormald [WW] for $ C_9 $ , and recently by Hatami [H] for $ C_7 $ . Each of these results uses probabilistic arguments (random regular graphs), no constructive proof is known. Haggkvist and Hell [HH] proved that for every integer~ $ g $ there is a graph~ $ U_g $ with odd girth at least~ $ g $ (that is, $ U_g $ does not contain odd cycle of length less than~ $ g $ ) such that every cubic graph of odd girth at least~ $ g $ maps homomorphically to~ $ U_g $ . Here, the graph~ $ U_g $ may have large degrees. This leads to a weaker version of the Pentagon problem: Question Is it true that for every $ k $ there exists a cubic graph $ H_k $ of girth~ $ k $ and an integer~ $ g $ such that every cubic graph of girth at least~ $ g $ maps homomorphically to~ $ H_k $ ? A particular question in this direction: does a high-girth cubic graph map to the Petersen graph? As an approach to this, we mention a result of DeVos and Samal [DS]: a cubic graph of girth at least~ $ 17 $ admits a homomorphism to the Clebsch graph. In context of the Pentagon problem, the following reformulation is particularly appealing: If $ G $ ~is a cubic graph of girth at least~ $ 17 $ , then there is a cut-continuous mapping from~ $ G $ to~ $ C_5 $ ; that is, there is a mapping $ f: E(G) \to E(C_5) $ such that for any cut $ X \subseteq E(C_5) $ the preimage $ f^{-1}(X) $ is a cut. (Here by cut we mean the edge-set of a spanning bipartite subgraph. A more thorough exposition of cut-continuous mappings can be found in~[DNR].)

## OPG bibliography (your starting point)
- [DNR] Matt DeVos, Jaroslav Nesetril, and Andre Raspaud, On edge-maps whose inverse preverses flows and tensions, Graph Theory in Paris: Proceedings of a Conference in Memory of Claude Berge, Birkhäuser 2006.
- [DS] Matt DeVos and Robert Samal, High girth cubic graphs map to the Clebsch graph
- [GHN] Anna Galluccio, Pavol Hell, and Jaroslav Nesetril, The complexity of $ H $ -colouring of bounded degree graphs, Discrete Math. 222 (2000), no.~1-3, 101--109, MathSciNet
- [HH] Roland Haggkvist and Pavol Hell, Universality of $ A $ -mote graphs, European J. Combin. 14 (1993), no.~1, 23--27.
- [H] Hamed Hatami, Random cubic graphs are not homomorphic to the cycle of size~7, J. Combin. Theory Ser. B 93 (2005), no.~2, 319--325, MathSciNet
- [KNS] Alexandr~V. Kostochka, Jaroslav Nesetril, and Petra Smolikova, Colorings and homomorphisms of degenerate and bounded degree graphs, Discrete Math. 233 (2001), no.~1-3, 257--276, Fifth Czech-Slovak International Symposium on Combinatorics, Graph Theory, Algorithms and Applications, (Prague, 1998), MathSciNet
- *[N] Jaroslav Nesetril, Aspects of structural combinatorics (graph homomorphisms and their use), Taiwanese J. Math. 3 (1999), no.~4, 381--423, MathSciNet
- [WW] I.M. Wanless and N.C. Wormald, Regular graphs with no homomorphisms onto cycles, J. Combin. Theory Ser. B 82 (2001), no.~1, 155--160, MathSciNet

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.