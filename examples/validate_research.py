#!/usr/bin/env python3
"""
Validate research checkpoint before generation.

Gates the generation phase by checking:
- Minimum story count (configurable, default 10)
- Minimum real URLs (not placeholders)
- No banned sources
- No duplicate URLs across stories
- Source budget limits (e.g., max 1 use of a specific domain)
- No placeholder/fabricated content markers

Usage:
    python3 validate_research.py [checkpoint_path]

Exit codes:
    0 = PASS (research is valid, proceed to generation)
    1 = FAIL (research has issues, do not generate)
"""

import re
import sys

# === CONFIGURATION ===
# Adjust these for your domain

DEFAULT_CHECKPOINT = "research_checkpoint.md"
MIN_STORY_COUNT = 10
MIN_REAL_URLS = 6

# Domains with usage limits: {domain: max_count}
BUDGET_DOMAINS = {
    "formula1.com": 1,
}

# Banned source domains — never use these
BANNED_DOMAINS = [
    # Add domains that consistently fail validation:
    # "example-paywall.com",
    # "example-403.com",
]

# Placeholder markers that indicate fabricated content
PLACEHOLDER_MARKERS = [
    "example.com",
    "placeholder",
    "lorem ipsum",
    "TBD",
    "TODO",
    "[insert",
    "[URL",
    "https://www.",  # bare domain with no path
]


def validate_research(checkpoint_path):
    """Validate research checkpoint. Returns list of errors."""
    try:
        with open(checkpoint_path) as f:
            content = f.read()
    except FileNotFoundError:
        return [f"MISSING: {checkpoint_path} not found. Run research phase first."]

    errors = []

    # Check minimum file size
    if len(content) < 500:
        errors.append(f"TOO SMALL: {len(content)} bytes (need 500+). Research appears incomplete.")
        return errors

    # Count stories
    story_count = len(re.findall(r'^## Story \d+:', content, re.MULTILINE))
    if story_count < MIN_STORY_COUNT:
        errors.append(
            f"INSUFFICIENT STORIES: {story_count} found. "
            f"Minimum {MIN_STORY_COUNT} required. "
            f"Research needs more stories before generation can proceed."
        )

    # Extract all URLs
    all_urls = re.findall(r'https?://[^\s,\)\]]+', content)
    all_urls_clean = [u.rstrip('.,;') for u in all_urls]

    # Check real URL count (exclude placeholder-looking URLs)
    real_urls = []
    for url in all_urls_clean:
        is_placeholder = False
        for marker in PLACEHOLDER_MARKERS:
            if marker in url.lower():
                is_placeholder = True
                break
        # Also check for URLs that are just a domain with no article path
        path = url.split('/', 3)
        if len(path) <= 3 or (len(path) > 3 and len(path[3]) < 5):
            is_placeholder = True
        if not is_placeholder:
            real_urls.append(url)

    if len(real_urls) < MIN_REAL_URLS:
        errors.append(
            f"INSUFFICIENT REAL URLS: {len(real_urls)} found. "
            f"Minimum {MIN_REAL_URLS} required. "
            f"Research must contain verified article URLs, not placeholders."
        )

    # Check budget domains
    for domain, max_count in BUDGET_DOMAINS.items():
        domain_urls = [u for u in all_urls_clean if domain in u]
        unique_domain = len(set(domain_urls))
        if unique_domain > max_count:
            errors.append(
                f"BUDGET EXCEEDED: {domain} used {unique_domain} times "
                f"(max {max_count}). Replace extras with other outlets."
            )

    # Check banned sources
    for url in all_urls_clean:
        for banned in BANNED_DOMAINS:
            if banned in url:
                errors.append(f"BANNED SOURCE: {url} — replace with approved outlet.")

    # Check for placeholder content in text
    content_lower = content.lower()
    for marker in PLACEHOLDER_MARKERS:
        if marker.lower() in content_lower and marker not in ("https://www.",):
            errors.append(f"PLACEHOLDER DETECTED: found '{marker}' in research content.")

    # Check URL uniqueness across stories
    stories = re.split(r'^## Story \d+:', content, flags=re.MULTILINE)
    url_to_story = {}
    for i, story_block in enumerate(stories[1:], 1):
        story_urls = re.findall(r'https?://[^\s,\)\]]+', story_block)
        for url in story_urls:
            url_clean = url.rstrip('.,;')
            if url_clean in url_to_story:
                errors.append(
                    f"DUPLICATE URL: {url_clean} used in Story {url_to_story[url_clean]} "
                    f"and Story {i}. Each story needs unique sources."
                )
            else:
                url_to_story[url_clean] = i

    return errors


if __name__ == "__main__":
    checkpoint = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CHECKPOINT

    print(f"Validating research: {checkpoint}")
    errors = validate_research(checkpoint)

    if errors:
        print(f"\nFAIL — {len(errors)} issue(s):\n")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("\nPASS — research checkpoint is valid.")
        sys.exit(0)
