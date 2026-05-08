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

# Problem: The Erdös-Hajnal Conjecture
Slug: the_erdos_hajnal_conjecture
Canonical URL: http://www.openproblemgarden.org/op/the_erdos_hajnal_conjecture
Posted: 2007-03-18
Subject path: Graph Theory » Extremal Graph Theory
Author(s): Erdos, Paul, Hajnal, Andras
Keywords: induced subgraph

## Statement(s)
**Conjecture.** For every fixed graph $ H $ , there exists a constant $ \delta(H) $ , so that every graph $ G $ without an induced subgraph isomorphic to $ H $ contains either a clique or an independent set of size $ |V(G)|^{\delta(H)} $ .

## Discussion (from OPG)
There are numerous interesting classes of graphs which are based upon forbidding one or more induced subgraphs. For instance: chordal graphs , split graphs , and claw-free graphs. Numerous other natural classes of graphs have been proved to have such characterizations, most famously perfect graphs , but also line graphs and comparability graphs . All of these classes are very well structured (far from random) and their members all either have large cliques or independent sets. On the flip side of this are random graphs . It is well known that a random graph on $ n $ vertices has both clique and independence number highly concentrated around $ 2 \log_2 n $ . The Erdos-Hajnal conjecture suggests a fundamental separation between these two worlds in terms of independence/clique sizes. Erdös and Hajnal proved that this conjecture is true for the recursive class of graphs $ {\mathcal C} $ defined as follows. The one vertex graph is in $ {\mathcal C} $ , and if $ G_1 $ and $ G_2 $ lie in $ {\mathcal C} $ , then the disjoint union of $ G_1 $ and $ G_2 $ lies in $ {\mathcal C} $ , as does the graph obtained from the disjoint union by adding an edge between $ v_1 $ and $ v_2 $ for every $ v_1 \in V(G_1) $ and $ v_2 \in V(G_2) $ . More generally, Alon, Pach, and Solymosi proved that if $ F $ is a graph with $ V(F) = \{v_1,v_2,\ldots,v_n\} $ for which the Erdös-Hajnal conjecture holds, and $ H_1,\ldots,H_n $ are graphs for which the Erdos-Hajnal conjecture holds, then the graph obtained from $ F $ by blowing up each vertex $ v_i $ with a copy of $ H_i $ (more precisely, starting from the disjoint union of $ H_1,H_2,\ldots,H_n $ , we add all possible edges between the vertices of $ V(H_i) $ and $ V(H_j) $ if $ ij \in E(F) $ ) also satisfies the Erdos-Hajnal conjecture. The Erdös-Hajnal property is known to hold for a number of small graphs (and using the above result this may be easily bootstrapped). For instance, the conjecture is known to hold when $ H $ is a path of three edges, and recently M. Chudnovsky and S. Safra have announced a proof when $ H $ is a bull (a triangle plus two pendant edges). However, our knowledge here is still quite limited. In particular, Lovasz has suggested the following very special case which remains open. Question Is the Erdös-Hajnal conjecture true when $ H \cong C_5 $ ?

## OPG bibliography (your starting point)
- [APS] N. Alon, J. Pach, and J. Solymosi, Ramsey-type theorems with forbidden subgraphs , Combinatorica 21 (2001), 155-170.
- [EH] P. Erdös and A. Hajnal, Ramsey-type theorems, Discrete Appl. Math. 25 (1989), 37-52 MathSciNet

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.