# Scenario List: Received-Date Finder

The cases I plan to check before building, in plain words. They come from reading all 20 sample manuscripts and from common ways dates are written in manuscripts. Each case will be covered by an automated test.

Expected result is always a date as `YYYY-MM-DD`, or `INVALID` when no date can be produced. Where I don't know the right answer, it says **To confirm** and points to a question for the product owner at the end.

## A. How the received date is introduced

| ID | Case | Expected |
|---|---|---|
| A1 | `Received: 2 Jan 2026` with a colon | 2026-01-02 |
| A2 | `Received 2 Jan 2026` without a colon | 2026-01-02 |
| A3 | Label in bold, date in normal text | 2026-01-02 |
| A4 | Different capitalisation: `received`, `RECEIVED` | 2026-01-02 |
| A5 | Other wording: `Date received`, `Received on`, `Manuscript received` | To confirm (Q3) |
| A6 | Label and date on different lines or in different table cells | 2026-01-02 |
| A7 | Extra spaces, non-breaking spaces or a tab between label and date | 2026-01-02 |
| A8 | Dash instead of colon: `Received - 2 Jan 2026` | 2026-01-02 |
| A9 | Label split into pieces by Word formatting (`Rece` + `ived`) | 2026-01-02 |
| A10 | Other labels used instead of Received: `Submitted`, `Published online`, `Issue date`, `Date accepted` (samples 08, 09) | To confirm (Q3) |

## B. Where it appears in the document

| ID | Case | Expected |
|---|---|---|
| B1 | Near the top, under the title and authors | 2026-01-02 |
| B2 | In a one-line "Article history" next to Revised and Accepted, separated by `;` (samples 01, 05, 07, 11) | received date only |
| B3 | At the very bottom, after the references (samples 02, 04, 07) | 2026-01-02 |
| B4 | In the page header (sample 13) | 2026-01-02 |
| B5 | In the page footer | 2026-01-02 |
| B6 | Inside a table (sample 15) | 2026-01-02 |
| B7 | Inside a text box | 2026-01-02 |
| B8 | In a footnote or endnote | 2026-01-02 |
| B9 | Very first line, before the title (samples 13, 14) | 2026-01-02 |
| B10 | Accepted listed before Received (samples 04, 15) | the Received date, not the first date found |
| B11 | Date inside a tracked change or a comment | To confirm (Q8) |
| B12 | Date in hidden text | To confirm (Q8) |

## C. Date formats (same date, written differently)

All of these should give **2026-01-02**, unless noted.

| ID | Format |
|---|---|
| C1 | `2 Jan 2026` |
| C2 | `2 January 2026` |
| C3 | `2026-01-02` |
| C4 | `2nd January 2026` (sample 20) |
| C5 | `January 2, 2026` and `Jan 2, 2026` |
| C6 | `02 Jan 2026` (leading zero) |
| C7 | `2026/01/02` |
| C8 | `02.01.2026` and `2.1.2026` (dotted). Day first or month first is To confirm (Q1) |
| C9 | `02-Jan-2026` |
| C10 | `2 Jan. 2026`, and month abbreviations such as `Sept.`, `Sep`, `Sept` (sample 20) |
| C11 | Capital letters: `2 JANUARY 2026` |
| C12 | With weekday: `Friday, 2 January 2026` |
| C13 | With time or timezone: `2026-01-02T10:30:00Z`, `2 Jan 2026, 10:30` |
| C14 | Comma after the month: `2 Jan, 2026` |
| C15 | In brackets: `Received: (2 Jan 2026)` |
| C16 | Month name in another language, e.g. `2 janvier 2026` (To confirm, Q9) |
| C17 | A valid leap day: `29 February 2028`. Expected 2028-02-29 |

## D. Slash dates and two-digit years

| ID | Case | Expected |
|---|---|---|
| D1 | `03/04/2026`: 3 April or 4 March? (samples 05, 06, 07) | To confirm (Q1) |
| D2 | `12/05/26`: two-digit year, and day/month order unclear (sample 18) | To confirm (Q1, Q2) |
| D3 | `13/01/2026`: only day/month can be right | 2026-01-13 |
| D4 | `01/13/2026`: only month/day can be right | To confirm (Q1) |
| D5 | `02/01/2026`: both readings are possible | To confirm (Q1) |
| D6 | Other dates in the same file hint at the order (sample 06: Revised 12 March, Accepted 28 March) | To confirm (Q1) |

## E. Dates and words that look right but are not the received date

