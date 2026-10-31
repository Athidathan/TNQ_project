"""End-to-end tests running the CLI against the 20 sample manuscripts."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Final
import pytest

from received_date.cli import run_cli

EXPECTED_CSV_PATH = Path(__file__).parent / "expected_samples.csv"


def load_expected_samples() -> list[dict[str, str]]:
    with open(EXPECTED_CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


EXPECTED_SAMPLES = load_expected_samples()

SAMPLE_DESCRIPTIONS: Final[dict[str, str]] = {
    "merged_01.docx": "Article history one-liner with received and revised",
    "merged_02.docx": "Bottom of file with italic full month",
    "merged_03.docx": "Dedicated line near top under title",
    "merged_04.docx": "Received at bottom with accepted at top",
    "merged_05.docx": "Ambiguous slash date 03/04/2026 [provisional Q1]",
    "merged_06.docx": "Ambiguous slash date with decoy hints [provisional Q1]",
    "merged_07.docx": "Ambiguous slash date at bottom [provisional Q1]",
    "merged_08.docx": "Missing received with accepted present [provisional Q3]",
    "merged_09.docx": "Prose received decoys with date accepted [provisional Q3]",
    "merged_10.docx": "Separate line under authors",
    "merged_11.docx": "Received with published online and issue date decoys",
    "merged_12.docx": "Corrupt non-zip document handled safely",
    "merged_13.docx": "Page header pipe-separated date metadata",
    "merged_14.docx": "Received alongside received in revised form decoy",
    "merged_15.docx": "Table row metadata extraction with joined cells",
    "merged_16.docx": "Multiple revision rounds ignored",
    "merged_17.docx": "Prose decoy rejected and bottom metadata line extracted",
    "merged_18.docx": "Two-digit year with ambiguous slash date [provisional Q1]",
    "merged_19.docx": "Impossible day 31 April rejected",
    "merged_20.docx": "Ordinal day format 2nd January",
}


@pytest.fixture(scope="module")
def cli_results(tmp_path_factory) -> dict[str, str]:
    """Run CLI on the manuscripts folder and return map of filename -> received_date."""
    tmp_dir = tmp_path_factory.mktemp("sample_run")
    out_csv = tmp_dir / "out.csv"
    ret = run_cli("manuscripts", str(out_csv))
    assert ret == 0, "CLI execution on manuscripts/ failed"

    with open(out_csv, encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ["file", "received_date"], f"Unexpected header: {header}"
        rows = list(reader)

    assert len(rows) == 20, f"Expected 20 sample manuscripts, got {len(rows)}"
    return {r[0]: r[1] for r in rows}


def test_samples_output_structure(cli_results: dict[str, str], report):
    """Verify that batch CLI execution on manuscripts outputs exactly 20 rows."""
    count = len(cli_results)
    report("[H2] Manuscripts batch run produces exactly 20 rows", "manuscripts folder", 20, count)
    assert count == 20


@pytest.mark.parametrize("sample", EXPECTED_SAMPLES, ids=lambda s: s["file"])
def test_sample_manuscript(cli_results: dict[str, str], sample: dict[str, str], report):
    """Verify each manuscript received date against the confirmed ground truth."""
    fname = sample["file"]
    expected = sample["expected"]
    desc = SAMPLE_DESCRIPTIONS.get(fname, f"Extraction for {fname}")
    check_label = f"[Sample {fname}] {desc}"

    actual = cli_results.get(fname, "MISSING_FROM_OUTPUT")
    report(check_label, fname, expected, actual)
    assert actual == expected
