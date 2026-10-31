"""Tests for CLI contract, output formatting, robustness, and edge cases (Group G and H)."""

from __future__ import annotations

import csv
from pathlib import Path
import zipfile
import pytest

from received_date.cli import main, run_cli


def make_minimal_docx(path: Path, text: str = "") -> None:
    """Create a minimal valid Word (.docx) file."""
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '</Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '</Relationships>'
    )
    doc_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body>'
        + (f'<w:p><w:r><w:t>{text}</w:t></w:r></w:p>' if text else '')
        + '</w:body>'
        '</w:document>'
    )
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", doc_xml)


def test_cli_empty_folder(tmp_path: Path, report):
    """G9: Empty input folder writes CSV with header only and exits 0."""
    out_csv = tmp_path / "out.csv"
    code = run_cli(str(tmp_path), str(out_csv))
    report("[G9] Empty input folder exits 0", "empty directory", 0, code)
    assert code == 0

    assert out_csv.exists()
    with open(out_csv, encoding="utf-8") as f:
        reader = list(csv.reader(f))
    report("[H1] Header row is exactly file,received_date", "empty directory", "file,received_date", ",".join(reader[0]))
    assert reader == [["file", "received_date"]]


def test_cli_missing_input_folder(tmp_path: Path, report):
    """G10: Missing input folder produces non-zero exit code."""
    non_existent = tmp_path / "does_not_exist"
    out_csv = tmp_path / "out.csv"
    code = run_cli(str(non_existent), str(out_csv))
    report("[G10] Non-existent input folder exits non-zero", "missing directory", 1, code)
    assert code != 0


def test_cli_usage_bad_args(report):
    """CLI prints usage and exits 2 when arguments count is not 2."""
    code = main(["only_one_arg"])
    report("CLI argument count validation exits 2", "1 arg given", 2, code)
    assert code == 2


