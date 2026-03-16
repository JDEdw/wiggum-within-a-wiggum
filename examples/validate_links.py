#!/usr/bin/env python3
"""
Validate output HTML for link and content defects.

Checks against the WwW defect taxonomy (D1-D12):
- D1: Incorrect source link (HTTP error)
- D2: Front page redirect
- D3: Duplicate source in one summary
- D4: Missing link on a summary
- D6: Source sharing between items
- D7: Summary word count (60-130 words)
- D9: Collapsed content (details/summary tags)
- D11: Single source on item (warning)

Usage:
    python3 validate_links.py <html_file> [report_output_path]
"""

import re
import sys
import time
import urllib.request
import urllib.error
from html.parser import HTMLParser
from collections import Counter
from datetime import datetime

# === CONFIGURATION ===
# Adjust these for your domain

DEFAULT_INPUT = "output.html"
DEFAULT_REPORT = "validation_report.md"
MIN_WORD_COUNT = 60
MAX_WORD_COUNT = 130

# Domains known to block automated requests but have valid articles.
# Links to these domains get format-only checks, not HTTP checks.
BOT_BLOCKED_DOMAINS = {"skysports.com"}

# === HTML PARSER ===


class StoryParser(HTMLParser):
    """Parse HTML into story blocks with links and summaries."""

    def __init__(self):
        super().__init__()
        self.stories = []
        self.all_links = []
        self._in_story = False
        self._in_title = False
        self._in_source = False
        self._current_story = None
        self._current_text = []
        self._tag_stack = []

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        self._tag_stack.append(tag)

        if tag == "div" and "story" in attrs_d.get("class", ""):
            self._in_story = True
            self._current_story = {"title": "", "links": [], "summary": ""}

        if tag in ("h2", "h3") and self._in_story:
            self._in_title = True
            self._current_text = []

        if tag == "p" and "source" in attrs_d.get("class", ""):
            self._in_source = True

        if tag == "a" and "href" in attrs_d:
            href = attrs_d["href"]
            if href.startswith("http"):
                self.all_links.append(href)
                if self._current_story is not None:
                    self._current_story["links"].append(href)

    def handle_endtag(self, tag):
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

        if tag in ("h2", "h3") and self._in_title:
            self._in_title = False
            if self._current_story is not None:
                self._current_story["title"] = "".join(self._current_text).strip()

        if tag == "p" and self._in_source:
            self._in_source = False

        if tag == "div" and self._in_story and self._current_story is not None:
            self._in_story = False
            self.stories.append(self._current_story)
            self._current_story = None

    def handle_data(self, data):
        if self._in_title:
            self._current_text.append(data)
        if self._in_story and self._current_story is not None:
            if not self._in_title and not self._in_source:
                self._current_story["summary"] += data


# === LINK CHECKER ===


def check_link(url, timeout=15):
    """Check if a URL resolves to HTTP 200 and isn't a homepage redirect."""
    from urllib.parse import urlparse

    domain = urlparse(url).netloc.lower()
    for blocked in BOT_BLOCKED_DOMAINS:
        if blocked in domain:
            path = urlparse(url).path.rstrip("/")
            if not path or path in ("", "/index.html"):
                return "HOMEPAGE_REDIRECT", 0, url
            return "OK", 200, url
    try:
        req = urllib.request.Request(url, method="HEAD", headers={
            "User-Agent": "Mozilla/5.0 (compatible; LinkValidator/1.0)"
        })
        resp = urllib.request.urlopen(req, timeout=timeout)
        final_url = resp.url if hasattr(resp, "url") else url
        parsed = urlparse(final_url)
        path = parsed.path.rstrip("/")
        if not path or path in ("", "/index.html", "/index.htm"):
            return "HOMEPAGE_REDIRECT", resp.status, final_url
        return "OK", resp.status, final_url
    except urllib.error.HTTPError as e:
        return "HTTP_ERROR", e.code, url
    except Exception:
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; LinkValidator/1.0)"
            })
            resp = urllib.request.urlopen(req, timeout=timeout)
            final_url = resp.url if hasattr(resp, "url") else url
            parsed = urlparse(final_url)
            path = parsed.path.rstrip("/")
            if not path or path in ("", "/index.html", "/index.htm"):
                return "HOMEPAGE_REDIRECT", resp.status, final_url
            return "OK", resp.status, final_url
        except urllib.error.HTTPError as e2:
            return "HTTP_ERROR", e2.code, url
        except Exception as e2:
            return "ERROR", str(e2)[:80], url


# === VALIDATOR ===


