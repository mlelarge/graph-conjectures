#!/usr/bin/env python3
"""Phase 0 of the relations pipeline: merge the OPG and arXiv corpora into a
single node table, apply deterministic identity merges, extract seed edges,
and cut tagging batches.

Outputs (all under data/relations_work/):
  nodes.json    — one record per statement, namespaced ids opg:<slug> / arxiv:<safe_id>__NN
  seeds.json    — deterministic edge candidates (mentions, matches, internal refs)
  batches/batch_NN.json — tagging batches for Workflow A
"""
import json
import os
import re
from collections import defaultdict

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(ROOT, "data")
OUT = os.path.dirname(os.path.abspath(__file__))

CTX_MAX = 1500  # cap context/discussion text per node
BATCH_SIZE = 55

# OPG subject_path level-2 label -> cluster (None = needs agent tagging)
OPG_CLUSTER = {
    "Coloring": "coloring",
    "Directed Graphs": "directed",
    "Topological Graph Theory": "topological",
    "Infinite Graphs": "infinite",
    "Extremal Graph Theory": "extremal_ramsey",
    "Algebraic Graph Theory": "algebraic_spectral",
    "Hypergraphs": "hypergraphs_set_systems",
    "Probabilistic Graph Theory": "probabilistic_random",
    "Graph Algorithms": "algorithms_complexity",
    "Basic Graph Theory": None,
}


def clip(s, n=CTX_MAX):
    s = (s or "").strip()
    return s[:n] + ("…" if len(s) > n else "")


def load_json(*parts):
    with open(os.path.join(DATA, *parts)) as f:
        return json.load(f)


