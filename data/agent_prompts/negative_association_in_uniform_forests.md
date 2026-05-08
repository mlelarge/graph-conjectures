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

# Problem: Negative association in uniform forests
Slug: negative_association_in_uniform_forests
Canonical URL: http://www.openproblemgarden.org/op/negative_association_in_uniform_forests
Posted: 2008-06-30
Subject path: Graph Theory » Probabilistic Graph Theory
Author(s): Pemantle, Robin
Keywords: forest, negative association

## Statement(s)
**Conjecture.** Let $ G $ be a finite graph, let $ e,f \in E(G) $ , and let $ F $ be the edge set of a forest chosen uniformly at random from all forests of $ G $ . Then \[ {\mathbb P}(e \in F \mid f \in F}) \le {\mathbb P}(e \in F) \]

## Discussion (from OPG)
The FKG inequality is the cornerstone of a respectable theory of positive association; If a natural lattice condition holds, we can use it to deduce positive association. On the other hand, the theory of negative associations is still lacking good techniques. See Pemantle's lovely paper [P] for an excellent description of this situation. The conjecture highlighted above seems to be almost obviously true, but we have no tools to prove it. Modifying the conjecture by replacing "forest" by "spanning tree" gives a true statement which was proved by Feder and Mihail [FM]. Actually, they prove that this holds more generally for uniform bases of balanced matroids. Perhaps surprisingly, this is false for general matroids, see [SW].

## OPG bibliography (your starting point)
- [FM] T. Feder and M. Mihail, Balanced Matroids. Proc 24th Annual STOC 26 - 38 (1992).
- *[P] R. Pemantle, Towards a theory of negative dependence , Journal of Mathematical Physics 41 (2000), 1371–1390.
- [SW] P. D. Seymour and D. J. A. Welsh, Combinatorial applications of an inequality from statistical mechanics. Math. Proc. Camb. Phil. Soc. 77 485 - 495 (1975).

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.