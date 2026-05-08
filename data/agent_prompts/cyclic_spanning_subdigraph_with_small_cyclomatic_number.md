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

# Problem: Cyclic spanning subdigraph with small cyclomatic number
Slug: cyclic_spanning_subdigraph_with_small_cyclomatic_number
Canonical URL: http://www.openproblemgarden.org/op/cyclic_spanning_subdigraph_with_small_cyclomatic_number
Posted: 2013-06-02
Subject path: Graph Theory » Directed Graphs
Author(s): Bondy, J. Adrian

## Statement(s)
**Conjecture.** Let $ D $ be a digraph all of whose strong components are nontrivial. Then $ D $ contains a cyclic spanning subdigraph with cyclomatic number at most $ \alpha(D) $ .

## Discussion (from OPG)
The {\it cyclomatic number} of a digraph $ D=(V,A) $ is $ |A|-|V|+1 $ . For a strong digraph, it correspond to the minimum of directed ears in a directed ears decomposition. (See Chapter 5 of [BM]). $ \alpha(D) $ denotes the {\it stability number} of the digraph $ D $ , that is the maximum number of pairwise non-adjacent vertices. Bessy and Thomassé [BT04] showed that any nontrivial strong digraph $ D $ has a spanning subdigraph which is the union of $ \alpha $ directed cycles. However, the structure of this subdigraph might be rather complicated. This leads one to ask whether there always exists a spanning subdigraph whose structure is relatively simple, one which is easily seen to be the union of $ \alpha $ directed cycles. A natural candidate would be a spanning subdigraph built from a directed cycle by adding $ \alpha(D)-1 $ directed ears. But or any $ \alpha \geq 2 $ , there exists a digraph $ D $ with stability number $ \alpha $ requiring at least $ 2\alpha -2 $ directed ears. See Chapter 19 of [BM08]. A possible way around this problem is to allow spanning subdigraphs which are disjoint union of strong digraphs. Such digraph are called cyclic (because each arc lies on a directed cycle). The conjecture was formulated by Bondy[B], based on a remark of Chen and Manalastas [CM]. The Conjecture holds for $ \alpha(D)=1 $ by Camion's Theorem [C] and also for $ \alpha(D)=2 $ and $ \alpha(D)=3 $ by theorems of Chen and Manalastas [CM] and S. Thomassé (unpublished), respectively. The conjecture implies not only the above-mentioned Bessy--Thomassé Theorem, but also a result of Thomassé [Thom01], that the vertex set of any strong digraph $ D $ with $ \alpha(D) \geq 2 $ can be partitioned into $ \alpha(D)-1 $ directed paths, as well as another theorem of Bessy and Thomassé [BT03], that every strong digraph $ D $ has a strong spanning subdigraph with at most $ n+2\alpha(D)-2 $ arcs.

## OPG bibliography (your starting point)
- [BT03] S. Bessy and S. Thomassé, Every strong digraph has a spanning strong subgraph with at most $ n+2\alpha-2 $ arcs. J. Combin. Theory Ser. B 87 (2003), 289--299.
- [BT04] S. Bessy and S. Thomassé, Three min-max theorems concerning cyclic orders of strong digraphs. In Integer Programming and Combinatorial Optimization, 132--138. Lecture Notes in Comput. Sci., Vol. 3064, Springer, Berlin.
- *[B95] J.A. Bondy, Basic graph theory: paths and circuits. In Handbook of Combinatorics, Vol. 1, 3--110. Elsevier, Amsterdam.
- [BM] J.A. Bondy and U.S.R. Murty, Graph Theory, volume 244 of Graduate Texts in Mathematics. Springer, 2008.
- [C] P. Camion, Chemins et circuits hamiltoniens des graphes complets. C. R. Acad. Sci. Paris 249 (1959), 2151--2152.
- [CM] C.C. Chen C.C. and Jr. P. Manalastas, Every finite strongly connected digraph of stability 2 has a Hamiltonian path. Discrete Math. 44 (1983), 243--250.
- [T] S. Thomassé, Covering a strong digraph by $ \alpha-1 $ disjoint paths: a proof of Las Vergnas' conjecture. J. Combin. Theory Ser. B 83 (2001), 331--333.

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.