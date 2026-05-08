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

# Problem: Packing T-joins
Slug: packing_t_joins
Canonical URL: http://www.openproblemgarden.org/op/packing_t_joins
Posted: 2007-03-07
Subject path: Graph Theory » Coloring » Edge coloring
Author(s): DeVos, Matt
Keywords: packing, T-join

## Statement(s)
**Conjecture.** There exists a fixed constant $ c $ (probably $ c=1 $ suffices) so that every graft with minimum $ T $ -cut size at least $ k $ contains a $ T $ -join packing of size at least $ (2/3)k-c $ .

## Discussion (from OPG)
Definitions: A graft consists of a graph $ G=(V,E) $ together with a distinguished set $ T \subseteq V $ of even cardinality. A $ T $ - cut is an edge-cut $ \delta(X) $ of $ G $ with the property that $ |X \cap T| $ is odd. A $ T $ - join is a set $ S \subseteq E $ with the property that a vertex of $ (V,S) $ has odd degree if and only if it is in $ T $ . A $ T $ -join packing is a set of pairwise disjoint T-joins. It is an easy fact that every $ T $ -join and every $ T $ -cut intersect in an odd number of elements. It follows easily from this that the maximum size of a $ T $ -join packing is always less than or equal to the minimum size of a $ T $ -cut. There is a simple example of a graft with $ |T|=4 $ with minimum $ T $ -cut size $ k $ which contains only $ (2/3)k $ disjoint T-joins. The above conjecture asserts that this is essentially the worst case. DeVos and Seymour [DS] have obtained a partial result toward the above conjecture, proving that every graft with minimum $ T $ -cut size $ k $ contains a $ T $ -join packing of size at least the floor of $ (1/3)k $ . Definition: We say that a graft $ G $ is an $ r $ - graph if $ G $ is $ r $ -regular, $ T=V $ , and every $ T $ -cut of G has size at least $ r $ . Conjecture (Rizzi) If $ G $ is an $ r $ -graph, then $ G $ contains a $ T $ -join packing of size at least $ r-2 $ . In an $ r $ -graph, every perfect matching is a $ T $ -join, so the above conjecture is true with room to spare for $ r $ -graphs which are $ r $ -edge-colorable. Indeed, Seymour had earlier conjectured that every $ r $ -graph contains $ r-2 $ disjoint perfect matchings. This however was disproved by Rizzi [R] who constructed for every $ r>2 $ an $ r $ -graph in which every two perfect matchings intersect. Rizzi suggested the above problem as a possible fix for Seymour's conjecture. DeVos and Seymour have proved that every $ r $ -graph has a $ T $ -join packing of size at least the floor of $ r/2 $ . Definition: Let $ G $ be a graph and let $ T $ be the set of vertices of $ G $ of odd degree. A $ T $ -join of $ (G,T) $ is defined to be a postman set . Note that when $ T $ is the set of vertices of odd degree, a cocycle of $ G $ is a $ T $ -cut if and only if it has odd size. Rizzi has shown that the following conjecture is equivalent to the above conjecture in the special case when $ r $ is odd. Conjecture (The packing postman sets conjecture (Rizzi)) If every odd edge-cut of $ G $ has size $ >2k+1 $ then the edges of $ G $ may be partitioned into $ 2k+1 $ postman sets. The Petersen graph (or more generally any non $ (2k+1) $ -edge-colorable $ (2k+1) $ -graph) shows that the above conjecture would be false with the weaker assumption that every odd edge-cut has size $ >2k $ . The following conjecture asserts that odd edge-cut size $ >2k $ is enough (for the same conclusion) if we assume in addition that G has no Petersen minor. Conjecture (Conforti, Johnson) If $ G $ has no Petersen minor and every odd edge-cut of $ G $ has size $ >2k $ then the edges of $ G $ may be partitioned into $ 2k+1 $ postman sets. Gerard Cornuejols [C] has kindly offered $5000 for a solution to this conjecture. However, it will be tough to find a quick proof since this conjecture does imply the 4-color theorem. Robertson, Seymour, Sanders, and Thomas [RSST] have proved the above conjecture for cubic graphs. Conforti and Johnson [CJ] proved it under the added hypothesis that G has no 4-wheel minor.

## OPG bibliography (your starting point)
- [CJ] M. Conforti and E.L. Johnson, Two min-max theorems for graphs noncontractible to a four wheel, preprint.
- [C] G. Cornuejols, Combinatorial Optimization, packing and covering, SIAM, Philadelphia (2001).
- [R] R. Rizzi, Indecomposable r-Graphs and Some Other Counterexamples, J. Graph Theory 32 (1999) 1-15. MathSciNet
- [RSST] N. Robertson, D.P. Sanders, P.D. Seymour, and R. Thomas, A New Proof of the Four-Color Theorem, Electron. Res. Announc., Am. Math. Soc. 02, no 1 (1996) 17-25.
- [S] P.D. Seymour, Some Unsolved Problems on One-Factorizations of Graphs, in Graph Theory and Related Topics, edited by J.A. Bondy and U.S.R. Murty, Academic Press, New York 1979) 367-368.

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.