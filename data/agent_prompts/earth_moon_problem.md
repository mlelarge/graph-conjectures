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

# Problem: Earth-Moon Problem
Slug: earth_moon_problem
Canonical URL: http://www.openproblemgarden.org/op/earth_moon_problem
Posted: 2013-03-06
Subject path: Graph Theory » Coloring » Vertex coloring
Author(s): Ringel, G.

## Statement(s)
**Problem.** What is the maximum number of colours needed to colour countries such that no two countries sharing a common border have the same colour in the case where each country consists of one region on earth and one region on the moon ?

## Discussion (from OPG)
In term of graphs, it can be rephrased as follows. What is the maximum chromatic number of a graph $ G $ which is the union of two planar graphs (on the same vertex set)? If a graph $ G $ on $ n $ vertices is the union of two planar graphs, then it has at most $ 2(3n-6) $ edges, and so it is has a vertex of degree at most $ 11 $ . An easy induction shows that $ G $ is 12-colourable, as observed by Heawood [He]. Gardner [G] reported an example requiring 9 colours (the join of $ C_5 $ and $ K_6 $ ). It is not known if configurations exist requiring 10, 11, or 12 colours. More generally, one may ask for the maximum chromatic number of the union of $ k $ planar graphs. Problem What is the maximum chromatic number of a graph $ G $ which is the union of $ k $ planar graphs? The same reasoning as above shows that $ 6k $ colours are always sufficient. The minimum number of planar graphs to decompose a complete graph [BW] gives a lower bound of $ 6k-2 $ for $ k \ne 2 $ .

## OPG bibliography (your starting point)
- [BW] L. W. Beineke and A. T. White, Topological Graph Theory, Selected Topics in Graph Theory, L. W. Beineke and R. J. Wilson, eds., Academic Press, 15-50, 1978.
- [G] M. Gardner, Mathematical Recreations: The Coloring of Unusual Maps Leads Into Uncharted Territory. Sci. Amer. 242, 14-22, 1980.
- [He] P.J. Heawood, Map Colour Theorems. Quart. J. Pure Appl. Math. 24, 332-338, 1890.
- *[R] G. Ringel, Färbungsprobleme auf Flachen und Graphen. Berlin: Deutsche Verlag der Wissenschaften, 1959.

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.