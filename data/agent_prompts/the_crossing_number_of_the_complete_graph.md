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

# Problem: The Crossing Number of the Complete Graph
Slug: the_crossing_number_of_the_complete_graph
Canonical URL: http://www.openproblemgarden.org/op/the_crossing_number_of_the_complete_graph
Posted: 2007-05-11
Subject path: Graph Theory » Topological Graph Theory » Crossing numbers
Keywords: complete graph, crossing number

## Statement(s)
**Conjecture.** $ \displaystyle cr(K_n) = \frac 14 \floor{\frac n2} \floor{\frac{n-1}2} \floor{\frac{n-2}2} \floor{\frac{n-3}2} $

## Discussion (from OPG)
(This discussion appears as [M].) A drawing of a graph $ G $ in the plane has the vertices represented by distinct points and the edges represented by polygonal lines joining their endpoints such that: \item no edge contains a vertex other than its endpoints, \item no two adjacent edges share a point other than their common endpoint, \item two nonadjacent edges share at most one point at which they cross transversally, and \item no three edges cross at the same point. The conjectured value for the crossing number of $ K_n $ is known to be an upper bound. This is shown by exhibiting a drawing with that number of crossings. If $ n = 2m $ , place $ m $ vertices regularly spaced along two circles of radii 1 and 2, respectively. Two vertices on the inner circle are connected by a straight line; two vertices on the outer circle are connected by a polygonal line outside the circle. A vertex on the inner circle is connected to one on the outer circle with a polygonal line segment of minimum possible positive winding angle around the cylinder. A simple count shows that the number of crossings in such a drawing achieves the conjectured minimum. For $ n = 2m-1 $ we delete one vertex from the drawing described and achieve the conjectured minimum. The conjecture is known to be true for $ n $ at most 10 [G]. If the conjecture is true for $ n = 2m $ , then it is also true for $ n-1 $ . This follows from an argument counting the number of crossings in drawings of all $ K_{n-1} $ 's contained in an optimal drawing of $ K_n $ . It would also be interesting to prove that the conjectured upper bound is asymptotically correct, that is, that $ \lim \frac{cr(K_n)}{\binom{n}4} = \frac38 $ . The best known lower bound is due to Kleitman [K], who showed that this limit is at least $ 3/10 $ .

## OPG bibliography (your starting point)
- [G] R. Guy, The decline and fall of Zarankiewicz's theorem, in Proof Techniques in Graph Theory (F. Harary Ed.), Academic Press, New York (1969) 63-69.
- [K] D. Kleitman, The crossing number of $ K_{5,n} $ , J. Combin. Theory 9 (1970) 315-323.
- [M] B. Mohar, Problem of the Month

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.