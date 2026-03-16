# Probability Model for Streak Confidence

## The Question

After observing N consecutive zero-defect cycles, how confident are we that the system is reliable?

## Setup

Let p = the probability that a single cycle produces zero defects.

We observe N consecutive successes. We want to estimate p and put a lower bound on it.

## Bayesian Approach

Assume a uniform prior on p: Beta(1, 1).

After observing N successes and 0 failures, the posterior is Beta(N+1, 1).

### Expected value of p

```
E[p | N successes] = (N + 1) / (N + 2)
```

| N | E[p] |
|---|------|
| 1 | 0.667 |
| 3 | 0.800 |
| 5 | 0.857 |
| 10 | 0.917 |
| 20 | 0.955 |
| 50 | 0.981 |

### 95% Lower Bound on p

The 95% lower bound (5th percentile of the posterior) is:

```
p_lower = 0.05^(1/(N+1))
```

| N | 95% Lower Bound |
|---|-----------------|
| 1 | 0.224 |
| 3 | 0.473 |
| 5 | 0.549 |
| 10 | 0.741 |
| 20 | 0.861 |
| 28 | 0.900 |
| 50 | 0.942 |

## Why 5 Is the Default Threshold

At N = 5 consecutive clean cycles:
- Expected p = 0.857 (roughly 6 out of 7 cycles will be clean)
- 95% lower bound = 0.549 (we're 95% confident p > 0.55)

This is not a strong statistical guarantee. It is a *practical* threshold that balances:
- Enough evidence to justify reducing human oversight
- Not so many cycles that the meta-loop becomes impractical
- The human gate provides the final safety check

For high-stakes systems, increase the threshold to 10+ or 20+.

## Non-Independence Caveat

The model assumes independent trials. In practice:
- Fixes accumulate — later cycles benefit from earlier bug fixes
- The system is deterministic in some ways (same validator, same coaching file)
- Model behavior may vary with different input data

This means the true confidence is likely **higher** than the naive model for structural bugs (they get fixed permanently) but potentially **lower** for data-dependent bugs (they may only surface with certain inputs).

## Practical Recommendation

| Risk Level | Streak Target | Approx 95% LB |
|------------|--------------|----------------|
| Low (internal tool, human reviews output) | 5 | 0.55 |
| Medium (customer-facing, monitored) | 10 | 0.74 |
| High (autonomous, unmonitored) | 20+ | 0.86+ |

Always keep the human gate regardless of streak length. The model gives you confidence in the system's reliability, not a guarantee.
