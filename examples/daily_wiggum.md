# DAILY WIGGUM — SELF-QA PROTOCOL
# The worker agent runs this every morning.
# It reviews its own output, fixes defects, tracks progress.
# Exit condition: zero defects on today's output.
# Do NOT skip steps. Do NOT reorder steps.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## PART 0: OUTPUT EXISTS CHECK — MANDATORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FIRST: Check that today's output file exists.

If file does NOT exist:
- Do NOT declare 0 defects
- Do NOT update the index
- Alert the human immediately
- Stop. Do not continue. Exit now.

If file DOES exist: check content quality metrics next.
(Example: story count >= minimum threshold)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## PART 1: CHECK INDEX / LANDING PAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Verify the index/landing page:
A) File exists
B) Today's output is linked
C) All links are working
D) Design matches the benchmark

Record INDEX_STATUS as PASS or list every failed item.
If not PASS: fix it yourself, verify, repeat until PASS.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## PART 2: FIRST-RUN QA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run the automated validator against today's output.

Record FIRST_RUN_DEFECTS = total defect count.
Record FIRST_RUN_CATEGORIES = defect taxonomy numbers.

If FIRST_RUN_DEFECTS = 0: skip to Part 4.
If FIRST_RUN_DEFECTS > 0: continue to Part 3.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## PART 3: SELF-COACHING — FIX DEFECTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Maximum iterations: 5
Exit condition: validator reports 0 defects
Hard failures exit immediately regardless of count.

Each iteration:
A) Read the validation output carefully
B) For each defect, add a coaching note:
   - Taxonomy number
   - What went wrong specifically
   - What to do differently next time
   - Is this a repeat defect?
C) Fix the defects:
   1. Read coaching.md fully
   2. Read the source/reference material
   3. Verify every fact against source material
   4. Fix the output directly
D) Re-run the validator
E) Record iteration defect count

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## PART 4: CONSECUTIVE CLEAN DAY TRACKER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Read consecutive_clean_days.txt (create with 0 if missing).

If FIRST_RUN_DEFECTS = 0: increment counter.
Else: reset counter to 0.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## PART 5: LOG ENTRY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Append a structured log entry with today's values:
Date, First_Run_Defects, Iteration counts, Final_Defects,
Index_Status, Consecutive_Clean, Comments.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## PART 6: INDEPENDENCE CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If CONSECUTIVE_CLEAN >= 5:
  Notify the human:
  "I have achieved N consecutive zero-defect runs.
   The Daily Wiggum may no longer be needed.
   I appear ready to run independently.
   Shall I stop the daily loop?"

  Continue running until human confirms.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## PART 7: STATUS REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Send status report to human:
- First-run defect count
- Whether self-coaching ran
- Final defect count after coaching
- Iteration count
- Defect categories coached
- Index status
- Consecutive clean streak
- Links to output and progress log

EMERGENCY ESCALATION if:
- Output cannot be validated by deadline
- Defects remain after 5 iterations
- Something breaks unrecoverably
