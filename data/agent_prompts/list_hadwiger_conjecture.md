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

# Problem: List Hadwiger Conjecture
Slug: list_hadwiger_conjecture
Canonical URL: http://www.openproblemgarden.org/op/list_hadwiger_conjecture
Posted: 2014-07-07
Subject path: Graph Theory » Coloring » Vertex coloring
Author(s): Kawarabayashi, Ken-ichi, Mohar, Bojan
Keywords: Hadwiger conjecture, list colouring, minors

## Statement(s)
**Conjecture.** Every $ K_t $ -minor-free graph is $ c t $ -list-colourable for some constant $ c\geq1 $ .

## Discussion (from OPG)
Hadwiger's conjecture asserts that every $ K_t $ - minor -free graph is $ (t − 1) $ -colourable. Robertson, Seymour and Thomas [RST] proved Hadwiger's conjecture for $ t \leq 6 $ . It remains open for $ t \geq 7 $ . In fact, it is open whether every $ K_t $ -minor-free graph is $ ct $ -colourable for some constant $ c\geq 1 $ . It is natural to consider analogous problems for list colourings . First, consider planar graphs. While every planar graph is 4-colourable, Erdös, Rubin and Taylor. [ERT] conjectured that some planar graph is not 4-list-colourable, and that every planar graph is 5-list-colourable. The first conjecture was verified by Voigt [V] and the second by Thomassen [T]. More generally, Borowiecki [B] asked whether every $ K_t $ -minor-free graph is $ (t − 1) $ -list-colourable, which is true for $ t \leq 4 $ but false for $ t = 5 $ by Voigt’s example. Kawarabayashi and Mohar [KM] proposed the stated conjecture, and suggested it might be true with $ c=\frac{3}{2} $ . Barát, Joret and Wood [BJW] proved that $ c\geq\frac{4}{3} $ . In particular, they constructed a $ K_{3t+2} $ -minor-free graph that is not $ 4t $ -list-colourable.

## OPG bibliography (your starting point)
- [B] Mieczyslaw Borowiecki. Research problem 172 . Discrete Math., 121:235–236, 1993. .
- [BJW] Janos Barát, Gwenael Joret, David R. Wood. Disproof of the List Hadwiger Conjecture , Electronic J. Combinatorics 18:P232, 2011.
- [ERT] Paul Erdo ̋s, Arthur L. Rubin, and Herbert Taylor. Choosability in graphs . In Proc. West Coast Conference on Combinatorics, Graph Theory and Computing, vol. XXVI of Congress. Numer., pp. 125–157. Utilitas Math., 1980. MathSciNet .
- *[KM] Ken-ichi Kawarabayashi and Bojan Mohar. A relaxed Hadwiger’s conjecture for list colorings . J. Combin. Theory Ser. B, 97(4):647–651, 2007. MathSciNet .
- [RST] Neil Robertson, Paul D. Seymour, and Robin Thomas. Hadwiger’s conjecture for $ K_6 $ -free graphs . Combinatorica, 13(3):279–361, 1993. MathSciNet .
- [T] Carsten Thomassen. Every planar graph is 5-choosable . J. Combin. Theory Ser. B, 62(1):180–181, 1994. MathSciNet .

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.