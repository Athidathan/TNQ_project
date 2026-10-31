# Scenario List: Received-Date Extractor (Problem 1)

**How to read this:** every scenario says where it came from and what we expect.
- **SEEN** = found in the 20 sample manuscripts (file number given)
- **LIKELY** = not in the samples, but plausible in real manuscripts (hidden test set)
- **OPEN** = we do not know the right answer yet; see the Open Questions at the bottom (Q1, Q2, ...) to ask the product owner

Expected output is always `YYYY-MM-DD` or `INVALID`.

---

## A. Label wording (how the received date is introduced)

| ID | Scenario | Source | Expected |
|---|---|---|---|
| A1 | `Received: 2 Jan 2026` (standard, colon) | SEEN 03, 10, 16 | 2026-01-02 |
| A2 | `Received 2 Jan 2026` (no colon) | SEEN 13, 14 | 2026-01-02 |
| A3 | Label bold, date in normal text (label and date in different formatting runs) | SEEN 03, 10 | 2026-01-02 |
| A4 | Lowercase / uppercase / mixed: `received`, `RECEIVED` | LIKELY | 2026-01-02 |
| A5 | Variants: `Date received`, `Received on`, `Manuscript received`, `Date of receipt` | LIKELY | 2026-01-02 (confirm list, Q3) |
| A6 | Label and date on separate lines, or in separate table cells | SEEN 15 (table) | 2026-01-02 |
| A7 | Extra spaces, non-breaking spaces, tab between label and date | LIKELY | 2026-01-02 |
| A8 | Full-width or odd colon, or a dash instead of colon (`Received - 2 Jan 2026`) | LIKELY | 2026-01-02 |
| A9 | Label split across Word runs (`Rece` + `ived`) so plain text search must join runs | LIKELY | 2026-01-02 |
| A10 | Substitute labels: `Submitted`, `Date submitted`, `Published online`, `Issue date`, `Date accepted` instead of Received | SEEN 08, 09 | OPEN Q3 (likely INVALID) |

## B. Location in the document

| ID | Scenario | Source | Expected |
|---|---|---|---|
| B1 | Near the top, under the title/authors | SEEN 03, 10, 11 | 2026-01-02 |
| B2 | In a one-line "Article history" with Revised/Accepted on the same line, `;` separated | SEEN 01, 05, 07, 11 | received only |
| B3 | At the very bottom (after references) | SEEN 02, 04, 07 | 2026-01-02 |
| B4 | In the page header | SEEN 13 | 2026-01-02 |
| B5 | In the page footer | LIKELY | 2026-01-02 |
| B6 | Inside a table | SEEN 15 | 2026-01-02 |
| B7 | Inside a text box / shape | LIKELY | 2026-01-02 |
| B8 | In a footnote or endnote | LIKELY | 2026-01-02 |
| B9 | First line of the file, before the title | SEEN 13, 14 (contributors line) | 2026-01-02 |
| B10 | Order differs: Accepted before Received (must pick by label, not by position) | SEEN 04, 15 | 2026-01-02 |
| B11 | Date inside a tracked change (inserted or deleted text) or a comment | LIKELY | OPEN Q8 |
| B12 | Hidden text (Word "hidden" font attribute) | LIKELY | OPEN Q8 |

## C. Date formats (the same date, written differently)

Target for all of these: **2026-01-02** unless the format is ambiguous.

