# Build Plan: Received-Date Finder + Automated Tests

This document is a complete spec. Follow it stage by stage. After every stage, run the verification step, fix problems, then **commit** before moving on.

## 1. Goal

Build a command-line tool that reads every `.docx` manuscript in a folder, finds the date the manuscript was **received**, and writes a CSV with that date as `YYYY-MM-DD` (or `INVALID` when no date can be produced). Build an automated test suite for it that produces `test_report.csv`.

This is a Quality Engineering hackathon. **The tests and the reasoning behind them matter more than the tool code.** Every rule must be explicit, visible and covered by a test.

## 2. Hard requirements (from the problem statement)

1. Language: Python 3.12.
2. `./run.sh input_folder output.csv` at the repository top level. It reads every `.docx` in the folder and writes the CSV. It must work on a clean Ubuntu machine with Python 3.12. If any library is needed, `run.sh` must install it.
3. CSV format: header row `file,received_date`, then one row per file. `file` is the file name. `received_date` is `YYYY-MM-DD` or `INVALID`.
4. `test_report.csv` at the top level, produced by running the tests. Columns, in this order: `checks,input,expected,actual,result`.
   - `checks`: what the test checks
   - `input`: the input given
   - `expected`: the expected output
   - `actual`: the actual output
   - `result`: `PASS` or `FAIL`
5. A README explaining how to run the tests.
6. Everything committed to the git repository. Only commits made before the 3-hour mark count.

## 3. Decisions already made

| Choice | Decision | Reason |
|---|---|---|
| Language | Python 3.12 | easy to handle, standard library covers everything |
| Reading .docx | Open the zip and parse the XML ourselves (`zipfile`, `xml.etree.ElementTree`) | full control: headers, footers, footnotes, text boxes, tables, split text |
| Date parsing | Our own explicit rules and patterns, validated with `datetime` | no hidden guessing; every ambiguity is a visible decision |
| Test framework | `pytest` | standard |
| Tool dependencies | **None** (standard library only) | `run.sh` needs no installs, so nothing can fail on a clean machine |
| Test inputs | The 20 sample manuscripts are the primary test input. Generated `.docx` fixtures are an optional extra stage (Stage 6) | most scenarios are in the samples |

Do **not** add `python-docx`, `dateutil`, `dateparser` or any other library to the tool.

## 4. Repository layout

The 20 samples are in `./manuscripts/` and the scenario list is `./scenarios.md` (both already exist at the root).

```
.
├── run.sh                      # ./run.sh input_folder output.csv
├── run_tests.sh                # runs pytest, writes test_report.csv
├── requirements.txt            # pytest only (tests, not the tool)
├── README.md
├── scenarios.md                # already exists
├── manuscripts/                # already exists: 20 sample .docx
├── src/
│   └── received_date/
│       ├── __init__.py
│       ├── rules.py            # ALL changeable decisions live here (section 6)
│       ├── docx_text.py        # .docx -> list of text blocks
│       ├── dates.py            # text -> YYYY-MM-DD or a reason it failed
│       ├── finder.py           # blocks -> the received date
│       └── cli.py              # folder -> CSV
└── tests/
    ├── conftest.py             # writes test_report.csv
    ├── expected_samples.csv    # hand-written correct answers for the 20 samples
    ├── test_samples.py
    ├── test_dates.py
    ├── test_finder.py
    ├── test_cli.py
    └── fixtures.py             # (Stage 6, optional) builds small .docx files in code
```

## 5. Module design

### 5.1 `docx_text.py`: read the document
- Open the file with `zipfile.ZipFile`. If it is not a valid zip (empty, corrupt, password-protected, wrong format), raise a clear `DocxReadError`. **Never let one bad file stop the run.**
- Read these parts if present: `word/document.xml`, `word/header*.xml`, `word/footer*.xml`, `word/footnotes.xml`, `word/endnotes.xml`.
- A text **block** is one paragraph (`w:p`). Join all its text pieces (`w:t`) so a label split across formatting runs (`Rece` + `ived`) comes back as one string. Treat `w:tab` and `w:br` as a space.
- Include text inside text boxes (`w:txbxContent`) and tracked insertions (`w:ins`). Deleted text uses `w:delText`, which is a different tag and so is naturally excluded.
- Tables: also output one extra block per table row, made by joining the cells of that row with a space (so `| Received | 2026-01-02 |` becomes `Received 2026-01-02`).
- Normalise: replace non-breaking spaces (`\u00a0`) and runs of whitespace with a single space, and strip.
- Return blocks in document order. Keep the part name with each block (useful for debugging and tests).

