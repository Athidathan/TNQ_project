"""CLI entry point for batch processing manuscript .docx files to CSV.

Usage:
    python -m received_date.cli <input_folder> <output_csv>
"""

from __future__ import annotations

import csv
from pathlib import Path
import sys
from typing import Sequence

from received_date import rules
from received_date.docx_text import DocxReadError, read_docx_blocks
from received_date.finder import find_received_date


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


def process_manuscript(file_path: Path) -> str:
    """Process a single .docx manuscript and return its received date or 'INVALID'."""
    try:
        blocks = read_docx_blocks(file_path)
        return find_received_date(blocks)
    except (DocxReadError, Exception):
        # Never crash the entire batch run on an individual file failure
        return "INVALID"


def run_cli(input_folder_str: str, output_csv_str: str) -> int:
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

    results: list[tuple[str, str]] = []
    for f in files:
        date_str = process_manuscript(f)
        results.append((f.name, date_str))

    # Write CSV with standard header
    with open(output_path, "w", newline="", encoding="utf-8") as out_f:
        writer = csv.writer(out_f, lineterminator="\n")
        writer.writerow(["file", "received_date"])
        for fname, dval in results:
            writer.writerow([fname, dval])

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Main CLI entry point."""
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:
        sys.stderr.write("Usage: python -m received_date.cli <input_folder> <output.csv>\n")
        return 2

    return run_cli(args[0], args[1])


if __name__ == "__main__":
    sys.exit(main())
