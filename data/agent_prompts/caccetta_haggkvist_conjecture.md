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

# Problem: Caccetta-Häggkvist Conjecture
Slug: caccetta_haggkvist_conjecture
Canonical URL: http://www.openproblemgarden.org/op/caccetta_haggkvist_conjecture
Posted: 2013-02-28
Subject path: Graph Theory » Directed Graphs
Author(s): Caccetta, L., Häggkvist, Roland

## Statement(s)
**Conjecture.** Every simple digraph of order $ n $ with minimum outdegree at least $ r $ has a cycle with length at most $ \lceil n/r\rceil $

## Discussion (from OPG)
It is one of the most famous conjectures in graph theory. It has many alternative formulations and lots of work have been done around it. Many interesting conjectures are related to it. See [Sul]. It is in particular implied by a conjecture of Thomassé and Hoàng-Reed Conjecture . The Caccetta-Häggkvist Conjecture is a generalization of an earlier conjecture of Behzad, Chartrand, and Wall, who conjectured it only for diregular digraphs. Caccetta-H äggkvist Conjecture has been proved for $ r\leq \sqrt{n/2} $ by Shen [She1]. For $ r\geq n/2 $ it is trivial. But already for $ r=n/3 $ , it is still open as well as Behzad-Chartrand-Wall Conjecture Conjecture Every simple $ n $ -vertex digraph with minimum outdegree at least $ r/3 $ and minimum indegree at least $ r/3 $ has a cycle with length at most $ 3 $ . This conjecture would be implied by Seymour's Second Neighbourhood Conjecure . Shen [She2] also proved the following approximate version. Theorem Every simple digraph of order $ n $ with minimum outdegree at least $ r $ has a cycle with length at most $ n/r + 73 $ . Bollobás and Scott [BS] proposed a weighted version of the Caccetta-Häggkvist Conjecture. Conjecture Let $ w:E(D) \rightarrow [0,1] $ be a weight function on the arcs of a digraph $ D $ . If $ \sum_{u\in N^-(v)} w(uv) \geq 1 $ and $ \sum_{u\in N^+(v)} w(vu) \geq 1 $ for all $ v\in V(D) $ , then there is a directed cycle in $ D $ of total weight at least 1. They gave a nice proof that there is a directed path of total weight at least 1.

## OPG bibliography (your starting point)
- [BCW] M. Behzad, G. Chartrand, and C. Wall. On minimal regular digraphs with given girth. Fundamenta Mathematicae, 69:227–231, 1970.
- [BS] B. Bollobás and A. D. Scott, A proof of a conjecture of {B}ondy concerning paths in weighted digraphs. J. Combin. Theory Ser. B, 66:283-292, 1996.
- *[CH] L. Caccetta and R. Häggkvist. On minimal digraphs with given girth. Congressus Numerantium, XXI, 1978
- [She1J. Shen. On the girth of digraphs. Discrete Math, 211(1-3):167–181, 2000.
- [She2] J. Shen. On the Caccetta-Häggkvist conjecture. Graphs and Combinatorics, 18(3):645–654, 2002.
- [Sul] Blair D. Sullivan: A Summary of Problems and Results related to the Caccetta-Häggkvist Conjecture

Now perform the review and emit the JSON in <review_json>...</review_json> tags. Output nothing after the closing tag.