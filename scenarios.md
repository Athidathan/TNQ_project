#### Category 1: Date Format Normalization (Equivalence Partitioning)

* **Standard ISO Date**: Direct `YYYY-MM-DD` format (e.g., `Received: 2023-08-15` $\rightarrow$ `2023-08-15`).
* **Full Month Name with Day & Year**: e.g., `Received 14 October 2022` or `Received October 14, 2022` $\rightarrow$ `2022-10-14`.
* **Abbreviated Month Name**: e.g., `Recd: 05-Jan-2021` or `Jan 5, 2021` $\rightarrow$ `2021-01-05`.
* **Ordinal Number Days**: e.g., `Received on the 21st of March, 2020` or `July 3rd, 2024` $\rightarrow$ `2020-03-21` / `2024-07-03`.
* **Numeric Separators**: Slash (`/`), dot (`.`), and hyphen (`-`) variants (e.g., `12.04.2023`, `12/04/2023`).
* **Two-Digit Year**: e.g., `Received 10/12/23` (needs deterministic century resolution, e.g., $2023$).

#### Category 2: Disambiguation & Distractor Handling (Negative Boundaries)

* **Keyword Collision**: Document contains "Received: [Date]", "Accepted: [Date]", "Revised: [Date]", and "Published online: [Date]". The tool must extract *only* the Received date and ignore the others.
* **Bibliography & Citation False Positives**: Citations in references containing phrases like *"Retrieved / Received 12 May 2018 from https..."*. The tool must not mistake reference citations for manuscript metadata.
* **Revision Dates**: Documents stating *"Received 10 Jan 2022; Received in revised form 18 Feb 2022"*. The tool must prioritize the initial submission date unless specified otherwise.
* **Case and Punctuation Variance**: Handling `RECEIVED:`, `Received -`, `Date received:`, `Date of Receipt:`, and lowercase `received:`.

#### Category 3: Document Layout & Structural Locations

* **Main Body Paragraph**: Date located within front-matter paragraphs below the title/authors.
* **Table Metadata**: Date located inside a header table or two-column metadata table.
* **Header / Footer**: Date placed in running document headers or footers.
* **Footnotes / Front-Matter Notes**: Date placed in an unnumbered title footnote or author note block.

#### Category 4: Edge Cases & `INVALID` Output Rules

* **Missing Date**: The file contains author details and text, but no received date is mentioned $\rightarrow$ output `INVALID`.
* **Incomplete Date**: The file states only month and year (e.g., `Received March 2021`) or season (e.g., `Received Spring 2022`) $\rightarrow$ output `INVALID` (or PO rule).
* **Nonsensical / Impossible Dates**: e.g., `Received 30 February 2023` or `Received 31/04/2022` $\rightarrow$ output `INVALID`.
* **Corrupted / Empty Files**: Zero-byte file, non-docx file with `.docx` extension, or unreadable XML package $\rightarrow$ tool handles exception gracefully and outputs `INVALID`.
* **Future Dates**: Dates set beyond the current calendar date (e.g., `Received 2099-01-01`) $\rightarrow$ flag as invalid/anomaly.

#### Category 5: Batch CLI Execution (`run.sh`)

* **Folder with Mixed Files**: Input folder contains non-docx files (`.pdf`, `.txt`, hidden `.~lock...docx` files). The tool must filter and process only valid `.docx` files.
* **Spaces in Filenames**: Files named with spaces or symbols (e.g., `manuscript final draft (1).docx`).
* **Empty Input Directory**: Clean run producing an empty CSV with only headers (`file,received_date`).
* **Idempotency & Clean Installation**: `run.sh` installs all necessary dependencies silently and runs without interactive prompts on a fresh Ubuntu environment.

---

### Questions to Ask the Product Owner (High-Value QE Move)

The brief notes: *"Our product owner is in the room. Ask them anything you need to know."* In a QE assessment, proactively identifying ambiguities and confirming business rules with the PO scores top marks. Here are the exact questions to ask:

1. **Ambiguous Numeric Dates**: *"When a date is formatted numerically as `04/05/2023`, should we assume `DD/MM/YYYY` (UK/Indian academic standard) or `MM/DD/YYYY` (US standard)?"*
2. **Incomplete Dates**: *"If a document only specifies Month and Year (e.g., 'Received August 2022'), should that be normalized to the 1st of the month (`2022-08-01`) or marked `INVALID`?"*
3. **Multiple Submissions**: *"If both an original received date and a revised received date appear, should we strictly capture the initial received date?"*
4. **Scope of Extraction**: *"Can the received date appear inside headers, footers, or metadata tables, or is it guaranteed to be in the body paragraphs?"*

