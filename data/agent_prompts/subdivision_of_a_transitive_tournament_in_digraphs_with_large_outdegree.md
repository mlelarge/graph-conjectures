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

# Problem: Subdivision of a transitive tournament in digraphs with large outdegree.
Slug: subdivision_of_a_transitive_tournament_in_digraphs_with_large_outdegree
Canonical URL: http://www.openproblemgarden.org/op/subdivision_of_a_transitive_tournament_in_digraphs_with_large_outdegree
Posted: 2013-03-04
Subject path: Graph Theory » Directed Graphs
Author(s): Mader, W.

## Statement(s)
**Conjecture.** For all $ k $ there is an integer  $ f(k) $ such that every digraph of minimum outdegree at least  $ f(k) $ contains a subdivision of a transitive tournament of order $ k $ .

## Discussion (from OPG)
A fundamental result of Mader [M1] states that for every integer $ k $ there is a smallest $ g(k) $ so that every graph of average degree at least $ g(k) $ contains a subdivision of a complete graph on $ k $ vertices. Bollobás and Thomason [BT] as well as Komlós and Szemerédi [KS] showed that $ g $ is quadratic in $ k $ . The above conjecture is a digraph analogue of this result. However one cannot replace the minimum outdegree in this conjecture by the average degree as in Mader's analogue for graphs: consider the complete bipartite graph $ K_{n,n} $ and orient all edges from the first to the second class. The resulting digraph has average degree $ n $ but not even a transitive tournament on 3 vertices. One might be tempted to conjecture that large minimum outdegree would even force the existence of a subdivision of a large complete digraph. However, for all $ n $ Thomassen [T] constructed a digraph on $ n $ vertices whose minimum outdegree is at least $ \frac{1}{2} \log_2 n $ but which does not contain an even directed cycle (and thus no complete digraph on 3 vertices). A simpler construction was found by DeVos et al. [DMMS]. It is easy to see that  $ f(1)=0 $ and $ f(2)=1 $ . Mader [M3] showed that $ f(4) = 3 $ . Even the existence of  $ f(5) $ is not known.

## OPG bibliography (your starting point)
- [BT] B. Bollobás and A. Thomason, Proof of a conjecture of Mader, Erdös and Hajnal on topological complete subgraphs, European Journal of Combinatorics 19 (1998), 883–887.
- [DMMS] M. DeVos, J. McDonald, B. Mohar, and D. Scheide, Immersing complete digraphs, European Journal of Combinatorics, 33 (2012), no 6, 1294-1302.
- [KS] J. Komlós and E. Szemerédi, Topological Cliques in Graphs II, Combinatorics, Probability and Computing 5 (1996), 70–90.
- [M1] W. Mader, Homomorphieeigenschaften und mittlere Kantendichte von Graphen, Math. Annalen 174 (1967), 265–268.
- * [M2] W. Mader, Degree and Local Connectivity in Digraphs, Combinatorica 5 (1985), 161–165.
- [M3] W. Mader, On Topological Tournaments of order 4 in Digraphs of Outdegree 3, Journal of Graph Theory 21 (1996), 371–376.
- [T] C. Thomassen, Even Cycles in Directed Graphs, European Journal of Combinatorics 6 (1985), 85–89.

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.