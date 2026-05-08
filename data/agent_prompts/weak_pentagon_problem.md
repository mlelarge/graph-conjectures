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

# Problem: Weak pentagon problem
Slug: weak_pentagon_problem
Canonical URL: http://www.openproblemgarden.org/op/weak_pentagon_problem
Posted: 2007-07-13
Subject path: Graph Theory » Coloring » Homomorphisms
Author(s): Samal, Robert
Keywords: Clebsch graph, cut-continuous mapping, edge-coloring, homomorphism, pentagon

## Statement(s)
**Conjecture.** If $ G $ is a cubic graph not containing a triangle, then it is possible to color the edges of $ G $ by five colors, so that the complement of every color class is a bipartite graph.

## Discussion (from OPG)
This conjecture has several reformulations: the conclusion of the conjecture can be replaced by either of the following: \item $ G $ has a homomorphism to the Clebsch graph . \item there is a cut-continuous mapping from $ G $ to $ C_5 $ . For the latter variant, few definitions are in place. A cut-continuous mapping from a graph~ $ G $ to a graph~ $ H $ is a mapping $ f : E(G) \to E(H) $ such that the preimage of every cut in~ $ H $ is a cut in~ $ G $ . Here, by a cut in~ $ H $ we mean the edge-set of a spanning bipartite subgraph of~ $ H $ ---less succinctly, it is the set of all edges leaving some subset of vertices of~ $ H $ . Cut-continuous mappings are closely related with graph homomorphisms (see [DNR], [S]). In particular, every homomorphism from~ $ G $ to~ $ H $ naturally induces a cut-continuous mapping from~ $ G $ to~ $ H $ ; thus, the presented conjecture can be thought of as a weaker version of Nesetril's Pentagon problem . We mention a generalization of the conjecture, that deals with longer cycles/larger number of colors. The $ n $ -dimensional projective cube , denoted $ PQ_n $ , is the simple graph obtained from the $ (n+1) $ -dimensional cube~ $ Q_{n+1} $ by identifying pairs of antipodal vertices (vertices that differ in all coordinates). Note that $ PQ_4 $ is the Clebsch graph . Question What is the largest integer $ k $ with the property that all cubic graphs of sufficiently high girth have a homomorphism to $ PQ_{2k} $ ? Again, the question has several reformulations due to the following simple proposition. Proposition For every graph $ G $ and nonnegative integer $ k $ , the following properties are equivalent. \item There exists a coloring of~ $ E(G) $ by $ 2k+1 $ colors so that the complement of every color class is a bipartite graph. \item $ G $ has a homomorphism to $ PQ_{2k} $ \item $ G $ has a cut-continuous mapping to~ $ C_{2k+1} $ There are high-girth cubic graphs with the largest cut of size less then $ 0.94\cdot |E| $ . Such graphs do not admit a homomorphism to $ PQ_{2k} $ for any $ k \ge 8 $ , so there is indeed some largest integer~ $ k $ in the above question. To bound this largest~ $ k $ from below, recall that every cubic graph maps homomorphically to $ K_4 = PQ_2 $ . Moreover, it is known [DS] that cubic graphs of girth at least 17 admit a homomorphism to $ PQ_4 $ (the Clebsch graph). This shows $ k\ge 2 $ (and also provides a support for the main conjecture).

## OPG bibliography (your starting point)
- [DNR] Matt DeVos, Jaroslav Nesetril and Andre Raspaud: On edge-maps whose inverse preserves flows and tensions, \MRref{MR2279171}
- *[DS] Matt Devos, Robert Samal: \arXiv[High Girth Cubic Graphs Map to the Clebsch Graph}{math.CO/0602580}
- [S] Robert Samal, On XY mappings, PhD thesis, Charles University 2006, tech. report

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.