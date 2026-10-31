"""Tests for date parsing across all scenarios in Group C, D, and F."""

from __future__ import annotations

import pytest
from received_date.dates import (
    DateError,
    DateErrorReason,
    parse_date,
    parse_date_or_invalid,
)

DATE_SCENARIO_CASES = [
    # Group C: Format variations
    ("C1", "C1 standard abbreviated month", "2 Jan 2026", "2026-01-02"),
    ("C2", "C2 full month name", "2 January 2026", "2026-01-02"),
    ("C3", "C3 ISO format YYYY-MM-DD", "2026-01-02", "2026-01-02"),
    ("C4", "C4 ordinal day with suffix", "2nd January 2026", "2026-01-02"),
    ("C5", "C5 US order with comma full month", "January 2, 2026", "2026-01-02"),
    ("C5", "C5 US order with comma short month", "Jan 2, 2026", "2026-01-02"),
    ("C6", "C6 leading zero on day", "02 Jan 2026", "2026-01-02"),
    ("C7", "C7 slashed ISO YYYY/MM/DD", "2026/01/02", "2026-01-02"),
    ("C8", "C8 dotted ambiguous date [provisional Q1]", "2.1.2026", "INVALID"),
    ("C8", "C8 dotted ambiguous zero-padded [provisional Q1]", "02.01.2026", "INVALID"),
    ("C8", "C8 dotted unambiguous day > 12", "21.12.2026", "2026-12-21"),
    ("C9", "C9 hyphenated ambiguous date [provisional Q1]", "02-01-2026", "INVALID"),
    ("C9", "C9 hyphenated with month name", "02-Jan-2026", "2026-01-02"),
    ("C10", "C10 month abbreviation with dot", "2 Jan. 2026", "2026-01-02"),
    ("C10", "C10 four-letter Sept abbreviation with dot", "4th Sept. 2026", "2026-09-04"),
    ("C11", "C11 uppercase month name", "2 JANUARY 2026", "2026-01-02"),
    ("C12", "C12 leading weekday with comma", "Friday, 2 January 2026", "2026-01-02"),
    ("C13", "C13 ISO date with ISO time and UTC Z", "2026-01-02T10:30:00Z", "2026-01-02"),
    ("C13", "C13 date with time and timezone IST", "2 Jan 2026, 10:30 IST", "2026-01-02"),
    ("C14", "C14 comma after month name", "2 Jan, 2026", "2026-01-02"),
    ("C15", "C15 parentheses wrapped date", "(2 Jan 2026)", "2026-01-02"),
    ("C15", "C15 square bracket wrapped date", "[2 Jan 2026]", "2026-01-02"),
    ("C16", "C16 French month name [provisional Q9]", "2 janvier 2026", "INVALID"),
    ("C17", "C17 valid leap day in leap year", "29 February 2028", "2028-02-29"),

    # Group D: Slash and two-digit dates
    ("D1", "D1 slash ambiguous date [provisional Q1]", "03/04/2026", "INVALID"),
    ("D2", "D2 two-digit year ambiguous [provisional Q1, Q2]", "12/05/26", "INVALID"),
    ("D3", "D3 slash unambiguous day > 12", "13/01/2026", "2026-01-13"),
    ("D4", "D4 slash unambiguous month slot > 12", "01/13/2026", "2026-01-13"),
    ("D5", "D5 slash both readings valid [provisional Q1]", "02/01/2026", "INVALID"),

    # Group F: Invalid calendar and non-date cases
    ("F3", "F3 impossible day 31 April", "31/04/2026", "INVALID"),
    ("F3", "F3 impossible day 31 April in words", "31 April 2026", "INVALID"),
    ("F3", "F3 impossible day 32 Jan", "32 Jan 2026", "INVALID"),
    ("F3", "F3 impossible day 0 Jan", "0 Jan 2026", "INVALID"),
    ("F4", "F4 leap day in non-leap year", "29 February 2026", "INVALID"),
    ("F5", "F5 month 13", "2026-13-01", "INVALID"),
    ("F5", "F5 month 00", "2026-00-10", "INVALID"),
    ("F6", "F6 partial month and year only [provisional Q5]", "Mar 2026", "INVALID"),
    ("F6", "F6 partial year only [provisional Q5]", "2026", "INVALID"),
    ("F7", "F7 pending non-date", "pending", "INVALID"),
    ("F7", "F7 N/A non-date", "N/A", "INVALID"),
    ("F7", "F7 TBD non-date", "TBD", "INVALID"),
    ("F11", "F11 misspelled month Janaury [provisional Q7]", "2 Janaury 2026", "INVALID"),
]


@pytest.mark.parametrize("scenario_id,check,raw_input,expected", DATE_SCENARIO_CASES)
def test_date_parsing_scenarios(report, scenario_id: str, check: str, raw_input: str, expected: str):
    actual = parse_date_or_invalid(raw_input)
    report(f"[{scenario_id}] {check}", raw_input, expected, actual)
    assert actual == expected


def test_date_error_reasons(report):
    # Test specific DateError reasons for deep QA
    with pytest.raises(DateError) as exc_info:
        parse_date("03/04/2026")
    report("[D1] Ambiguous date raises AMBIGUOUS", "03/04/2026", DateErrorReason.AMBIGUOUS.value, exc_info.value.reason.value)
    assert exc_info.value.reason == DateErrorReason.AMBIGUOUS

    with pytest.raises(DateError) as exc_info:
        parse_date("31/04/2026")
    report("[F3] Impossible day raises IMPOSSIBLE", "31/04/2026", DateErrorReason.IMPOSSIBLE.value, exc_info.value.reason.value)
    assert exc_info.value.reason == DateErrorReason.IMPOSSIBLE

    with pytest.raises(DateError) as exc_info:
        parse_date("Mar 2026")
    report("[F6] Partial date raises PARTIAL [provisional Q5]", "Mar 2026", DateErrorReason.PARTIAL.value, exc_info.value.reason.value)
    assert exc_info.value.reason == DateErrorReason.PARTIAL

    with pytest.raises(DateError) as exc_info:
        parse_date("random garbage text")
    report("[F7] Garbage raises UNPARSEABLE", "random garbage text", DateErrorReason.UNPARSEABLE.value, exc_info.value.reason.value)
    assert exc_info.value.reason == DateErrorReason.UNPARSEABLE
