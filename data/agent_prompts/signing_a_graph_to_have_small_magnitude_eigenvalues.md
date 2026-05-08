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

# Problem: Signing a graph to have small magnitude eigenvalues
Slug: signing_a_graph_to_have_small_magnitude_eigenvalues
Canonical URL: http://www.openproblemgarden.org/op/signing_a_graph_to_have_small_magnitude_eigenvalues
Posted: 2013-03-24
Subject path: Graph Theory
Author(s): Bilu, Yonatan, Linial, Nathan
Keywords: eigenvalue, expander, Ramanujan graph, signed graph, signing

## Statement(s)
**Conjecture.** If $ A $ is the adjacency matrix of a $ d $ -regular graph, then there is a symmetric signing of $ A $ (i.e. replace some $ +1 $ entries by $ -1 $ ) so that the resulting matrix has all eigenvalues of magnitude at most $ 2 \sqrt{d-1} $ .

## Discussion (from OPG)
A graph $ H $ is a $ k $ - lift of a graph $ G $ if there is a $ k $ -to- $ 1 $ map $ f : V(H) \rightarrow V(G) $ which is locally injective in the sense that the restriction of $ f $ to the neighbourhood of every vertex is an injection. We can construct a random $ k $ -lift of $ G $ with vertex set $ V(G) \times \{1,\ldots,k\} $ by adding a (uniformly chosen) random matching between $ \{v\} \times \{1,\ldots,k\} $ and $ \{w\} \times \{1,\ldots,k\} $ whenever $ vw \in E(G) $ . If $ H $ is a $ k $ -lift of $ G $ , then every eigenvalue of $ G $ will also be an eigenvalue of $ H $ , but in addition $ H $ will have $ (k-1) |V(G)| $ new eigenvalues. There has been considerable interest and investigation into the behaviour of these new eigenvalues for a random $ k $ -lift, since it is expected that they should generally be small in magnitude. In particular, if $ G $ is a Ramanujan graph (a $ d $ -regular graph for which all nontrivial eigenvalues are at most $ 2 \sqrt{d-1} $ ) it may be possible to construct a new Ramanujan graph by taking a suitable $ k $ -lift of $ G $ . A series of increasingly strong results have shown that a random $ k $ -lift of a $ d $ -regular Ramanujan graph will have all new eigenvalues at most $ O(d^{3/4}) $ (Friedman [F]), $ O(d^{2/3}) $ (Linial and Pruder [LP]) and $ O(\sqrt{d} \log d) $ (Lubetzky, Sudakov, and Vu [LSV]). An interesting paper of Bilu and Linial [BL] investigates 2-lifts of graphs. Let $ G $ be a graph and let $ H $ be a 2-lift of $ G $ with vertex set $ V(G) \times \{1,2\} $ as above. Every eigenvector of $ G $ extends naturally to an eigenvector of $ H $ which is constant on each fiber (set of the form $ \{u\} \times \{1,2\} $ ). Thus, we may assume that all of the new eigenvalues are associated with eigenvectors which sum to zero on each fiber. So, each of these new eigenvectors is completely determined by its behaviour on $ V(G) \times \{1\} $ . Now we assign a signature $ \pm 1 $ to each edge of $ G $ to form a signed graph $ G^* $ by assigning each edge $ uv \in E(G) $ for which $ (u,1)(v,1) \in E(H) $ a sign of $ 1 $ and every other edge of $ G $ sign $ -1 $ . It is straightforward to verify that the restriction of any new eigenvector of $ H $ to $ V(G) \times \{1\} $ will then be an eigenvector of $ G^* $ . Thus, the above conjecture is equivalent to the conjecture that every $ d $ -regular graph has a $ 2 $ -lift so that all new eigenvalues have magnitude at most $ 2 \sqrt{d-1} $ . Furthermore, a positive solution to this conjecture for $ d $ -regular Ramanujan graphs would yield families of $ d $ -regular expanders.

## OPG bibliography (your starting point)
- *[BL] Y. Bilu, N. Linial, Lifts, discrepancy and nearly optimal spectral gap, Combinatorica 26 (5) (2006) 495–519. MathSciNet
- [F] J. Friedman, Relative expanders or weakly relatively Ramanujan graphs, Duke Math. J. 118 (1) (2003) 19–35. MathSciNet
- [LP] N. Linial, D. Puder, Word maps and spectra of random graph lifts, Random Structures Algorithms 37 (1) (2010) 100–135. MathSciNet
- [LSV] E. Lubetzky, B. Sudakov, V Vu, Spectra of lifted Ramanujan graphs. Adv. Math. 227 (2011), no. 4, 1612–1645. MathSciNet

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.