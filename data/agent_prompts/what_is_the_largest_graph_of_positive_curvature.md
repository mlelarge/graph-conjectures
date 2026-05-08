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

# Problem: What is the largest graph of positive curvature?
Slug: what_is_the_largest_graph_of_positive_curvature
Canonical URL: http://www.openproblemgarden.org/op/what_is_the_largest_graph_of_positive_curvature
Posted: 2007-03-10
Subject path: Graph Theory » Topological Graph Theory » Planar graphs
Author(s): DeVos, Matt, Mohar, Bojan
Keywords: curvature, planar graph

## Statement(s)
**Problem.** What is the largest connected planar graph of minimum degree 3 which has everywhere positive combinatorial curvature, but is not a prism or antiprism ?

## Discussion (from OPG)
Definition: For a graph $ G $ embedded in the sphere, the combinatorial curvature of a vertex $ v $ is defined to be $ 1 - \frac{ {\mathit deg}(v)}{2} + \sum_{f \sim v} \frac{1}{ {\mathit size}(f) } $ (here the summation is over all faces $ f $ incident with $ v $ ). Let $ G $ be a graph embedded in the sphere, and consider the polygonal surface formed by treating each face of size $ n $ as a regular $ n $ -gon of side length $ 1 $ . The gaussian curvature at a vertex $ v $ is defined to be $ 2 \pi $ minus the sum of the angles incident with $ v $ . So, our vertex $ v $ has positive curvature if the sum of the incident angles is less than $ 2 \pi $ . In fact, the combinatorial curvature at $ v $ is exactly $ 2 \pi $ times the gaussian curvature, so these quantities will always have the same sign. Let us call a convex polyhedron regular-faced if each face is a regular polygon. Based on the previous discussion, we know that every convex regular-faced polyhedron gives us a graph with everywhere positive combinatorial curvature. Indeed, we may view planar graphs with everywhere positive curvature as a kind of generalization of these polyhedra. The polyhedra in this class have been studied and classified. The Platonic solids and Archimedean solids are all convex and regular faced, and there are two infinite families: prisms and antiprisms . In addition to this, there are 92 other exceptional ones, known as Johnson Solids . Euler's formula tells us that the sum of the combinatorial curvatures over all of the vertices is equal to 2. Indeed, the combinatorial curvature is exactly what we get when we assign $ 1 $ to each vertex and face, $ -1 $ to each edge, and then "discharge" evenly onto the vertices. So, if we wish to construct large planar graphs where every vertex has positive curvature, we will need to make the curvature arbitrarily small. This can be achieved with prisms and antiprisms, but apart from these two families, all other graphs with everywhere positive curvature have a bounded number of vertices. Improving upon [DM], Zhang [Z] has shown this upper bound to be at most 580. The great rhombicosidodecahedron has 120 vertices and everywhere positive curvature (this is the largest regular-faced convex polyhedron which is not a prism or antiprism). Reti, Bitay, and Kosztolanyi [RBK] have improved upon this lower bound by constructing a graph with everywhere positive curvature and 138 vertices. These are the best bounds I (M. DeVos) know of.

## OPG bibliography (your starting point)
- [DM] M. DeVos and B. Mohar, An analogue of the Descarte-Euler formula for infinite graphs and Higuchi's conjecture preprint.
- [H] Y. Higuchi, Combinatorial curvature for planar graph, J. Graph Theory, Vol 38 (2001), no. 4, 220-229. MathSciNet
- [RBK] T. Reti, E. Bitay, and Zs. Kosztolanyi, On the polyhedral graphs with positive combinatorial curvature , Acta Polytechnica Hungarica Vol. 2, No. 2 (2005) 19-37.
- [Z] L. Zhang, A result on combinatorial curvature for embedded graphs on a surface, Discrete Math (2007) in press

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.