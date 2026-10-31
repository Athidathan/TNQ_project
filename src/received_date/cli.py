"""CLI entry point for batch processing manuscript .docx files to CSV.

Usage:
    python -m received_date.cli <input_folder> <output_csv> [--reason] [--policy <ambiguous|dmy|mdy|infer>]
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys
from typing import Sequence

from received_date import rules
from received_date.docx_text import DocxReadError, read_docx_blocks
from received_date.finder import find_received_date_with_reason


def collect_docx_files(input_dir: Path) -> list[Path]:
    """Collect docx files directly in input_dir according to rules."""
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_dir}")

    files: list[Path] = []
    # Direct children only (Q10)
    for entry in input_dir.iterdir():
        if not entry.is_file():
            continue
        # Skip Word temporary lock files (Q10)
        if rules.SKIP_LOCK_FILES and entry.name.startswith("~$"):
            continue
        # Case-insensitive .docx extension
        if entry.name.lower().endswith(".docx"):
            files.append(entry)

    if rules.SORT_OUTPUT_BY_FILENAME:
        files.sort(key=lambda p: p.name)

    return files


def process_manuscript_with_reason(
    file_path: Path,
    policy: str | None = None,
) -> tuple[str, str]:
    """Process a single .docx manuscript and return (received_date_or_invalid, reason)."""
    try:
        blocks = read_docx_blocks(file_path)
        return find_received_date_with_reason(blocks, policy=policy)
    except DocxReadError as exc:
        return "INVALID", f"Corrupted or invalid docx package: {exc}"
    except Exception as exc:
        return "INVALID", f"Unexpected read failure: {exc}"


def process_manuscript(file_path: Path, policy: str | None = None) -> str:
    """Process a single .docx manuscript and return its received date or 'INVALID'."""
    date_val, _ = process_manuscript_with_reason(file_path, policy=policy)
    return date_val


def run_cli(
    input_folder_str: str,
    output_csv_str: str,
    include_reason: bool = False,
    policy: str | None = None,
) -> int:
    """Execute the core batch CLI workflow.
    
    Returns:
        0 on success, non-zero on command-level error (missing folder, bad arguments).
    """
    input_path = Path(input_folder_str)
    output_path = Path(output_csv_str)

    try:
        files = collect_docx_files(input_path)
    except (FileNotFoundError, NotADirectoryError) as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 1

    if rules.CREATE_OUTPUT_DIR:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    results: list[tuple[str, str, str]] = []
    for f in files:
        date_str, reason_str = process_manuscript_with_reason(f, policy=policy)
        results.append((f.name, date_str, reason_str))

    # Write CSV
    with open(output_path, "w", newline="", encoding="utf-8") as out_f:
        writer = csv.writer(out_f, lineterminator="\n")
        if include_reason:
            writer.writerow(["file", "received_date", "reason"])
            for fname, dval, rsn in results:
                writer.writerow([fname, dval, rsn])
        else:
            writer.writerow(["file", "received_date"])
            for fname, dval, _ in results:
                writer.writerow([fname, dval])

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Main CLI entry point with optional flags for reasons and date policies."""
    args_list = list(sys.argv[1:] if argv is None else argv)

    parser = argparse.ArgumentParser(
        description="Extract manuscript received dates from Word (.docx) files to CSV."
    )
    parser.add_argument("input_folder", help="Directory containing .docx manuscript files")
    parser.add_argument("output_csv", help="Path for destination CSV report")
    parser.add_argument(
        "--reason",
        "-r",
        action="store_true",
        help="Include a 'reason' column explaining matches or invalid results",
    )
    parser.add_argument(
        "--policy",
        "-p",
        choices=["ambiguous", "dmy", "mdy", "infer"],
        default=None,
        help="Slash date policy: ambiguous (INVALID), dmy (Day/Month), mdy (Month/Day), infer (smart document inference)",
    )

    policy_map = {
        "ambiguous": "INVALID_IF_AMBIGUOUS",
        "dmy": "DMY",
        "mdy": "MDY",
        "infer": "INFER_DOCUMENT_CONTEXT",
    }

    try:
        parsed = parser.parse_args(args_list)
    except SystemExit as exc:
        return exc.code

    chosen_policy = policy_map.get(parsed.policy) if parsed.policy else None
    return run_cli(
        parsed.input_folder,
        parsed.output_csv,
        include_reason=parsed.reason,
        policy=chosen_policy,
    )


if __name__ == "__main__":
    sys.exit(main())
