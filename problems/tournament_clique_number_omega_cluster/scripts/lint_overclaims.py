#!/usr/bin/env python3
"""Lint for scope overclaims (the H16/H18 recurring failure mode): a UNIVERSAL phrasing
('all', 'no ... exists', 'provably', 'dead at order N', 'minimal/exact list') that rests on a
SAMPLED or partial computation. Run after any edit to ledger.json / docs to confirm 0 residuals.

A line is FLAGGED if it matches a universal/absolute marker AND is NOT in a clearly-scoped or
documenting context. Exit code = number of flags (0 = clean)."""
import re, sys, glob, os, json

BAD = [
    r"\bPROVABLY\b", r"\bprovably (do|does|don't|doesn't|reach|transfer|exist)",
    r"all single-orbit", r"no single-orbit circulant of order", r"NO single-orbit",
    r"dead at order ?<?=?\d", r"ceiling ?=?4 below", r"of order ?<?=?\d+ (gives|has|with)",
    r"needs order ?>?=?\d", r"\b20 minimal\b", r"minimal infeasible cell", r"the 20-set list is exact",
    r"all .* have omega_vec<=\d",
]
# contexts that make a universal marker OK (scoped, or documenting a prior fix)
SCOPED = [
    "sampled", "scope tested", "exhaustive only", "exhaustive ONLY", "not exhaustive",
    "not a universal", "did not", "did NOT", "found no", "found NO", "FOUND below",
    "D36", "D37",  # decision entries that QUOTE old phrasings to document the repair
    "listed infeasible", "listed sets", "for every odd n", "for all odd n", "for every n", "infinitely many", "iso-distinct", "exhaustive", "complete scan", "all 2^",
]
BADre = [re.compile(p) for p in BAD]
def flag_line(line):
    if not any(r.search(line) for r in BADre): return False
    low = line.lower()
    if any(s.lower() in low for s in SCOPED): return False
    return True

flags = []
files = ["ledger.json"] + sorted(glob.glob("docs/*.md"))
for f in files:
    if not os.path.exists(f): continue
    if f.endswith(".json"):
        # scan each string value (the ledger is one big object; split on field for readable line context)
        blob = json.dumps(json.load(open(f)), indent=2)
        for i, line in enumerate(blob.splitlines(), 1):
            if flag_line(line): flags.append((f, i, line.strip()[:120]))
    else:
        for i, line in enumerate(open(f), 1):
            if flag_line(line): flags.append((f, i, line.strip()[:120]))

for f, i, s in flags:
    print(f"FLAG {f}:{i}: {s}")
print(f"\n{len(flags)} scope-overclaim flag(s).")
sys.exit(len(flags))
