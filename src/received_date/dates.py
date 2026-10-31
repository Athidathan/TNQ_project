"""Date parsing and normalization logic.

Converts various manuscript date representations into standardized 'YYYY-MM-DD'
or raises DateError with a specific reason:
  - AMBIGUOUS: Could be multiple valid dates (e.g. 03/04/2026 under INVALID_IF_AMBIGUOUS policy)
  - IMPOSSIBLE: Real calendar date cannot exist (e.g. 31 April, 29 Feb in non-leap year, month 13)
  - PARTIAL: Only month/year or year provided (e.g. Mar 2026, 2026)
  - UNPARSEABLE: Not recognizable as a date or unsupported format/language
"""

from __future__ import annotations

import datetime
import enum
import re
from typing import Final

from received_date import rules


class DateErrorReason(str, enum.Enum):
    AMBIGUOUS = "AMBIGUOUS"
    IMPOSSIBLE = "IMPOSSIBLE"
    PARTIAL = "PARTIAL"
    UNPARSEABLE = "UNPARSEABLE"


class DateError(Exception):
    """Raised when a date string cannot be resolved into a valid, unambiguous date."""

    def __init__(self, reason: DateErrorReason, message: str = "") -> None:
        self.reason = reason
        self.message = message or reason.value
        super().__init__(f"[{self.reason.value}] {self.message}")


MONTH_NAMES: Final[dict[str, int]] = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}

# Regex to detect partial dates (Q5)
PARTIAL_DATE_REGEXES: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(
        r"^(?:january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|august|aug|september|sep|sept|october|oct|november|nov|december|dec)\.?\s+\d{4}$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\d{4}\s+(?:january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|august|aug|september|sep|sept|october|oct|november|nov|december|dec)\.?$",
        re.IGNORECASE,
    ),
    re.compile(r"^\d{4}-\d{2}$"),
    re.compile(r"^\d{4}$"),
)

# Regex to strip leading weekday
WEEKDAY_PREFIX_REGEX = re.compile(
    r"^(?:mon(?:day)?|tue(?:sday)?|wed(?:nesday)?|thu(?:rsday)?|fri(?:day)?|sat(?:urday)?|sun(?:day)?)[, ]+\s*",
    re.IGNORECASE,
)

# Regex to strip trailing time and timezone info
TIME_TRAIL_REGEX = re.compile(
    r"(?:[T\s]\d{1,2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:\s*(?:Z|[A-Z]{2,4}|[+-]\d{2}:?\d{2}))?|\s+(?:Z|[A-Z]{2,4}|[+-]\d{2}:?\d{2}))\s*$",
    re.IGNORECASE,
)


def _strip_date_affixes(raw: str) -> str:
    """Strip wrappers (brackets, quotes), leading weekday, trailing time/timezone/punctuation."""
    text = raw.strip()

    # Strip enclosing quotes, brackets, parentheses
    while text and (
        (text.startswith("(") and text.endswith(")"))
        or (text.startswith("[") and text.endswith("]"))
        or (text.startswith("{") and text.endswith("}"))
        or (text.startswith('"') and text.endswith('"'))
        or (text.startswith("'") and text.endswith("'"))
    ):
        text = text[1:-1].strip()

    # Strip leading weekday
    text = WEEKDAY_PREFIX_REGEX.sub("", text).strip()

    # Strip trailing time and timezone
    text = TIME_TRAIL_REGEX.sub("", text).strip()

    # Strip trailing period or comma
    text = text.rstrip(".,;: ")

    return text


def _validate_calendar_date(year: int, month: int, day: int) -> datetime.date:
    """Validate calendar date components, raising DateError(IMPOSSIBLE) on failure."""
    try:
        return datetime.date(year, month, day)
    except ValueError as exc:
        raise DateError(DateErrorReason.IMPOSSIBLE, f"Invalid calendar date ({year}-{month}-{day}): {exc}") from exc


def _expand_year(year_str: str) -> int:
    """Expand 2-digit or 4-digit year string."""
    y = int(year_str)
    if len(year_str) == 2:
        return rules.TWO_DIGIT_YEAR_BASE + y
    return y