| ID | Format | Source |
|---|---|---|
| C1 | `2 Jan 2026` | SEEN 01, 03, 10 |
| C2 | `2 January 2026` | SEEN 02, 04, 14 |
| C3 | `2026-01-02` (ISO) | SEEN 15 |
| C4 | `2nd January 2026` (ordinal) | SEEN 20 |
| C5 | `January 2, 2026` and `Jan 2, 2026` (US order, with comma) | LIKELY |
| C6 | `02 Jan 2026` (leading zero) | SEEN 15 (`04 Mar 2026`) |
| C7 | `2026/01/02` | LIKELY |
| C8 | `2.1.2026` and `02.01.2026` (dotted, day first in Europe) | SEEN 20 (`21.12.2026` in Accepted) |
| C9 | `02-01-2026` and `02-Jan-2026` | LIKELY |
| C10 | `2 Jan. 2026`, `Sept.` / `Sep` / `Sept` (abbreviation with or without dot) | SEEN 20 (`Sept.`) |
| C11 | Upper case month: `2 JANUARY 2026` | LIKELY |
| C12 | With weekday: `Friday, 2 January 2026` | LIKELY |
| C13 | With time or timezone: `2026-01-02T10:30:00Z`, `2 Jan 2026, 10:30 IST` | LIKELY |
| C14 | `2 Jan, 2026` (comma after month) | LIKELY |
| C15 | Date wrapped in brackets or parentheses: `Received: (2 Jan 2026)` | LIKELY |
| C16 | Month name in another language (`2 janvier 2026`, `2 Januar 2026`) | LIKELY, OPEN Q9 |
| C17 | Valid leap day: `29 February 2028` | LIKELY | expected 2028-02-29 |

## D. Slash and two-digit dates (ambiguous formats)

| ID | Scenario | Source | Expected |
|---|---|---|---|
| D1 | `03/04/2026` (3 April or 4 March?) | SEEN 05, 06, 07 | OPEN Q1 |
| D2 | `12/05/26` (two-digit year; 12 May or 5 Dec; 2026 or 1926?) | SEEN 18 | OPEN Q1 + Q2 |
| D3 | `13/01/2026` (day over 12, so only day/month works) | LIKELY | 2026-01-13 |
| D4 | `01/13/2026` (month over 12 in the second slot, so only month/day works) | LIKELY | OPEN Q1 |
| D5 | `02/01/2026` (both readings valid, no clue) | LIKELY | OPEN Q1 |
| D6 | Other dates in the same file disambiguate it (file 06: Revised 12 March, Accepted 28 March makes 03/04 = 4 March) | SEEN 06 | OPEN Q1 |

## E. Decoys (dates and words that look right but are not the received date)

| ID | Scenario | Source | Expected |
|---|---|---|---|
| E1 | Prose containing "received": `We received 120 samples on 5 May 2025.` | SEEN 17 | do not use; INVALID if nothing else |
| E2 | Prose: `We received the final calibration files on 14 February 2025` | SEEN 09 | do not use |
| E3 | `Received in revised form 4 March 2026` next to the real `Received 2 January 2026` | SEEN 14 | 2026-01-02 (the first, not the revised one) |
| E4 | Revised / Accepted / Published dates present, Received missing | SEEN 08, 09 | INVALID (confirm Q3) |
| E5 | Reference list entries with a date label (`Accessed: 12 January 2026`) | SEEN 17 | do not use |
| E6 | Reference entry about "Author Contributions" (a heading word near a date) | SEEN 13 | do not use |
| E7 | "Received" in a citation title (e.g. a cited paper called "Received wisdom...") | LIKELY | do not use |
| E8 | `Revised (round 2)`, multiple Revised dates | SEEN 16 | received unaffected |
| E9 | Two Received lines with different dates (resubmission, or conflict) | LIKELY | OPEN Q4 |
| E10 | Date appears twice, identically (header and body) | LIKELY | that date |
| E11 | `Published online` and `Issue date` printed after the real Received date | SEEN 11 | 2026-01-02 |

## F. Missing and invalid dates (expected: INVALID)

| ID | Scenario | Source | Expected |
|---|---|---|---|
| F1 | No Received label anywhere | SEEN 08, 09, 17 | INVALID (Q3) |
| F2 | `Received:` label present, date empty | LIKELY | INVALID |
| F3 | Impossible day: `31/04/2026`, `31 April 2026`, `32 Jan 2026`, `0 Jan 2026` | SEEN 19 (`31/04/2026`) | INVALID |
| F4 | `29 February 2026` (not a leap year) | SEEN 19 (in Revised) | INVALID if in Received |
| F5 | Month 13 or `00`: `2026-13-01`, `2026-00-10` | LIKELY | INVALID |
| F6 | Partial date: `Mar 2026`, `2026` only | SEEN 18 (in Revised) | OPEN Q5 |
| F7 | Non-date text: `Received: pending`, `Received: N/A`, `Received: TBD` | LIKELY | INVALID |
| F8 | Future date relative to today (e.g. year 2031) | SEEN 18 (Accepted `2031`) | OPEN Q6 |
| F9 | Received later than Accepted/Revised in the same file | LIKELY | OPEN Q6 |
| F10 | Very old or implausible year (`1899`) | LIKELY | OPEN Q6 |
| F11 | Date with typo (`2 Janaury 2026`) | LIKELY | OPEN Q7 |

