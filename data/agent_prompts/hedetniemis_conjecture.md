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

# Problem: Hedetniemi's Conjecture
Slug: hedetniemis_conjecture
Canonical URL: http://www.openproblemgarden.org/op/hedetniemis_conjecture
Posted: 2008-05-25
Subject path: Graph Theory » Coloring » Vertex coloring
Author(s): Hedetniemi, Stephen T.
Keywords: categorical product, coloring, homomorphism, tensor product

## Statement(s)
**Conjecture.** If $ G,H $ are simple finite graphs, then $ \chi(G \times H) = \min \{ \chi(G), \chi(H) \} $ .

## Discussion (from OPG)
This beautiful and seemingly innocent conjecture asserts a deep and important property of graph coloring. It is undoubtedly one of the most significant unsolved problems in graph coloring and graph homomorphisms. We write $ G \rightarrow H $ if there is a homomorphism from $ G $ to $ H $ . The graph $ G \times H $ has a two natural projection maps (projecting onto either the first or second coordinate), and these maps are homomorphisms to $ G $ and to $ H $ . So, in short, $ G \times H \rightarrow G $ and $ G \times H \rightarrow H $ . A graph is $ n $ -colorable if and only if it has a homomorphism to $ K_n $ . Combining this with the transitivity of $ \rightarrow $ we find that $ \chi(G \times H) \le \min\{ \chi(G), \chi(H) \} $ (indeed, if $ \chi(G) = n $ , then $ G \times H \rightarrow G $ and $ G \rightarrow K_n $ , so $ G \times H \rightarrow K_n $ - equivalently, $ G \times H $ is $ n $ -colorable). So, the hard direction of Hedetniemi's Conjecture is to prove that $ \chi(G \times H) \ge \min \{ \chi(G), \chi(H) \} $ . Let's define $ P(n) $ to be the proposition that $ \chi(G \times H) \ge n $ whenever $ \chi(G) \ge n $ and $ \chi(H) \ge n $ . Then the above conjecture is equivalent to the statement that $ P(n) $ holds for every positive integer $ n $ . Now $ P(1) $ holds trivially and $ P(2) $ follows from the observation that the product of two graphs each of which contains an edge is a graph which contains an edge. The next case is quite easy too, if $ \chi(G) \ge 3 $ and $ \chi(H) \ge 3 $ , then both $ G $ and $ H $ contain an odd cycle. Since the product of two odd cycles contains an odd cycle, this shows $ \chi(G \times H) \ge 3 $ . The next case up, $ P(4) $ was proved by El-Zahar and Sauer by way of a beautiful argument. It is open for all higher values. A key tool in the proof of El-Zahar and Sauer is the use of exponential graphs. For any pair of graphs $ G, H $ the exponential graph $ G^H $ is a graph whose vertex set consists of all mappings $ f: V(H) \rightarrow V(G) $ . Two vertices $ f,g $ are adjacent if $ f(x)g(y) $ is an edge of $ G $ whenever $ xy $ is an edge of $ H $ . It is easy to see the relevance of $ K_n^G $ to this problem. If we have an $ n $ -coloring $ f $ of $ G \times H $ , then for every vertex $ x \in V(H) $ , there is a mapping $ f_x : V(G) \rightarrow V(K_n) $ given by $ f_x(v) = f(v,x) $ . This associates each $ x \in V(H) $ with a vertex in $ K_n^G $ . Now it is easy to verify that whenever $ x,y $ are adjacent vertices in $ H $ , the maps $ f_x $ and $ f_y $ are adjacent in $ K_n^G $ . Rather more surprisingly, Hedetniemi's conjecture may be reformulated as follows: Conjecture (version 2 of Hedetniemi) If $ \chi(G) > n $ , then $ K_n^G $ is $ n $ -colorable. The following conjecture asserts that Hedetniemi's conjecture still holds with circular chromatic number instead of the usual chromatic number. Here $ \chi_c(G) $ is the circular chromatic number of $ G $ . Since $ \chi(G) = \lceil \chi_c(G) \rceil $ this is a generalization of the original conjecture. Conjecture (Zhu) If $ G $ and $ H $ are finite simple graphs then $ \chi_c(G \times H) = \min\{ \chi_c(G), \chi_c(H) \} $ . A graph $ G $ has circular chromatic number $ \frac{n}{k} $ for positive integers $ n,k $ if and only if $ G $ has a homomorphism to the graph $ K_{n/k} $ . This is a graph whose vertex set consists of $ n $ vertices cyclically ordered, with two vertices adjacent if they are distance $ \ge k $ apart in the cyclic ordering. So again, we may state this conjecture in terms of homomorphisms to graphs of the form $ K_{n/k} $ . More generally, let us call a graph $ K $ multiplicative if $ G \times H \rightarrow K $ implies either $ G \rightarrow K $ or $ H \rightarrow K $ . Now Hedetniemi's conjecture asserts that every $ K_n $ is multiplicative and Zhu's conjecture asserts that every $ K_{n/k} $ is multiplicative. With this terminology, El-Zahar and Sauer proved that $ K_3 $ is multiplicative. A clever generalization of their argument due to Haggkvist, Hell, Miller and Neumann Lara showed that every odd cycle is multiplicative. Recently, Tardif bootstrapped this theorem with the help of a couple of interesting operators on the category of graphs to prove the $ K_{n/k} $ is multiplicative whenever $ n/k < 4 $ . Ignoring trivial cases and equivalences, these are essentially the only graphs known to be multiplicative. It might be tempting to hope that all graphs are multiplicative, but this is false. To construct a non-multiplicative graph, take two graphs $ G,H $ with the property that $ G \not\rightarrow H $ and $ H \not\rightarrow G $ (for instance $ K_3 $ and the Grotzsch Graph). Now $ G \times H $ is not multiplicative since $ G \not\rightarrow G \times H $ and $ H \not\rightarrow G \times H $ , but $ G \times H \rightarrow G \times H $ . It seems that there is no general conjecture as to what graphs are multiplicative. Some other Cayley graphs look like reasonable candidates to me (M. DeVos), but I haven't any evidence one way or the other. Poljak and Rodl defined the function $ f(n) = \min \{ \chi(G \times H) : \chi(G) = n = \chi(H) \} $ . So, Hedetniemi's conjecture is equivalent to $ f(n) = n $ . Using an interesing inequality relating the chromatic number of a digraph $ D $ to the chromatic number of a type of line graph of $ D $ , they were able to prove the following quite surprising result: Either $ f $ is bounded by $ 9 $ or $ \lim_{n \rightarrow \infty} f(n) = \infty $ . There are a number of interesting partial results not mentioned here, and the reader is encouraged to see the survey article by Zhu.

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.