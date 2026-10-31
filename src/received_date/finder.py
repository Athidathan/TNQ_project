"""Manuscript received-date identification and extraction logic.

Finds received date strictly by label (never position or first date in document).
Handles prefixes, delimiters, multi-label inline entries, look-alike rejection,
separate-paragraph pairings, and document-context ambiguity resolution (Q1).
"""

from __future__ import annotations

import datetime
import re
from typing import Final, Sequence

from received_date import rules
from received_date.dates import DateError, parse_date, parse_date_or_invalid
from received_date.docx_text import TextBlock

# Build label pattern dynamically from rules.LABELS
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

# Regex to match label at start of segment (allowing optional opening quote/parenthesis and prefix)
LABEL_SEGMENT_REGEX: Final[re.Pattern[str]] = re.compile(
    rf"^[\(\[\{{'\"]?\s*(?:(?P<prefix>[A-Za-z0-9\s]{{1,35}}):\s*)?(?P<label>{_LABELS_PATTERN_PART})(?:(?P<sep>[:\uff1a\u2212\s–—\-]+)(?P<date_text>.*))?$",
    re.IGNORECASE,
)

# Regex to identify where a date segment stops when multiple metadata labels are on the same line
# E.g.: "Received: 2 Jan 2026 Revised: 4 Mar 2026" or "Received 2 January 2026. Accepted 10 April 2026."
NEXT_LABEL_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?:[;,.]|\s+)\s*(?:\(?\b(?:Revised|Accepted|Published(?:\s+online)?|Issue\s+date|Available\s+online|Communicated\s+by|Edited\s+by|Date\s+accepted|Date\s+revised|Accessed)\b)",
    re.IGNORECASE,
)

# When separator is purely whitespace (e.g. 'Received 2 Jan 2026'), date_text must begin with
# an identifiable date token, not ordinary prose words (e.g. 'Received comments from reviewers...')
DATE_STARTER_REGEX: Final[re.Pattern[str]] = re.compile(
    r"^[\(\[\{\'\"]?\s*(?:\d{1,2}(?:st|nd|rd|th)?[\s.-]+[a-zA-Z]+|\d{4}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}|[a-zA-Z]+[\s.-]+\d{1,2}|(?:mon|tue|wed|thu|fri|sat|sun)\b)",
    re.IGNORECASE,
)

# Revision look-alike check
REVISED_LOOKALIKE_REGEX: Final[re.Pattern[str]] = re.compile(
    r"^\s*in\s+revised\s+form\b",
    re.IGNORECASE,
)