## G. File-level robustness (the tool must never crash the whole run)

| ID | Scenario | Source | Expected |
|---|---|---|---|
| G1 | Corrupt "docx" that is not a zip (2 KB random bytes) | SEEN 12 | one row, INVALID, run continues |
| G2 | Empty (0-byte) file | LIKELY | one row, INVALID |
| G3 | Valid docx with no text | LIKELY | INVALID |
| G4 | Non-docx file in the folder (`.txt`, `.pdf`, `.doc`) | LIKELY | skipped (Q10) |
| G5 | Word lock/temp files (`~$merged_01.docx`) | LIKELY | skipped (Q10) |
| G6 | Uppercase extension `.DOCX` | LIKELY | processed |
| G7 | Subfolders inside the input folder | LIKELY | OPEN Q10 |
| G8 | Password-protected docx | LIKELY | INVALID, no crash |
| G9 | Empty input folder | LIKELY | CSV with header only, exit 0 |
| G10 | Input folder path does not exist, or not provided | LIKELY | clear error message, non-zero exit |
| G11 | Very large docx (many pages) | LIKELY | finishes in reasonable time |

## H. Output contract (CSV and report)

| ID | Scenario | Expected |
|---|---|---|
| H1 | Header row is exactly `file,received_date` | header present |
| H2 | One row per `.docx`, file column = file name | rows == number of docx files |
| H3 | File name containing comma, quote, space or unicode | CSV properly quoted |
| H4 | Row order (alphabetical vs. discovery order) | OPEN Q11 |
| H5 | `output.csv` already exists | overwritten, no duplicate rows |
| H6 | Output path in a folder that does not exist yet | OPEN Q11 |
| H7 | Dates always zero-padded (`2026-01-02`, not `2026-1-2`) | yes |
| H8 | `test_report.csv` has columns `checks,input,expected,actual,result` with PASS/FAIL | produced by the test run |
| H9 | `run.sh` works on a clean Ubuntu with Python 3.12 or Node 22, installs its own dependencies | verified in a clean container |
| H10 | Running twice gives the same output (deterministic) | yes |

---

## Open Questions for the Product Owner

Each question says why it matters. Do not assume the answer; ask.

- **Q1. Slash dates (`03/04/2026`): day/month or month/day?** Appears in 3 of the 20 samples. Options: always day/month; infer from the other dates in the file; or mark ambiguous ones INVALID. Wrong guess means a silently wrong date.
- **Q2. Two-digit years (`12/05/26`): which century?** Is `26` 2026? Is there a cutoff?
- **Q3. Which labels count as "received"?** Is `Submitted` the same thing? If Received is missing but `Published online` or `Accepted` exists, is the answer INVALID or should we fall back?
- **Q4. Two different Received dates in one file:** take the first, the earliest, the latest, or INVALID?
- **Q5. Partial dates (`Mar 2026`):** INVALID, or default to the first of the month?
- **Q6. Plausibility rules:** is a future date, a date after Accepted, or a very old year INVALID, or is a calendar-valid date always accepted?
- **Q7. Typos in month names (`Janaury`):** fix by fuzzy matching, or INVALID?
- **Q8. Hidden content:** should dates in tracked changes (inserted or deleted), comments or hidden text count?
- **Q9. Non-English month names:** in scope?
- **Q10. Which files are processed?** Only `.docx` at the top level of the folder? Subfolders? Lock files?
- **Q11. Output details:** row order, and what to do if the output folder doesn't exist.