### 5.2 `dates.py`: turn text into a date
`parse_date(text) -> str` returning `YYYY-MM-DD`, or raising `DateError(reason)` where reason is one of `AMBIGUOUS`, `IMPOSSIBLE`, `PARTIAL`, `UNPARSEABLE`.

Before matching, strip: surrounding brackets/parentheses, a leading weekday (`Friday,`), a trailing time or timezone (`10:30`, `Z`, `IST`, `T10:30:00Z`), a trailing full stop.

Formats to support (each one a clear, separate pattern):
- Year first: `2026-01-02`, `2026/01/02`, `2026.01.02`
- Day, month name, year: `2 Jan 2026`, `02 January 2026`, `2nd January 2026`, `2 Jan. 2026`, `2 Jan, 2026`, `2 JANUARY 2026`, `4th Sept. 2026`
- Month name, day, year: `January 2, 2026`, `Jan 2, 2026`
- Numeric with separators `/`, `.`, `-`: `02/01/2026`, `2.1.2026`, `21.12.2026`, `02-01-2026`
- `02-Jan-2026`
- Two-digit years: `12/05/26` (see rules)
- Month names: full names and common abbreviations (`Jan`, `Sep`, `Sept`), case-insensitive, optional trailing dot.

Validation: build the date with `datetime.date(y, m, d)`. Anything that fails is `IMPOSSIBLE` (this covers `31/04/2026`, `29 February 2026`, month 13, day 0 or 32). `29 February 2028` is valid.

Numeric dates where the day/month order is unclear are handled by the policy in `rules.py` (decision Q1). If the first number is above 12, only day/month is possible; if the second is above 12, only month/day is possible.

### 5.3 `finder.py`: find the received date
Find the date **by its label**, not by position and not by "first date in the file".
1. Split each block into segments on `;` and `|`.
2. A segment is a *received candidate* only if the word `received` (case-insensitive) is a **label**: it starts the segment, optionally after a short prefix that ends in a colon (for example `Article history:`), and is followed by an optional `:` or `-` and then the date text. Also accept the label variants in `rules.LABELS`.
3. Reject these look-alikes:
   - `Received in revised form ...` (a revision date, not the received date)
   - `received` inside a sentence (`We received 120 samples on 5 May 2025`)
   - `Date accepted`, `Accepted`, `Revised`, `Published online`, `Issue date`, `Accessed`
4. Pass the text after the label to `dates.parse_date`.
5. Combine candidates (section 6, Q4 for conflicts). No candidate, or a candidate whose date fails to parse, gives `INVALID`.

### 5.4 `cli.py`: folder to CSV
- Usage: `python -m received_date.cli input_folder output.csv`
- List `*.docx` files directly inside the folder (case-insensitive extension; skip names starting with `~$`; sorted by name). See Q10 and Q11.
- For each file: call the reader and the finder; on any reading error write `INVALID`. Wrap each file in its own try/except so one bad file never stops the run.
- Write the CSV with the `csv` module (so commas or quotes in file names are quoted correctly), header `file,received_date`, overwriting any existing file. Create the output file's parent folder if it does not exist.
- Missing or non-folder input path: print a clear error to stderr and exit with a non-zero code. Empty folder: write a header-only CSV and exit 0.
- Print nothing else to stdout except an optional one-line summary.