| ID | Case | Expected |
|---|---|---|
| E1 | Sentence in the body: `We received 120 samples on 5 May 2025` (sample 17) | ignored |
| E2 | Sentence in the acknowledgements: `We received the final calibration files on 14 February 2025` (sample 09) | ignored |
| E3 | `Received 2 January 2026; Received in revised form 4 March 2026` (sample 14) | 2026-01-02 |
| E4 | Revised, Accepted or Published dates present but no Received (samples 08, 09) | INVALID, To confirm (Q3) |
| E5 | A reference entry with a date, e.g. `Accessed: 12 January 2026` (sample 17) | ignored |
| E6 | A reference entry whose title contains "Contributions", next to a date (sample 13) | ignored |
| E7 | The word "received" inside a cited paper's title | ignored |
| E8 | Several Revised dates, e.g. `Revised (round 2)` (sample 16) | does not affect the Received date |
| E9 | Two different Received dates in one file | To confirm (Q4) |
| E10 | The same Received date written twice (e.g. header and body) | that date |
| E11 | `Published online` and `Issue date` printed after the real Received date (sample 11) | 2026-01-02 |

## F. Missing or invalid dates

| ID | Case | Expected |
|---|---|---|
| F1 | No Received label anywhere (samples 08, 09, 17) | INVALID (Q3) |
| F2 | `Received:` with nothing after it | INVALID |
| F3 | Day that does not exist: `31/04/2026` (sample 19), `31 April 2026`, `32 Jan 2026`, `0 Jan 2026` | INVALID |
| F4 | `29 February 2026` (2026 is not a leap year; sample 19, in Revised) | INVALID if it is the Received date |
| F5 | Month 13 or 00: `2026-13-01`, `2026-00-10` | INVALID |
| F6 | Partial date: `Mar 2026` or `2026` alone (sample 18, in Revised) | To confirm (Q5) |
| F7 | Not a date: `Received: pending`, `N/A`, `TBD` | INVALID |
| F8 | Date in the future, e.g. year 2031 (sample 18, in Accepted) | To confirm (Q6) |
| F9 | Received later than Accepted or Revised | To confirm (Q6) |
| F10 | Implausibly old year, e.g. `1899` | To confirm (Q6) |
| F11 | Misspelt month: `2 Janaury 2026` | To confirm (Q7) |

## G. Problem files and folders (the tool must never stop halfway)

| ID | Case | Expected |
|---|---|---|
| G1 | File with a .docx name that is not a real Word file (sample 12) | one row, INVALID, run continues |
| G2 | Empty (0 byte) file | one row, INVALID |
| G3 | Valid Word file with no text | INVALID |
| G4 | Other file types in the folder (`.txt`, `.pdf`, `.doc`) | To confirm (Q10) |
| G5 | Word temporary files such as `~$merged_01.docx` | To confirm (Q10) |
| G6 | Capital extension `.DOCX` | processed |
| G7 | Sub-folders inside the input folder | To confirm (Q10) |
| G8 | Password-protected Word file | one row, INVALID |
| G9 | Empty input folder | CSV with only the header row |
| G10 | Input folder missing or not given | clear error message, non-zero exit |
| G11 | Very large manuscript | finishes in reasonable time |

## H. Output and how it is run

| ID | Case | Expected |
|---|---|---|
| H1 | Header row is exactly `file,received_date` | yes |
| H2 | One row per .docx file, `file` is the file name | row count equals file count |
| H3 | File name with a comma, quote, space or non-English letters | correctly quoted in the CSV |
| H4 | Order of the rows | To confirm (Q11) |
| H5 | `output.csv` already exists | overwritten, no duplicate rows |
| H6 | Output folder does not exist yet | To confirm (Q11) |
| H7 | Dates always zero-padded: `2026-01-02`, not `2026-1-2` | yes |
| H8 | `test_report.csv` has columns `checks,input,expected,actual,result`, result PASS or FAIL | produced by running the tests |
| H9 | `./run.sh input_folder output.csv` works on a clean Ubuntu with Python 3.12 or Node 22 and installs what it needs | tested on a clean machine |
| H10 | Running twice gives identical output | yes |

## Questions for the product owner

1. **Slash dates (`03/04/2026`):** day/month or month/day? Three of the 20 samples use this style.
2. **Two-digit years (`12/05/26`):** is `26` always 2026, or is there a cutoff?
3. **Which labels count as "received"?** Is `Submitted` the same? If Received is missing but `Accepted` or `Published online` exists, should the answer be INVALID?
4. **Two different Received dates in one file:** use the first, the earliest, the latest, or INVALID?
5. **Partial dates (`Mar 2026`):** INVALID, or assume the 1st of the month?
6. **Sense checks:** should a future date, a date after Accepted, or a very old year be INVALID, or is any real calendar date fine?
7. **Misspelt months (`Janaury`):** correct them or mark INVALID?
8. **Hidden content:** do dates in tracked changes, comments or hidden text count?
9. **Other languages:** are non-English month names in scope?
10. **Which files are processed?** Only `.docx` at the top level of the folder? What about sub-folders and Word temporary files?
11. **Output details:** what order should rows be in, and what should happen if the output folder does not exist?
