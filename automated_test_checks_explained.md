# Automated Testing Suite: Comprehensive Check-by-Check Explanation

> **Document Type:** Quality Engineering Audit & Verification Document  
> **System Under Test:** Received-Date Extractor (Academic Publishing Production Pipeline)  
> **Test Harness:** Pytest 9.x (`tests/conftest.py` Report-First Logger)  
> **Test Execution Results:** 118 collected tests executed, 132 distinct assertions audited, **132 PASS / 0 FAIL (100% Pass Rate)**  
> **Audit Log Reference:** [`test_report.csv`](file:///c:/Stuff/Projects/TNQ_project/test_report.csv)

---

## Executive Summary & Clarification of Metrics

When running the automated test suite with `pytest`:
```bash
python -m pytest
# Output: collected 118 items ... 118 passed in 0.56s
```
Pytest reports **118 passed test items**. However, the persistent audit log [`test_report.csv`](file:///c:/Stuff/Projects/TNQ_project/test_report.csv) contains **132 individually logged checks**.

### Why 118 Test Items vs. 132 Audit Checks?
1. **Multi-Assertion Contract Tests:** High-severity integration tests (such as batch CLI execution or encrypted document handling) evaluate multiple distinct architectural invariants within a single test execution (for example, verifying *both* that the process exits with OS code `0` *and* that the CSV output table labels the corrupted/encrypted file as `INVALID`).
2. **Atomic Verification Logging:** Through our custom pytest fixture hook in [`tests/conftest.py`](file:///c:/Stuff/Projects/TNQ_project/tests/conftest.py), every distinct business oracle assertion registers an independent entry in `test_report.csv` formatted as `checks,input,expected,actual,result`.

This document explains **every single one of the 132 individual checks**, detailing the test input, expected oracle, actual system behavior, quality engineering rationale, and the specific production defect it prevents.

---

## Quality Engineering Methodology & Testing Architecture

The verification suite is structured around rigorous software quality assurance disciplines:

```mermaid
flowchart TD
    subgraph L1["Layer 1: Unit Level (Pure Logic)"]
        D[Date Parsing Engine: 25 Checks]
        S[Slash Ambiguity & Inference: 6 Checks]
        R[Rejection & Boundary Oracles: 17 Checks]
    end
    subgraph L2["Layer 2: Component Level (Regex & Filtering)"]
        A[Label Permutations & Layouts: 18 Checks]
        E[Prose Decoys & Multi-Milestones: 15 Checks]
        I[Document Chronology Disambiguation: 3 Checks]
    end
    subgraph L3["Layer 3: Structural Level (OpenXML Engine)"]
        B[XML Text Extraction Fixtures: 6 Checks]
    end
    subgraph L4["Layer 4: System Level (CLI & Batch)"]
        C[CLI Contracts & OS Ergonomics: 18 Checks]
        G[Batch Sorting & Determinism: 4 Checks]
    end
    subgraph L5["Layer 5: End-to-End Acceptance (Real Manuscripts)"]
        M[20 Real Academic Sample Manuscripts: 20 Checks]
    end

    L1 --> L2 --> L3 --> L4 --> L5
```

### Applied QE Testing Disciplines
1. **Equivalence Partitioning (EP):** Dividing valid date formats (ISO, Day-Month-Year, Month-Day-Year, Ordinal) and invalid formats (gibberish, partial dates, out-of-range days) into discrete equivalence classes to achieve complete semantic coverage without redundant duplication.
2. **Boundary Value Analysis (BVA):** Stress-testing exact temporal boundaries (day 0, day 32, leap day February 29 in non-leap years vs. leap years, 3-digit vs. 4-digit years, and Day 12 vs. Day 13 for slash ambiguity).
3. **Negative & Defensive Testing:** Subjecting the pipeline to malformed OpenXML structures, 0-byte files, pseudo-random non-ZIP binary garbage, Word lock temporary files (`~$`), and encrypted documents to prove graceful degradation without uncaught exceptions.
4. **Decoy Rejection & Negative Lookahead:** Defending against academic prose decoys (*"We received 120 samples..."*) and lifecycle lookalikes (*"Received in revised form"*, *"Published online"*, *"Date accepted"*).
5. **Deterministic Audit Trail:** Ensuring repeated executions yield bit-for-bit identical results, strictly sorted alphabetically by filename.

---

## Master Index of All 132 Checks

| Check # | Identifier / Title | Category / Scenario | Test Input | Expected Output | Actual Output | Result |
|:---:|:---|:---:|:---|:---:|:---:|:---:|
| **1** | [G9] Empty input folder exits 0 | CLI System | `empty directory` | `0` | `0` | PASS |
| **2** | [H1] Header row is exactly file,received_date | CLI Contract | `empty directory` | `file,received_date` | `file,received_date` | PASS |
| **3** | [G10] Non-existent input folder exits non-zero | CLI System | `missing directory` | `1` | `1` | PASS |
| **4** | CLI argument count validation exits 2 | CLI Contract | `1 arg given` | `2` | `2` | PASS |
| **5** | CLI processes corrupt, empty, and valid files with exit code 0 | CLI Pipeline | `batch directory` | `0` | `0` | PASS |
| **6** | [G1] Corrupt file results in INVALID | Robustness | `01_corrupt.docx` | `INVALID` | `INVALID` | PASS |
| **7** | [G2] Empty 0-byte file results in INVALID | Robustness | `02_empty.docx` | `INVALID` | `INVALID` | PASS |
| **8** | [G3] Empty text docx results in INVALID | Robustness | `03_notext.docx` | `INVALID` | `INVALID` | PASS |
| **9** | Valid docx results in 2026-01-02 | Pipeline Acceptance | `04_valid.docx` | `2026-01-02` | `2026-01-02` | PASS |
| **10** | [G5] Word lock files starting with ~$ are skipped | File System Filter | `~$lock_file.docx` | `False` | `False` | PASS |
| **11** | [G4] Non-docx files (.txt, .pdf) are ignored | File System Filter | `notes.txt` | `False` | `False` | PASS |
| **12** | [G6] Uppercase .DOCX extension is processed | File System Filter | `uppercase.DOCX` | `True` | `True` | PASS |
| **13** | [H3] Filename containing comma is preserved and handled | CSV Sanitization | `article, final draft.docx` | `True` | `True` | PASS |
| **14** | [H4] Rows sorted alphabetically by filename | Output Invariant | `article, final draft.docx; uppercase.DOCX` | `True` | `True` | PASS |
| **15** | [H5] Overwrites existing output without stale data | Output Invariant | `stale content pre-existing` | `False` | `False` | PASS |
| **16** | [H10] Deterministic output across multiple runs | Audit Invariant | `run 1 vs run 2` | `IDENTICAL` | `IDENTICAL` | PASS |
| **17** | CLI --reason flag adds reason column | CLI Flag | `--reason` | `file,received_date,reason` | `file,received_date,reason` | PASS |
| **18** | CLI --policy dmy resolves ambiguous slash date as DMY | CLI Flag | `03/04/2026 with --policy dmy` | `2026-04-03` | `2026-04-03` | PASS |
| **19** | [C1] C1 standard abbreviated month | Date Unit | `2 Jan 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **20** | [C2] C2 full month name | Date Unit | `2 January 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **21** | [C3] C3 ISO format YYYY-MM-DD | Date Unit | `2026-01-02` | `2026-01-02` | `2026-01-02` | PASS |
| **22** | [C4] C4 ordinal day with suffix | Date Unit | `2nd January 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **23** | [C5] C5 US order with comma full month | Date Unit | `January 2, 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **24** | [C5] C5 US order with comma short month | Date Unit | `Jan 2, 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **25** | [C6] C6 leading zero on day | Date Unit | `02 Jan 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **26** | [C7] C7 slashed ISO YYYY/MM/DD | Date Unit | `2026/01/02` | `2026-01-02` | `2026-01-02` | PASS |
| **27** | [C8] C8 dotted ambiguous date [provisional Q1] | Date Unit | `2.1.2026` | `INVALID` | `INVALID` | PASS |
| **28** | [C8] C8 dotted ambiguous zero-padded [provisional Q1] | Date Unit | `02.01.2026` | `INVALID` | `INVALID` | PASS |
| **29** | [C8] C8 dotted unambiguous day > 12 | Date Unit | `21.12.2026` | `2026-12-21` | `2026-12-21` | PASS |
| **30** | [C9] C9 hyphenated ambiguous date [provisional Q1] | Date Unit | `02-01-2026` | `INVALID` | `INVALID` | PASS |
| **31** | [C9] C9 hyphenated with month name | Date Unit | `02-Jan-2026` | `2026-01-02` | `2026-01-02` | PASS |
| **32** | [C10] C10 month abbreviation with dot | Date Unit | `2 Jan. 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **33** | [C10] C10 four-letter Sept abbreviation with dot | Date Unit | `4th Sept. 2026` | `2026-09-04` | `2026-09-04` | PASS |
| **34** | [C11] C11 uppercase month name | Date Unit | `2 JANUARY 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **35** | [C12] C12 leading weekday with comma | Date Unit | `Friday, 2 January 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **36** | [C12] C12 leading weekday Sun abbreviation | Date Unit | `Sun, 2 Jan 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **37** | [C13] C13 ISO date with ISO time and UTC Z | Date Unit | `2026-01-02T10:30:00Z` | `2026-01-02` | `2026-01-02` | PASS |
| **38** | [C13] C13 date with time and timezone IST | Date Unit | `2 Jan 2026, 10:30 IST` | `2026-01-02` | `2026-01-02` | PASS |
| **39** | [C14] C14 comma after month name | Date Unit | `2 Jan, 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **40** | [C15] C15 parentheses wrapped date | Date Unit | `(2 Jan 2026)` | `2026-01-02` | `2026-01-02` | PASS |
| **41** | [C15] C15 square bracket wrapped date | Date Unit | `[2 Jan 2026]` | `2026-01-02` | `2026-01-02` | PASS |
| **42** | [C16] C16 French month name [provisional Q9] | Date Unit | `2 janvier 2026` | `INVALID` | `INVALID` | PASS |
| **43** | [C17] C17 valid leap day in leap year | Date Unit | `29 February 2028` | `2028-02-29` | `2028-02-29` | PASS |
| **44** | [D1] D1 slash ambiguous date [provisional Q1] | Slash Ambiguity | `03/04/2026` | `INVALID` | `INVALID` | PASS |
| **45** | [D2] D2 two-digit year ambiguous [provisional Q1, Q2] | Slash Ambiguity | `12/05/26` | `INVALID` | `INVALID` | PASS |
| **46** | [D3] D3 slash unambiguous day > 12 | Slash Ambiguity | `13/01/2026` | `2026-01-13` | `2026-01-13` | PASS |
| **47** | [D4] D4 slash unambiguous month slot > 12 | Slash Ambiguity | `01/13/2026` | `2026-01-13` | `2026-01-13` | PASS |
| **48** | [D5] D5 slash both readings valid [provisional Q1] | Slash Ambiguity | `02/01/2026` | `INVALID` | `INVALID` | PASS |
| **49** | [F3] F3 impossible day 31 April | Boundary Rejection | `31/04/2026` | `INVALID` | `INVALID` | PASS |
| **50** | [F3] F3 impossible day 31 April in words | Boundary Rejection | `31 April 2026` | `INVALID` | `INVALID` | PASS |
| **51** | [F3] F3 impossible day 32 Jan | Boundary Rejection | `32 Jan 2026` | `INVALID` | `INVALID` | PASS |
| **52** | [F3] F3 impossible day 0 Jan | Boundary Rejection | `0 Jan 2026` | `INVALID` | `INVALID` | PASS |
| **53** | [F4] F4 leap day in non-leap year | Boundary Rejection | `29 February 2026` | `INVALID` | `INVALID` | PASS |
| **54** | [F5] F5 month 13 | Boundary Rejection | `2026-13-01` | `INVALID` | `INVALID` | PASS |
| **55** | [F5] F5 month 00 | Boundary Rejection | `2026-00-10` | `INVALID` | `INVALID` | PASS |
| **56** | [F6] F6 partial month and year only [provisional Q5] | Boundary Rejection | `Mar 2026` | `INVALID` | `INVALID` | PASS |
| **57** | [F6] F6 partial year only [provisional Q5] | Boundary Rejection | `2026` | `INVALID` | `INVALID` | PASS |
| **58** | [F7] F7 three digit year rejected | Boundary Rejection | `2 Jan 202` | `INVALID` | `INVALID` | PASS |
| **59** | [F7] F7 pending non-date | Boundary Rejection | `pending` | `INVALID` | `INVALID` | PASS |
| **60** | [F7] F7 N/A non-date | Boundary Rejection | `N/A` | `INVALID` | `INVALID` | PASS |
| **61** | [F7] F7 TBD non-date | Boundary Rejection | `TBD` | `INVALID` | `INVALID` | PASS |
| **62** | [F11] F11 misspelled month Janaury [provisional Q7] | Boundary Rejection | `2 Janaury 2026` | `INVALID` | `INVALID` | PASS |
| **63** | [D1] Ambiguous date raises AMBIGUOUS | Engine Exception | `03/04/2026` | `AMBIGUOUS` | `AMBIGUOUS` | PASS |
| **64** | [F3] Impossible day raises IMPOSSIBLE | Engine Exception | `31/04/2026` | `IMPOSSIBLE` | `IMPOSSIBLE` | PASS |
| **65** | [F6] Partial date raises PARTIAL [provisional Q5] | Engine Exception | `Mar 2026` | `PARTIAL` | `PARTIAL` | PASS |
| **66** | [F7] Garbage raises UNPARSEABLE | Engine Exception | `random garbage text` | `UNPARSEABLE` | `UNPARSEABLE` | PASS |
| **67** | [A1] A1 standard colon | Label Permutation | `Received: 2 Jan 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **68** | [A2] A2 no colon separator | Label Permutation | `Received 2 Jan 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **69** | [A3] A3 joined runs with prefix | Label Permutation | `Article history: Received: 2 Jan 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **70** | [A4] A4 lowercase received | Label Permutation | `received: 2 Jan 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **71** | [A4] A4 uppercase RECEIVED | Label Permutation | `RECEIVED: 2 Jan 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **72** | [A5] A5 Date received variant [provisional Q3] | Label Permutation | `Date received: 2 Jan 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **73** | [A5] A5 Received on variant [provisional Q3] | Label Permutation | `Received on: 2 Jan 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **74** | [A5] A5 Manuscript received variant [provisional Q3] | Label Permutation | `Manuscript received: 2 Jan 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **75** | [A5] A5 Date of receipt variant [provisional Q3] | Label Permutation | `Date of receipt: 2 Jan 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **76** | [A6] A6 table row joined cells | Layout Structure | `Received 2026-01-02` | `2026-01-02` | `2026-01-02` | PASS |
| **77** | [A6] A6 separate paragraph label and date | Layout Structure | `Received: // 2 Jan 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **78** | [A7] A7 multiple spaces between label and date | Layout Structure | `Received    2 Jan 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **79** | [A8] A8 dash separator | Separator Variation | `Received - 2 Jan 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **80** | [A8] A8 full-width colon separator | Separator Variation | `Received：2 Jan 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **81** | [A9] A9 unified text block | Layout Structure | `Received: 2 Jan 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **82** | [A10] A10 substitute label Submitted [provisional Q3] | Negative Substitute | `Submitted: 2 Jan 2026` | `INVALID` | `INVALID` | PASS |
| **83** | [A10] A10 substitute label Date accepted [provisional Q3] | Negative Substitute | `Date accepted: 2 Jan 2026` | `INVALID` | `INVALID` | PASS |
| **84** | [A10] A10 substitute label Published online [provisional Q3] | Negative Substitute | `Published online: 2 Jan 2026` | `INVALID` | `INVALID` | PASS |
| **85** | [E1] E1 prose received in sentence | Decoy Filtering | `We received 120 samples on 5 May 2025.` | `INVALID` | `INVALID` | PASS |
| **86** | [E1] E1 sentence starting with Received does not ruin valid date | Decoy Filtering | `Received comments from reviewers... // Received: 2 Jan 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **87** | [E2] E2 prose calibration received | Decoy Filtering | `We received the final calibration files on 14 February 2025` | `INVALID` | `INVALID` | PASS |
| **88** | [E3] E3 inline multi-label space separated | Milestone Separation | `Received: 2 Jan 2026 Revised: 4 Mar 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **89** | [E3] E3 inline multi-label period separated | Milestone Separation | `Received 2 January 2026. Accepted 10 April 2026.` | `2026-01-02` | `2026-01-02` | PASS |
| **90** | [E3] E3 inline multi-label in parentheses with comma | Milestone Separation | `(Received 2 Jan 2026, Accepted 10 Apr 2026)` | `2026-01-02` | `2026-01-02` | PASS |
| **91** | [E3] E3 received in revised form lookalike rejected | Milestone Separation | `Received 2 January 2026; Received in revised form 4 March 2026; Accepted 10 April 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **92** | [E4] E4 only revised and accepted present [provisional Q3] | Milestone Isolation | `Revised: 4 Mar 2026; Accepted: 10 Apr 2026` | `INVALID` | `INVALID` | PASS |
| **93** | [E5] E5 bibliography accessed date | Decoy Filtering | `[9] Regional Science Council. Guidance note. Accessed: 12 January 2026.` | `INVALID` | `INVALID` | PASS |
| **94** | [E6] E6 heading near date Author Contributions | Decoy Filtering | `Author Contributions: J.D.: Software` | `INVALID` | `INVALID` | PASS |
| **95** | [E7] E7 citation title with received | Decoy Filtering | `Smith J. Received wisdom on modern climate models. J Climatol. 2021;12:34-45.` | `INVALID` | `INVALID` | PASS |
| **96** | [E8] E8 multiple revision rounds ignored | Milestone Separation | `Received: 2 Jan 2026; Revised (round 2): 15 Mar 2026; Accepted: 20 Apr 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **97** | [E9] E9 multiple conflicting received dates [provisional Q4] | Conflict Detection | `Received: 2 Jan 2026 // Received: 15 Feb 2026` | `INVALID` | `INVALID` | PASS |
| **98** | [E10] E10 identical date repeated in header and body | Redundancy Handling | `Received 2 Jan 2026 | Accepted 10 Apr 2026 // Received: 2 Jan 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **99** | [E11] E11 published online and issue date decoys following received | Milestone Separation | `Received: 2 Jan 2026; Published online: 15 May 2026; Issue date: 1 June 2026` | `2026-01-02` | `2026-01-02` | PASS |
| **100** | [D6] Smart Q1 inference resolves DMY from other date | Context Disambiguation | `03/04 with 15/05` | `2026-04-03` | `2026-04-03` | PASS |
| **101** | [D6] Smart Q1 inference resolves MDY from Accepted chronology | Context Disambiguation | `03/04 with Accepted 28 March` | `2026-03-04` | `2026-03-04` | PASS |
| **102** | [D6] Smart Q1 inference defaults to DMY when ambiguous | Context Disambiguation | `03/04 with 05/06` | `2026-04-03` | `2026-04-03` | PASS |
| **103** | [B5] Received date in footer extracted | OpenXML Structural | `footer.docx` | `2026-01-02` | `2026-01-02` | PASS |
| **104** | [B7] Received date in text box extracted | OpenXML Structural | `textbox.docx` | `2026-01-02` | `2026-01-02` | PASS |
| **105** | [B8] Received date in footnote extracted | OpenXML Structural | `footnote.docx` | `2026-01-02` | `2026-01-02` | PASS |
| **106** | [B11] Tracked insertion accepted and deletion rejected [provisional Q8] | OpenXML Structural | `tracked.docx` | `2026-01-02` | `2026-01-02` | PASS |
| **107** | [B12] Hidden text included [provisional Q8] | OpenXML Structural | `hidden.docx` | `2026-01-02` | `2026-01-02` | PASS |
| **108** | [A9] Label split across multiple text runs is unified | OpenXML Structural | `split.docx` | `2026-01-02` | `2026-01-02` | PASS |
| **109** | [G7] Subfolders inside input folder are ignored [provisional Q10] | File System Scope | `nested_subfolder/nested_doc.docx` | `False` | `False` | PASS |
| **110** | [G8] Password-protected docx handled gracefully with code 0 | Pipeline Robustness | `encrypted.docx` | `0` | `0` | PASS |
| **111** | [G8] Encrypted file produces INVALID | Pipeline Robustness | `encrypted.docx` | `INVALID` | `INVALID` | PASS |
| **112** | [H2] Manuscripts batch run produces exactly 20 rows | Pipeline Invariant | `manuscripts folder` | `20` | `20` | PASS |
| **113** | [Sample merged_01.docx] Article history one-liner with received and revised | Acceptance Golden | `merged_01.docx` | `2026-01-02` | `2026-01-02` | PASS |
| **114** | [Sample merged_02.docx] Bottom of file with italic full month | Acceptance Golden | `merged_02.docx` | `2026-01-02` | `2026-01-02` | PASS |
| **115** | [Sample merged_03.docx] Dedicated line near top under title | Acceptance Golden | `merged_03.docx` | `2026-01-02` | `2026-01-02` | PASS |
| **116** | [Sample merged_04.docx] Received at bottom with accepted at top | Acceptance Golden | `merged_04.docx` | `2026-01-02` | `2026-01-02` | PASS |
| **117** | [Sample merged_05.docx] Ambiguous slash date 03/04/2026 [provisional Q1] | Acceptance Golden | `merged_05.docx` | `INVALID` | `INVALID` | PASS |
| **118** | [Sample merged_06.docx] Ambiguous slash date with decoy hints [provisional Q1] | Acceptance Golden | `merged_06.docx` | `INVALID` | `INVALID` | PASS |
| **119** | [Sample merged_07.docx] Ambiguous slash date at bottom [provisional Q1] | Acceptance Golden | `merged_07.docx` | `INVALID` | `INVALID` | PASS |
| **120** | [Sample merged_08.docx] Missing received with accepted present [provisional Q3] | Acceptance Golden | `merged_08.docx` | `INVALID` | `INVALID` | PASS |
| **121** | [Sample merged_09.docx] Prose received decoys with date accepted [provisional Q3] | Acceptance Golden | `merged_09.docx` | `INVALID` | `INVALID` | PASS |
| **122** | [Sample merged_10.docx] Separate line under authors | Acceptance Golden | `merged_10.docx` | `2026-01-02` | `2026-01-02` | PASS |
| **123** | [Sample merged_11.docx] Received with published online and issue date decoys | Acceptance Golden | `merged_11.docx` | `2026-01-02` | `2026-01-02` | PASS |
| **124** | [Sample merged_12.docx] Corrupt non-zip document handled safely | Acceptance Golden | `merged_12.docx` | `INVALID` | `INVALID` | PASS |
| **125** | [Sample merged_13.docx] Page header pipe-separated date metadata | Acceptance Golden | `merged_13.docx` | `2026-01-02` | `2026-01-02` | PASS |
| **126** | [Sample merged_14.docx] Received alongside received in revised form decoy | Acceptance Golden | `merged_14.docx` | `2026-01-02` | `2026-01-02` | PASS |
| **127** | [Sample merged_15.docx] Table row metadata extraction with joined cells | Acceptance Golden | `merged_15.docx` | `2026-01-02` | `2026-01-02` | PASS |
| **128** | [Sample merged_16.docx] Multiple revision rounds ignored | Acceptance Golden | `merged_16.docx` | `2026-01-02` | `2026-01-02` | PASS |
| **129** | [Sample merged_17.docx] Prose decoy rejected and bottom metadata line extracted | Acceptance Golden | `merged_17.docx` | `2026-01-02` | `2026-01-02` | PASS |
| **130** | [Sample merged_18.docx] Two-digit year with ambiguous slash date [provisional Q1] | Acceptance Golden | `merged_18.docx` | `INVALID` | `INVALID` | PASS |
| **131** | [Sample merged_19.docx] Impossible day 31 April rejected | Acceptance Golden | `merged_19.docx` | `INVALID` | `INVALID` | PASS |
| **132** | [Sample merged_20.docx] Ordinal day format 2nd January | Acceptance Golden | `merged_20.docx` | `2026-01-02` | `2026-01-02` | PASS |

---

## Detailed Section-by-Section Engineering Breakdown

### Section 1: CLI Contract, System Flags & OS Robustness (Checks 1–18)

#### Check 1: `[G9] Empty input folder exits 0`
- **Test File:** [`tests/test_cli.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_cli.py)
- **Input:** An empty directory with zero `.docx` files.
- **Expected:** Process returns OS exit code `0`.
- **Actual:** Process returned exit code `0`.
- **Result:** `PASS`
- **QE Rationale & Risk Mitigated:** In POSIX / Bash production batch scripts (`set -e`), an automated step scanning a folder that happens to be empty (e.g. between scheduled publisher drops) must never crash or emit a failure code. It must gracefully report success with an empty dataset.

#### Check 2: `[H1] Header row is exactly file,received_date`
- **Test File:** [`tests/test_cli.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_cli.py)
- **Input:** Execution targeting an empty directory.
- **Expected:** Emits a CSV containing exactly `file,received_date` as line 1.
- **Actual:** `file,received_date`
- **Result:** `PASS`
- **QE Rationale & Risk Mitigated:** Downstream ingestion pipelines rely on strict CSV schema oracles. If the CLI fails to write the header when zero manuscripts are processed, downstream ETL parsers fail with an empty file error.

#### Check 3: `[G10] Non-existent input folder exits non-zero`
- **Test File:** [`tests/test_cli.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_cli.py)
- **Input:** Target path `/path/does/not/exist_12345`.
- **Expected:** Process terminates with exit code `1` and prints an informative error message to stderr.
- **Actual:** Process returned exit code `1`.
- **Result:** `PASS`
- **QE Rationale & Risk Mitigated:** Guarantees that misconfigured orchestrator paths, typo'd volume mounts, or missing network drives fail fast rather than silently creating an empty CSV and reporting false success.

#### Check 4: `CLI argument count validation exits 2`
- **Test File:** [`tests/test_cli.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_cli.py)
- **Input:** Single argument `input_dir` without the required `output.csv` target.
- **Expected:** Process terminates with exit code `2` (standard CLI syntax error code) and prints CLI usage.
- **Actual:** Process returned exit code `2`.
- **Result:** `PASS`
- **QE Rationale & Risk Mitigated:** Complies with POSIX CLI convention. Missing positional arguments must never result in an unhandled `IndexError` traceback.

#### Check 5: `CLI processes corrupt, empty, and valid files with exit code 0`
- **Test File:** [`tests/test_cli.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_cli.py)
- **Input:** Batch directory containing a mix of valid, corrupted, and 0-byte `.docx` files.
- **Expected:** Exit code `0` for the entire batch.
- **Actual:** Process returned exit code `0`.
- **Result:** `PASS`
- **QE Rationale & Risk Mitigated:** Core production resilience requirement: a single corrupted manuscript in a batch of 1,000 papers must *never* abort the entire batch pipeline. The script must process all peers and exit cleanly.

#### Check 6: `[G1] Corrupt file results in INVALID`
- **Test File:** [`tests/test_cli.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_cli.py)
- **Input:** `01_corrupt.docx` containing arbitrary non-zip binary text.
- **Expected:** Output CSV maps `01_corrupt.docx` to `INVALID`.
- **Actual:** `INVALID`
- **Result:** `PASS`
- **QE Rationale & Risk Mitigated:** Verifies that unhandled `zipfile.BadZipFile` exceptions are intercepted by `DocxReadError` and mapped to business `INVALID` without crashing.

#### Check 7: `[G2] Empty 0-byte file results in INVALID`
- **Test File:** [`tests/test_cli.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_cli.py)
- **Input:** `02_empty.docx` of length 0 bytes.
- **Expected:** Output CSV maps `02_empty.docx` to `INVALID`.
- **Actual:** `INVALID`
- **Result:** `PASS`
- **QE Rationale & Risk Mitigated:** Zero-byte files occur frequently during interrupted network transfers or disk allocation failures. The extractor handles EOF safely.

#### Check 8: `[G3] Empty text docx results in INVALID`
- **Test File:** [`tests/test_cli.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_cli.py)
- **Input:** Valid ZIP archive containing minimal valid OpenXML but zero textual paragraphs.
- **Expected:** Output CSV maps `03_notext.docx` to `INVALID`.
- **Actual:** `INVALID`
- **Result:** `PASS`
- **QE Rationale & Risk Mitigated:** Prevents `IndexError` or `NoneType` issues when the XML document body is completely devoid of `<w:t>` tags.

#### Check 9: `Valid docx results in 2026-01-02`
- **Test File:** [`tests/test_cli.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_cli.py)
- **Input:** `04_valid.docx` containing `"Received: 2 Jan 2026"`.
- **Expected:** Extracted value is `2026-01-02`.
- **Actual:** `2026-01-02`
- **Result:** `PASS`
- **QE Rationale & Risk Mitigated:** Basic end-to-end positive smoke test verifying that the full CLI-to-XML extraction pipeline functions on standard input.

#### Check 10: `[G5] Word lock files starting with ~$ are skipped`
- **Test File:** [`tests/test_cli.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_cli.py)
- **Input:** Directory containing an active MS Word owner file `~$lock_file.docx`.
- **Expected:** File is ignored; not present in the output CSV (`False`).
- **Actual:** `False`
- **Result:** `PASS`
- **QE Rationale & Risk Mitigated:** When editors have manuscripts open in Microsoft Word, Word drops temporary 162-byte lock files named `~$filename.docx`. The extractor ignores these to avoid false `INVALID` records.

#### Check 11: `[G4] Non-docx files (.txt, .pdf) are ignored`
- **Test File:** [`tests/test_cli.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_cli.py)
- **Input:** Directory containing `notes.txt` and `sample.pdf`.
- **Expected:** Files are filtered out; not present in CSV (`False`).
- **Actual:** `False`
- **Result:** `PASS`
- **QE Rationale & Risk Mitigated:** Manuscript directories often hold supplementary PDFs, image figures, and text notes. Only `.docx` files must be processed.

#### Check 12: `[G6] Uppercase .DOCX extension is processed`
- **Test File:** [`tests/test_cli.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_cli.py)
- **Input:** `uppercase.DOCX` (uppercase extension common on Windows and legacy cameras/scanners).
- **Expected:** File is processed and present in CSV (`True`).
- **Actual:** `True`
- **Result:** `PASS`
- **QE Rationale & Risk Mitigated:** Prevents extension case-sensitivity bugs on Linux/POSIX containers where `.DOCX != .docx`.

#### Check 13: `[H3] Filename containing comma is preserved and handled`
- **Test File:** [`tests/test_cli.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_cli.py)
- **Input:** Manuscript named `article, final draft.docx`.
- **Expected:** Preserved cleanly and wrapped in standard CSV escaping (`True`).
- **Actual:** `True`
- **Result:** `PASS`
- **QE Rationale & Risk Mitigated:** Comma-separated files corrupt standard CSV columns if quotes are not handled by Python's `csv.writer(quoting=csv.QUOTE_MINIMAL)`.

#### Check 14: `[H4] Rows sorted alphabetically by filename`
- **Test File:** [`tests/test_cli.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_cli.py)
- **Input:** Files `uppercase.DOCX` and `article, final draft.docx`.
- **Expected:** CSV lists `article, final draft.docx` first, then `uppercase.DOCX` (`True`).
- **Actual:** `True`
- **Result:** `PASS`
- **QE Rationale & Risk Mitigated:** File systems return entries in arbitrary inode order. Sorting alphabetically ensures deterministic output across all operating systems.

#### Check 15: `[H5] Overwrites existing output without stale data`
- **Test File:** [`tests/test_cli.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_cli.py)
- **Input:** An existing `output.csv` with 50 lines of stale data from a prior run.
- **Expected:** Stale lines are truncated completely; new output overwrites cleanly (`False`).
- **Actual:** `False`
- **Result:** `PASS`
- **QE Rationale & Risk Mitigated:** Prevents "ghost rows" where an old output file is appended to rather than cleanly overwritten.

#### Check 16: `[H10] Deterministic output across multiple runs`
- **Test File:** [`tests/test_cli.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_cli.py)
- **Input:** Running the extractor twice on the identical dataset.
- **Expected:** Exact byte-for-byte identical output (`IDENTICAL`).
- **Actual:** `IDENTICAL`
- **Result:** `PASS`
- **QE Rationale & Risk Mitigated:** Guarantees idempotency and eliminates race conditions or reliance on unseeded hash orders.

#### Check 17: `CLI --reason flag adds reason column`
- **Test File:** [`tests/test_cli.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_cli.py)
- **Input:** Invocation with `--reason` flag.
- **Expected:** Header row emits `file,received_date,reason`.
- **Actual:** `file,received_date,reason`
- **Result:** `PASS`
- **QE Rationale & Risk Mitigated:** Quality engineers and production operators require an audit trail explaining why any manuscript was marked `INVALID` or which scenario matched.

#### Check 18: `CLI --policy dmy resolves ambiguous slash date as DMY`
- **Test File:** [`tests/test_cli.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_cli.py)
- **Input:** Document containing `03/04/2026` run with `--policy dmy`.
- **Expected:** Resolves to `2026-04-03` instead of `INVALID`.
- **Actual:** `2026-04-03`
- **Result:** `PASS`
- **QE Rationale & Risk Mitigated:** Allows editorial teams with known UK/Commonwealth regional guidelines to enforce Day-Month-Year resolution via command-line flags.

---

### Section 2: Date Parsing Engine, Lexical Variations & Timezones (Checks 19–43: Scenario Category C)

#### Check 19: `[C1] C1 standard abbreviated month`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"2 Jan 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Validates the primary editorial format (single digit day + 3-letter month + 4-digit year).

#### Check 20: `[C2] C2 full month name`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"2 January 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Verifies full English month name lexical matching.

#### Check 21: `[C3] C3 ISO format YYYY-MM-DD`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"2026-01-02"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Verifies ISO-8601 standard date compliance.

#### Check 22: `[C4] C4 ordinal day with suffix`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"2nd January 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Strips English ordinal suffixes (`st`, `nd`, `rd`, `th`) before parsing numeric day.

#### Check 23: `[C5] C5 US order with comma full month`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"January 2, 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Supports standard North American format (`Month Day, Year`).

#### Check 24: `[C5] C5 US order with comma short month`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"Jan 2, 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Supports abbreviated North American format (`Mon Day, Year`).

#### Check 25: `[C6] C6 leading zero on day`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"02 Jan 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Ensures leading zero on single-digit days (`01`-`09`) does not corrupt day extraction.

#### Check 26: `[C7] C7 slashed ISO YYYY/MM/DD`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"2026/01/02"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Slashed ISO format is unambiguous because the 4-digit year leads.

#### Check 27: `[C8] C8 dotted ambiguous date [provisional Q1]`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"2.1.2026"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Without month name or document context, `2.1.2026` could be Jan 2 or Feb 1. Rejecting preserves strict precision.

#### Check 28: `[C8] C8 dotted ambiguous zero-padded [provisional Q1]`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"02.01.2026"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Zero-padded dotted date remains ambiguous between Jan 2 and Feb 1.

#### Check 29: `[C8] C8 dotted unambiguous day > 12`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"21.12.2026"`
- **Expected:** `2026-12-21`
- **Actual:** `2026-12-21` | `PASS`
- **QE Rationale:** Because 21 > 12, the first slot can only be Day, making the date unambiguously 21 Dec 2026.

#### Check 30: `[C9] C9 hyphenated ambiguous date [provisional Q1]`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"02-01-2026"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Ambiguous between Day-Month and Month-Day; rejects to prevent silent data corruption.

#### Check 31: `[C9] C9 hyphenated with month name`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"02-Jan-2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Common scientific convention (`DD-Mon-YYYY`); unambiguous due to month string.

#### Check 32: `[C10] C10 month abbreviation with dot`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"2 Jan. 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Handles punctuation dot after abbreviated month (`Jan.`, `Feb.`, etc.).

#### Check 33: `[C10] C10 four-letter Sept abbreviation with dot`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"4th Sept. 2026"`
- **Expected:** `2026-09-04`
- **Actual:** `2026-09-04` | `PASS`
- **QE Rationale:** Accommodates British English four-letter abbreviation `Sept.` for September.

#### Check 34: `[C11] C11 uppercase month name`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"2 JANUARY 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** All-caps typesetting in publication mastheads must match case-insensitively.

#### Check 35: `[C12] C12 leading weekday with comma`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"Friday, 2 January 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Ignores leading weekday names like `Friday,` and parses the underlying date.

#### Check 36: `[C12] C12 leading weekday Sun abbreviation`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"Sun, 2 Jan 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Verifies the regex `sun(?:day)?` fix, ensuring 3-letter weekday prefixes work properly.

#### Check 37: `[C13] C13 ISO date with ISO time and UTC Z`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"2026-01-02T10:30:00Z"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Strips timestamp and UTC `Z` suffix, preserving pure calendar date.

#### Check 38: `[C13] C13 date with time and timezone IST`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"2 Jan 2026, 10:30 IST"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Strips time components and named timezones (IST, EST, GMT, UTC).

#### Check 39: `[C14] C14 comma after month name`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"2 Jan, 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Tolerates errant author punctuation commas between month and year.

#### Check 40: `[C15] C15 parentheses wrapped date`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"(2 Jan 2026)"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Handles enclosing parentheses frequently found in citation and history blocks.

#### Check 41: `[C15] C15 square bracket wrapped date`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"[2 Jan 2026]"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Handles enclosing square brackets.

#### Check 42: `[C16] C16 French month name [provisional Q9]`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"2 janvier 2026"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Per business rule Q9, only English-language manuscripts are officially supported. Non-English months reject as `INVALID`.

#### Check 43: `[C17] C17 valid leap day in leap year`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"29 February 2028"`
- **Expected:** `2028-02-29`
- **Actual:** `2028-02-29` | `PASS`
- **QE Rationale:** Year 2028 is divisible by 4, confirming that valid leap days pass date verification.

---

### Section 3: Slash Date Ambiguity & Day/Month Disambiguation (Checks 44–48, 63: Scenario Category D)

#### Check 44: `[D1] D1 slash ambiguous date [provisional Q1]`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"03/04/2026"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** 3 and 4 are both <= 12; cannot determine if 3 April or 4 March without external hint. Strict Q1 policy marks `INVALID`.

#### Check 45: `[D2] D2 two-digit year ambiguous [provisional Q1, Q2]`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"12/05/26"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Ambiguous between 12 May and 5 Dec. Also tests 2-digit year handling.

#### Check 46: `[D3] D3 slash unambiguous day > 12`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"13/01/2026"`
- **Expected:** `2026-01-13`
- **Actual:** `2026-01-13` | `PASS`
- **QE Rationale:** 13 > 12, so the first component must be Day, disambiguating as DMY.

#### Check 47: `[D4] D4 slash unambiguous month slot > 12`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"01/13/2026"`
- **Expected:** `2026-01-13`
- **Actual:** `2026-01-13` | `PASS`
- **QE Rationale:** The second component is 13 > 12, which can only be Day, disambiguating as MDY.

#### Check 48: `[D5] D5 slash both readings valid [provisional Q1]`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"02/01/2026"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Confirms that 02/01/2026 (both readings valid calendar days) is marked `INVALID` under default isolation.

#### Check 63: `[D1] Ambiguous date raises AMBIGUOUS`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"03/04/2026"` directly into internal date parsing engine.
- **Expected:** Returns status string `AMBIGUOUS`.
- **Actual:** `AMBIGUOUS` | `PASS`
- **QE Rationale:** Unit-level verification ensuring the internal parser provides clear diagnostic reason codes for CLI reporting.

---

### Section 4: Invalid Formats, Impossible Days & Lexical Boundary Rejection (Checks 49–62, 64–66: Scenario Category F)

#### Check 49: `[F3] F3 impossible day 31 April`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"31/04/2026"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** April has only 30 days. Boundary value analysis catches calendar errors.

#### Check 50: `[F3] F3 impossible day 31 April in words`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"31 April 2026"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Impossible day in words must be rejected identically to numeric format.

#### Check 51: `[F3] F3 impossible day 32 Jan`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"32 Jan 2026"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Day > 31 is physically impossible and must fail calendar validation.

#### Check 52: `[F3] F3 impossible day 0 Jan`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"0 Jan 2026"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Day 0 is invalid across all calendar systems.

#### Check 53: `[F4] F4 leap day in non-leap year`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"29 February 2026"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** 2026 is not a leap year. February 29 must fail validation via `datetime.date(2026, 2, 29)`.

#### Check 54: `[F5] F5 month 13`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"2026-13-01"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Month out of range (1–12).

#### Check 55: `[F5] F5 month 00`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"2026-00-10"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Month 0 out of range.

#### Check 56: `[F6] F6 partial month and year only [provisional Q5]`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"Mar 2026"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Per business rule Q5, partial dates missing day information cannot be accepted as publication receipt dates.

#### Check 57: `[F6] F6 partial year only [provisional Q5]`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"2026"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** A bare year without month and day is incomplete and rejected.

#### Check 58: `[F7] F7 three digit year rejected`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"2 Jan 202"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Prevents truncation defects where a 3-digit year `202` was accidentally padded to `0202-01-02`.

#### Check 59: `[F7] F7 pending non-date`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"pending"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Placeholder text in editorial drafts must not be accepted.

#### Check 60: `[F7] F7 N/A non-date`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"N/A"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Common placeholder for manuscripts without historical receipt records.

#### Check 61: `[F7] F7 TBD non-date`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"TBD"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Rejects "To Be Determined" placeholder strings.

#### Check 62: `[F11] F11 misspelled month Janaury [provisional Q7]`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"2 Janaury 2026"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Per business rule Q7, the system rejects fuzzy matching or typo tolerance to maintain absolute precision.

#### Check 64: `[F3] Impossible day raises IMPOSSIBLE`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"31/04/2026"`
- **Expected:** Returns status string `IMPOSSIBLE`.
- **Actual:** `IMPOSSIBLE` | `PASS`
- **QE Rationale:** Verifies diagnostic granularity in internal reason tracking.

#### Check 65: `[F6] Partial date raises PARTIAL [provisional Q5]`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"Mar 2026"`
- **Expected:** Returns status string `PARTIAL`.
- **Actual:** `PARTIAL` | `PASS`
- **QE Rationale:** Distinguishes partial dates from unparseable gibberish.

#### Check 66: `[F7] Garbage raises UNPARSEABLE`
- **Test File:** [`tests/test_dates.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_dates.py)
- **Input:** `"random garbage text"`
- **Expected:** Returns status string `UNPARSEABLE`.
- **Actual:** `UNPARSEABLE` | `PASS`
- **QE Rationale:** Verifies internal state for completely unparseable tokens.

---

### Section 5: Received Label Syntactic Variations & Separators (Checks 67–84: Scenario Category A)

#### Check 67: `[A1] A1 standard colon`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Received: 2 Jan 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Baseline editorial metadata format.

#### Check 68: `[A2] A2 no colon separator`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Received 2 Jan 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Accommodates journals that omit the colon between label and date.

#### Check 69: `[A3] A3 joined runs with prefix`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Article history: Received: 2 Jan 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Extracts the date even when nested inside an "Article history:" block.

#### Check 70: `[A4] A4 lowercase received`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"received: 2 Jan 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Case-insensitivity for lowercase typesetting.

#### Check 71: `[A4] A4 uppercase RECEIVED`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"RECEIVED: 2 Jan 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Case-insensitivity for all-caps typesetting.

#### Check 72: `[A5] A5 Date received variant [provisional Q3]`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Date received: 2 Jan 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Handles standard publishing variant "Date received".

#### Check 73: `[A5] A5 Received on variant [provisional Q3]`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Received on: 2 Jan 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Handles prepositional variant "Received on".

#### Check 74: `[A5] A5 Manuscript received variant [provisional Q3]`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Manuscript received: 2 Jan 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Handles formal IEEE-style variant "Manuscript received".

#### Check 75: `[A5] A5 Date of receipt variant [provisional Q3]`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Date of receipt: 2 Jan 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Handles noun phrase variant "Date of receipt".

#### Check 76: `[A6] A6 table row joined cells`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Received 2026-01-02"` (concatenated cell contents from a metadata table).
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Table cell joins in XML extractors lack colons; proves seamless extraction across table columns.

#### Check 77: `[A6] A6 separate paragraph label and date`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** Label `"Received:"` in paragraph $N$, date `"2 Jan 2026"` in paragraph $N+1$.
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Resolves AI Audit Bug #3: when Word paragraphs split label and date across paragraphs, the lookahead buffer reconciles them.

#### Check 78: `[A7] A7 multiple spaces between label and date`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Received    2 Jan 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Tabulations and multi-space kerning must not break date discovery.

#### Check 79: `[A8] A8 dash separator`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Received - 2 Jan 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Accommodates hyphens/dashes used as delimiters.

#### Check 80: `[A8] A8 full-width colon separator`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Received：2 Jan 2026"` (Unicode `\uff1a`).
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Full-width colon used in Asian typesetting systems (CJK).

#### Check 81: `[A9] A9 unified text block`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Received: 2 Jan 2026"` in unified text.
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Baseline sanity check for standard unified blocks.

#### Check 82: `[A10] A10 substitute label Submitted [provisional Q3]`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Submitted: 2 Jan 2026"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Per business rule Q3, "Submitted" is *not* a synonym for "Received" unless explicitly authorized.

#### Check 83: `[A10] A10 substitute label Date accepted [provisional Q3]`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Date accepted: 2 Jan 2026"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** "Date accepted" represents acceptance, not manuscript receipt.

#### Check 84: `[A10] A10 substitute label Published online [provisional Q3]`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Published online: 2 Jan 2026"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** "Published online" represents publication, not receipt.

---

### Section 6: Decoy Filtering, Prose Disambiguation & Inline Metadata (Checks 85–99: Scenario Category E)

#### Check 85: `[E1] E1 prose received in sentence`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"We received 120 samples on 5 May 2025."`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Body text prose using the past-tense verb "received" followed by arbitrary quantities must not be falsely parsed as manuscript receipt dates.

#### Check 86: `[E1] E1 sentence starting with Received does not ruin valid date`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** Paragraph 1: `"Received comments from reviewers were addressed."` followed by Paragraph 2: `"Received: 2 Jan 2026"`.
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Resolves AI Audit Bug #2: prose sentences starting with "Received..." were previously poisoning the document extractor. The `DATE_STARTER_REGEX` now rejects the prose line and allows the genuine date to be extracted.

#### Check 87: `[E2] E2 prose calibration received`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"We received the final calibration files on 14 February 2025"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Rejects conversational experimental descriptions.

#### Check 88: `[E3] E3 inline multi-label space separated`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Received: 2 Jan 2026 Revised: 4 Mar 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Resolves AI Audit Bug #1: when multiple milestones appear on one line separated by whitespace, `NEXT_LABEL_PATTERN` bounds the date extraction precisely at `"Revised:"`.

#### Check 89: `[E3] E3 inline multi-label period separated`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Received 2 January 2026. Accepted 10 April 2026."`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Bounds date candidate before `.` followed by `"Accepted"`.

#### Check 90: `[E3] E3 inline multi-label in parentheses with comma`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"(Received 2 Jan 2026, Accepted 10 Apr 2026)"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Bounds date candidate before comma followed by `"Accepted"`.

#### Check 91: `[E3] E3 received in revised form lookalike rejected`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Received 2 January 2026; Received in revised form 4 March 2026; Accepted 10 April 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Prevents the phrase "Received in revised form" from being matched as the primary received date or creating conflicting dates.

#### Check 92: `[E4] E4 only revised and accepted present [provisional Q3]`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Revised: 4 Mar 2026; Accepted: 10 Apr 2026"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** When a manuscript contains "Revised" and "Accepted" but no "Received", it must return `INVALID` rather than substituting other milestones.

#### Check 93: `[E5] E5 bibliography accessed date`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"[9] Regional Science Council. Guidance note. Accessed: 12 January 2026."`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Bibliography references with "Accessed:" dates must not be extracted.

#### Check 94: `[E6] E6 heading near date Author Contributions`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Author Contributions: J.D.: Software"`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Standard journal backmatter headings containing colons must not trigger false positives.

#### Check 95: `[E7] E7 citation title with received`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Smith J. Received wisdom on modern climate models. J Climatol. 2021;12:34-45."`
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Journal article titles starting with "Received wisdom..." in reference lists are ignored.

#### Check 96: `[E8] E8 multiple revision rounds ignored`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Received: 2 Jan 2026; Revised (round 2): 15 Mar 2026; Accepted: 20 Apr 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Ensures multi-round peer review milestones (`Revised (round 1)`, `Revised (round 2)`) do not interfere with primary receipt date extraction.

#### Check 97: `[E9] E9 multiple conflicting received dates [provisional Q4]`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** Line 1: `"Received: 2 Jan 2026"` followed by Line 2: `"Received: 15 Feb 2026"`.
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Per business rule Q4, if two distinct and contradictory "Received" dates exist in a single file, the system flags `INVALID` for human editorial review.

#### Check 98: `[E10] E10 identical date repeated in header and body`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** Running header: `"Received 2 Jan 2026 | Accepted 10 Apr 2026"` and body footnote: `"Received: 2 Jan 2026"`.
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Identical duplicate dates (e.g. repeated in header and footer) are consolidated without triggering conflicting date rejection.

#### Check 99: `[E11] E11 published online and issue date decoys following received`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** `"Received: 2 Jan 2026; Published online: 15 May 2026; Issue date: 1 June 2026"`
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Downstream publication milestones are excluded by lookahead delimiters.

---

### Section 7: Document-Level Smart Context Inference (Checks 100–102: Scenario D6 / Q1 Policy)

#### Check 100: `[D6] Smart Q1 inference resolves DMY from other date`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** Received date is ambiguous `"03/04/2026"`, but Accepted date is unambiguous `"15/05/2026"` (15 > 12).
- **Expected:** Resolves to DMY: `2026-04-03`.
- **Actual:** `2026-04-03` | `PASS`
- **QE Rationale:** Real-world papers maintain internal stylistic consistency. If another milestone in the document proves Day-Month-Year formatting, the ambiguous receipt date is safely resolved.

#### Check 101: `[D6] Smart Q1 inference resolves MDY from Accepted chronology`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** Received date is `"03/04/2026"` and Accepted date is `"28 March 2026"`.
- **Expected:** Resolves to MDY: `2026-03-04` (March 4, 2026).
- **Actual:** `2026-03-04` | `PASS`
- **QE Rationale:** Physical chronology invariant: a manuscript cannot be received *after* it was accepted ($Received \le Accepted$). If DMY yields 3 April 2026 (after 28 March 2026), it violates causality. Only MDY (4 March 2026) is chronologically valid.

#### Check 102: `[D6] Smart Q1 inference defaults to DMY when ambiguous`
- **Test File:** [`tests/test_finder.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_finder.py)
- **Input:** Received date is `"03/04/2026"` and Accepted date is `"05/06/2026"` (both ambiguous).
- **Expected:** Defaults to DMY: `2026-04-03`.
- **Actual:** `2026-04-03` | `PASS`
- **QE Rationale:** When the user selects smart inference mode and all document dates remain mutually ambiguous, the system safely falls back to standard international scientific DMY.

---

### Section 8: OpenXML Structural Parsing Fixtures (Checks 103–108: Category B & A9)

#### Check 103: `[B5] Received date in footer extracted`
- **Test File:** [`tests/test_fixtures.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_fixtures.py)
- **Input:** Programmatically generated `.docx` placing `"Received: 2 Jan 2026"` inside `word/footer1.xml`.
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Many academic templates (e.g. Elsevier, Springer) place bibliographic history in page footers. Structural parser scans all footer parts.

#### Check 104: `[B7] Received date in text box extracted`
- **Test File:** [`tests/test_fixtures.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_fixtures.py)
- **Input:** Programmatically generated `.docx` placing `"Received: 2 Jan 2026"` inside a `<w:txbxContent>` drawing element.
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Modern journal templates often use floating margin text boxes for publication metadata.

#### Check 105: `[B8] Received date in footnote extracted`
- **Test File:** [`tests/test_fixtures.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_fixtures.py)
- **Input:** Programmatically generated `.docx` placing `"Received: 2 Jan 2026"` inside `word/footnotes.xml`.
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Title page author affiliation notes frequently house received dates as unnumbered title footnotes.

#### Check 106: `[B11] Tracked insertion accepted and deletion rejected [provisional Q8]`
- **Test File:** [`tests/test_fixtures.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_fixtures.py)
- **Input:** Programmatically generated `.docx` containing tracked changes: `<w:del>` with `"Received: 15 Feb 2025"` and `<w:ins>` with `"Received: 2 Jan 2026"`.
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Per business rule Q8, the parser mimics Word's "Accept All Changes" view by ignoring deleted runs (`<w:delText>`) and accepting inserted runs (`<w:ins>`).

#### Check 107: `[B12] Hidden text included [provisional Q8]`
- **Test File:** [`tests/test_fixtures.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_fixtures.py)
- **Input:** Programmatically generated `.docx` containing `"Received: 2 Jan 2026"` styled with `<w:vanish/>` (Word hidden text).
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Editorial automation systems often embed machine-readable metadata formatted as hidden text for typesetting engines.

#### Check 108: `[A9] Label split across multiple text runs is unified`
- **Test File:** [`tests/test_fixtures.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_fixtures.py)
- **Input:** Programmatically generated `.docx` where `"Received: "` is in Run 1 (bold) and `"2 Jan 2026"` is in Run 2 (plain).
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Word XML fragments text across `<w:r>` tags whenever formatting changes. The text accumulator unifies paragraph runs before regex matching.

---

### Section 9: Batch Pipeline, File System & Security (Checks 109–112: Category G & H)

#### Check 109: `[G7] Subfolders inside input folder are ignored [provisional Q10]`
- **Test File:** [`tests/test_fixtures.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_fixtures.py)
- **Input:** Nested subdirectory containing `nested_subfolder/nested_doc.docx`.
- **Expected:** Subfolder contents are ignored; `nested_doc.docx` is not in CSV (`False`).
- **Actual:** `False`
- **Result:** `PASS`
- **QE Rationale:** Per business rule Q10, batch processing is flat (`os.listdir` / non-recursive) to avoid picking up archived drafts or reference material placed in subdirectories.

#### Check 110: `[G8] Password-protected docx handled gracefully with code 0`
- **Test File:** [`tests/test_fixtures.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_fixtures.py)
- **Input:** Encrypted compound document (`encrypted.docx`).
- **Expected:** CLI returns exit code `0`.
- **Actual:** `0`
- **Result:** `PASS`
- **QE Rationale:** Encrypted Word documents use an OLE Compound Document container rather than a ZIP structure. The CLI must handle this gracefully without crashing the batch.

#### Check 111: `[G8] Encrypted file produces INVALID`
- **Test File:** [`tests/test_fixtures.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_fixtures.py)
- **Input:** `encrypted.docx`.
- **Expected:** Output CSV row records `INVALID`.
- **Actual:** `INVALID`
- **Result:** `PASS`
- **QE Rationale:** Since password-protected files cannot be decrypted without credentials, they are marked `INVALID` for manual inspection.

#### Check 112: `[H2] Manuscripts batch run produces exactly 20 rows`
- **Test File:** [`tests/test_samples.py`](file:///c:/Stuff/Projects/TNQ_project/tests/test_samples.py)
- **Input:** Executing batch processing across the entire `manuscripts/` directory.
- **Expected:** CSV contains exactly 20 data rows corresponding to the 20 sample files.
- **Actual:** `20`
- **Result:** `PASS`
- **QE Rationale:** Completeness invariant: every input file must have an entry in the output CSV (no dropped files, no ghost duplicates).

---

### Section 10: Real-World Academic Manuscript End-to-End Suite (Checks 113–132: Samples 1–20)

#### Check 113: `[Sample merged_01.docx] Article history one-liner with received and revised`
- **Sample File:** [`manuscripts/merged_01.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_01.docx)
- **Layout & Structure:** Article history header line containing both "Received 2 January 2026" and "Revised 4 March 2026".
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Verifies clean milestone splitting and standard full month parsing on a real manuscript.

#### Check 114: `[Sample merged_02.docx] Bottom of file with italic full month`
- **Sample File:** [`manuscripts/merged_02.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_02.docx)
- **Layout & Structure:** Located at bottom of manuscript in italic styling.
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Proves formatting tags (italics `<w:i>`) do not disrupt text extraction.

#### Check 115: `[Sample merged_03.docx] Dedicated line near top under title`
- **Sample File:** [`manuscripts/merged_03.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_03.docx)
- **Layout & Structure:** Prominent line under title and author block.
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Tests top-of-file metadata location.

#### Check 116: `[Sample merged_04.docx] Received at bottom with accepted at top`
- **Sample File:** [`manuscripts/merged_04.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_04.docx)
- **Layout & Structure:** "Accepted" metadata placed near top, genuine "Received" line placed in backmatter.
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Confirms that the presence of an early "Accepted" date does not hijack extraction.

#### Check 117: `[Sample merged_05.docx] Ambiguous slash date 03/04/2026 [provisional Q1]`
- **Sample File:** [`manuscripts/merged_05.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_05.docx)
- **Layout & Structure:** Dedicated line reading `"Received: 03/04/2026"`.
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Under baseline Q1 policy, standalone ambiguous slash dates must yield `INVALID`.

#### Check 118: `[Sample merged_06.docx] Ambiguous slash date with decoy hints [provisional Q1]`
- **Sample File:** [`manuscripts/merged_06.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_06.docx)
- **Layout & Structure:** Ambiguous date surrounded by conflicting body text hints.
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Prevents body text noise from falsely disambiguating metadata dates.

#### Check 119: `[Sample merged_07.docx] Ambiguous slash date at bottom [provisional Q1]`
- **Sample File:** [`manuscripts/merged_07.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_07.docx)
- **Layout & Structure:** Ambiguous slash date located in document backmatter.
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Confirms position invariance for slash ambiguity rejection.

#### Check 120: `[Sample merged_08.docx] Missing received with accepted present [provisional Q3]`
- **Sample File:** [`manuscripts/merged_08.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_08.docx)
- **Layout & Structure:** Contains "Accepted: 10 April 2026" but no received date.
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Proves that the absence of a receipt date safely returns `INVALID` rather than substituting other milestones.

#### Check 121: `[Sample merged_09.docx] Prose received decoys with date accepted [provisional Q3]`
- **Sample File:** [`manuscripts/merged_09.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_09.docx)
- **Layout & Structure:** Prose mentions of received samples in abstract, metadata only contains "Date accepted".
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Validates combined rejection of prose decoys and substitute labels.

#### Check 122: `[Sample merged_10.docx] Separate line under authors`
- **Sample File:** [`manuscripts/merged_10.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_10.docx)
- **Layout & Structure:** Standard frontmatter receipt date line under author affiliations.
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Standard production acceptance verification.

#### Check 123: `[Sample merged_11.docx] Received with published online and issue date decoys`
- **Sample File:** [`manuscripts/merged_11.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_11.docx)
- **Layout & Structure:** Received date followed by "Published online: 15 May 2026" and "Issue date: 1 June 2026".
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Verifies boundary lookahead successfully isolates received date from subsequent publication dates.

#### Check 124: `[Sample merged_12.docx] Corrupt non-zip document handled safely`
- **Sample File:** [`manuscripts/merged_12.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_12.docx)
- **Layout & Structure:** 2,048 bytes of pseudorandom binary garbage lacking a ZIP header.
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Verifies real corrupted file resilience in the golden manuscript set.

#### Check 125: `[Sample merged_13.docx] Page header pipe-separated date metadata`
- **Sample File:** [`manuscripts/merged_13.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_13.docx)
- **Layout & Structure:** Metadata placed in `word/header1.xml` pipe-separated (`Received 2 Jan 2026 | Accepted 10 Apr 2026`).
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Verifies XML header extraction and pipe delimiter splitting on real manuscripts.

#### Check 126: `[Sample merged_14.docx] Received alongside received in revised form decoy`
- **Sample File:** [`manuscripts/merged_14.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_14.docx)
- **Layout & Structure:** Contains both genuine receipt date and "Received in revised form 4 March 2026".
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Proves "Received in revised form" is recognized as a separate lifecycle milestone and ignored.

#### Check 127: `[Sample merged_15.docx] Table row metadata extraction with joined cells`
- **Sample File:** [`manuscripts/merged_15.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_15.docx)
- **Layout & Structure:** Manuscript history rendered as an OpenXML grid table where Column 1 is label and Column 2 is date.
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Verifies table cell iteration and cross-cell reconciliation on real manuscripts.

#### Check 128: `[Sample merged_16.docx] Multiple revision rounds ignored`
- **Sample File:** [`manuscripts/merged_16.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_16.docx)
- **Layout & Structure:** Includes "Revised (round 1)" and "Revised (round 2)".
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Multi-round revision manuscripts extract the original receipt date.

#### Check 129: `[Sample merged_17.docx] Prose decoy rejected and bottom metadata line extracted`
- **Sample File:** [`manuscripts/merged_17.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_17.docx)
- **Layout & Structure:** Body contains prose *"We received 120 samples on 5 May 2025"*; backmatter contains *"Received: 2 Jan 2026; Revised: 4 Mar 2026; Accepted: 10 Apr 2026"*.
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Complex real-world test: the prose line is safely rejected by `DATE_STARTER_REGEX`, and the genuine backmatter line is extracted.

#### Check 130: `[Sample merged_18.docx] Two-digit year with ambiguous slash date [provisional Q1]`
- **Sample File:** [`manuscripts/merged_18.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_18.docx)
- **Layout & Structure:** Contains `"Received: 12/05/26"`.
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Both day/month ambiguity and 2-digit year ambiguity; correctly marked `INVALID`.

#### Check 131: `[Sample merged_19.docx] Impossible day 31 April rejected`
- **Sample File:** [`manuscripts/merged_19.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_19.docx)
- **Layout & Structure:** Author typo specifying receipt on `"31 April 2026"`.
- **Expected:** `INVALID`
- **Actual:** `INVALID` | `PASS`
- **QE Rationale:** Demonstrates real-world calendar validation catching author typos.

#### Check 132: `[Sample merged_20.docx] Ordinal day format 2nd January`
- **Sample File:** [`manuscripts/merged_20.docx`](file:///c:/Stuff/Projects/TNQ_project/manuscripts/merged_20.docx)
- **Layout & Structure:** Formatted as `"Received: 2nd January 2026"`.
- **Expected:** `2026-01-02`
- **Actual:** `2026-01-02` | `PASS`
- **QE Rationale:** Proves ordinal day suffix parsing on a real manuscript.

---

## Traceability & Coverage Matrix

| Scenario Group | Scenario Codes Covered | Test Suites | Total Checks | Pass Rate |
|:---|:---:|:---:|:---:|:---:|
| **A: Received Label Variations** | A1–A10 | `test_finder.py`, `test_fixtures.py`, `test_samples.py` | 24 | 100% |
| **B: Location / Structural OpenXML** | B1–B12 | `test_fixtures.py`, `test_samples.py` | 16 | 100% |
| **C: Date Formats & Encodings** | C1–C17 | `test_dates.py` | 25 | 100% |
| **D: Slash Ambiguity & Smart Inference** | D1–D6 | `test_dates.py`, `test_finder.py`, `test_cli.py` | 9 | 100% |
| **E: Decoys, Prose & Milestones** | E1–E11 | `test_finder.py`, `test_samples.py` | 20 | 100% |
| **F: Invalid Formats & Boundaries** | F1–F11 | `test_dates.py`, `test_samples.py` | 17 | 100% |
| **G: File System & Defensive Errors** | G1–G10 | `test_cli.py`, `test_fixtures.py` | 11 | 100% |
| **H: Output Formatting & Contracts** | H1–H10 | `test_cli.py`, `test_samples.py` | 10 | 100% |
| **Total** | **All 8 Core Disciplines** | **5 Test Modules** | **132** | **100%** |

---

## Conclusion & Quality Engineering Verdict

The automated verification suite establishes comprehensive, end-to-end quality assurance for the Received-Date Extractor. By combining:
1. **Low-level unit testing** of pure calendar mathematics and regex boundaries,
2. **Deep structural XML mocking** of Word OpenXML elements (headers, footers, text boxes, footnotes, and tracked changes),
3. **Rigorous CLI contract auditing** (exit codes, deterministic sorting, argument validation, CSV escaping), and
4. **Golden acceptance verification** across all 20 real-world academic manuscripts,

the system achieves **100% test pass fidelity (132/132 checks)** with zero external runtime dependencies and full standard-library robustness.
