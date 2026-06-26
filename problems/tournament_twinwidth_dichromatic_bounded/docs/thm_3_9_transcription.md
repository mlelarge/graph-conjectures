# Citation verification: arXiv:2310.04265 Theorem 3.9 and the 9^omega bound

Source: arXiv:2310.04265, Aboulker, Aubian, Charbit, Lopes, "Clique number of tournaments", 2023.
PDF downloaded to Refs/2310.04265.pdf (17 pages, md5 via curl from arxiv.org/pdf/2310.04265 on 2026-06-05).
Page/section references below are from `pdftotext` extraction (/tmp/paper.txt line numbers in brackets).

## Theorem 3.9 (EXACT statement) [paper Sec 3.2, ~p.6, lines 551-564]

Let T be a class of digraphs.
1. If T is a class of TOURNAMENTS that is chiVec-bounded by a function f, then T^subst
   (closure under substitution) is chiVec-bounded by function g(w) = (3 w f(w))^w.
2. If there exists K such that for every digraph D in T the underlying (undirected) graph of D
   has chromatic number at most K, then T^subst is chiVec-bounded by function g(w) = (3K)^w.

NO twin-width hypothesis appears anywhere in Theorem 3.9. The hypothesis is on the BASE class T
(chiVec-bounded tournaments / bounded-underlying-chromatic digraphs), and the conclusion is for the
SUBSTITUTION CLOSURE T^subst, not for all tournaments.

## How "chiVec(T) <= 9^{omegaVec(T)}" arises [lines 680-687]

VERBATIM (paper): "the hereditary closure of {S~_n, n in N} ... is easily seen to be exactly
{TT1, TT2, C3}^subst. Therefore the FIRST ITEM implies chiVec(T) <= 9^{omegaVec(T)} for any T which
is a SUBTOURNAMENT of some S~_n."

So the 9^omega bound is a CLASS-SPECIFIC COROLLARY of Theorem 3.9 case 1, instantiated at the base
class {TT1,TT2,C3}. It is NOT a general all-tournament inequality. (Within {TT1,TT2,C3} the only
non-acyclic member is C3 with chiVec=2, omegaVec=2 [oracle-confirmed]; the binding f collapses the
(3 w f(w))^w form to the constant base 9 => g(w)=9^w.)

## The omegaVec(S_n) >= log_9(n) lower bound [lines 705-712]

The paper DEFINES S_n = Delta(1, S_{n-1}, S_{n-1}) (S_1 = TT_1) -- IDENTICAL to the ledger's S_k.
It states chiVec(S_n) = n, and "Since S_n is obviously a subtournament of S~_n, we have therefore
omegaVec(S_n) >= log_9(n)." i.e. log_9 n = log_9 chiVec(S_n) <= omegaVec(S_n) directly from the
9^omega bound + chiVec(S_n)=n. The paper adds "it could be that this logarithm is not necessary"
and "The clique number of S_k for k>=5 is not known."

## PROVENANCE CORRECTION to ledger H5 / D2

The ledger attributes the log_9 lower bound to arXiv:2602.09863 (Crew-Fan-Koerts-Moore-Spirkl).
That is WRONG for THIS bound: omegaVec(S_n) >= log_9(n) is proved INSIDE arXiv:2310.04265 itself
(lines 705-712), as an immediate consequence of its own Theorem 3.9. No external paper is needed
for the S_k route. (arXiv:2602.09863 may separately characterize unbounded-omegaVec towers, but the
self-contained re-derivation the ledger's H5 lists -- chiVec(S_n)=n, chiVec<=9^omega via Thm 3.9 =>
omega>=log_9 n -- is the paper's OWN argument and is now verified.)

## Conjecture 3.12 is GENUINELY OPEN [lines 739-742]

"Let k >= 1. The class of tournaments with twin-width at most k is chiVec-bounded." -- stated as a
CONJECTURE. Conj 3.13 => 3.12 (Thm 3.14) is also open. So branch (b) ("3.12 trivial corollary of
Thm 3.9") is FALSE: Thm 3.9 does NOT give chiVec <= 9^omega for ALL tournaments, only for the
substitution closure of {TT1,TT2,C3}; the general bounded-tww case is unresolved.

## VERDICT: branch (a) holds

Thm 3.9 is a substitution-closure chiVec-boundedness theorem (conditional on the base class), NOT a
clean general chiVec <= 9^omega inequality. The open_crux's derivation line "chiVec(D_n) <=
9^{omegaVec(D_n)} via Thm 3.9" is SUPPORTED (not struck): D_n = S_k lies in {TT1,TT2,C3}^subst,
exactly the class the corollary covers. The seeded DISPROVE lean is NOT flipped to PROVE.

## Oracle cross-checks (run 2026-06-05)
- chiVec/omegaVec/tww(C3) = 2 / 2 / 1.
- chiVec|omegaVec over all n<=7 tournaments: {1:1, 2:3, 3:3}; chiVec|(omegaVec,tww): (1,0)->1,
  (2,1)->3, (2,2)->3, (3,3)->3.  => chiVec CAN exceed omegaVec (so 3.12 not trivially chiVec=omegaVec).
- 0 violations of chiVec <= 9^omegaVec over all 532 tournaments on n<=7; max gap chiVec-omegaVec=+1
  at (n=7, chiVec=3, omegaVec=2), occurring at twin-width 1.
