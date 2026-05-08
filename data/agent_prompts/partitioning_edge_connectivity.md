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

# Problem: Partitioning edge-connectivity
Slug: partitioning_edge_connectivity
Canonical URL: http://www.openproblemgarden.org/op/partitioning_edge_connectivity
Posted: 2007-03-07
Subject path: Graph Theory » Basic Graph Theory » Connectivity
Author(s): DeVos, Matt
Keywords: edge-coloring, edge-connectivity

## Statement(s)
**Question.** Let $ G $ be an $ (a+b+2) $ - edge-connected graph. Does there exist a partition $ \{A,B\} $ of $ E(G) $ so that $ (V,A) $ is $ a $ -edge-connected and $ (V,B) $ is $ b $ -edge-connected?

## Discussion (from OPG)
By the Nash-Williams/Tutte theorem ([NW] or [T]) on disjoint spanning trees, the above conjecture is true if $ G $ is $ 2(a+b) $ -edge-connected. This is the only partial result I know of. Here is a related conjecture. Conjecture There exists a fixed integer $ k $ so that every $ k $ -edge-connected graph $ G=(V,E) $ has a subset of edges $ S $ with the property that every edge-cut of $ G $ has between $ \frac{1}{3} $ and $ \frac{2}{3} $ of its edges in $ S $ . The values $ \frac{1}{3} $ and $ \frac{2}{3} $ are of no special importance in the above conjecture. Indeed, an affirmative answer to the above problem with $ \frac{1}{3} $ and $ \frac{2}{3} $ replaced by $ \frac{1}{t} $ and $ 1 - \frac{1}{t} $ for any $ t > 0 $ would still be valuable - and in particular, would imply the 2+epsilon flow conjecture . Definition: Let $ G=(V,E) $ be a graph and let $ P=\{E_1,E_2,...,E_t\} $ be a partition of $ E $ . We say that $ P $ is $ k $ -courteous if $ G \setminus E_i $ is $ k $ -edge-connected for every $ 1 \le i \le t $ . Problem What is the smallest integer $ t $ so that every 3-edge-connected graph has a 2-courteous coloring of size $ t $ ? It is known (see [DJS]) that $ 4 \le t \le 10 $ . It would be quite interesting if the truth were in fact $ t=4 $ . An improvement on the current upper bound would have some consequences for certain flow problems and cycle-cover problems. In general, one may define a function $ H : {\mathbb Z}^2 \rightarrow {\mathbb Z} \cup \{\infty\} $ so that $ H(a,b) $ is the smallest integer $ t $ (or $ \infty $ if none exists) so that every $ a $ -edge-connected graph has a $ b $ -courteous coloring of size $ t $ . It is known (see [DJS]) that $ H(2k+2,2k+1) = \infty $ , and that $ 2k+1 < H(2k+1,2k) < C 100^k $ . Two special cases when better values are known are $ 2 < H(4,2) < 5 $ and $ 5 < H(5,4) < 31 $ .

## OPG bibliography (your starting point)
- [DJS] M. DeVos, T. Johnson, P.D. Seymour, Cut-coloring and circuit covering
- [Ed] J. Edmonds, Minimum Partition of a Matriod into Independent Subsets, J. Res. Nat. Bur. Standards 69B (1965) 67-72. MathSciNet
- [NW] C.S.J.A. Nash-Williams, Edge Disjoint Spanning Trees of Finite Graphs, J. London Math. Soc. 36 (1961) 445-450. MathSciNet
- [T] W.T. Tutte, On the problem of decomposing a graph into n connected factors, J. London Math. Soc. 36 (1961), 221-230. MathSciNet

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.