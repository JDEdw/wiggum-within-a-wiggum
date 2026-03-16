# The Meta-Loop

## Concept

The Meta-Loop applies the WwW quality loop to itself. Instead of running one production cycle per day and waiting to see if it works, you run 10+ simulated cycles in a single session. Each cycle exercises the full pipeline. You fix what breaks between cycles. You stop when you hit the streak target.

This converts "I think it works" into "I ran it 24 times, found and fixed 9 bugs, and the last 5 were clean."

## How It Works

```
SESSION START
│
├── C1: Full pipeline run
│   └── Coach scores: 3 defects (D1, D7, D7)
│       Fix: regex in enforce_sources.sh
│
├── C2: Full pipeline run
│   └── Coach scores: 1 defect (D6)
│       Fix: URL dedup logic
│
├── C3: Full pipeline run
│   └── Coach scores: 0 defects ✓ (streak: 1)
│
├── C4: Full pipeline run
│   └── Coach scores: 2 defects (D1, D12)
│       streak reset to 0
│       Fix: source verification post-processor
│
├── ...
│
├── C20: 0 defects ✓ (streak: 5)
│   └── STOP — confidence threshold met
│
SESSION END
```

## What You Learn

Each cycle has the potential to surface a different class of failure:

- **C1-C5**: Obvious bugs. Missing files, wrong paths, broken regex.
- **C5-C10**: Edge cases. What happens when the model returns markdown fences? When a source is paywalled? When the gateway crashes mid-generation?
- **C10-C15**: Interaction effects. The word count trimmer breaks a URL. The dedup logic removes a story's only source. The research validator passes placeholder content.
- **C15+**: Stability proof. If you can run 5 consecutive clean cycles after fixing everything above, you have empirical evidence the system works.

## Nuclear Clean Between Cycles

Each cycle must start from a clean state to simulate real production:

```bash
# Delete all session artifacts
find ~/.openclaw -name "*.jsonl" -delete
echo '{"version":1,"sessions":{}}' > ~/.openclaw/agents/main/sessions/sessions.json
find ~/.openclaw -name "*.session" -delete
find ~/.openclaw -name "transcript*" -delete

# Clear previous output
rm -f research_checkpoint.md research_status.txt
rm -f preview-site/f1/f1-newsletter-*.html
```

Without nuclear cleans, the agent may use cached context from previous cycles, hiding real failures.

## Probability Model

After N consecutive zero-defect cycles, you can estimate the probability of the next cycle being clean.

If you assume each cycle is an independent trial with unknown probability p of success:

- After 5 consecutive successes with a uniform prior on p, the expected value of p is 6/7 (≈ 0.857).
- The 95% lower bound on p is approximately 0.45 — which is why 5 is a minimum, not a guarantee.

To get a 95% lower bound of p > 0.90, you need approximately 28 consecutive successes.

In practice, cycles are not independent (fixes accumulate), so the actual confidence is higher than the naive model suggests. But the model gives you a floor.

See [probability-model.md](probability-model.md) for the math.

## When to Use the Meta-Loop

Use it when:
- Deploying a new agent pipeline for the first time
- After significant changes to the pipeline (new model, new validator, new prompt)
- After a production failure — run the meta-loop to verify the fix

Don't use it when:
- Making a minor config change (just run one cycle)
- The daily Wiggum is already tracking a clean streak
