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

# Problem: Oriented trees in n-chromatic digraphs
Slug: oriented_trees_in_n_chromatic_digraphs
Canonical URL: http://www.openproblemgarden.org/op/oriented_trees_in_n_chromatic_digraphs
Posted: 2013-02-25
Subject path: Graph Theory » Directed Graphs
Author(s): Burr, S. A.

## Statement(s)
**Conjecture.** Every digraph with chromatic number at least $ 2k-2 $ contains every oriented tree of order $ k $ as a subdigraph.

## Discussion (from OPG)
The conjectured bound is best possible, because a regular tournament of order $ 2k-3 $ does not contain the oriented tree consisting of a vertex dominating $ k-1 $ leaves. Let $ f $ be the function $ f $ such that every oriented tree of order $ k $ is $ f(k) $ -universal, that is contained in every digraph with chromatic number at least $ f(k) $ . Burr proved that $ f(k) \leq (k-1)^2 $ . This was slightly improved by Addario-Berry et al. [AHL+] who proved $ f(k)\leq k^2/2-k/2+1 $ . Burr's conjecture has been proved only in few particular cases of digraphs: tournaments, and acyclic digraphs. Kühn, Mycroft, and Osthus [KMS] showed that every oriented tree of order $ k $ is contained in every tournament of order $ 2k-2 $ for all sufficiently large $ k $ (so proving a Conjecture of Sumner); Addario-Berry et al. [AHL+] proved that every acyclic digraph with chromatic number $ k $ contains every oriented tree of order $ k $ . Burr's conjecture or some approximation have been also proved for special classes of trees. Gallai-Roy's celebrated theorem states that every directed path of order $ k $ is $ k $ -universal; El-Sahili [E] proved that every oriented path of order $ 4 $ is $ 4 $ -universal and that the antidirected path of order $ 5 $ is $ 5 $ -universal; Addario-Berry, Havet, and Thomassé [AHT] showed that every oriented path of order $ k $ whose vertex set can be partioned into two directed paths is $ k $ -universal; Addario-Berry et al. [AHL+] showed that antidirected trees (oriented trees in which every vertex has in-degree $ 0 $ or out-degree $ 0 $ ) are $ 5k $ -universal. Havet, generalizing a conjecture of Havet and Thomassé (see [H]) on tournaments, conjectured that the following could also be true. Conjecture Every digraph with chromatic number at least $ k+\ell+1 $ contains every oriented tree of order $ k $ with $ k $ leaves.

## OPG bibliography (your starting point)
- [AHL+] L. Addario-Berry, F. Havet, C. Linhares Sales, B. Reed, and S. Thomassé. Oriented trees in digraphs. Discrete Mathematics, 313(8):967-974, 2013.
- [AHT] L. Addario-Berry, F. Havet, and S. Thomassé, Paths with two blocks in $ n $ -chromatic digraphs, J. of Combinatorial Theory Ser. B, 97 (2007), 620--626.
- * [B] A. Burr, Subtrees of directed graphs and hypergraphs, Proceedings of the Eleventh Southeastern Conference on Combinatorics, Graph Theory and Computing, Boca Raton, Congr. Numer., 28 (1980), 227--239.
- [H] F. Havet, Trees in tournaments. Discrete Mathematics 243 (2002), no. 1-3, 121--134.
- [KOM] D. Kühn, D. Osthus, and R. Mycroft, A proof of Sumner's universal tournament conjecture for large tournaments, Proceedings of the London Mathematical Society 102 (2011), 731--766.

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.