def main():
    problems = load_json("problems.json")
    arxiv = load_json("arxiv_conjectures.json")
    matches = load_json("arxiv_opg_matches.json")
    internal_refs = load_json("arxiv_internal_refs.json")

    nodes = []

    # ---- OPG nodes -------------------------------------------------------
    opg_by_slug = {}
    for p in problems:
        review = load_json("reviews", p["slug"] + ".json")
        sp = p.get("subject_path") or []
        cluster = OPG_CLUSTER.get(sp[1]["label"]) if len(sp) > 1 else None
        node = {
            "id": "opg:" + p["slug"],
            "source": "opg",
            "kind": "Conjecture",
            "name": p["title"],
            "statement": clip(p.get("statement_text"), 2000),
            "context": clip(p.get("discussion_text")),
            "cluster": cluster,
            "status": review.get("status"),
            "status_confidence": review.get("confidence"),
            "url": p.get("canonical_url"),
            "attributed_to": ", ".join(
                a.get("label", a.get("slug", "")) if isinstance(a, dict) else str(a)
                for a in (p.get("authors") or [])
            ),
            "posted": p.get("posted_at"),
            "same_as": [],
        }
        nodes.append(node)
        opg_by_slug[p["slug"]] = node

    # ---- arXiv nodes (review_id = safe_id__NN in file order per paper) ---
    by_paper = defaultdict(list)
    for c in arxiv:
        by_paper[c["safe_id"]].append(c)
    arxiv_nodes_by_paper = defaultdict(list)
    for sid, items in by_paper.items():
        for i, c in enumerate(items):
            rid = f"{sid}__{i:02d}"
            name_rec = load_json("arxiv_names", rid + ".json")
            review = load_json("arxiv_reviews", rid + ".json")
            node = {
                "id": "arxiv:" + rid,
                "source": "arxiv",
                "kind": c["kind"],
                "name": name_rec["nice_name"],
                "local_title": c["title"],
                "statement": clip(c.get("statement_text"), 2000),
                "context": clip(c.get("context_text")),
                "cluster": None,
                "status": review.get("status"),
                "status_confidence": review.get("confidence"),
                "url": c.get("abs_url"),
                "attributed_to": c.get("attributed_to") or "",
                "posted": c.get("published"),
                "paper_title": c.get("paper_title"),
                "same_as": [],
            }
            nodes.append(node)
            arxiv_nodes_by_paper[sid].append(node)

    # ---- identity merges from manual_confirmed arxiv_opg_matches --------
    # match["title"] looks like "Mader's Conjecture (Conjecture 2)"; the item's
    # local title ("Conjecture 2") should appear in it. Merge only when the
    # item within the paper is unambiguous.
    merged, ambiguous = 0, []
    candidate_equiv = []
    for sid, m in matches.items():
        slug = m["opg_slug"]
        if slug not in opg_by_slug or sid not in arxiv_nodes_by_paper:
            continue
        pool = arxiv_nodes_by_paper[sid]
        hits = [n for n in pool if n["local_title"] and n["local_title"] in m["title"]]
        if len(hits) != 1 and len(pool) == 1:
            hits = pool
        if m.get("manual_confirmed") and len(hits) == 1:
            hits[0]["same_as"].append("opg:" + slug)
            opg_by_slug[slug]["same_as"].append(hits[0]["id"])
            merged += 1
        else:
            candidate_equiv.append({
                "arxiv_node": hits[0]["id"] if len(hits) == 1 else None,
                "arxiv_paper": sid,
                "opg_node": "opg:" + slug,
                "match_title": m["title"],
                "score": m.get("score"),
                "manual_confirmed": bool(m.get("manual_confirmed")),
                "note": "fuzzy arxiv_opg_match; needs verification"
                        if not m.get("manual_confirmed") else
                        "manual_confirmed but ambiguous item within paper",
            })
            if m.get("manual_confirmed"):
                ambiguous.append(sid)

    # ---- seed edges: OPG title cross-mentions with quotes ----------------
    def norm(s):
        return re.sub(r"\s+", " ", (s or "").lower()).strip()

    titles = {p["slug"]: norm(p["title"]) for p in problems}
    mention_edges = []
    for p in problems:
        text = norm((p.get("statement_text") or "") + " " + (p.get("discussion_text") or ""))
        raw = re.sub(r"\s+", " ", (p.get("statement_text") or "") + " " + (p.get("discussion_text") or ""))
        for slug, t in titles.items():
            if slug == p["slug"] or len(t) < 12 or t not in text:
                continue
            i = text.find(t)
            quote = raw[max(0, i - 120):i + len(t) + 120].strip()
            mention_edges.append({
                "from": "opg:" + p["slug"],
                "mentions": "opg:" + slug,
                "quote": quote,
            })

    # ---- internal refs: paper-level hints --------------------------------
    ref_hints = []
    for sid, refs in internal_refs.items():
        for r in refs:
            tgt = r.get("studies_paper")
            ref_hints.append({
                "from_paper": sid,
                "from_nodes": [n["id"] for n in arxiv_nodes_by_paper.get(sid, [])],
                "studies_paper": tgt,
                "studies_nodes": [n["id"] for n in arxiv_nodes_by_paper.get(tgt, [])],
                "contribution": r.get("paper_contribution", ""),
            })

    # ---- write outputs ----------------------------------------------------
    with open(os.path.join(OUT, "nodes.json"), "w") as f:
        json.dump(nodes, f, indent=1, ensure_ascii=False)
    with open(os.path.join(OUT, "seeds.json"), "w") as f:
        json.dump({
            "opg_mentions": mention_edges,
            "candidate_equivalences": candidate_equiv,
            "internal_ref_hints": ref_hints,
        }, f, indent=1, ensure_ascii=False)

    # ---- tagging batches: skip arxiv nodes merged into an OPG node --------
    to_tag = [n for n in nodes if not (n["source"] == "arxiv" and n["same_as"])]
    os.makedirs(os.path.join(OUT, "batches"), exist_ok=True)
    n_batches = 0
    for i in range(0, len(to_tag), BATCH_SIZE):
        batch = [
            {
                "id": n["id"],
                "name": n["name"],
                "kind": n["kind"],
                "statement": n["statement"],
                "context": n["context"],
                "known_cluster": n["cluster"],
            }
            for n in to_tag[i:i + BATCH_SIZE]
        ]
        with open(os.path.join(OUT, "batches", f"batch_{i // BATCH_SIZE:02d}.json"), "w") as f:
            json.dump(batch, f, indent=1, ensure_ascii=False)
        n_batches += 1

    print(f"nodes: {len(nodes)} ({len(problems)} opg + {len(nodes) - len(problems)} arxiv)")
    print(f"identity merges: {merged} (ambiguous manual_confirmed: {ambiguous})")
    print(f"candidate equivalences: {len(candidate_equiv)}")
    print(f"mention edges: {len(mention_edges)}; internal ref hints: {len(ref_hints)}")
    print(f"to tag: {len(to_tag)} in {n_batches} batches of {BATCH_SIZE}")


if __name__ == "__main__":
    main()
