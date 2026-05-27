# D67: Forced-Frontier Probe

The refined width theorem gives the safe bound
\[
\operatorname{pw}(J),\operatorname{tw}(J)\le 8+2|H|.
\]
This is enough for an FPT-by-\(|H|\) theorem, but it is not enough for
general Path-FAS.  The natural next attempt is to avoid adding every
endpoint of \(H\) to every bag.  Since a feasible forced-backedge graph
must be a linear forest, one might hope to replace long closed
segments of an \(H\)-path by a constant-size summary.

`scripts/forced_frontier_probe.py` measures exactly how much of the
forced forest is live at each score-window sweep cut.

## 1. Definitions

At a sweep position \(p\), each vertex is:

* **closed** if its score window ends before \(p\);
* **active** if its score window contains \(p\);
* **future** if its score window starts after \(p\).

For the forced-backedge graph \(H\):

* an \(H\)-component is **live** if it intersects the active band, or
  if it has at least one closed vertex and at least one future vertex;
* a **dormant crossing component** has closed and future vertices but
  no active vertex;
* a **crossing \(H\)-edge** joins vertices in different
  closed/active/future categories.

The optimistic endpoint-compressed frontier size reported by the
script is
\[
  |A_p| + 2\cdot(\text{number of live }H\text{-components at }p).
\]
This is only a diagnostic.  It assumes, optimistically, that each live
forced component can be summarized by two boundary handles.  The
script does **not** prove that such a summary is sound.

## 2. What The Probe Shows

Two clean families already separate the possibilities.

### Transitive / no forced backedges

When \(H=\varnothing\), the frontier is just the active score-window
band.  Hall feasibility bounds this by 9, exactly as expected.

### Reversed matching

For the reversed-matching family on \(2m\) vertices, \(H\) is a
matching for \(m\ge 10\).  The score-window active band stays small,
but the number of live forced components grows linearly:

| m | n | \(|H|\) | max active | max live H-components | max compressed frontier |
|---:|---:|---:|---:|---:|---:|
| 10 | 20 | 10 | 7 | 10 | 27 |
| 20 | 40 | 20 | 7 | 20 | 47 |
| 40 | 80 | 40 | 7 | 40 | 87 |

So the naive compression "two handles per live \(H\)-component" does
not improve the \(8+2|H|\) theorem on this family.  It is essentially
the same bound.

This is a serious negative diagnostic.  The forced-frontier route
cannot merely compress each live component independently.  It must
also quotient many independent forced components simultaneously, or
exploit extra structure of the LFO degree/cycle constraints.

### Random skew

Random-skew samples show the same qualitative behavior at lower
density:

| n | \(|H|\) | max active | max live H-components | max compressed frontier |
|---:|---:|---:|---:|---:|
| 24 | 2  | 6 | 2  | 10 |
| 50 | 5  | 6 | 3  | 12 |
| 80 | 9  | 6 | 6  | 18 |
| 120| 14 | 7 | 11 | 28 |

The live-component count tracks the number of forced components rather
than the active-window width.  Again, componentwise endpoint
compression is not enough.

## 3. Consequence

The bounded-\(|H|\) theorem is now solid:

\[
\text{Path-FAS} \in \mathrm{FPT}(|H|).
\]

But the most naive generalization to arbitrary \(H\) fails as a
polynomial route.  Any next compression lemma must do one of two
harder things:

1. **Global quotient of many dormant components.**  Show that many
   independent live forced components are extension-equivalent and do
   not need separate identities.
2. **Exploit LFO forest constraints beyond J-width.**  Use degree-2
   and acyclicity to rule out, merge, or cheaply decide large sets of
   crossing forced components.

Without one of these, the \(2|H|\) endpoint term is not an artifact of
the proof; it is visible in the simplest matching family.

## 4. Next Mathematical Target

The right next lemma is therefore sharper than the original
"forced-forest frontier" slogan:

> **Dormant-Matching Quotient Lemma.**  In a score-window sweep where
> many disjoint forced edges are simultaneously dormant crossing
> components, their individual identities can be replaced by a
> polynomial-size aggregate without changing Path-FAS extendability.

If this lemma is true, the reversed-matching obstruction is harmless.
If false, the matching family is the substrate for the next hardness
attempt.

This is now the decisive local question for the positive route.

## 5. Reproduction

```bash
uv run python problems/path_matching_fas/scripts/forced_frontier_probe.py \
  --family reversed_matching --sizes 5,10,20,40

uv run python problems/path_matching_fas/scripts/forced_frontier_probe.py \
  --family random_skew --sizes 24,50,80,120

uv run pytest problems/path_matching_fas/tests/test_forced_frontier_probe.py -q
```
