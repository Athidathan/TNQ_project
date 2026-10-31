"""Pytest configuration and test reporting hook.

Writes test_report.csv at the repository root with columns:
  checks,input,expected,actual,result
"""

from __future__ import annotations

import csv
from pathlib import Path
import sys
from typing import Any, Callable
import pytest

REPORT_ROWS: list[dict[str, str]] = []


@pytest.fixture
def report() -> Callable[[str, Any, Any, Any], None]:
    """Fixture to record a test check into the test report before assertions.
    
    Sanitizes newlines to ensure each test check occupies exactly one line in the CSV.
    """

    def _record(checks: str, input_val: Any, expected: Any, actual: Any) -> None:
        expected_str = str(expected).replace("\r", "").replace("\n", " ").strip()
        actual_str = str(actual).replace("\r", "").replace("\n", " ").strip()
        input_str = str(input_val).replace("\r", "").replace("\n", " ").strip()
        checks_str = str(checks).replace("\r", "").replace("\n", " ").strip()
        result = "PASS" if expected_str == actual_str else "FAIL"
        REPORT_ROWS.append(
            {
                "checks": checks_str,
                "input": input_str,
                "expected": expected_str,
                "actual": actual_str,
                "result": result,
            }
        )

    return _record


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Session finish hook: write test_report.csv at the project root."""
    repo_root = Path(__file__).resolve().parent.parent
    report_path = repo_root / "test_report.csv"
    fieldnames = ["checks", "input", "expected", "actual", "result"]
    try:
        with open(report_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(REPORT_ROWS)
    except PermissionError:
        # File is locked by an external program (e.g., Microsoft Excel)
        backup_path = repo_root / "test_report_new.csv"
        with open(backup_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(REPORT_ROWS)
        sys.stderr.write(
            "\n[WARNING] 'test_report.csv' is currently locked by another application (e.g. Excel).\n"
            "Wrote updated report to 'test_report_new.csv'. Close Excel to overwrite 'test_report.csv'.\n"
        )
