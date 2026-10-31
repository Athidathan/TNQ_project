# Received-Date Extractor & Automated Verification Suite

A robust, standard-library-only command-line tool and Quality Engineering test suite that scans Word (`.docx`) manuscripts, identifies the official **received date**, and standardizes it to `YYYY-MM-DD` (or `INVALID` when ambiguous or unparseable).

Built for Python 3.12+ without external runtime dependencies.

---

## 1. Quick Start

### Running the Tool
On any clean Linux/macOS machine with Python 3.12+:
```bash
chmod +x run.sh

# Standard hackathon run (outputs: file,received_date)
./run.sh manuscripts output.csv

# Optional: Include explanation reasons for valid/invalid files (outputs: file,received_date,reason)
./run.sh manuscripts output.csv --reason

# Optional: Run with smart Q1 document-context date inference
./run.sh manuscripts output.csv --reason --policy infer
```

Directly via Python:
```bash
# Linux / macOS
PYTHONPATH=src python3 -m received_date.cli manuscripts output.csv [--reason] [--policy infer]

# Windows PowerShell
$env:PYTHONPATH="src"; python -m received_date.cli manuscripts output.csv --reason
```

### Running the Automated Tests
Run the test runner to set up a virtual environment, install pytest, run tests, and generate `test_report.csv`:
```bash
chmod +x run_tests.sh
./run_tests.sh
```

Or using an existing pytest environment:
```bash
pytest
```

---

## 2. Output Specifications

### Main Tool Output (`output.csv`)
The output CSV conforms to the hackathon specification:
- Header row: `file,received_date`
- One row per `.docx` file in the input directory, sorted alphabetically by filename.
- Date is formatted as `YYYY-MM-DD` (e.g., `2026-01-02`) or `INVALID`.
- Fully quotes filenames with special characters, commas, and spaces.

Example:
```csv
file,received_date
merged_01.docx,2026-01-02
merged_02.docx,2026-01-02
merged_05.docx,INVALID
merged_12.docx,INVALID
merged_13.docx,2026-01-02
```

### Automated Test Report (`test_report.csv`)
Every test execution records results in `test_report.csv` at the repository root before asserting:
- Columns in order: `checks,input,expected,actual,result`
- Every check maps directly to scenario IDs in `scenarios.md` (e.g. `[C1]`, `[B5]`, `[F3]`).
- `result` is strictly `PASS` or `FAIL`.

> **Comprehensive Check-by-Check Explanation:**  
> For an exhaustive audit of all 118 collected tests yielding 132 individual checks recorded in `test_report.csv`, see [`automated_test_checks_explained.md`](automated_test_checks_explained.md). It details the input, expected oracle, observed output, quality engineering rationale, and risk mitigation for every single test check.

---

## 3. Architecture & Design Principles

The tool is built strictly using the **Python Standard Library** (`zipfile`, `xml.etree.ElementTree`, `datetime`, `re`, `csv`, `pathlib`):
1. **Zero External Runtime Dependencies**: `run.sh` requires no network access and no `pip install`, ensuring 100% reliability on clean target machines.
2. **Direct XML Parsing**: Rather than relying on high-level wrappers that hide document structure, the tool parses the underlying WordprocessingML package directly:
   - Document body (`word/document.xml`)
   - Page headers (`word/header*.xml`)
   - Page footers (`word/footer*.xml`)
   - Footnotes (`word/footnotes.xml`)
   - Endnotes (`word/endnotes.xml`)
   - Text boxes (`w:txbxContent`) and tracked insertions (`w:ins`)
   - Tables (`w:tbl`): synthesizes row-level text blocks so split cell layouts (`| Received | 2026-01-02 |`) are preserved and extracted.
   - Text runs (`w:t`): concatenates adjacent runs, ensuring formatted strings split across runs (`Rece` + `ived`) are reassembled.