### 5.5 `run.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"   # but keep the user's paths working: resolve them before cd
...
PYTHONPATH=src python3 -m received_date.cli "$INPUT" "$OUTPUT"
```
- Validate that exactly two arguments are given; otherwise print usage and exit 2.
- Resolve the input and output paths to absolute paths **before** changing directory, so relative paths given by the user still work.
- The tool needs no installs, so `run.sh` must not call pip.
- Make it executable (`chmod +x run.sh`) and commit the executable bit.

### 5.6 `run_tests.sh` and the report
- Create a virtual environment, install `requirements.txt` (pytest), and run `pytest`. Write `test_report.csv` at the repository root.
- If `python3 -m venv` is unavailable on a clean Ubuntu (package `python3-venv` missing), the script should say so clearly and print the fix, rather than failing silently.
- `conftest.py` provides a `report` fixture. Each test calls it as `report(check, input, expected, actual)`; the helper records the row **before** asserting, so failing tests are still recorded as `FAIL`. At the end of the session, write all rows to `test_report.csv` with columns `checks,input,expected,actual,result`.
- Each test name or `checks` text starts with the scenario ID from `scenarios.md` (e.g. `B4 header`, `F3 impossible day`). This maps the report straight back to the scenario list.

## 6. Rules and open decisions (all in `rules.py`)

Eleven questions are still open with the product owner. The tool needs a behaviour in the meantime, so each has a **PROVISIONAL** default. Put every one of these in `rules.py` as a clearly named setting with a comment `PROVISIONAL (waiting for product owner, Qn)`, so it can be changed in one place. **Tests for provisional rules must say so in their `checks` text** (for example `[provisional Q1]`).

| Q | Question | PROVISIONAL default |
|---|---|---|
| Q1 | Slash/dot dates like `03/04/2026`: day/month or month/day? | **Never guess.** If both orders give a real date, the result is `INVALID` (ambiguous). If only one order is possible (e.g. `13/01/2026`), use it. Setting: `SLASH_POLICY` with values `INVALID_IF_AMBIGUOUS` (default), `DMY`, `MDY`. |
| Q2 | Two-digit years (`12/05/26`) | `26` means 2026 (add 2000). Setting: `TWO_DIGIT_YEAR_BASE = 2000`. (Sample 18 is still ambiguous because of Q1.) |
| Q3 | Which labels count as "received"? | Only: `Received`, `Date received`, `Received on`, `Manuscript received`, `Date of receipt`. No fallback to `Submitted`, `Accepted`, `Published online` etc. Setting: `LABELS`. |
| Q4 | Several different Received dates in one file | `INVALID`. Identical repeats count as one date. |
| Q5 | Partial dates (`Mar 2026`, `2026`) | `INVALID` |
| Q6 | Plausibility (future date, after Accepted, very old year) | No plausibility checks. Any real calendar date is accepted. |
| Q7 | Misspelt months (`Janaury`) | `INVALID` (no fuzzy matching) |
| Q8 | Hidden text, tracked changes, comments | Include text in hidden runs and tracked insertions. Exclude deleted text and comments. |
| Q9 | Non-English month names | Not supported: `INVALID` |
| Q10 | Which files are processed | `.docx` (any capitalisation) directly in the folder only; skip `~$` temp files; ignore other file types and sub-folders |
| Q11 | Output details | Rows sorted by file name; create the output folder if missing |

## 7. Ground truth for the 20 samples (`tests/expected_samples.csv`)

This file is **hand-written from reading the manuscripts**. It is the test oracle. **Never generate it by running the tool**: that would only test that the tool agrees with itself.

Columns: `file,expected,status,note`. `status` is `confirmed` (the manuscript text is unambiguous) or `provisional` (depends on an open question; the expected value follows the provisional default in section 6).

| file | expected | status | note |
|---|---|---|---|
| merged_01.docx | 2026-01-02 | confirmed | "Article history: Received: 2 Jan 2026; Revised…; Accepted…" |
| merged_02.docx | 2026-01-02 | confirmed | bottom of file, italic, full month |
| merged_03.docx | 2026-01-02 | confirmed | own line near top |
| merged_04.docx | 2026-01-02 | confirmed | Received at very bottom; Accepted is at the top |
| merged_05.docx | INVALID | provisional (Q1) | `Received: 03/04/2026` ambiguous |
| merged_06.docx | INVALID | provisional (Q1) | `03/04/2026`; Revised/Accepted in March hint at 4 March, but the tool must not guess |
| merged_07.docx | INVALID | provisional (Q1) | `Received: 03/04/2026` at the bottom |
| merged_08.docx | INVALID | provisional (Q3) | only `Accepted` present |
| merged_09.docx | INVALID | provisional (Q3) | only `Date accepted`; prose "received" decoys |
| merged_10.docx | 2026-01-02 | confirmed | own line |
| merged_11.docx | 2026-01-02 | confirmed | Received near top; `Published online` and `Issue date` at the bottom are decoys |
| merged_12.docx | INVALID | confirmed | not a real .docx file (corrupt); must not crash |
| merged_13.docx | 2026-01-02 | confirmed | in the page header: `Received 2 Jan 2026 \| Accepted…` (no colon, pipe separated) |
| merged_14.docx | 2026-01-02 | confirmed | `Received 2 January 2026; Received in revised form 4 March 2026` |
| merged_15.docx | 2026-01-02 | confirmed | table row, ISO format; Accepted listed first |
| merged_16.docx | 2026-01-02 | confirmed | also has `Revised (round 2)` |
| merged_17.docx | INVALID | provisional (Q3) | only prose "We received 120 samples on 5 May 2025" |
| merged_18.docx | INVALID | provisional (Q1) | `12/05/26`: two-digit year and ambiguous order |
| merged_19.docx | INVALID | confirmed | `31/04/2026`: impossible under either day/month order |
| merged_20.docx | 2026-01-02 | confirmed | `Received: 2nd January 2026` |

Before relying on this table, **open each file and check the Received line yourself** (for example with `python -c` printing the blocks from Stage 1). If you find a disagreement, stop and report it instead of silently changing the table.

## 8. Test design

**`test_samples.py`**: one parametrised test per row of `expected_samples.csv`, run through the real `cli` on the `manuscripts` folder (end-to-end), plus a check that the output has 20 rows and the right header.

**`test_dates.py`**: one parametrised table of `(text, expected)` for the formats in section 5.2, including every format in group C of `scenarios.md`, plus the invalid cases (F3 to F7, F11), leap day `29 February 2028`, and slash-date cases D3 to D5 under the provisional policy.

**`test_finder.py`**: small text-block examples (no .docx needed) covering the label and decoy scenarios: A1 to A9, E1 to E10.

**`test_cli.py`**: output contract and robustness using temporary folders: H1 to H7, G1 to G3, G5, G6, G9, G10, a file name with a comma, `output.csv` already existing, running twice gives identical output (H10).

**Stage 6 (optional)**: `fixtures.py` builds minimal `.docx` files in code (a zip with `[Content_Types].xml`, `_rels/.rels`, `word/document.xml`, and optionally header/footer/footnotes parts) so we can test scenarios the samples do not contain: B5 footer, B7 text box, B8 footnote, B11/B12 tracked changes and hidden text, A9 split runs, G7 sub-folders, G8 password-protected file. Do this only if time allows. In the README, say plainly which scenarios are covered by samples and which are not.

Scenarios marked "To confirm" in `scenarios.md` must be tested against the provisional default, with `[provisional Qn]` in the `checks` text.

## 9. Build stages (verify and commit after each)

Time budget: about 2 hours.

| Stage | Build | Verify before moving on | Time |
|---|---|---|---|
| 0 | Folder layout, `rules.py`, `requirements.txt`, empty modules, `git init` or clone, first commit | `python3 --version` shows 3.12; layout matches section 4 | 10 min |
| 1 | `docx_text.py` | Print the blocks for samples 03, 13 (header), 15 (table), and 12 (must raise `DocxReadError`, not crash). Check the Received line appears in each (except 12) | 20 min |
| 2 | `dates.py` + `test_dates.py` + `conftest.py` report | `pytest tests/test_dates.py` passes; `test_report.csv` appears with the 5 correct columns | 25 min |
| 3 | `finder.py` + `test_finder.py` | All A and E scenario tests pass, especially the decoys | 20 min |
| 4 | `cli.py` + `run.sh` + `test_cli.py` | `./run.sh manuscripts out.csv` gives 20 rows and the right header; CSV tests pass | 15 min |
| 5 | `expected_samples.csv` + `test_samples.py` | All 20 samples match the ground truth. For any mismatch, decide whether the tool or the ground truth is wrong by reading the manuscript. **Never edit expected values just to make a test pass** | 15 min |
| 6 | Optional generated fixtures | New tests pass; note coverage in README | 20 min |
| 7 | `README.md`, `run_tests.sh`, clean-machine check, final commit and push | See section 10 | 15 min |

Commit after every stage with a clear message (for example `Stage 3: finder with label rules and decoy tests`). Push at least once before the 2:45 mark.

## 10. Final checks (Stage 7)

1. On a clean Ubuntu container (for example `docker run -it ubuntu:24.04`) with Python 3.12 and only the repository copied in: `./run.sh manuscripts out.csv` works with no installs.
2. `./run_tests.sh` creates `test_report.csv` with the five columns and rows marked `PASS` or `FAIL`.
3. `test_report.csv` and `out.csv` are produced by running the commands, not edited by hand. Commit `test_report.csv`.
4. README contains: what the tool does, how to run it, how to run the tests, the table of provisional decisions (section 6) as "assumptions pending product owner confirmation", and which scenarios are covered by which tests.
5. The exported Claude chat is in the repository, `scenarios.md` is committed, and everything is pushed before the 3-hour mark.

## 11. Working rules for the AI assistant building this

- Do one stage at a time and stop for the verification step. Report what you ran and what you saw.
- Use the Python standard library only in `src/`.
- Do not widen the scope (no extra features, no other file formats).
- Do not change a rule, an expected value, or a test to make something pass without saying so and explaining why.
- Explain each module in plain words as you write it; the candidate must be able to defend every decision in a debrief.
- If something in this plan is unclear or seems wrong, ask before guessing.
