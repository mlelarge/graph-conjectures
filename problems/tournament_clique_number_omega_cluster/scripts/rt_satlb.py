"""Independent SAT-based exact omega_vec for AC_7[AC_7] (full and deletions).

omega_vec(D) = min over linear orders s of clique number of backedge graph.
We model: choose a linear order (via betweenness / position) is one route, but the
standard cleaner SAT model for 'exists order with backedge clique <= k-1' is:

omega_vec(D) <= K  iff  there exists an order s.t. backedge graph is (K)-clique-free...
Hard to SAT directly because clique-freeness is global. Instead use the EQUIVALENT
characterization via the repo's known reduction. But to stay INDEPENDENT, use:

omega_vec(D) >= k  is certified by: for the FIXED tournament, in EVERY order some k vertices
form a backedge clique = some k vertices that are 'reverse-transitively-ordered'. A backedge
k-clique is just a transitive subtournament of size k oriented so that in the chosen order
they appear in reverse. Actually: a set S is a backedge clique under order s iff s restricted
to S is the REVERSE of a topological order of the (transitive) tournament on S, i.e. S induces
a TRANSITIVE subtournament and is ordered oppositely. So a backedge clique of size k EXISTS
under order s iff there's a transitive k-subtournament whose linear (transitive) order is the
reverse of s's restriction.

So omega_vec(D) = min over orders s of [ max transitive subtournament S whose order matches
reverse of s ]. The set of transitive subtournaments is order-independent (a transitive
k-subtournament has a UNIQUE internal order). Under order s, it is a backedge clique iff s
lists it in exactly the reverse of its transitive order.

Therefore: omega_vec(D) = min over s of max over transitive subtournaments T of
[ |T| if s|T == reverse(transitive_order(T)) else (largest backedge sub-chain) ].

This is exactly: omega_vec(D) = the minimum, over orders, of the longest 'backward transitive
chain'. We can compute it via the SAT 'no backward k-clique' = order the vertices so that no
transitive k-subset is placed fully backward.

Independent exact route for n=7 (49 vtx): use an ILP/SAT solver if available; else verify the
claim differently. We have python-sat? Check.
"""
import sys
try:
    from pysat.solvers import Glucose4
    from pysat.card import CardEnc
    HAVE = True
except Exception as e:
    HAVE = False
    print("no pysat:", e)
print("pysat available:", HAVE)
sys.stdout.flush()
