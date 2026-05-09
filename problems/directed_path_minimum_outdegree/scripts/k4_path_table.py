"""Generate a per-(S, T) length-8 path table for the (2,2,1,1) closure proof.

Output: a Markdown table of (S, T) -> sample length-8 path, suitable for
inclusion in the proof artifact.

Vertex labelling: 0..7 = v_0..v_7, 8 = x, 9 = y.
"""

import itertools
from k4_local_miner import (
    V_D, V_C, derive_forced, has_path_of_length, pred_C,
    shape_A1_configs, shape_A2_configs, shape_B_configs,
)
from k4_audit import find_path_of_length


def vertex_label(v: int) -> str:
    if v < 8:
        return f"v_{v}"
    if v == 8:
        return "x"
    if v == 9:
        return "y"
    return f"?{v}"


def fmt_path(path):
    return " -> ".join(vertex_label(v) for v in path)


def find_all_paths_of_length(adj, target=8, limit=100):
    """Return up to `limit` distinct directed simple paths of length target."""
    found = []
    def dfs(v, visited, path):
        if len(path) - 1 == target:
            found.append(list(path))
            return
        if len(found) >= limit:
            return
        for w in sorted(adj[v]):
            if w not in visited:
                visited.add(w)
                path.append(w)
                dfs(w, visited, path)
                if len(found) >= limit:
                    return
                path.pop()
                visited.discard(w)

    for start in sorted(adj):
        if len(found) >= limit:
            break
        visited = {start}
        path = [start]
        dfs(start, visited, path)
    return found


def collect_per_st_paths():
    """For each (S, T), find a sample length-8 path that holds in EVERY
    completion (or report multiple paths if no single path works)."""
    all_configs = []
    for label, S, T, _, _ in shape_A1_configs():
        all_configs.append((label, S, T))
    for label, S, T, _, _ in shape_A2_configs():
        all_configs.append((label, S, T))
    for label, S, T, _, _ in shape_B_configs():
        all_configs.append((label, S, T))

    table = []
    for label, S, T in all_configs:
        result = derive_forced(S, T)
        if result is None or len(result) == 2:
            continue
        forced, forbidden, out_confirmed, out_excluded = result

        # Free choices
        free_choices = []
        for v in V_D:
            need = 4 - len(out_confirmed[v])
            if v in S:
                cand_set = V_C - {v} - out_excluded[v] - out_confirmed[v]
            else:
                cand_set = V_D - {v} - out_excluded[v] - out_confirmed[v]
            if need > 0:
                free_choices.append((v, need, sorted(cand_set)))
        free_choices.sort(key=lambda x: (len(x[2]) - x[1], x[0]))

        # Enumerate all completions, find common length-8 paths
        completions_paths = []

        def recurse(idx, arcs):
            if idx == len(free_choices):
                # Antiparallel check
                for (a, b) in arcs:
                    if (b, a) in arcs:
                        return
                # 4-outregular
                out_count = {v: 0 for v in V_D}
                for (u, _) in arcs:
                    out_count[u] += 1
                if any(out_count[v] != 4 for v in V_D):
                    return
                adj = {v: set() for v in V_D}
                for (u, w) in arcs:
                    adj[u].add(w)
                paths = find_all_paths_of_length(adj, target=8, limit=10)
                completions_paths.append(paths)
                return

            v, need, cand = free_choices[idx]
            valid_cand = [w for w in cand if (w, v) not in arcs]
            if len(valid_cand) < need:
                return

            for combo in itertools.combinations(valid_cand, need):
                for w in combo:
                    arcs.add((v, w))
                recurse(idx + 1, arcs)
                for w in combo:
                    arcs.discard((v, w))

        initial = set(forced)
        recurse(0, initial)

        # Find a path that's present in MAX number of completions (ideally all)
        path_counts = {}
        for paths in completions_paths:
            seen = set()
            for path in paths:
                key = tuple(path)
                if key in seen:
                    continue
                seen.add(key)
                path_counts[key] = path_counts.get(key, 0) + 1

        n_comp = len(completions_paths)
        # Sort by completion-count descending
        ranked = sorted(path_counts.items(), key=lambda x: -x[1])
        best_path = list(ranked[0][0]) if ranked else None
        best_count = ranked[0][1] if ranked else 0

        table.append({
            'label': label,
            'S': sorted(S),
            'T': sorted(T),
            'num_completions': n_comp,
            'best_path': best_path,
            'best_path_coverage': best_count,
            'covers_all': best_count == n_comp,
        })
    return table


def main():
    table = collect_per_st_paths()
    print("# Length-8 path table for (2,2,1,1) closure at n=10")
    print()
    print("Each entry shows a length-8 directed simple path that exists in")
    print("the **majority** of completions of the given (S, T) configuration.")
    print("If `covers_all` is true, the path is present in **every** completion.")
    print()
    print("Vertex labelling: v_0..v_7 are path vertices (with longest path")
    print("v_0 -> v_1 -> ... -> v_7), x and y are the two off-path vertices.")
    print()
    print("| Label | S | T | #completions | best path | covers_all |")
    print("|---|---|---|---:|---|:---:|")
    for entry in table:
        path_str = fmt_path(entry['best_path']) if entry['best_path'] else "n/a"
        covers = "yes" if entry['covers_all'] else f"{entry['best_path_coverage']}/{entry['num_completions']}"
        S_str = ', '.join(f"v_{s}" for s in entry['S'])
        T_str = ', '.join(f"v_{t}" for t in entry['T'])
        print(f"| {entry['label']} | {{{S_str}}} | {{{T_str}}} | {entry['num_completions']} | {path_str} | {covers} |")


if __name__ == '__main__':
    main()