def validate(html_path):
    """Run all validations and return defect list."""
    with open(html_path) as f:
        html = f.read()

    parser = StoryParser()
    parser.feed(html)
    defects = []
    stories = parser.stories

    # DEFECT 9: Collapsed content
    if re.search(r'<details[\s>]|<summary[\s>]', html, re.IGNORECASE):
        defects.append(("DEFECT 9", "Found <details>/<summary> tags", ""))

    if not stories:
        all_links = re.findall(r'href="(https?://[^"]+)"', html)
        if not all_links:
            defects.append(("DEFECT 4", "No links found in output", ""))
            return defects, stories, all_links

        checked = {}
        for url in all_links:
            if url in checked:
                continue
            time.sleep(0.3)
            result, status, final = check_link(url)
            checked[url] = (result, status, final)
            if result == "HOMEPAGE_REDIRECT":
                defects.append(("DEFECT 2", f"Front page redirect: {url} -> {final}", url))
            elif result == "HTTP_ERROR":
                defects.append(("DEFECT 1", f"HTTP {status}: {url}", url))
            elif result == "ERROR":
                defects.append(("DEFECT 1", f"Connection error: {url} ({status})", url))

        url_counts = Counter(all_links)
        for url, count in url_counts.items():
            if count > 1:
                defects.append(("DEFECT 3", f"Duplicate link used {count}x: {url}", url))

        return defects, stories, all_links

    # Story-level checks
    all_urls_by_story = {}
    for i, story in enumerate(stories):
        label = story["title"][:60] or f"Story #{i+1}"

        if not story["links"]:
            defects.append(("DEFECT 4", f"No links in: {label}", ""))

        link_counts = Counter(story["links"])
        for url, count in link_counts.items():
            if count > 1:
                defects.append(("DEFECT 3", f"Duplicate in '{label}': {url} ({count}x)", url))

        for url in set(story["links"]):
            all_urls_by_story.setdefault(url, []).append(label)

        if len(set(story["links"])) == 1:
            defects.append(("DEFECT 11", f"Single source — verify minor/niche: {label}", ""))

        summary = story.get("summary", "").strip()
        word_count = len(summary.split())
        if word_count < MIN_WORD_COUNT:
            defects.append(("DEFECT 7", f"Too short ({word_count} words, min {MIN_WORD_COUNT}): {label}", ""))
        elif word_count > MAX_WORD_COUNT:
            defects.append(("DEFECT 7", f"Too long ({word_count} words, max {MAX_WORD_COUNT}): {label}", ""))

    # DEFECT 6: Cross-story source sharing
    for url, labels in all_urls_by_story.items():
        if len(labels) > 1:
            defects.append(("DEFECT 6", f"URL in {len(labels)} stories: {url}", url))

    # Check links (sample up to 20)
    unique_links = list(set(l for s in stories for l in s["links"]))[:20]
    for url in unique_links:
        time.sleep(0.3)
        result, status, final = check_link(url)
        if result == "HOMEPAGE_REDIRECT":
            defects.append(("DEFECT 2", f"Front page redirect: {url} -> {final}", url))
        elif result == "HTTP_ERROR":
            defects.append(("DEFECT 1", f"HTTP {status}: {url}", url))
        elif result == "ERROR":
            defects.append(("DEFECT 1", f"Connection error: {url} ({status})", url))

    return defects, stories, unique_links


def write_report(defects, stories, links_checked, html_path, report_path):
    """Write validation report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = len(defects)
    lines = [
        "# Validation Report",
        f"**File:** {html_path}",
        f"**Date:** {now}",
        f"**Stories found:** {len(stories)}",
        f"**Links checked:** {len(links_checked)}",
        f"**Total defects:** {total}",
        f"**Result:** {'PASS' if total == 0 else 'FAIL'}",
        "",
    ]
    if not defects:
        lines.append("No defects found.")
    else:
        by_type = {}
        for dtype, desc, url in defects:
            by_type.setdefault(dtype, []).append((desc, url))
        for dtype in sorted(by_type.keys()):
            lines.append(f"## {dtype}")
            for desc, url in by_type[dtype]:
                lines.append(f"- {desc}")
            lines.append("")

    report = "\n".join(lines)
    with open(report_path, "w") as f:
        f.write(report)
    return report


if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    report_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_REPORT

    print(f"Validating: {input_path}")
    defects, stories, links = validate(input_path)
    report = write_report(defects, stories, links, input_path, report_path)
    print(report)
    print(f"\nReport written to: {report_path}")

    has_hard_fail = any(d[0] in ("DEFECT 9", "DEFECT 10", "DEFECT 12") for d in defects)
    sys.exit(1 if has_hard_fail or len(defects) > 0 else 0)
