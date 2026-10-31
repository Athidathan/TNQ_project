"""Manuscript received-date identification and extraction logic.

Finds received date strictly by label (never position or first date in document).
Handles prefixes, delimiters, look-alike rejection, and multi-candidate resolution.
"""

from __future__ import annotations

import re
from typing import Final, Sequence

from received_date import rules
from received_date.dates import DateError, parse_date
from received_date.docx_text import TextBlock

# Build label pattern dynamically from rules.LABELS
# Sorted by descending length so multi-word variants match before single words
_SORTED_LABELS: Final[list[str]] = sorted(rules.LABELS, key=len, reverse=True)
_LABELS_PATTERN_PART: Final[str] = "|".join(re.escape(lbl) for lbl in _SORTED_LABELS)

# Look-alikes to reject if prefix matches these
_DISALLOWED_PREFIXES: Final[set[str]] = {
    "accepted",
    "revised",
    "published",
    "published online",
    "issue date",
    "accessed",
    "date accepted",
    "date revised",
}

# Regex to match label at the start of a segment (optionally preceded by a short prefix ending in colon)
# Followed by separator (colon, dash, fullwidth colon, whitespace) and the candidate date text
LABEL_SEGMENT_REGEX: Final[re.Pattern[str]] = re.compile(
    rf"^(?:(?P<prefix>[A-Za-z0-9\s]{{1,35}}):\s*)?(?P<label>{_LABELS_PATTERN_PART})(?:(?P<sep>[:\uff1a\u2212\s–—\-]+)(?P<date_text>.*))?$",
    re.IGNORECASE,
)

# Regex to reject revision dates disguised as received dates
REVISED_LOOKALIKE_REGEX: Final[re.Pattern[str]] = re.compile(
    r"^\s*in\s+revised\s+form\b",
    re.IGNORECASE,
)


def is_received_candidate(segment: str) -> tuple[bool, str]:
    """Determine if a segment is a received date candidate.
    
    Returns:
        (is_candidate, date_text_after_label)
    """
    clean_seg = segment.strip()
    if not clean_seg:
        return False, ""

    m = LABEL_SEGMENT_REGEX.match(clean_seg)
    if not m:
        return False, ""

    prefix = m.group("prefix")
    if prefix and prefix.strip().lower() in _DISALLOWED_PREFIXES:
        return False, ""

    date_text = m.group("date_text") or ""
    date_text = date_text.strip()

    # Reject look-alike "Received in revised form ..."
    if REVISED_LOOKALIKE_REGEX.search(date_text):
        return False, ""

    return True, date_text


def find_received_date(blocks: Sequence[TextBlock | str]) -> str:
    """Find the manuscript received date from a collection of text blocks.
    
    Returns:
        ISO formatted date 'YYYY-MM-DD', or 'INVALID' if no valid received date found
        or if ambiguities/conflicts arise.
    """
    valid_dates: list[str] = []
    failed_candidates: list[tuple[str, str]] = []

    for block in blocks:
        text = block.text if isinstance(block, TextBlock) else str(block)
        # Split block into segments separated by semicolons or vertical pipes
        segments = [seg.strip() for seg in re.split(r"[;|]", text) if seg.strip()]

        for seg in segments:
            candidate, date_text = is_received_candidate(seg)
            if not candidate:
                continue

            if not date_text:
                # Label with no trailing date text (e.g. standalone table header cell)
                continue

            try:
                dt_iso = parse_date(date_text)
                valid_dates.append(dt_iso)
            except DateError as exc:
                failed_candidates.append((seg, exc.reason.value))

    # Evaluate collected candidates
    if not valid_dates and not failed_candidates:
        # Scenario F1: No received date found anywhere
        return "INVALID"

    if failed_candidates:
        # A received date was stated but failed parsing (e.g. impossible day, ambiguous, partial)
        return "INVALID"

    unique_dates = list(dict.fromkeys(valid_dates))  # Preserves first-seen order
    if len(unique_dates) == 1:
        # Unambiguous (either single candidate or identical repeats across headers/body)
        return unique_dates[0]

    # Multiple distinct dates found under Received labels (Scenario E9)
    if rules.MULTIPLE_RECEIVED_POLICY == "INVALID":
        return "INVALID"
    elif rules.MULTIPLE_RECEIVED_POLICY == "FIRST":
        return unique_dates[0]
    elif rules.MULTIPLE_RECEIVED_POLICY == "EARLIEST":
        return min(unique_dates)
    elif rules.MULTIPLE_RECEIVED_POLICY == "LATEST":
        return max(unique_dates)

    return "INVALID"