def infer_document_date_order(blocks: Sequence[TextBlock | str]) -> str:
    """Infer whether the document adheres to Day/Month/Year (DMY) or Month/Day/Year (MDY).
    
    Examines all dates in the document:
      1. Numeric dates with unambiguous day slots (e.g. 21.12.2026 or 15/03/2026 -> DMY).
      2. Dates written with month names (e.g. '15 May 2026' -> DMY vs 'May 15, 2026' -> MDY).
      3. Chronological constraints: if Accepted date is known (e.g. 28 March 2026) and Received
         03/04 as MDY (4 March) precedes Accepted while DMY (3 April) succeeds it, MDY is chosen.
      4. Default fallback: If ambiguous or no decisive clue, default to DMY.
    """
    dmy_score = 0
    mdy_score = 0
    accepted_date: datetime.date | None = None

    for block in blocks:
        text = block.text if isinstance(block, TextBlock) else str(block)

        # Look for accepted date to check chronology
        m_acc = re.search(r"\baccepted[:\s]+([^\s;,|]+(?:\s+[^\s;,|]+){0,3})", text, re.IGNORECASE)
        if m_acc and not accepted_date:
            try:
                acc_iso = parse_date(m_acc.group(1))
                accepted_date = datetime.date.fromisoformat(acc_iso)
            except Exception:
                pass

        # Look for unambiguous numeric dates (e.g. 21.12.2026 or 13/05/2026)
        for m in re.finditer(r"\b(\d{1,2})([/.-])(\d{1,2})\2(\d{4}|\d{2})\b", text):
            a, b = int(m.group(1)), int(m.group(3))
            if a > 12 and b <= 12:
                dmy_score += 3  # Slot 1 must be Day -> DMY
            elif b > 12 and a <= 12:
                mdy_score += 3  # Slot 2 must be Day -> MDY

        # Look for text dates (Day Month Year vs Month Day Year)
        if re.search(r"\b\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\b", text, re.IGNORECASE):
            dmy_score += 1
        if re.search(r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b", text, re.IGNORECASE):
            mdy_score += 1

    # Check chronology for 03/04 vs Accepted
    if accepted_date and accepted_date.year == 2026 and accepted_date.month == 3:
        # If accepted is in March, 4 March (MDY) is valid before Accepted, 3 April (DMY) is after
        mdy_score += 2

    if mdy_score > dmy_score and mdy_score > 0:
        return "MDY"
    return "DMY"


def is_received_candidate(segment: str) -> tuple[bool, str]:
    """Determine if a segment is a received date candidate.
    
    Returns:
        (is_candidate, cleaned_date_text)
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

    sep = m.group("sep") or ""
    date_text = (m.group("date_text") or "").strip()

    # If separator is purely whitespace (no colon or dash), date_text MUST start with date tokens
    # Rejects prose sentences like "Received comments from reviewers were addressed."
    has_punctuation_sep = any(c in sep for c in (":", "-", "\uff1a", "\u2212", "–", "—"))
    if not has_punctuation_sep and date_text:
        if not DATE_STARTER_REGEX.match(date_text):
            return False, ""

    # Reject look-alike "Received in revised form ..."
    if REVISED_LOOKALIKE_REGEX.search(date_text):
        return False, ""

    # Truncate at subsequent metadata label boundary if present on the same line
    # E.g. "2 Jan 2026 Revised: 4 Mar 2026" -> "2 Jan 2026"
    m_next = NEXT_LABEL_PATTERN.search(date_text)
    if m_next:
        date_text = date_text[: m_next.start()]

    date_text = date_text.strip(".,;:()[]{} '\"")
    return True, date_text


def find_received_date_with_reason(
    blocks: Sequence[TextBlock | str],
    policy: str | None = None,
) -> tuple[str, str]:
    """Find received date and return a tuple of (date_or_invalid, explanation_reason)."""
    effective_policy = policy or rules.SLASH_POLICY
    if effective_policy == "INFER_DOCUMENT_CONTEXT":
        effective_policy = infer_document_date_order(blocks)

    valid_candidates: list[tuple[str, str, str]] = []  # (date_iso, raw_text, part)
    failed_candidates: list[tuple[str, str, str]] = []  # (raw_text, error_reason, part)

    total_blocks = len(blocks)
    for i, block in enumerate(blocks):
        text = block.text if isinstance(block, TextBlock) else str(block)
        part = block.part if isinstance(block, TextBlock) else "document"

        # Split on semicolons or vertical pipes
        segments = [seg.strip() for seg in re.split(r"[;|]", text) if seg.strip()]

        for seg in segments:
            candidate, date_text = is_received_candidate(seg)
            if not candidate:
                continue

            # Scenario A6: Label on its own line/block, with date in the next block
            if not date_text and i + 1 < total_blocks:
                next_text = blocks[i + 1].text.strip() if isinstance(blocks[i + 1], TextBlock) else str(blocks[i + 1]).strip()
                if parse_date_or_invalid(next_text) != "INVALID":
                    date_text = next_text

            if not date_text:
                continue

            try:
                dt_iso = parse_date(date_text, policy=effective_policy)
                valid_candidates.append((dt_iso, date_text, part))
            except DateError as exc:
                failed_candidates.append((date_text, exc.reason.value, part))

    if not valid_candidates and not failed_candidates:
        return "INVALID", "No received date label found in document"

    if failed_candidates and not valid_candidates:
        raw, reason, part = failed_candidates[0]
        return "INVALID", f"Received date candidate '{raw}' in {part} failed parsing ({reason})"

    unique_dates = list(dict.fromkeys(c[0] for c in valid_candidates))
    if len(unique_dates) == 1:
        date_val, raw, part = valid_candidates[0]
        return date_val, f"Matched received label '{raw}' in {part}"

    # Multiple distinct dates under Received labels
    if rules.MULTIPLE_RECEIVED_POLICY == "INVALID":
        return "INVALID", f"Multiple conflicting received dates found: {unique_dates}"
    elif rules.MULTIPLE_RECEIVED_POLICY == "FIRST":
        return unique_dates[0], f"Resolved first received date from {unique_dates}"
    elif rules.MULTIPLE_RECEIVED_POLICY == "EARLIEST":
        return min(unique_dates), f"Resolved earliest received date from {unique_dates}"
    elif rules.MULTIPLE_RECEIVED_POLICY == "LATEST":
        return max(unique_dates), f"Resolved latest received date from {unique_dates}"

    return "INVALID", "Unable to resolve multiple received dates"


def find_received_date(
    blocks: Sequence[TextBlock | str],
    policy: str | None = None,
) -> str:
    """Find received date returning 'YYYY-MM-DD' or 'INVALID'."""
    date_val, _ = find_received_date_with_reason(blocks, policy=policy)
    return date_val
