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

# Problem: Faithful cycle covers
Slug: faithful_cycle_covers
Canonical URL: http://www.openproblemgarden.org/op/faithful_cycle_covers
Posted: 2007-03-07
Subject path: Graph Theory » Basic Graph Theory » Cycles
Author(s): Seymour, Paul D.
Keywords: cover, cycle

## Statement(s)
**Conjecture.** If $ G = (V,E) $ is a graph, $ p : E \rightarrow {\mathbb Z} $ is admissable, and $ p(e) $ is even for every $ e \in E(G) $ , then $ (G,p) $ has a faithful cover.

## Discussion (from OPG)
Definition: Let $ G=(V,E) $ be a graph and let $ p:E \rightarrow {\mathbb Z} $ . A list $ L $ of cycles of $ G $ is a faithful (cycle) cover of $ (G,p) $ if every edge $ e $ of $ G $ occurs in exactly $ p(e) $ cycles of $ L $ . Thus, the cycle double cover conjecture is equivalent to the statement that $ (G,2) $ has a faithful cover for every graph $ G $ with no bridge . We define the map $ p $ to be admissable if $ p(e) $ satisfies the following properties: i $ p $ is nonnegative. ii $ p(S) $ is even for every edge-cut $ S $ . iii $ p(e) \le p(S)/2 $ for every edge-cut $ S $ and edge $ e \in S $ . It is easy to see that $ G $ has a faithful cover only if $ p $ is admissable. However, the converse is false. A counterexample is obtained by taking the Petersen graph, putting weight $ 2 $ on the edges of a perfect matching, and $ 1 $ elsewhere. More generally, for a graph G=(V,E), one may consider the vector space of real numbers indexed by E. We associate every circuit C with its incidence vector. Most of the basic questions about this space are solved. Seymour [S] has shown that a vector p can be written as a nonnegative rational combination of cycles if and only if it satisfies conditions (i) and (iii) in the definition of admissable. It is an easy exercise to show that for a 3-edge-connected graph G, a vector p can be written as an integer combination of cycles if and only if p satisfies (ii) in the definition of admissable. Seymour's conjecture is equivalent to the statement that every admissable map may be realized as a half-integer combination of circuits. Note the similarity of this to The Berge-Fulkerson conjecture . The most interesting result about faithful covers is a theorem of Alspach, Goddyn, and Zhang which resolved a conjecture of Seymour. They prove that whenever $ G $ has no minor isomorphic to Petersen , every admissable map has a corresponding faithful cover. For a general graph $ G $ with no bridge, Bermond, Jackson, and Jaeger [BJJ] proved that $ (G,4) $ has a faithful cover and Fan [F] proveed that $ (G,6) $ has a faithful cover. DeVos, Johnson, and Seymour [DJS] proved that $ (G,p) $ has a faithful cover whenever $ p $ is admissable and there is a nonnegative integer $ k $ such that $ 32k+83 < p(e) < 36k+88 $ holds for every edge $ e $ . However, little else seems to be known. In particular, it does not appear to be known if there exist integers $ a,b $ with $ a-b $ arbitrarily large so that $ (G,p) $ has a faithful cover whenever $ p $ is an admissable function taking on only the values $ a,b $ . Such a result would appear to require an idea not contained in any of the aforementioned papers. The analogous problem for oriented circuit covers does not appear to be very promising. It is easy to see that for an orientation of a series parallel graph G and a map $ p:E(G) \rightarrow G $ which satisfies the obvious conditions, that $ (G,p) $ will have a circuit cover using every edge in its given direction. However, even with a $ K_4 $ minor, there is a great deal of forcing, and nothing much looks like it would be true.

## OPG bibliography (your starting point)
- \[AGZ] B. Alspach, L. Goddyn, and C-Q Zhang, Graphs with the circuit cover property , Trans. Amer. Math. Soc., 344 (1994), 131-154. MathSciNet
- [BJJ] J.C. Bermond, B. Jackson, and F. Jaeger, Shortest covering of graphs with cycles, J. Combinatorial Theory Ser. B 35 (1983), 297-308. MathSciNet
- [DJS] M. DeVos, T. Johnson, P.D. Seymour, Cut-coloring and circuit covering
- [F] G. Fan, Integer flows and cycle covers, J. Combinatorial Theory Ser. B 54 (1992), 113-122. MathSciNet
- [S] P.D. Seymour, Sums of circuits in Graph Theory and Related Topics edited by J.A. Bondy and U.S.R. Murty, Academic Press, New York/Berlin (1979), 341-355. MathSciNet

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.