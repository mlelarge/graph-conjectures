# Negative calibration: oriented 4-CDCs cannot explain snarks

This note records the first correction to the CDC/gadget route.

MMRT 2025 prove that an oriented $d$-cycle double cover is equivalent
to an $H_d$-flow, where

$$
H_d=\{e_i-e_j:i\ne j,\ 1\le i,j\le d\}.
$$

For $d=4$, this does give an $S^2$-flow after identifying the
hyperplane $\sum_i x_i=0$ with $\mathbb{R}^3$ and scaling. But in a
cubic graph it gives more: it induces a nowhere-zero 4-flow.

Identify the four coordinate labels with the four elements of
$\mathbb{Z}_2^2$. Map the H4 value $e_i-e_j$ to $i+j$ in
$\mathbb{Z}_2^2$. Since $i\ne j$, this value is nonzero. At a cubic
vertex, three H4 values sum to zero only when their coordinate labels
form a directed triangle, so their induced $\mathbb{Z}_2^2$ values
also sum to zero. Thus every cubic H4-flow gives a nowhere-zero
$\mathbb{Z}_2^2$-flow, equivalently a 3-edge-colouring.

Consequences:

- no snark has an oriented 4-CDC;
- Petersen is the warning example: it has an $S^2$-flow, but no
  oriented 4-CDC;
- the CDC route must use a strictly more general weighted/geometric
  certificate producing $\Sigma_4$-flows, not the discrete subset
  $H_4$.

Regression coverage lives in
[tests/test_cdc_negative_calibration.py](../tests/test_cdc_negative_calibration.py).
