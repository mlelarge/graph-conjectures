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

# Problem: Grunbaum's Conjecture
Slug: grunbaums_conjecture
Canonical URL: http://www.openproblemgarden.org/op/grunbaums_conjecture
Posted: 2007-04-04
Subject path: Graph Theory » Topological Graph Theory » Coloring
Author(s): Grunbaum, Branko
Keywords: coloring, surface

## Statement(s)
**Conjecture.** If $ G $ is a simple loopless triangulation of an orientable surface , then the dual of $ G $ is 3-edge-colorable.

## Discussion (from OPG)
The Four Color Theorem is equivalent to the statement that every cubic planar graph with no bridge is 3- edge-colorable . This is precisely equivalent to Grunbaum's conjecture restricted to the plane. Thus, Grunbaum's conjecture, if true, would imply the Four Color Theorem. Indeed, this conjecture suggests a deep generalization of the 4-color theorem. Definition: A cubic graph $ G $ is a snark if $ G $ is internally 4-edge-connected and $ G $ is not 3-edge-colorable. Grunbaum's conjecture states that no snark is the dual of a simple loopless triangulation of an orientable surface. In this light, the conjecture looks to be almost obviously false. To find a counterexample, it suffices to embed a snark in an orientable surface so that the dual has no loops or parallel edges. Of course, the difficulty is in satisfying this last constraint. All known embeddings of snarks in orientable surfaces give rise to either loops or parallel edges in the dual. It is striking to compare this conjecture with the Orientable cycle double cover conjecture . Both conjectures may be stated in terms of embedding snarks in orientable surfaces as follows: Conjecture (Grunbaum's conjecture (version 2)) Every embedding of a snark in an orientable surface has a cycle of length 1 or 2 (a loop or parallel edges) in the dual. Conjecture (Orientable cycle double cover conjecture) Every snark may be embedded in an orientable surface so that the dual graph has no cycle of length 1 (no loop). In this light it may look unlikely that both Grunbaum's conjecture and the orientable cycle double cover conjecture are true. I (M. DeVos) don't have a strong sense for or against either of these conjectures, and I don't believe there is a strong consensus among experts. Mohar and Robertson have suggested the following weak version of Grunbaum's conjecture: There exists a fixed constant $ k $ so that the dual of every loopless triangulation of an orientable surface of face-width $ >k $ is 3-edge-colorable. Robertson has suggested that this may still hold true even for nonorientable surfaces. The following conjecture is a further weakening of Grunbaum's conjecture which would allow the parameter $ k $ to depend on the surface. This is probably the weakest open problem in this vein. Conjecture (Weak Grunbaum conjecture) For every orientable surface $ \Sigma $ , there is a fixed constant $ k $ so that the dual of every loopless triangulation of $ \Sigma $ with face-width $ >k $ is 3-edge-colorable.

## OPG bibliography (your starting point)
- [G] B. Grunbaum, Conjecture 6. In Recent progress in combinatorics, (W.T. Tutte Ed.), Academic Press (1969) 343.

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.