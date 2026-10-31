# QE Hackathon – Problem Statements and Scoring

## Format and rules
Every candidate gets some problem and has 3 hours to finish it, using Claude throughout.
*   **Who:** freshers, 0-1 year. No publishing knowledge needed.
*   **Language:** Python or JavaScript, candidate’s choice.
*   **AI use:** Claude is allowed and expected.

## What every candidate submits
1.  **Scenario list.** In the first 30 minutes and before building: the cases they plan to check, in plain words.
2.  A git repository or a shared path (an empty one we give them) holding their code, their tests, a README, their exported Claude chat, `run.sh` and `test_report.csv`.

## Time plan

| Time | What happens |
| :--- | :--- |
| 0:00–0:15 | Read the problem and the sample manuscripts |
| 0:15–0:45 | Write the scenario list, and submit it. |
| 0:45–2:45 | Build and test with Claude; ask the product owner questions |
| 2:45–3:00 | Final push to the repository or upload to the shared path |
| After | 10-minute debrief per shortlisted candidate |

---

## Problem 1: Find and clean the received date

Candidates build a tool that finds the received date in manuscript Word files and converts it to YYYY-MM-DD. They get only a short problem statement and 20 sample manuscripts.

### Problem statement
> *Our system needs the date each manuscript was received. It is written inside the manuscript Word file, in many different ways. Build a tool that finds the received date in each manuscript and converts it to YYYY-MM-DD.*

1.  Write the tool in Python or JavaScript, and write automated tests for it.
2.  Push everything to the git repository we give you: your code, your tests, a README that says how to run the tests, and your Claude chat, exported. Only commits made before the 3-hour mark count.
3.  At the top level of the repository, put `run.sh` . `./run.sh input_folder output.csv` must read every `docx` file in the folder and write a CSV. It must work on a clean Ubuntu machine with Python 3.12 or Node 22. If your code needs any libraries, `run.sh` must install them.
4.  The CSV has a header row `file,received_date`, then one row per file. `file` is the file name, `received_date` is the date as YYYY-MM-DD, or INVALID if a date cannot be produced.
5.  Also at the top level, put `test_report.csv`, produced by running your tests. Its columns are `checks,input,expected,actual,result`: what the test checks, the input, the expected output, the actual output, and PASS or FAIL.

*The attached folder `sample_manuscripts` has 20 manuscripts. Our product owner is in the room. Ask them anything you need to know.*