"""End-to-end tests running the CLI against the 20 sample manuscripts."""

from __future__ import annotations

import csv
from pathlib import Path
import pytest

from received_date.cli import run_cli

EXPECTED_CSV_PATH = Path(__file__).parent / "expected_samples.csv"


def load_expected_samples() -> list[dict[str, str]]:
    with open(EXPECTED_CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


EXPECTED_SAMPLES = load_expected_samples()


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
    note = sample["note"]
    status = sample["status"]

    actual = cli_results.get(fname, "MISSING_FROM_OUTPUT")
    check_label = f"[Sample {fname}] expected={expected} ({status}: {note})"
    report(check_label, fname, expected, actual)
    assert actual == expected
