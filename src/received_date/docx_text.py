"""Read structured text blocks from a Word (.docx) manuscript package.

Follows build_plan.md Section 5.1:
- Uses only Python standard library (zipfile, xml.etree.ElementTree).
- Raises DocxReadError on corrupt, non-zip, password-protected, or unreadable files.
- Reads document, headers, footers, footnotes, and endnotes.
- Joins run text so split runs (e.g. 'Rece' + 'ived') are unified.
- Handles text inside textboxes (w:txbxContent) and tracked insertions (w:ins).
- Excludes deleted text (w:del, w:delText) and comments.
- Emits combined blocks for table rows (w:tr) so table-based dates are captured.
- Normalizes whitespace and non-breaking spaces.
"""

from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

# XML Namespaces used in WordprocessingML
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
TAG_P = f"{{{W_NS}}}p"
TAG_R = f"{{{W_NS}}}r"
TAG_T = f"{{{W_NS}}}t"
TAG_TAB = f"{{{W_NS}}}tab"
TAG_BR = f"{{{W_NS}}}br"
TAG_CR = f"{{{W_NS}}}cr"
TAG_TBL = f"{{{W_NS}}}tbl"
TAG_TR = f"{{{W_NS}}}tr"
TAG_TC = f"{{{W_NS}}}tc"
TAG_TXBX = f"{{{W_NS}}}txbxContent"
TAG_INS = f"{{{W_NS}}}ins"
TAG_DEL = f"{{{W_NS}}}del"
TAG_DEL_TEXT = f"{{{W_NS}}}delText"


class DocxReadError(Exception):
    """Raised when a docx file cannot be read, opened, or parsed."""


@dataclass(frozen=True)
class TextBlock:
    """A single normalized block of text from a docx part.
    
    Attributes:
        text: The normalized textual content.
        part: The source XML part inside the .docx package (e.g. 'word/document.xml').
    """

    text: str
    part: str

    def __str__(self) -> str:
        return self.text


def normalize_whitespace(text: str) -> str:
    """Normalize non-breaking spaces and whitespace runs to single space."""
    text = text.replace("\u00a0", " ").replace("\u202f", " ")
    return " ".join(text.split()).strip()


def _extract_p_text(elem: ET.Element) -> str:
    """Extract direct text from a paragraph element, ignoring nested text boxes and deletions."""
    parts: list[str] = []

    def _walk(node: ET.Element) -> None:
        if node.tag in (TAG_DEL, TAG_DEL_TEXT, TAG_TXBX):
            # Exclude deleted text and nested textboxes (handled separately)
            return
        if node.tag == TAG_T and node.text:
            parts.append(node.text)
        elif node.tag in (TAG_TAB, TAG_BR, TAG_CR):
            parts.append(" ")
        for child in node:
            _walk(child)

    _walk(elem)
    return "".join(parts)


def _get_target_part_names(namelist: Sequence[str]) -> list[str]:
    """Return relevant Word XML part names in standard document reading order.
    
    Order:
      1. Headers: word/header*.xml (sorted)
      2. Document body: word/document.xml
      3. Footers: word/footer*.xml (sorted)
      4. Footnotes: word/footnotes.xml
      5. Endnotes: word/endnotes.xml
    """
    headers = sorted([n for n in namelist if re.match(r"^word/header\d*\.xml$", n)])
    body = [n for n in namelist if n == "word/document.xml"]
    footers = sorted([n for n in namelist if re.match(r"^word/footer\d*\.xml$", n)])
    footnotes = [n for n in namelist if n == "word/footnotes.xml"]
    endnotes = [n for n in namelist if n == "word/endnotes.xml"]
    return headers + body + footers + footnotes + endnotes


def read_docx_blocks(file_path: str | Path) -> list[TextBlock]:
    """Read all structured text blocks from a .docx file in document order.
    
    Raises:
        DocxReadError: If the file is missing, empty, not a valid zip,
                       encrypted, or has corrupted XML.
    """
    path = Path(file_path)
    if not path.exists():
        raise DocxReadError(f"File not found: {path}")
    if not path.is_file():
        raise DocxReadError(f"Path is not a regular file: {path}")

    try:
        zf = zipfile.ZipFile(path, "r")
    except (zipfile.BadZipFile, zipfile.LargeZipFile, IsADirectoryError, PermissionError) as exc:
        raise DocxReadError(f"Cannot open .docx package {path}: {exc}") from exc
    except Exception as exc:
        raise DocxReadError(f"Failed opening {path}: {exc}") from exc

    blocks: list[TextBlock] = []

    with zf:
        # Check if zip is encrypted/password protected
        try:
            namelist = zf.namelist()
        except Exception as exc:
            raise DocxReadError(f"Cannot read file table in {path}: {exc}") from exc

        parts = _get_target_part_names(namelist)
        if not parts and "word/document.xml" not in namelist:
            # Valid zip, but not a valid docx package structure
            raise DocxReadError(f"File {path} does not contain standard Word XML parts.")

        for part_name in parts:
            try:
                xml_bytes = zf.read(part_name)
            except (RuntimeError, zipfile.BadZipFile, KeyError) as exc:
                # RuntimeError is raised for password-protected/encrypted entries
                raise DocxReadError(f"Failed to read part {part_name} in {path}: {exc}") from exc

            try:
                root = ET.fromstring(xml_bytes)
            except ET.ParseError as exc:
                raise DocxReadError(f"Corrupt XML in {part_name} of {path}: {exc}") from exc

            def _process_node(node: ET.Element) -> None:
                if node.tag == TAG_TBL:
                    # Process table rows
                    for tr in node.findall(TAG_TR):
                        cell_texts: list[str] = []
                        for tc in tr.findall(TAG_TC):
                            # Collect individual paragraphs inside cell
                            for p in tc.findall(TAG_P):
                                pt = normalize_whitespace(_extract_p_text(p))
                                if pt:
                                    blocks.append(TextBlock(text=pt, part=part_name))
                            # Collect cell-wide text for the combined row block
                            cell_p_texts = [
                                normalize_whitespace(_extract_p_text(p))
                                for p in tc.iter(TAG_P)
                            ]
                            c_text = " ".join([t for t in cell_p_texts if t])
                            if c_text:
                                cell_texts.append(c_text)

                        # Output combined row block
                        row_text = normalize_whitespace(" ".join(cell_texts))
                        if row_text:
                            blocks.append(TextBlock(text=row_text, part=part_name))
                    return

                if node.tag == TAG_P:
                    # Output paragraph text
                    pt = normalize_whitespace(_extract_p_text(node))
                    if pt:
                        blocks.append(TextBlock(text=pt, part=part_name))
                    # Output any textboxes nested within this paragraph
                    for txbx in node.iter(TAG_TXBX):
                        for p in txbx.iter(TAG_P):
                            tpt = normalize_whitespace(_extract_p_text(p))
                            if tpt:
                                blocks.append(TextBlock(text=tpt, part=part_name))
                    return

                for child in node:
                    _process_node(child)

            _process_node(root)

    return blocks
