#!/bin/bash
# Wiggum Launcher — fires the daily QA loop via cron
#
# Runs at 5am daily. Copies the Wiggum prompt to the worker machine,
# then fires the agent framework to execute it.
#
# Prerequisites:
#   - SSH key access to worker machine
#   - Agent CLI installed on worker machine
#   - daily_wiggum.md prompt file in the same directory
#
# Cron entry:
#   0 5 * * * ~/wiggum_ollama.sh

WORKER_HOST="worker@your-pi-hostname"
AGENT_CLI="openclaw"  # or your agent framework CLI
PROMPT_FILE="$(dirname "$0")/daily_wiggum.md"
LOG=~/logs/daily_wiggum_$(date +%Y-%m-%d).log
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "$TIMESTAMP — Wiggum starting" >> "$LOG"

# Copy prompt to worker to avoid quoting issues over SSH
scp "$PROMPT_FILE" "${WORKER_HOST}:/tmp/daily_wiggum_prompt.md" >> "$LOG" 2>&1

# Fire the agent with the prompt
ssh "$WORKER_HOST" \
  "${AGENT_CLI} agent \
  --agent main \
  --timeout 600 \
  --json \
  --message \"\$(cat /tmp/daily_wiggum_prompt.md)\"" \
  >> "$LOG" 2>&1

echo "$(date '+%Y-%m-%d %H:%M:%S') — Wiggum complete" >> "$LOG"