3. **Decoy Rejection**: Extracts received dates strictly by explicit labels, explicitly rejecting look-alikes such as:
   - `Received in revised form 4 March 2026`
   - Prose sentences (e.g. `We received 120 samples on 5 May 2025`)
   - Substitute dates (`Date accepted`, `Revised`, `Published online`, `Issue date`, `Accessed`)
4. **Strict Calendar Validation**: Validates date logic with `datetime.date(y, m, d)`, catching impossible dates (e.g., 31 April, 29 Feb in non-leap years, month 13) and marking them `INVALID`.

---

## 4. Assumptions Pending Product Owner Confirmation

All business decisions subject to clarification are centralized in [`src/received_date/rules.py`](src/received_date/rules.py).
Each open decision has a clearly documented **PROVISIONAL** default:

| Decision ID | Question / Ambiguity | Provisional Default Setting | Reasoning |
|---|---|---|---|
| **Q1** | Numeric date ambiguity (`03/04/2026`): DD/MM or MM/DD? | `SLASH_POLICY = "INVALID_IF_AMBIGUOUS"` (Supports `"INFER_DOCUMENT_CONTEXT"` via `--policy infer`) | Baseline: Never guess (ambiguous = `INVALID`). Smart option: scans all dates across the manuscript for unambiguous Day/Month slots, text style (`DD Month` vs `Month DD`), and Accepted date chronology. If all are ambiguous, defaults to academic standard DMY. |
| **Q2** | Two-digit year expansion base (`12/05/26`) | `TWO_DIGIT_YEAR_BASE = 2000` | Expands `26` to `2026`. (Ambiguous day/month order still governed by Q1). |
| **Q3** | Accepted received labels | `LABELS = ("received", "date received", "received on", "manuscript received", "date of receipt")` | No fallback to `Submitted`, `Accepted`, or `Published online`. |
| **Q4** | Conflicting received dates in a single document | `MULTIPLE_RECEIVED_POLICY = "INVALID"` | Identical repeats across header/body count as one date. Different dates return `INVALID`. |
| **Q5** | Partial dates (`Mar 2026`, `2026`) | `ALLOW_PARTIAL_DATES = False` | Rejects partial dates as `INVALID`. |
| **Q6** | Plausibility checks (future dates, ancient years) | `CHECK_PLAUSIBILITY = False` | Accepts any valid calendar date without subjective cutoffs. |
| **Q7** | Misspelt month names (`Janaury`) | `ALLOW_FUZZY_MONTHS = False` | No fuzzy matching; returns `INVALID`. |
| **Q8** | Word tracked changes & hidden text | Include tracked insertions (`w:ins`) and hidden text (`w:vanish`); exclude deleted text (`w:delText`) and comments. | Reflects current accepted document text. |
| **Q9** | Non-English month names | `SUPPORT_NON_ENGLISH_MONTHS = False` | Returns `INVALID`. |
| **Q10** | File discovery scope | `RECURSIVE_DIRECTORY_SEARCH = False`, `SKIP_LOCK_FILES = True` | Processes `.docx` directly in the folder; ignores subfolders and `~$` lock files. |
| **Q11** | Output ordering & missing directory handling | `SORT_OUTPUT_BY_FILENAME = True`, `CREATE_OUTPUT_DIR = True` | Deterministic alphabetical sort; creates destination directories. |

---

## 5. Scenario Coverage Matrix