def parse_date(raw_text: str, policy: str | None = None) -> str:
    """Parse text into ISO formatted 'YYYY-MM-DD'.
    
    Args:
        raw_text: Input text containing a date representation.
        policy: Optional override for rules.SLASH_POLICY (e.g. 'DMY', 'MDY', 'INVALID_IF_AMBIGUOUS').
        
    Raises:
        DateError: If the date is ambiguous, impossible, partial, or unparseable.
    """
    effective_policy = policy or rules.SLASH_POLICY
    clean = _strip_date_affixes(raw_text)
    if not clean:
        raise DateError(DateErrorReason.UNPARSEABLE, "Empty date text")

    # Check for partial dates
    if not rules.ALLOW_PARTIAL_DATES:
        for p_re in PARTIAL_DATE_REGEXES:
            if p_re.match(clean):
                raise DateError(DateErrorReason.PARTIAL, f"Partial date not allowed: {raw_text}")

    # 1. Year first: YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD
    m_iso = re.match(r"^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})$", clean)
    if m_iso:
        y = int(m_iso.group(1))
        m = int(m_iso.group(2))
        d = int(m_iso.group(3))
        dt = _validate_calendar_date(y, m, d)
        return dt.isoformat()

    # 2. Day MonthName Year (e.g. 2 Jan 2026, 02 January 2026, 2nd January 2026, 2-Jan-2026)
    # Strictly require 4-digit or 2-digit years (rejects 3-digit years like '2 Jan 202')
    m_dmy = re.match(
        r"^(\d{1,2})(?:st|nd|rd|th)?[\s.-]+([a-zA-Z]+)\.?[\s,.-]+(\d{4}|\d{2})$",
        clean,
    )
    if m_dmy:
        day_val = int(m_dmy.group(1))
        month_word = m_dmy.group(2).lower()
        year_val = _expand_year(m_dmy.group(3))
        if month_word in MONTH_NAMES:
            month_val = MONTH_NAMES[month_word]
            dt = _validate_calendar_date(year_val, month_val, day_val)
            return dt.isoformat()
        else:
            raise DateError(DateErrorReason.UNPARSEABLE, f"Unrecognized month name: {month_word}")

    # 3. MonthName Day Year (e.g. January 2, 2026, Jan 2, 2026, Jan. 2, 2026)
    # Strictly require 4-digit or 2-digit years
    m_mdy = re.match(
        r"^([a-zA-Z]+)\.?[\s.-]+(\d{1,2})(?:st|nd|rd|th)?(?:,)?[\s.-]+(\d{4}|\d{2})$",
        clean,
    )
    if m_mdy:
        month_word = m_mdy.group(1).lower()
        day_val = int(m_mdy.group(2))
        year_val = _expand_year(m_mdy.group(3))
        if month_word in MONTH_NAMES:
            month_val = MONTH_NAMES[month_word]
            dt = _validate_calendar_date(year_val, month_val, day_val)
            return dt.isoformat()
        else:
            raise DateError(DateErrorReason.UNPARSEABLE, f"Unrecognized month name: {month_word}")

    # 4. Numeric with separators /, ., - : A / B / C (e.g. 02/01/2026, 2.1.2026, 12/05/26)
    # Strictly require 4-digit or 2-digit years
    m_num = re.match(r"^(\d{1,2})([/.-])(\d{1,2})\2(\d{4}|\d{2})$", clean)
    if m_num:
        a = int(m_num.group(1))
        b = int(m_num.group(3))
        year_val = _expand_year(m_num.group(4))

        # Check validity under Day/Month vs Month/Day
        dmy_valid = False
        try:
            dmy_date = datetime.date(year_val, b, a)
            dmy_valid = True
        except ValueError:
            pass

        mdy_valid = False
        try:
            mdy_date = datetime.date(year_val, a, b)
            mdy_valid = True
        except ValueError:
            pass

        if not dmy_valid and not mdy_valid:
            raise DateError(DateErrorReason.IMPOSSIBLE, f"Neither DD/MM nor MM/DD is a valid date: {raw_text}")

        # If identical (e.g. 05/05/2026), unambiguous
        if a == b and dmy_valid:
            return dmy_date.isoformat()

        # If only one interpretation is valid (e.g. 13/01/2026 or 01/13/2026)
        if dmy_valid and not mdy_valid:
            return dmy_date.isoformat()
        if mdy_valid and not dmy_valid:
            return mdy_date.isoformat()

        # Both interpretations are valid -> consult effective_policy
        if effective_policy == "INVALID_IF_AMBIGUOUS":
            raise DateError(
                DateErrorReason.AMBIGUOUS,
                f"Numeric date '{raw_text}' is ambiguous between DD/MM and MM/DD",
            )
        elif effective_policy == "DMY":
            return dmy_date.isoformat()
        elif effective_policy == "MDY":
            return mdy_date.isoformat()

    raise DateError(DateErrorReason.UNPARSEABLE, f"Unable to parse date from '{raw_text}'")


def parse_date_or_invalid(text: str, policy: str | None = None) -> str:
    """Safe date parser returning YYYY-MM-DD on success, or 'INVALID' on any DateError."""
    try:
        return parse_date(text, policy=policy)
    except DateError:
        return "INVALID"
