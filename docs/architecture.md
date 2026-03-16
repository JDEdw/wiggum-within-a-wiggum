# Architecture

## System Overview

WwW operates as a layered quality system with three levels of defense:

```
Level 1: Worker Self-Check
  The worker agent reads coaching.md before every run.
  It applies lessons from previous defects to new output.

Level 2: Mechanical Validation
  Automated scripts (validate_links.py, validate_research.py,
  enforce_sources.sh) catch objective, measurable defects.

Level 3: Coach Review
  A more capable agent applies the full defect taxonomy,
  including judgment calls that automation can't make
  (factual accuracy, summary quality, story prioritization).
```

## Component Roles

### Worker Agent
- Produces the actual output (newsletter, report, etc.)
- Reads coaching.md at the start of every run
- Has tool access: file editing, web search, messaging
- Runs on local/cheap hardware (Ollama on a mini PC)
- Never sees the coach's internal reasoning — only coaching notes

### Coach Agent
- Reviews worker output against the defect taxonomy
- Writes coaching notes (specific, actionable, taxonomy-tagged)
- Tracks the consecutive zero-defect streak
- Never produces the output directly
- Runs on a capable model (Claude via Claude Code)

### Validators
- `validate_research.py` — gates the research phase (minimum URLs, story count, no placeholders)
- `validate_links.py` — checks newsletter HTML for link defects, word counts, duplicates
- `enforce_sources.sh` — mechanical fallback that strips banned sources and deduplicates URLs

### Guardian
- Monitoring script that runs between pipeline phases
- Checks: Is the inference server up? Did the previous phase complete? Is the web server running?
- Auto-recovers from common failures (restart gateway, regenerate from checkpoint)
- Alerts the human on unrecoverable failures

## Data Flow

```
coaching.md ──────────────────────────────────────┐
                                                   │
research_checkpoint.md                             ▼
  │                                          ┌──────────┐
  │ validate_research.py                     │  Worker   │
  │ (gate: min URLs, stories, no placeholders)│  Agent   │
  ▼                                          └────┬─────┘
generate_newsletter.sh                            │
  │                                               │
  │ enforce_sources.sh (mechanical fallback)      │
  ▼                                               │
newsletter-YYYY-MM-DD.html                        │
  │                                               │
  │ validate_links.py (D1-D12 checks)            │
  ▼                                               │
defect_report ───────────────────────────────> ┌──┴───────┐
                                               │  Coach   │
coaching_notes ◄─────────────────────────────  │  Agent   │
                                               └──────────┘
streak_counter ◄───────────────────────────────────┘
```

## Defect Taxonomy

| ID | Name | Severity | Automated? |
|----|------|----------|------------|
| D1 | Incorrect source link | Standard | Yes (HTTP check) |
| D2 | Front page link | Standard | Yes (redirect detection) |
| D3 | Duplicate source in one summary | Standard | Yes |
| D4 | Missing article link | Standard | Yes |
| D5 | Article too old | Standard | No (requires judgment) |
| D6 | Source sharing between stories | Standard | Yes |
| D7 | Poor summary quality | Standard | Partial (word count) |
| D8 | Conflicting sources | Standard | No |
| D9 | Collapsed story (details/summary) | **Hard fail** | Yes |
| D10 | Factual hallucination | **Hard fail** | No |
| D11 | Single source on major story | **Hard fail** | Partial |
| D12 | Source doesn't confirm story | **Hard fail** | No |

Hard fails reset the streak regardless of total defect count.

## Independence Protocol

```
if consecutive_clean_days >= 5:
    send_message_to_human(
        "I have achieved N consecutive zero-defect runs."
        "I appear ready to run independently."
        "Shall I stop the daily loop?"
    )
    # Human must explicitly confirm
    # Agent continues running until confirmation received
```

The human gate is non-negotiable. The agent never self-promotes.

## Failure Recovery

The system handles common failures automatically:

| Failure | Recovery |
|---------|----------|
| Inference server down | Guardian restarts, re-warms model |
| Gateway crash | Guardian restarts gateway, regenerates from checkpoint |
| Empty/placeholder research | validate_research.py blocks generation |
| No newsletter file | Wiggum Part 0 detects, alerts human |
| Defects after 5 iterations | Emergency escalation to human |