| Scenario Group | Scenario IDs | Coverage Mechanism | Test Module |
|---|---|---|---|
| **A. Label Wording** | A1–A4, A6–A9 | Sample manuscripts & unit tests | `test_finder.py`, `test_samples.py` |
| | A5, A10 | Unit tests for label variants & distractors | `test_finder.py` |
| **B. Location** | B1, B2, B3, B4, B6, B9, B10 | Sample manuscripts (headers, tables, body) | `test_samples.py` |
| | B5, B7, B8, B11, B12 | Programmatic `.docx` fixtures (footers, text boxes, footnotes, tracked changes, hidden text) | `test_fixtures.py` |
| **C. Date Formats** | C1–C7, C9–C15, C17 | Comprehensive format unit tests | `test_dates.py` |
| | C8, C16 | Ambiguous dot dates and non-English tests | `test_dates.py` |
| **D. Slash Dates** | D1–D5 | Slash dates and 2-digit years | `test_dates.py` |
| **E. Decoys** | E1–E11 | Sentence decoys, revised look-alikes, citations | `test_finder.py`, `test_samples.py` |
| **F. Invalid Dates** | F1–F7, F11 | Missing dates, impossible calendar dates, partial dates | `test_dates.py`, `test_samples.py` |
| **G. Robustness** | G1, G2, G3, G5, G6, G9, G10 | Corrupt/0-byte/empty files, lock files, case-insensitivity, missing folders | `test_cli.py`, `test_samples.py` |
| | G7, G8 | Subfolders ignored, encrypted/password-protected packages | `test_fixtures.py` |
| **H. Output Contract**| H1–H7, H10 | CSV headers, column ordering, quoting, idempotency | `test_cli.py` |

---

## 6. Sample Manuscripts Ground Truth (`tests/expected_samples.csv`)

| File | Expected Date | Status | Notes |
|---|---|---|---|
| `merged_01.docx` | `2026-01-02` | Confirmed | Article history one-liner with Received, Revised, Accepted |
| `merged_02.docx` | `2026-01-02` | Confirmed | Bottom of file, italicized full month |
| `merged_03.docx` | `2026-01-02` | Confirmed | Dedicated line under title/authors |
| `merged_04.docx` | `2026-01-02` | Confirmed | Received at bottom; Accepted at top (order independence) |
| `merged_05.docx` | `INVALID` | Provisional (Q1) | `Received: 03/04/2026` ambiguous day/month |
| `merged_06.docx` | `INVALID` | Provisional (Q1) | `Received: 03/04/2026` ambiguous; no guessing from context |
| `merged_07.docx` | `INVALID` | Provisional (Q1) | `Received: 03/04/2026` at bottom |
| `merged_08.docx` | `INVALID` | Provisional (Q3) | Only `Accepted` date present |
| `merged_09.docx` | `INVALID` | Provisional (Q3) | Only `Date accepted`; body contains prose "received" decoy |
| `merged_10.docx` | `2026-01-02` | Confirmed | Separate line near top |
| `merged_11.docx` | `2026-01-02` | Confirmed | Received near top; `Published online` / `Issue date` decoys |
| `merged_12.docx` | `INVALID` | Confirmed | Corrupt file (not a zip package); safely handled |
| `merged_13.docx` | `2026-01-02` | Confirmed | Page header: `Received 2 Jan 2026 \| Accepted...` |
| `merged_14.docx` | `2026-01-02` | Confirmed | Real received date alongside `Received in revised form` decoy |
| `merged_15.docx` | `2026-01-02` | Confirmed | Metadata table row; cells joined and evaluated |
| `merged_16.docx` | `2026-01-02` | Confirmed | Multiple revision rounds present |
| `merged_17.docx` | `2026-01-02` | Confirmed | Contains prose decoy in body AND valid `Received: 2 Jan 2026` at bottom |
| `merged_18.docx` | `INVALID` | Provisional (Q1) | `Received: 12/05/26`: two-digit year and ambiguous order |
| `merged_19.docx` | `INVALID` | Confirmed | `Received: 31/04/2026`: impossible day (April 31) |
| `merged_20.docx` | `2026-01-02` | Confirmed | Ordinal format: `Received: 2nd January 2026` |

> **Note on `merged_17.docx`**: Direct inspection of the underlying XML in `merged_17.docx` confirms that while it includes a prose decoy sentence in the body (*"We received 120 samples on 5 May 2025"*), it also includes an official metadata history line at the bottom (*"Received: 2 Jan 2026; Revised: 4 Mar 2026; Accepted: 10 Apr 2026"*). The tool accurately rejects the prose decoy and extracts the confirmed received date `2026-01-02`.