def test_cli_robustness_corrupt_and_empty_files(tmp_path: Path, report):
    """G1, G2, G3: Corrupt, 0-byte, and empty-text files result in INVALID without crashing."""
    in_dir = tmp_path / "inputs"
    in_dir.mkdir()
    out_csv = tmp_path / "subfolder" / "out.csv"  # H6: create output folder if missing

    # G1: Corrupt random bytes
    (in_dir / "01_corrupt.docx").write_bytes(b"\x00\x01\x02\x03\x04" * 10)
    # G2: Empty 0-byte file
    (in_dir / "02_empty.docx").write_bytes(b"")
    # G3: Valid docx with no text
    make_minimal_docx(in_dir / "03_notext.docx", "")
    # Valid docx with received date
    make_minimal_docx(in_dir / "04_valid.docx", "Received: 2 Jan 2026")

    code = run_cli(str(in_dir), str(out_csv))
    report("CLI processes corrupt, empty, and valid files with exit code 0", "batch directory", 0, code)
    assert code == 0

    with open(out_csv, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = {r["file"]: r["received_date"] for r in rows}
    report("[G1] Corrupt file results in INVALID", "01_corrupt.docx", "INVALID", results.get("01_corrupt.docx"))
    report("[G2] Empty 0-byte file results in INVALID", "02_empty.docx", "INVALID", results.get("02_empty.docx"))
    report("[G3] Empty text docx results in INVALID", "03_notext.docx", "INVALID", results.get("03_notext.docx"))
    report("Valid docx results in 2026-01-02", "04_valid.docx", "2026-01-02", results.get("04_valid.docx"))

    assert results["01_corrupt.docx"] == "INVALID"
    assert results["02_empty.docx"] == "INVALID"
    assert results["03_notext.docx"] == "INVALID"
    assert results["04_valid.docx"] == "2026-01-02"


def test_cli_file_filtering_and_special_names(tmp_path: Path, report):
    """G4, G5, G6, H3, H4: Filter non-docx, lock files, handle uppercase .DOCX and commas in filename."""
    in_dir = tmp_path / "inputs"
    in_dir.mkdir()
    out_csv = tmp_path / "out.csv"

    # G5: Lock file starting with ~$
    (in_dir / "~$lock_file.docx").write_bytes(b"lock")
    # G4: Non-docx files ignored
    (in_dir / "notes.txt").write_text("notes")
    (in_dir / "paper.pdf").write_bytes(b"%PDF-1.4")
    # G6: Uppercase extension
    make_minimal_docx(in_dir / "uppercase.DOCX", "Received: 2 Jan 2026")
    # H3: Filename with comma and space
    make_minimal_docx(in_dir / "article, final draft.docx", "Received: 2 Jan 2026")

    code = run_cli(str(in_dir), str(out_csv))
    assert code == 0

    with open(out_csv, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    filenames = [r["file"] for r in rows]
    report("[G5] Word lock files starting with ~$ are skipped", "~$lock_file.docx", False, "~$lock_file.docx" in filenames)
    report("[G4] Non-docx files (.txt, .pdf) are ignored", "notes.txt", False, "notes.txt" in filenames)
    report("[G6] Uppercase .DOCX extension is processed", "uppercase.DOCX", True, "uppercase.DOCX" in filenames)
    report("[H3] Filename containing comma is preserved and handled", "article, final draft.docx", True, "article, final draft.docx" in filenames)

    assert "~$lock_file.docx" not in filenames
    assert "notes.txt" not in filenames
    assert "paper.pdf" not in filenames
    assert "uppercase.DOCX" in filenames
    assert "article, final draft.docx" in filenames

    # H4: Sorted order
    report("[H4] Rows sorted alphabetically by filename", "; ".join(filenames), True, filenames == sorted(filenames))
    assert filenames == sorted(filenames)


def test_cli_overwrite_and_idempotence(tmp_path: Path, report):
    """H5, H10: Overwrites existing output.csv and produces deterministic identical output."""
    in_dir = tmp_path / "inputs"
    in_dir.mkdir()
    out_csv = tmp_path / "out.csv"

    make_minimal_docx(in_dir / "doc1.docx", "Received: 2 Jan 2026")
    # Pre-populate out.csv with stale data
    out_csv.write_text("stale,header\nold,data\n", encoding="utf-8")

    run_cli(str(in_dir), str(out_csv))
    with open(out_csv, encoding="utf-8") as f:
        content_run1 = f.read()

    run_cli(str(in_dir), str(out_csv))
    with open(out_csv, encoding="utf-8") as f:
        content_run2 = f.read()

    report("[H5] Overwrites existing output without stale data", "stale content pre-existing", False, "old,data" in content_run1)
    report("[H10] Deterministic output across multiple runs", "run 1 vs run 2", "IDENTICAL", "IDENTICAL" if content_run1 == content_run2 else "DIFFERENT")
    assert "old,data" not in content_run1
    assert content_run1 == content_run2



def test_cli_reason_flag(tmp_path: Path, report):
    """Verify that --reason flag includes a third column with explanation reasons."""
    in_dir = tmp_path / "inputs"
    in_dir.mkdir()
    out_csv = tmp_path / "out.csv"

    make_minimal_docx(in_dir / "valid.docx", "Received: 2 Jan 2026")
    make_minimal_docx(in_dir / "missing.docx", "Accepted: 10 Apr 2026")

    code = main([str(in_dir), str(out_csv), "--reason"])
    assert code == 0

    with open(out_csv, encoding="utf-8") as f:
        reader = list(csv.reader(f))

    header = reader[0]
    report("CLI --reason flag adds reason column", "--reason", "file,received_date,reason", ",".join(header))
    assert header == ["file", "received_date", "reason"]

    row_map = {r[0]: (r[1], r[2]) for r in reader[1:]}
    assert row_map["valid.docx"][0] == "2026-01-02"
    assert "Matched received label" in row_map["valid.docx"][1]
    assert row_map["missing.docx"][0] == "INVALID"
    assert "No received date label found" in row_map["missing.docx"][1]


def test_cli_policy_flag(tmp_path: Path, report):
    """Verify that --policy dmy overrides slash policy to assume Day/Month/Year."""
    in_dir = tmp_path / "inputs"
    in_dir.mkdir()
    out_csv = tmp_path / "out.csv"

    make_minimal_docx(in_dir / "slash.docx", "Received: 03/04/2026")

    code = main([str(in_dir), str(out_csv), "--policy", "dmy"])
    assert code == 0

    with open(out_csv, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    actual = rows[0]["received_date"]
    report("CLI --policy dmy resolves ambiguous slash date as DMY", "03/04/2026 with --policy dmy", "2026-04-03", actual)
    assert actual == "2026-04-03"
