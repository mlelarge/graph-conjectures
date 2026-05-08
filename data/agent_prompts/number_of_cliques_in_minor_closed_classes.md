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

# Problem: Number of Cliques in Minor-Closed Classes
Slug: number_of_cliques_in_minor_closed_classes
Canonical URL: http://www.openproblemgarden.org/op/number_of_cliques_in_minor_closed_classes
Posted: 2009-10-12
Subject path: Graph Theory
Author(s): Wood, David R.
Keywords: clique, graph, minor

## Statement(s)
**Question.** Is there a constant $ c $ such that every $ n $ -vertex $ K_t $ -minor-free graph has at most $ c^tn $ cliques?

## Discussion (from OPG)
Here a clique is a (not neccessarily maximal) set of pairwise adjacent vertices in a graph. See [RW, NSTW] for early bounds on the number of cliques. Wood [W] proved that the number of cliques in an $ n $ -vertex $ K_t $ -minor-free graph is at most $ c^{t\sqrt{\log t}}n\enspace. $ Fomin et al. [FOT] improved this bound to $ c^{t\log\log t}n\enspace. $ These results are based on the fact that every $ n $ -vertex $ K_t $ -minor-free graph has at most $ ct\sqrt{\log t}n $ edges. This bound is tight for certain random graphs. So it is reasonable to expect that random graphs might also provide good lower bounds on the number of cliques. Update 2014: Choongbum Lee and Sang-il Oum [LO] recently answered this question in the affirmative, and even proved it for excluded subdivisions. In particular, they proved that every $ n $ -vertex graph with no $ K_t $ -subdivision has at most $ 2^{474t}n $ cliques and also at most $ 2^{14t+o(t)}n $ cliques. The question now is to determine the minimum constant. Wood [W] proved a lower bound of $ 3^{2t/3-o(t)}n $ using an appropriate sized complete graph minus a perfect matching. The same graph gives a lower bound of $ 3^{s-o(s)}n $ on the number of cliques in a graph with no $ K_s $ subdivision. Update (2019): Fox and Wei [FW] have proved that every graph on $ n $ vertices with no $ K_t $ -minor has at most $ 3^{2t/3+o(t)}n $ cliques. This bound is tight for $ n \geq 4t/3 $ .

## OPG bibliography (your starting point)
- [FOT] Fedor V. Fomin, Sang il Oum, and Dimitrios M. Thilikos. Rank-width and tree-width of $ H $ -minor-free graphs , European J. Combin. 31 (7), 1617–1628, 2010.
- [NSTW] Serguei Norine, Paul Seymour, Robin Thomas, Paul Wollan. Proper minor-closed families are small. J. Combin. Theory Ser. B , 96(5):754--757, 2006.
- [RW] Bruce Reed and David R. Wood. Fast separation in a graph with an excluded minor. In 2005 European Conf. on Combinatorics, Graph Theory and Applications (EuroComb '05), vol. AE of Discrete Math. Theor. Comput. Sci. Proceedings , pp. 45--50. 2005.
- * [W] David R. Wood. On the maximum number of cliques in a graph . Graphs Combin. , 23(3):337--352, 2007.
- [LO] Choongbum Lee and Sang-il Oum. Number of cliques in graphs with forbidden minor , 2014.
- [FW] Jacob Fox, Fan Wei. On the number of cliques in graphs with a forbidden minor

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.