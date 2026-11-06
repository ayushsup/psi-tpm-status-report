# T7 – Weekly Status Report Generator (TPM tool)

**Problem it solves:** in the "Monday morning" scenario, the Ledger client did not get Friday's status report, and the COO heard about a data problem from someone else. A TPM running two projects should never miss a Friday report. This tool reads the project tracker (Task 5) and writes a client-ready weekly status report for **each** client in seconds, so the Friday report is a 2-minute job: update the tracker, run the tool, read it once, send it.

**What it produces** (one Markdown file per project):
- Overall RAG status, next milestone and date, main point of the week
- Open risks and issues ranked by score (Probability × Impact), overdue ones flagged
- Actions due in the next 7 days, with owner
- Items closed since the last report
- "Where we need you" – actions that sit with the client

Markdown pastes cleanly into Gmail, Notion, Slack or a Google Doc.

## How to run

Requirements: Python 3.9+ and `openpyxl` (only needed for `.xlsx` input).

```bash
pip install openpyxl

# From the Excel tracker (tabs: "Summary" and "Risks & Issues")
python status_report.py --tracker sample_tracker.xlsx --date 2026-11-13 --out reports

# From CSV exports of the two tabs
python status_report.py --summary sample_summary.csv --risks sample_risks.csv --date 2026-11-13

# Run the tests
python test_status_report.py
```

Output example: `reports/2026-11-13_Kavach_status.md`. If `--date` is omitted, today's date is used; "overdue" means due before that date and not Closed.

**Tracker columns expected**
- Summary: `Project, Client, Status (RAG), Next milestone, Milestone date, Main problem, Owner`
- Risks & Issues: `ID, Project, Type, Description, Probability, Impact, Owner, Action, Due date, Status`

Probability and Impact are `Low / Medium / High`; the tool recomputes the score itself so a CSV without a Score column still works.

## How I used AI to build it

Built with Claude (Claude Code–style agent session) in about 1.5 hours including the tracker. I wrote the requirements and reviewed every run; the AI wrote the code.

**Prompts I used (shortened):**
1. *"Build a Python CLI that reads my project tracker Excel file (tabs 'Summary' and 'Risks & Issues') and writes one weekly status report per client as Markdown. Rank open items by Probability × Impact, flag overdue items against a `--date` argument, list actions due in the next 7 days, and items closed. Use only the standard library plus openpyxl. Also accept two CSV files instead of the Excel file."*
2. *"Run it on the real tracker for 2026-11-13 and show me the Kavach report."*
3. *"The report lists overdue items twice (once in an 'Overdue' section and again under 'Top risks'). Merge into one ranked list with an OVERDUE flag, and add a 'Where we need you' section for actions owned by the client."*
4. *"Add a few smoke tests for the scoring, the overdue/this-week/later buckets, and date parsing from Excel serial numbers."*

**Errors the AI made and how I corrected them**

1. **Legend rows became "projects".** The Summary tab has a small legend under the table (the RAG rule: Red / Amber / Green, and a "Report date" input cell). The first version filtered Summary rows only on "column A is not empty", so the tool generated six reports: Kavach, Ledger, *and* "Red", "Amber", "Green" and "Report date (edit):". I spotted it in the console output (`wrote reports/2026-11-13_Red_status.md`). Fix: a row is a project only if its `Status (RAG)` is one of Red/Amber/Green **and** it has a milestone date. Lesson: tell the AI what else lives on the sheet, not only the table.
2. **Wrong column in a tracker formula.** While building the tracker that feeds this tool, the AI wrote the "Open High-impact risks" count as `COUNTIFS(... Probability = "High" ...)` instead of the Impact column. The numbers looked plausible (4 and 3), which is exactly why I checked them by hand against the risk list (should be 5 and 1). Fix: point the formula at column F (Impact). Lesson: a formula that returns a believable number is not a correct formula – verify one value manually.

## Files
- `status_report.py` – the tool
- `test_status_report.py` – smoke tests
- `sample_tracker.xlsx`, `sample_summary.csv`, `sample_risks.csv` – the Task 5 tracker as sample input
- `reports/` – example output for 2026-11-13
