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

# Problem: The Crossing Number of the Hypercube
Slug: the_crossing_number_of_the_hypercube
Canonical URL: http://www.openproblemgarden.org/op/the_crossing_number_of_the_hypercube
Posted: 2007-05-11
Subject path: Graph Theory » Topological Graph Theory » Crossing numbers
Author(s): Erdos, Paul, Guy, Richard K.
Keywords: crossing number, hypercube

## Statement(s)
**Conjecture.** $ \displaystyle \lim \frac{cr(Q_d)}{4^d} = \frac{5}{32} $

## Discussion (from OPG)
It is known that $ cr(Q_d) = 0 $ for $ d = 1,2,3 $ and that $ cr(Q_4) = 8 $ . No other exact values are known. Madej [M] proved that $ cr(Q_d) \le 4^d/6 + o(4^d/6) $ . Faria and de Figueiredo [FF] improved the upper bound to $ (165/1024) 4^d $ . Sykora and Vrto [SV] proved that $ 4^d/20 + o(4^d/20) $ is a lower bound on $ cr(Q_d) $ .

## OPG bibliography (your starting point)
- *[EG] P. Erdős and R.K. Guy, Crossing number problems, Amer. Math. Monthly 80 (1973) 52-58.
- [FF] L. Faria, C.M.H. de Figueiredo, On Eggleton and Guy's conjectured upper bound for the crossing number of the $ n $ -cube, Math. Slovaca 50 (2000) 271-287.
- [M] T. Madej, Bounds for the crossing number of the $ n $ -cube, J. Graph Theory 15 (1991) 81-97.
- [SV] O. Sykora and I. Vrto, On crossing numbers of hypercubes and cube connected cycles, BIT 33 (1993) 232-237.

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.