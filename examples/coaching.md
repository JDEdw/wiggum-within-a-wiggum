# COACHING FILE
# Read this at the start of EVERY run.

## DEFECT TAXONOMY

### DEFECT 1: INCORRECT SOURCE LINK
The link does not go to the article described in the summary.
Every link must load the actual article. Verify before publishing.

### DEFECT 2: FRONT PAGE LINK
Link goes to a site homepage, not the specific article.
Every link must point to the specific article URL, not a domain root.

### DEFECT 3: DUPLICATE SOURCE IN ONE SUMMARY
The same article is linked more than once under a single summary.
Each source under a summary must be a different article.

### DEFECT 4: MISSING LINK
A summary appears with no clickable link.
Every summary must have at least one working link. No exceptions.

### DEFECT 5: STALE CONTENT
Content is older than your freshness threshold.
Exceptions: overlooked story now gaining traction, multi-day breaking news.

### DEFECT 6: SOURCE SHARING BETWEEN ITEMS
No two items may share the same source URL.
If one source covers two items, merge into one summary.
If an item cannot find its own unique source — drop it.

### DEFECT 7: POOR SUMMARY QUALITY
Each summary MUST be approximately 100 words.
Under 60 words = defect. Over 130 words = defect.
Summary must cover all major points, not just the lede.

### DEFECT 8: CONFLICTING SOURCES
When sources conflict, acknowledge the discrepancy or choose
the most credible/recent source and note others differ.

### DEFECT 9: COLLAPSED CONTENT
Never use <details> or <summary> tags.
Every item must be fully visible on page load. HARD FAIL.

### DEFECT 10: FACTUAL HALLUCINATION
A name, fact, or detail in the output does not match
the source material. HARD FAIL regardless of defect count.

### DEFECT 11: SINGLE SOURCE ON MAJOR ITEM
Major items must have minimum 2 independent source URLs
from different outlets. HARD FAIL if major item has only 1 source.

### DEFECT 12: SOURCE DOES NOT CONFIRM CONTENT
A source URL is topically related but does not contain
the specific facts described in the summary. HARD FAIL.

## BANNED SOURCES — DO NOT USE
Maintain a list of sources that consistently fail validation:
- Paywalled sites that time out
- Sites that block automated access (HTTP 403)
- Sources with fabricated/broken URLs
- Sites that only return homepage URLs

## SOURCE REQUIREMENTS
- Minimum N different outlets represented per output
- No single outlet used more than twice
- Verify every URL loads the actual article before including it

## SELF-CHECK (MANDATORY)
After writing but BEFORE declaring complete:
1. Read the source material
2. Read the output you just wrote
3. For EVERY name and fact — verify it matches source material
4. If ANY detail appears in output that is NOT in source = hallucination
