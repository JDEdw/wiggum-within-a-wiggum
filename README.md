# Wiggum Within a Wiggum (WwW)

**A two-agent AI quality loop architecture for building trust in autonomous systems.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## The Problem

You have an AI agent producing real output — newsletters, reports, code, content. The standard approach is the "Ralph Wiggum" loop: one agent runs, reflects on its own work, iterates. It works, but it has a ceiling. An agent coaching itself converges on its own blind spots.

You need something better before you hand it the keys.

## The Solution

**Two agents. Different capabilities. Clear roles.**

A more capable **coach** (e.g., Claude via Claude Code) applies a structured defect taxonomy to the **worker** agent's output, writes coaching notes, and tracks a consecutive zero-defect streak. The worker earns autonomy by hitting the streak target.

The coach never does the worker's job. It reviews, categorizes defects, writes coaching notes, and keeps score. The worker reads the coaching notes next run and improves.

```
┌─────────────────────────────────────────────────┐
│                  WwW LOOP                        │
│                                                  │
│   ┌──────────┐    output    ┌──────────────┐    │
│   │  Worker   │ ──────────> │    Coach      │    │
│   │  Agent    │             │    Agent      │    │
│   │ (Sam/     │ <────────── │ (Claude Code) │    │
│   │  Ollama)  │  coaching   │               │    │
│   └──────────┘   notes      └──────────────┘    │
│        │                          │              │
│        ▼                          ▼              │
│   [newsletter]            [defect taxonomy]      │
│   [next run]              [streak tracker]       │
│                           [coaching.md]          │
│                                                  │
│   EXIT: 5 consecutive zero-defect runs           │
│   GATE: Human confirms before independence       │
└─────────────────────────────────────────────────┘
```

## Key Ingredients

| Component | Purpose |
|-----------|---------|
| **Defect taxonomy** | Formal classification (D1-D12) so defects are tracked consistently, not ad hoc |
| **Coaching file** | Persistent notes the worker reads before every run — learns across sessions |
| **Streak tracker** | Consecutive zero-defect counter — resets to 0 on any defect |
| **Independence threshold** | 5 consecutive clean runs = ready for autonomy |
| **Human gate** | The human must explicitly confirm before the loop stops |
| **Hard fails** | Some defects (factual hallucination, collapsed content) are instant failures regardless of streak |

## The Meta-Loop Extension

WwW on its own is a daily production quality loop. But how do you build confidence *before* going live?

**Apply WwW to itself.** Run 10+ simulated production cycles in a single session:

1. Run a full production cycle (research → generate → validate)
2. Coach scores the output using the defect taxonomy
3. Fix whatever broke
4. Run the next cycle
5. Repeat until 5 consecutive zero-defect cycles

This is empirical confidence building through repeated proof, not assumption. Each cycle exercises the full pipeline including edge cases, model quirks, and integration failures.

```
Meta-Loop Session
─────────────────
C1:  3 defects → fix enforce_sources.sh regex
C2:  2 defects → fix URL dedup logic
C3:  1 defect  → fix word count enforcement
C4:  0 defects ✓
C5:  1 defect  → gateway crash recovery needed
C6:  0 defects ✓
C7:  0 defects ✓
C8:  0 defects ✓
C9:  0 defects ✓
C10: 0 defects ✓ → 5 consecutive ZD — STOP

Real bugs found and fixed: 4
Confidence: empirical, not assumed
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full system design.

### Production Pipeline (our implementation)

```
4:00am  Phase A    Research (worker agent + web search)
        ↓          validate_research.py gates output
4:20am  Phase B    Generate newsletter (LLM on local hardware)
        ↓          enforce_sources.sh mechanical fallback
        Phase C    Update index, deploy to preview server
4:30am  Guardian   Monitor script checks all systems, alerts on failure
5:00am  Wiggum     Daily QA loop — self-coaching with defect taxonomy
```

### Hardware

The reference implementation runs on consumer hardware:
- **Raspberry Pi 5** — worker agent (OpenClaw), web server, cron orchestration
- **Mini PC (Isaac)** — Ollama inference server (qwen3-coder:30b)
- **Mac** — coach agent (Claude Code), guardian scripts, Telegram relay

No cloud. No GPUs. No infrastructure bills.

## Example Files

| File | Description |
|------|-------------|
| [`examples/daily_wiggum.md`](examples/daily_wiggum.md) | Complete daily QA prompt — the worker's self-review protocol |
| [`examples/coaching.md`](examples/coaching.md) | Defect taxonomy and coaching notes — what the worker reads every run |
| [`examples/validate_links.py`](examples/validate_links.py) | Newsletter link validator — automated defect detection |
| [`examples/validate_research.py`](examples/validate_research.py) | Research checkpoint validator — gates Phase B |
| [`examples/wiggum_ollama.sh`](examples/wiggum_ollama.sh) | Launcher script — fires the daily Wiggum via cron |

## Adapting WwW to Your Use Case

The pattern is domain-agnostic. To apply it:

1. **Define your defect taxonomy.** What are the categories of errors in your domain? Which are hard fails?
2. **Write a coaching file.** Start with the taxonomy, add notes as defects appear.
3. **Build a validator.** Automated checks that catch what can be caught mechanically.
4. **Set your streak target.** 5 is our default — adjust based on your risk tolerance.
5. **Add the human gate.** The agent asks permission; the human confirms.

### Example domains

- **Code review agent** — taxonomy: security vulns, style violations, logic errors, missing tests
- **Customer support agent** — taxonomy: incorrect information, tone violations, missed escalation triggers
- **Data pipeline agent** — taxonomy: schema drift, null rate spikes, late delivery, duplicate records

## Prior Art & How This Differs

The Ralph Wiggum technique has a rich ecosystem:
- [Official Claude Code plugin](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum) by Anthropic
- [Geoffrey Huntley's original](https://github.com/ghuntley/how-to-ralph-wiggum)
- [ralph-orchestrator](https://github.com/mikeyobrien/ralph-orchestrator) — supports Telegram, multi-backend
- [Goose Ralph Loop](https://block.github.io/goose/docs/tutorials/ralph-loop/) — cross-model review

WwW extends these with specific additions not found elsewhere in the literature:

**Independence threshold:** The worker agent earns autonomy by hitting a consecutive ZD streak. The system tracks progress toward a specific target (5 consecutive ZDs) and the human confirms release. No existing implementation documents this pattern.

**Formal defect taxonomy:** D1-D12 with hard fail categories (exit code 1 regardless of total count). Quality is measured against a domain-specific taxonomy, not just pass/fail tests.

**Meta-Loop as confidence building:** Running the loop to build probabilistic pipeline confidence before deployment — tracking component confidence levels and watching them rise with each clean cycle. The math is explicit and honest.

**Coach never does the worker's job:** A hard rule that the coach agent never produces output directly. Every time the coach fixes content, the worker's path to independence gets longer.

If you've seen these patterns documented elsewhere — please open an issue. Happy to be wrong.

## Requirements

The examples in this repo use:
- [OpenClaw](https://openclaw.dev) — the agent framework running Sam on the Pi
- Ollama — local LLM inference
- A Telegram bot token (for notifications)

The WwW pattern itself is framework-agnostic. The defect taxonomy, coaching architecture, and independence threshold work with any agent framework. Adapt the example files to your stack.

## License

MIT. See [LICENSE](LICENSE).
