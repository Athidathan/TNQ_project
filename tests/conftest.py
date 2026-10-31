"""Pytest configuration and test reporting hook.

Writes test_report.csv at the repository root with columns:
  checks,input,expected,actual,result
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Callable
import pytest

REPORT_ROWS: list[dict[str, str]] = []


@pytest.fixture
def report() -> Callable[[str, Any, Any, Any], None]:
    """Fixture to record a test check into the test report before assertions."""

    def _record(checks: str, input_val: Any, expected: Any, actual: Any) -> None:
        expected_str = str(expected)
        actual_str = str(actual)
        result = "PASS" if expected_str == actual_str else "FAIL"
        REPORT_ROWS.append(
            {
                "checks": str(checks),
                "input": str(input_val),
                "expected": expected_str,
                "actual": actual_str,
                "result": result,
            }
        )

    return _record


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Session finish hook: write test_report.csv at the project root."""
    report_path = Path("test_report.csv")
    fieldnames = ["checks", "input", "expected", "actual", "result"]
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(REPORT_ROWS)
