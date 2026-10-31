"""Tests for received-date identification covering all Group A and Group E scenarios."""

from __future__ import annotations

import pytest
from received_date.docx_text import TextBlock
from received_date.finder import find_received_date

FINDER_SCENARIOS = [
    # Group A: Label variations
    ("A1", "A1 standard colon", ["Received: 2 Jan 2026"], "2026-01-02"),
    ("A2", "A2 no colon separator", ["Received 2 Jan 2026"], "2026-01-02"),
    ("A3", "A3 joined runs with prefix", ["Article history: Received: 2 Jan 2026"], "2026-01-02"),
    ("A4", "A4 lowercase received", ["received: 2 Jan 2026"], "2026-01-02"),
    ("A4", "A4 uppercase RECEIVED", ["RECEIVED: 2 Jan 2026"], "2026-01-02"),
    ("A5", "A5 Date received variant [provisional Q3]", ["Date received: 2 Jan 2026"], "2026-01-02"),
    ("A5", "A5 Received on variant [provisional Q3]", ["Received on: 2 Jan 2026"], "2026-01-02"),
    ("A5", "A5 Manuscript received variant [provisional Q3]", ["Manuscript received: 2 Jan 2026"], "2026-01-02"),
    ("A5", "A5 Date of receipt variant [provisional Q3]", ["Date of receipt: 2 Jan 2026"], "2026-01-02"),
    ("A6", "A6 table row joined cells", ["Received 2026-01-02"], "2026-01-02"),
    ("A7", "A7 multiple spaces between label and date", ["Received    2 Jan 2026"], "2026-01-02"),
    ("A8", "A8 dash separator", ["Received - 2 Jan 2026"], "2026-01-02"),
    ("A8", "A8 full-width colon separator", ["Received\uff1a2 Jan 2026"], "2026-01-02"),
    ("A9", "A9 unified text block", ["Received: 2 Jan 2026"], "2026-01-02"),
    ("A10", "A10 substitute label Submitted [provisional Q3]", ["Submitted: 2 Jan 2026"], "INVALID"),
    ("A10", "A10 substitute label Date accepted [provisional Q3]", ["Date accepted: 2 Jan 2026"], "INVALID"),
    ("A10", "A10 substitute label Published online [provisional Q3]", ["Published online: 2 Jan 2026"], "INVALID"),

    # Group E: Decoys and distractor handling
    ("E1", "E1 prose received in sentence", ["We received 120 samples on 5 May 2025."], "INVALID"),
    ("E2", "E2 prose calibration received", ["We received the final calibration files on 14 February 2025"], "INVALID"),
    (
        "E3",
        "E3 received in revised form lookalike rejected",
        ["Received 2 January 2026; Received in revised form 4 March 2026; Accepted 10 April 2026"],
        "2026-01-02",
    ),
    (
        "E4",
        "E4 only revised and accepted present [provisional Q3]",
        ["Revised: 4 Mar 2026; Accepted: 10 Apr 2026"],
        "INVALID",
    ),
    ("E5", "E5 bibliography accessed date", ["[9] Regional Science Council. Guidance note. Accessed: 12 January 2026."], "INVALID"),
    ("E6", "E6 heading near date Author Contributions", ["Author Contributions: J.D.: Software"], "INVALID"),
    (
        "E7",
        "E7 citation title with received",
        ["Smith J. Received wisdom on modern climate models. J Climatol. 2021;12:34-45."],
        "INVALID",
    ),
    (
        "E8",
        "E8 multiple revision rounds ignored",
        ["Received: 2 Jan 2026; Revised (round 2): 15 Mar 2026; Accepted: 20 Apr 2026"],
        "2026-01-02",
    ),
    (
        "E9",
        "E9 multiple conflicting received dates [provisional Q4]",
        ["Received: 2 Jan 2026", "Received: 15 Feb 2026"],
        "INVALID",
    ),
    (
        "E10",
        "E10 identical date repeated in header and body",
        [
            TextBlock("Received 2 Jan 2026 | Accepted 10 Apr 2026", "word/header1.xml"),
            TextBlock("Received: 2 Jan 2026", "word/document.xml"),
        ],
        "2026-01-02",
    ),
    (
        "E11",
        "E11 published online and issue date decoys following received",
        ["Received: 2 Jan 2026; Published online: 15 May 2026; Issue date: 1 June 2026"],
        "2026-01-02",
    ),
]


@pytest.mark.parametrize("scenario_id,check,blocks,expected", FINDER_SCENARIOS)
def test_finder_scenarios(report, scenario_id: str, check: str, blocks: list, expected: str):
    actual = find_received_date(blocks)
    input_repr = " // ".join(str(b) for b in blocks)
    report(f"[{scenario_id}] {check}", input_repr, expected, actual)
    assert actual == expected
