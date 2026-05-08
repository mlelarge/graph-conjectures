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

# Problem: The intersection of two perfect matchings
Slug: intersecting_two_perfect_matchings
Canonical URL: http://www.openproblemgarden.org/op/intersecting_two_perfect_matchings
Posted: 2007-08-30
Subject path: Graph Theory » Basic Graph Theory » Matchings
Author(s): Macajova, Edita, Skoviera, Martin
Keywords: cubic, nowhere-zero flow, perfect matching

## Statement(s)
**Conjecture.** Every bridgeless cubic graph has two perfect matchings $ M_1 $ , $ M_2 $ so that $ M_1 \cap M_2 $ does not contain an odd edge-cut.

## Discussion (from OPG)
Let $ G = (V,E) $ be a bridgeless cubic graph. A binary cycle (henceforth called cycle ) is a set $ C \subseteq E $ so that every vertex of $ (V,C) $ has even degree (equivalently, a cycle is any member of the binary cycle space). A postman join is a set $ J \subseteq E $ so that $ E \setminus J $ is a cycle. Note that since $ G $ is cubic, every perfect matching is a postman join. Next we state a well-known theorem of Jaeger in three equivalent forms. Theorem (Jaeger's 8-flow theorem) \item $ G $ has a nowhere-zero flow in the group $ {\mathbb Z}_2^3 $ . \item $ G $ has three cycles $ C_1,C_2,C_3 $ so that $ C_1 \cup C_2 \cup C_3 = E $ . \item $ G $ has three postman joins $ J_1,J_2,J_3 $ so that $ J_1 \cap J_2 \cap J_3 = \emptyset $ . The last of these statements is interesting, since The Berge Fulkerson Conjecture (if true) implies the following: Conjecture $ G $ has three perfect matchings $ M_1,M_2,M_3 $ so that $ M_1 \cap M_2 \cap M_3= \emptyset $ . So, we know that $ G $ has three postman joins $ J_1,J_2,J_3 $ with empty intersection, and it is conjectured that $ J_1,J_2,J_3 $ may be chosen so that each is a perfect matching, but now we see two statements in between the theorem and the conjecture. Namely, is it true that $ J_1,J_2,J_3 $ may be chosen so that one is a perfect matching? or two? The first of these was solved recently. Theorem (Macajova, Skoviera) $ G $ has two postman sets $ J_1,J_2 $ and one perfect matching $ M $ so that $ M \cap J_1 \cap J_2 = \emptyset $ The second of these asks for two perfect matchings $ M_1,M_2 $ and one postman join $ J $ so that $ M_1 \cap M_2 \cap J = \emptyset $ . It is an easy exercise to show that a set $ S \subseteq E $ contains a postman join if an only if $ S $ has nonempty intersection with every odd edge-cut. Therefore, finding two perfect matchings and one postman join with empty common intersection is precisely equivalent to the conjecture at the start of this page - find two perfect matchings whose intersection contains no odd edge-cut.

## OPG bibliography (your starting point)
- * Edita Macajova, Martin Skoviera, Fano colourings of cubic graphs and the Fulkerson conjecture. Theoret. Comput. Sci. 349 (2005), no. 1, 112--120. MathSciNet

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.