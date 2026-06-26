"""Sample n=18 candidate skeletons across a geng residue class and report
literal-greedy (proposal) and enriched (paper-faithful) Lemma 4.7 certificate
fails. Args: n res mod  (e.g. 18 0 200 streams ~1/200 of the class)."""
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import networkx as nx
import core
import h3_lower_lemma47 as H

GENG = "/opt/homebrew/bin/geng"

def main():
    n = int(sys.argv[1]); res = int(sys.argv[2]); mod = int(sys.argv[3])
    cmd = [GENG, "-tC", "-d4", f"-D{n-9}", str(n), f"{res}/{mod}"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    tot = arb3 = lit_pass = lit_fail = enr_pass = enr_fail = 0
    enr_fail_examples = []
    for line in p.stdout:
        line = line.strip()
        if not line:
            continue
        nn, edges = core._graph6_to_edges(line)
        g = nx.Graph(); g.add_nodes_from(range(nn)); g.add_edges_from(edges)
        tot += 1
        if not H.arboricity_ge(g, 3):
            continue
        arb3 += 1
        ok, info, _ = H.lemma47_certificate(nn, edges)
        if ok: lit_pass += 1
        else: lit_fail += 1
        eok, einfo = H.lemma47_certificate_enriched(nn, edges)
        if eok: enr_pass += 1
        else:
            enr_fail += 1
            if len(enr_fail_examples) < 20:
                enr_fail_examples.append((line, einfo))
    p.wait()
    print(f"n={n} res={res}/{mod}: total={tot} arb3={arb3} "
          f"LIT(pass={lit_pass},fail={lit_fail}) "
          f"ENR(pass={enr_pass},fail={enr_fail})")
    for line, info in enr_fail_examples:
        print("  ENR-FAIL", line, info)

if __name__ == "__main__":
    main()
