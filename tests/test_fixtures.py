"""Tests for advanced edge-case scenarios using programmatic .docx fixtures (Stage 6).

Covers scenarios not represented in the 20 sample manuscripts:
  - B5: Received date in page footer
  - B7: Received date inside text box shape
  - B8: Received date inside footnote
  - B11: Date in tracked insertion vs deleted text
  - B12: Date in hidden text
  - A9: Label split across Word formatting runs
  - G7: Subfolders in input folder ignored
  - G8: Password-protected docx handled gracefully
"""

from __future__ import annotations

import csv
from pathlib import Path

from received_date.cli import run_cli
from received_date.docx_text import read_docx_blocks
from received_date.finder import find_received_date
from tests.fixtures import (
    create_encrypted_docx,
    create_footer_docx,
    create_footnote_docx,
    create_hidden_text_docx,
    create_split_runs_docx,
    create_textbox_docx,
    create_tracked_changes_docx,
)


def test_scenario_b5_footer(tmp_path: Path, report):
    """B5: Received date in page footer."""
    fpath = tmp_path / "footer.docx"
    create_footer_docx(fpath, "Received: 2 Jan 2026")
    blocks = read_docx_blocks(fpath)
    actual = find_received_date(blocks)
    report("[B5] Received date in footer extracted", "footer.docx", "2026-01-02", actual)
    assert actual == "2026-01-02"


def test_scenario_b7_textbox(tmp_path: Path, report):
    """B7: Received date inside text box shape."""
    fpath = tmp_path / "textbox.docx"
    create_textbox_docx(fpath, "Received: 2 Jan 2026")
    blocks = read_docx_blocks(fpath)
    actual = find_received_date(blocks)
    report("[B7] Received date in text box extracted", "textbox.docx", "2026-01-02", actual)
    assert actual == "2026-01-02"


def test_scenario_b8_footnote(tmp_path: Path, report):
    """B8: Received date inside footnote."""
    fpath = tmp_path / "footnote.docx"
    create_footnote_docx(fpath, "Received: 2 Jan 2026")
    blocks = read_docx_blocks(fpath)
    actual = find_received_date(blocks)
    report("[B8] Received date in footnote extracted", "footnote.docx", "2026-01-02", actual)
    assert actual == "2026-01-02"


def test_scenario_b11_tracked_changes(tmp_path: Path, report):
    """B11: Tracked changes: inserted text is included, deleted text is excluded."""
    fpath = tmp_path / "tracked.docx"
    create_tracked_changes_docx(
        fpath,
        inserted_text="Received: 2 Jan 2026",
        deleted_text="Received: 1 Jan 2020",
    )
    blocks = read_docx_blocks(fpath)
    actual = find_received_date(blocks)
    report("[B11] Tracked insertion accepted and deletion rejected [provisional Q8]", "tracked.docx", "2026-01-02", actual)
    assert actual == "2026-01-02"


def test_scenario_b12_hidden_text(tmp_path: Path, report):
    """B12: Hidden text attribute (w:vanish) is parsed."""
    fpath = tmp_path / "hidden.docx"
    create_hidden_text_docx(fpath, "Received: 2 Jan 2026")
    blocks = read_docx_blocks(fpath)
    actual = find_received_date(blocks)
    report("[B12] Hidden text included [provisional Q8]", "hidden.docx", "2026-01-02", actual)
    assert actual == "2026-01-02"


def test_scenario_a9_split_runs(tmp_path: Path, report):
    """A9: Label split across Word formatting runs ('Rece' + 'ived: ' + '2 Jan ' + '2026')."""
    fpath = tmp_path / "split.docx"
    create_split_runs_docx(fpath, ["Rece", "ived: ", "2 Jan ", "2026"])
    blocks = read_docx_blocks(fpath)
    actual = find_received_date(blocks)
    report("[A9] Label split across multiple text runs is unified", "split.docx", "2026-01-02", actual)
    assert actual == "2026-01-02"


def test_scenario_g7_subfolders_ignored(tmp_path: Path, report):
    """G7: Subfolders inside input folder are ignored."""
    in_dir = tmp_path / "inputs"
    in_dir.mkdir()
    sub_dir = in_dir / "nested_subfolder"
    sub_dir.mkdir()
    out_csv = tmp_path / "out.csv"

    # File in root
    f_root = in_dir / "root_doc.docx"
    create_textbox_docx(f_root, "Received: 2 Jan 2026")

    # File in subfolder
    f_sub = sub_dir / "nested_doc.docx"
    create_textbox_docx(f_sub, "Received: 2 Jan 2026")

    code = run_cli(str(in_dir), str(out_csv))
    assert code == 0

    with open(out_csv, encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    processed_names = [r["file"] for r in reader]
    report("[G7] Subfolders inside input folder are ignored [provisional Q10]", "nested_subfolder/nested_doc.docx", False, "nested_doc.docx" in processed_names)
    assert "root_doc.docx" in processed_names
    assert "nested_doc.docx" not in processed_names


def test_scenario_g8_encrypted_docx(tmp_path: Path, report):
    """G8: Password-protected docx produces INVALID without crashing the run."""
    in_dir = tmp_path / "inputs"
    in_dir.mkdir()
    out_csv = tmp_path / "out.csv"

    enc_file = in_dir / "encrypted.docx"
    create_encrypted_docx(enc_file)

    code = run_cli(str(in_dir), str(out_csv))
    report("[G8] Password-protected docx handled gracefully with code 0", str(enc_file), 0, code)
    assert code == 0

    with open(out_csv, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    res_map = {r["file"]: r["received_date"] for r in rows}
    report("[G8] Encrypted file produces INVALID", "encrypted.docx", "INVALID", res_map.get("encrypted.docx"))
    assert res_map.get("encrypted.docx") == "INVALID"
