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

# Problem: Jorgensen's Conjecture
Slug: jorgensens_conjecture
Canonical URL: http://www.openproblemgarden.org/op/jorgensens_conjecture
Posted: 2007-03-10
Subject path: Graph Theory » Basic Graph Theory » Minors
Author(s): Jorgensen, Leif K.
Keywords: connectivity, minor

## Statement(s)
**Conjecture.** Every 6- connected graph without a $ K_6 $ minor is apex (planar plus one vertex).

## Discussion (from OPG)
For $ n \le 5 $ , the class of graphs with no $ K_n $ minor is very well understood. Simple graphs without $ K_3 $ minors are forests. Graphs without $ K_4 $ minors are called series-parallel graphs , and have a simple construction. Finally, Wagner [W] obtained a construction for all graphs without $ K_5 $ minors. For $ n \ge 6 $ , an explicit characterization of those graphs without $ K_n $ minors appears hopeless. The graph minors project of Robertson and Seymour give a rough structure theorem for such classes, but much remains unknown. In particular, this conjecture and Thomas' conjecture highly connected graphs with no $ K_n $ -minor suggest interesting properties of highly connected graphs without $ K_n $ minors which appear quite difficult to resolve. Part of the interest in graphs without $ K_n $ minors stems from Hadwiger's conjecture (every loopless graph without a $ K_{n+1} $ minor is $ n $ -colorable). Indeed, Wagner's work on graphs with no $ K_5 $ minor was done while studying the $ n=4 $ case of Hadwiger. More recently, Robertson, Seymour, and Thomas [RST] proved Hadwiger's conjecture for $ n=5 $ , and in doing so came somewhat close to proving Jorgensoen's conjecture. The thrust of their argument is to prove that any minimal counterexample to Hadwiger for $ n=5 $ is apex. However, in doing so, they exploit both connectivity and coloring properties of a minimal counterexample. It would appear to be difficult to modify their argument to prove Jorgensen's conjecture. DeVos, Hegde, Kawarabayashi, Norine, Thomas, and Wollan proved this conjecture true for all sufficiently large graphs [KNTWa,KNTWb].

## OPG bibliography (your starting point)
- [RST] N. Robertson, P. D. Seymour, R. Thomas, Hadwiger's conjecture for $ K\sb 6 $ -free graphs . Combinatorica 13 (1993), no. 3, 279-361. MathSciNet
- [W] K. Wagner Uber eine Eigenschaft der ebenen Komplexe, Math. Ann 114 (1937) 570-590. MathSciNet
- [KNTWa] Ken-ichi Kawarabayashi, Serguei Norine, Robin Thomas, Paul Wollan. $ K_6 $ minors in 6-connected graphs of bounded tree-width. J. Combinatorial Theory, Series B, 136:1--32, 2019
- [KNTWb] Ken-ichi Kawarabayashi, Serguei Norine, Robin Thomas, Paul Wollan. $ K_6 $ minors in large 6-connected graphs. J. Combinatorial Theory, Series B, 129:158-203, 2019.

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.