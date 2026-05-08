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

# Problem: The three 4-flows conjecture
Slug: three_4_flows_conjecture
Canonical URL: http://www.openproblemgarden.org/op/three_4_flows_conjecture
Posted: 2007-03-07
Subject path: Graph Theory » Coloring » Nowhere-zero flows
Author(s): DeVos, Matt
Keywords: nowhere-zero flow

## Statement(s)
**Conjecture.** For every graph $ G $ with no bridge , there exist three disjoint sets $ A_1,A_2,A_3 \subseteq E(G) $ with $ A_1 \cup A_2 \cup A_3 = E(G) $ so that $ G \setminus A_i $ has a nowhere-zero 4-flow for $ 1 \le i \le 3 $ .

## Discussion (from OPG)
A graph $ G $ has a nowhere-zero 4-flow if and only if there exist disjoint sets $ A_1,A_2,A_3 \subseteq E(G) $ with $ A_1 \cup A_2 \cup A_3 = E(G) $ so that $ G\A_i $ has a nowhere-zero 2-flow for $ 1 \le i \le 3 $ . Thus, the above conjecture is true with room to spare for such graphs. Since every 4-edge-connected graph and every 3- edge-colorable cubic graph has a nowhere-zero 4-flow, this conjecture is automatically true for these families. As with the 5-flow conjecture or the cycle double cover conjecture , establishing this conjecture comes down to proving it for cubic graphs which are not 3-edge-colorable. This conjecture is a consequence of the Petersen coloring conjecture , and it implies the Orientable cycle four cover conjecture . The latter implication follows immediately from the fact that every graph with a nowhere-zero 4-flow has an orientable cycle double cover. Actually, it is possible that for every graph $ G $ with no cut-edge, there exist disjoint sets $ A_B_1,B_2 \subseteq E(G) $ with $ A \cup B_1 \cup B_2 = E(G) $ and so that $ G\B_1 $ and $ G\B_2 $ have nowhere-zero 3-flows and $ G\A $ has a nowhere-zero 2-flow. The Petersen graph has such a decomposition ( $ B_1 $ and $ B_2 $ should be alternate edges of some 8-circuit) and so does every graph with a nowhere-zero 4-flow. If this stronger statement is true, then it would imply the oriented eight cycle four cover conjecture.

## OPG bibliography (your starting point)
- [J] F. Jaeger, On circular flows in graphs. Finite and infinite sets, Vol. I, II (Eger, 1981), 391--402, Colloq. Math. Soc. János Bolyai, 37, North-Holland, Amsterdam, 1984.. MathSciNet

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.