"""Generate machine-readable certificate for the delta=4, n=10 proof.

Output: ../data/k4_n10_certificate.json

Certificate format:

{
  "metadata": {
    "theorem": "...",
    "n": 10,
    "delta": 4,
    "vertex_labels": "0..7 = v_0..v_7, 8 = x, 9 = y",
    "checker_version": "1",
    "python_version": "...",
    "generated_at_utc": "..."
  },
  "configurations": [
    {
      "S": [4, 5, 6, 7],
      "T": [5, 6],
      "u_set": [4, 7],
      "shape": "A1",
      "forced_arcs": [[0, 1], [0, 5], ...],
      "num_completions": 176,
      "completions": [
        {"arcs_hash": "...", "path": [0, 1, ...]},
        ...
      ]
    },
    ...
  ],
  "summary": {
    "total_configurations": 24,
    "total_completions": 3664,
    "total_obstructions": 0,
    "all_closed": true
  }
}

Note: this script imports from k4_independent_check.py only (the
shared-code-free module). The certificate is reproducible by running:

  uv run python scripts/k4_independent_check.py

and then generating this file.
"""

import json
import sys
import platform
import datetime
from pathlib import Path
from k4_independent_check import all_valid_st, check_st_pair


PROBLEM_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROBLEM_ROOT / 'data'


def classify_shape(S, T):
    """Classify (S, T) as Shape A1, A2, or B based on cyclic-run lengths of S.

    V(C) = {1, ..., 7} cyclically. |S| = 4. Possible run multisets:
    - [4]: Shape A1 (4-cyclic-interval).
    - [3, 1]: Shape A2 (3-block + isolated).
    - [2, 2]: Shape B (2 separated pairs).
    """
    S_set = set(S)
    if len(S_set) != 4:
        return f'unknown(|S|={len(S_set)})'

    # Find an anchor vertex not in S to break the cyclic ambiguity.
    anchor = None
    for v in range(1, 8):
        if v not in S_set:
            anchor = v
            break
    if anchor is None:
        return f'unknown(S=V(C))'

    # Walk the cycle starting just after the anchor, recording runs.
    runs = []
    next_v = anchor + 1 if anchor < 7 else 1
    cur_run = 0
    for _ in range(7):
        if next_v in S_set:
            cur_run += 1
        else:
            if cur_run > 0:
                runs.append(cur_run)
                cur_run = 0
        next_v = next_v + 1 if next_v < 7 else 1
    if cur_run > 0:
        runs.append(cur_run)

    run_multiset = sorted(runs, reverse=True)
    if run_multiset == [4]:
        return 'A1'
    if run_multiset == [3, 1]:
        return 'A2'
    if run_multiset == [2, 2]:
        return 'B'
    return f'unknown(runs={run_multiset})'


def main():
    pairs = all_valid_st()
    print(f"Generating certificate for {len(pairs)} (S, T) configurations...")

    configurations = []
    total_completions = 0
    total_obstructions = 0

    for (S, T) in pairs:
        result = check_st_pair(S, T)
        if result['status'] != 'closed':
            print(f"  WARNING: S={result['S']} T={result['T']}: {result['status']}")
            total_obstructions += result.get('num_obstructions', 0)
            continue
        shape = classify_shape(set(result['S']), set(result['T']))
        u_set = sorted(set(result['S']) - set(result['T']))
        configurations.append({
            'S': result['S'],
            'T': result['T'],
            'u_set': u_set,
            'shape': shape,
            'forced_arcs': [[u, v] for (u, v) in result['forced_arcs']],
            'forced_arc_count': result['forced_arc_count'],
            'num_completions': result['num_completions'],
            'completions': result['completions'],
        })
        total_completions += result['num_completions']
        print(f"  S={result['S']} T={result['T']} ({shape}): "
              f"{result['num_completions']} completions")

    certificate = {
        'metadata': {
            'theorem': "Every oriented graph D with delta+(D) >= 4 and |V(D)| = 10 contains a directed simple path of length 8.",
            'n': 10,
            'delta': 4,
            'vertex_labels': "0..7 = v_0..v_7, 8 = x, 9 = y",
            'cycle_C': "v_1 -> v_2 -> ... -> v_7 -> v_1",
            'checker_version': '1',
            'python_version': platform.python_version(),
            'generated_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'rule_set': [
                'R-loop', 'R-path', 'R-cycle', 'R-T', 'R-F3',
                'R-Claim12', 'R-LemmaA-rev', 'R-AP', 'R-out',
                'R-score', 'R-VCS', 'P1', 'P2',
            ],
            'source': 'scripts/k4_independent_check.py',
        },
        'configurations': configurations,
        'summary': {
            'total_configurations': len(configurations),
            'total_completions': total_completions,
            'total_obstructions': total_obstructions,
            'all_closed': total_obstructions == 0 and len(configurations) == len(pairs),
        },
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / 'k4_n10_certificate.json'
    with open(out_path, 'w') as f:
        json.dump(certificate, f, indent=2, sort_keys=True)
    print()
    print(f"Wrote certificate to {out_path.relative_to(PROBLEM_ROOT)}")
    print(f"  configurations: {certificate['summary']['total_configurations']}")
    print(f"  total completions: {certificate['summary']['total_completions']}")
    print(f"  total obstructions: {certificate['summary']['total_obstructions']}")
    print(f"  all closed: {certificate['summary']['all_closed']}")


if __name__ == '__main__':
    main()
