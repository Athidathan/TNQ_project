"""Programmatic .docx fixture generators for edge cases not covered by sample manuscripts."""

from __future__ import annotations

import io
from pathlib import Path
import zipfile

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

CONTENT_TYPES_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  {extra_overrides}
</Types>"""

RELS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""


def build_docx(path: Path, doc_xml: str, extra_parts: dict[str, str] | None = None) -> None:
    """Build a complete .docx package on disk from XML strings."""
    extra = extra_parts or {}
    overrides = []
    if "word/footer1.xml" in extra:
        overrides.append(
            '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
        )
    if "word/footnotes.xml" in extra:
        overrides.append(
            '<Override PartName="/word/footnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/>'
        )

    content_types = CONTENT_TYPES_TEMPLATE.format(extra_overrides="\n  ".join(overrides))

    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", RELS_TEMPLATE)
        z.writestr("word/document.xml", doc_xml)
        for part_name, part_content in extra.items():
            z.writestr(part_name, part_content)


def create_footer_docx(path: Path, footer_text: str = "Received: 2 Jan 2026") -> None:
    """Scenario B5: Received date located inside a page footer (word/footer1.xml)."""
    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W_NS}">
  <w:body>
    <w:p><w:r><w:t>Manuscript body text without date metadata.</w:t></w:r></w:p>
  </w:body>
</w:document>"""

    footer_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="{W_NS}">
  <w:p><w:r><w:t>{footer_text}</w:t></w:r></w:p>
</w:ftr>"""

    build_docx(path, doc_xml, {"word/footer1.xml": footer_xml})


def create_textbox_docx(path: Path, text: str = "Received: 2 Jan 2026") -> None:
    """Scenario B7: Received date located inside a text box (w:txbxContent)."""
    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W_NS}">
  <w:body>
    <w:p>
      <w:r><w:t>Body paragraph with an embedded shape.</w:t></w:r>
      <w:r>
        <w:drawing>
          <w:txbxContent>
            <w:p><w:r><w:t>{text}</w:t></w:r></w:p>
          </w:txbxContent>
        </w:drawing>
      </w:r>
    </w:p>
  </w:body>
</w:document>"""
    build_docx(path, doc_xml)


def create_footnote_docx(path: Path, note_text: str = "Received: 2 Jan 2026") -> None:
    """Scenario B8: Received date located inside a footnote (word/footnotes.xml)."""
    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W_NS}">
  <w:body>
    <w:p><w:r><w:t>Article title with footnote marker.</w:t></w:r></w:p>
  </w:body>
</w:document>"""

    footnotes_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:footnotes xmlns:w="{W_NS}">
  <w:footnote w:id="1">
    <w:p><w:r><w:t>{note_text}</w:t></w:r></w:p>
  </w:footnote>
</w:footnotes>"""

    build_docx(path, doc_xml, {"word/footnotes.xml": footnotes_xml})


def create_tracked_changes_docx(
    path: Path,
    inserted_text: str = "Received: 2 Jan 2026",
    deleted_text: str = "Received: 1 Jan 2020",
) -> None:
    """Scenario B11: Tracked insertion (included) and tracked deletion (excluded)."""
    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W_NS}">
  <w:body>
    <w:p>
      <w:del><w:delText>{deleted_text}</w:delText></w:del>
      <w:ins><w:r><w:t>{inserted_text}</w:t></w:r></w:ins>
    </w:p>
  </w:body>
</w:document>"""
    build_docx(path, doc_xml)


def create_hidden_text_docx(path: Path, text: str = "Received: 2 Jan 2026") -> None:
    """Scenario B12: Hidden text attribute (w:vanish)."""
    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W_NS}">
  <w:body>
    <w:p>
      <w:r>
        <w:rPr><w:vanish/></w:rPr>
        <w:t>{text}</w:t>
      </w:r>
    </w:p>
  </w:body>
</w:document>"""
    build_docx(path, doc_xml)


def create_split_runs_docx(path: Path, pieces: list[str]) -> None:
    """Scenario A9: Label and date split across consecutive XML text runs."""
    runs_xml = "".join(f"<w:r><w:t>{p}</w:t></w:r>" for p in pieces)
    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W_NS}">
  <w:body>
    <w:p>{runs_xml}</w:p>
  </w:body>
</w:document>"""
    build_docx(path, doc_xml)


def create_encrypted_docx(path: Path) -> None:
    """Scenario G8: Password-protected / encrypted zip file structure."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("word/document.xml", b"fake protected content")
    raw = bytearray(buf.getvalue())
    # Set encryption bit (bit 0) in local and central directory headers
    loc_idx = raw.find(b"PK\x03\x04")
    if loc_idx != -1:
        raw[loc_idx + 6] |= 0x01
    cd_idx = raw.find(b"PK\x01\x02")
    if cd_idx != -1:
        raw[cd_idx + 8] |= 0x01
    path.write_bytes(raw)
