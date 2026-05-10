# SMS build & smoke spike

Spike outcome on v1.0.0: **builds clean, smoke passes**. Earth–Moon
workflow is operational. v2.0.0 mainline has disqualifying drift
(removed `--thickness2` flag); v1.0.0 is the baseline for any cited run.

## Environment

- Host: darwin 25.4.0, arm64 (Apple Silicon).
- Compiler: Apple clang 21.0.0 (libc++ from MacOSX 25 SDK).
- Tooling: cmake 4.3.2, boost 1.90.0_1, coreutils 9.11 (provides `nproc` on
  PATH), python 3.11.13 in a uv venv at
  [`.venv/`](../.venv/).
- SMS clones inspected: first at mainline `cf890fda5e9da0f749a40b638998bbbf2a1cd092`
  (`v2.0.0-2-gcf890fd`, 2025-10-31), then re-pinned to tag **`v1.0.0`** at
  `2d5a22a3d3b2fcc6f5eeebdfbdbe2031b53ac55b` (2024-12-16). All
  reproducible solver runs use the v1.0.0 pin.

## What worked

On the v1.0.0 pin:

- `git submodule update --init --recursive` — pulls `cadical_sms`.
- `./build-and-install.sh -l` — clean C++ build, no patches needed (no
  `<sstream>` issue at this commit; boost headers pull it transitively).
  Local install into `~/.local/`.
- `uv pip install --python ../../.venv/bin/python .` — installs `pysms`
  into the venv (the script's `pip install .` step fails because the venv
  activation doesn't propagate into the build script's subshell — work
  around with explicit `uv pip`).
- `uv pip install --python ../../.venv/bin/python more-itertools networkx`
  — required Python deps not declared in pyproject at this tag.
- 11-vertex Earth-Moon smoke
  (`-v 11 --directed --earthmoon 9 --args-SMS " --thickness2 5"`):
  SAT in 0.38s, `ThicknessTwoChecker` invoked 3726 times, biplanar
  $\chi \ge 9$ witness emitted. Logged to `/tmp/sms_v1_smoke.log`.

On the v2.0.0-2-gcf890fd mainline (kept here as audit trail, not for use):

- C++ side built clean **after** the `<sstream>` include patch below.
- `pysms` install via `uv pip`.
- `--earthmoon` smoke **failed** because `smsg` no longer accepts
  `--thickness2`.

## Patches applied to the clone

These are local patches; not upstreamed. They live only in the (gitignored)
clone tree and need to be re-applied if the clone is ever re-created.

### Patch A — `encodings/planarity.py`: `solveArgs` arity

Required at **both v1.0.0 and v2.0.0**. This is a bug in the v1.0.0
release itself: `pysms.graph_builder.GraphEncodingBuilder.solveArgs`
already had signature `(self, args, forwarding_args)` at that tag, but
`encodings/planarity.py` shipped calling the older single-argument form.
Two-line patch following the pattern in `encodings/efx.py`:

```diff
-args = getPlanarParser().parse_args()
+args, forwarding_args = getPlanarParser().parse_known_args()
 b = PlanarGraphBuilder(args.vertices, directed=args.directed,
                        staticInitialPartition=args.static_partition,
                        underlyingGraph=args.underlying_graph)
 b.add_constraints_by_arguments(args)
-b.solveArgs(args)
+b.solveArgs(args, forwarding_args)
```

### Patch B — `src/useful.h`: missing `<sstream>` include

Required only on **v2.0.0 mainline**, not v1.0.0. Apple clang 21 / current
libc++ no longer transitively includes `<sstream>` through other headers,
and the `LOG` macro in v2's `useful.h` uses `std::ostringstream` directly
while `src/sms.cpp` uses `std::istringstream`. v1.0.0's `useful.h` includes
boost headers that pull `<sstream>` transitively, so the build is clean
there without this patch.

## v2.0.0 disqualifying drift

The smoke test from `docs/applications.md`,

```bash
python ./encodings/planarity.py -v 11 --directed --earthmoon 9 \
    --args-SMS " --thickness2 5"
```

runs end-to-end on **v1.0.0** (the build that the SAT 2023 paper
describes), but **fails on v2.0.0 mainline** because `smsg` no longer
accepts `--thickness2`. Confirmed by inspection of `src/options.cpp` on
mainline: the only planarity-related CLI flags are `--planar` and
`--planarity-frequency`. The class `ThicknessTwoChecker` still exists
in `src/graphPropagators/planarity.{hpp,cpp}` on mainline but is not
instantiated from `options.cpp`. The encoding script's
`paramsSMS["thickness2"] = "5"` would therefore be inert at minimum,
and likely wrong (the directed `--planar` propagator is *not* a
thickness-2 check). On v1.0.0 the flag exists in `smsg --help` and the
propagator's call counter increments during the smoke run, so the
encoding is actually exercised.

This is why v1.0.0 is the canonical pin: any solver run on v2 mainline
would silently relax the thickness-2 constraint, and a SAT result there
would be meaningless as Earth–Moon evidence.

## Smoke test — passed on v1.0.0

Command:

```bash
gtimeout 120 python ./encodings/planarity.py -v 11 --directed --earthmoon 9 \
    --args-SMS " --thickness2 5"
```

Result: SAT in 0.376517 s wall-clock. Solution emitted as a directed-graph
adjacency list (the biplanar decomposition representation). Statistics
include `ThicknessTwoChecker: 3726 calls, 2775 added clauses` —
confirming the propagator is wired in and the constraint is being
enforced. Full log: `/tmp/sms_v1_smoke.log`.

## Time-boxed `--earthmoon_candidate2` run

Launched on v1.0.0 with a 10-minute hard budget (the harness's per-call
maximum). Run metadata captured to
`data/candidate2_smoke/run_<timestamp>.meta.txt`, full solver output to
`data/candidate2_smoke/run_<timestamp>.log`. Outcome documented in a
follow-up commit; the planning/lit baseline does not include this run.

## Sequence for the next session (longer budget)

1. Run `--earthmoon_candidate1` (19 vertices, KSS report ~12 h) as a
   reproduction baseline; compare wall-clock to KSS.
2. Run a small published-negative regression: `--earthmoon 10` at
   $n \le 13$, expecting UNSAT (KSS: all biplanar graphs on $n \le 13$
   are 9-colourable; verify the bound from the paper body).
3. Re-run `--earthmoon_candidate2` at a multi-hour budget once we have
   confidence from steps 1–2 that the pipeline matches KSS's behaviour.
