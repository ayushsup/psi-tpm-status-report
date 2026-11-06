# Weekly status report generator

A small command-line tool for a TPM running more than one client project. It reads the project tracker (the Task 5 Excel file, or CSV exports of its two tabs) and writes a weekly status report for each client as Markdown.

## Why I built this one

In the assignment scenario the Ledger client didn't get Friday's report, and the COO heard about a data problem from someone else before he heard it from us. That's the kind of thing that costs you trust far out of proportion to the actual problem. If I'm already keeping the tracker up to date during the week, the Friday report should fall out of it in a couple of minutes, not take an hour of rewriting. So: update tracker, run tool, read it once, send.

Each report has:

- overall RAG, next milestone and its date, the main point of the week
- open risks and issues ranked by probability × impact, with overdue items flagged
- what's due in the next 7 days and who owns it
- what got closed since last time
- a "where we need you" section for anything that sits with the client

Markdown because it pastes cleanly into Gmail, Slack, Notion or a Google Doc without fuss.

## Running it

Python 3.9 or newer. `openpyxl` only if you feed it an .xlsx.

```bash
pip install openpyxl

# from the Excel tracker (needs tabs called "Summary" and "Risks & Issues")
python status_report.py --tracker sample_tracker.xlsx --date 2026-11-13 --out reports

# or from CSV exports of the two tabs
python status_report.py --summary sample_summary.csv --risks sample_risks.csv --date 2026-11-13

# tests
python test_status_report.py
```

You get one file per project, e.g. `reports/2026-11-13_Kavach_status.md`. Leave out `--date` and it uses today. "Overdue" means due before the report date and not marked Closed.

Columns it expects:

- Summary: `Project, Client, Status (RAG), Next milestone, Milestone date, Main problem, Owner`
- Risks & Issues: `ID, Project, Type, Description, Probability, Impact, Owner, Action, Due date, Status`

Probability and Impact are Low / Medium / High. The score is recomputed in the tool, so a CSV without a Score column is fine.

## How the AI was used

I built this with Claude in an agent session, alongside the tracker. Roughly an hour and a half for both. I wrote what I wanted and checked each run; the AI wrote the code.

The prompts, shortened a bit:

1. "Build a Python CLI that reads my project tracker Excel file (tabs 'Summary' and 'Risks & Issues') and writes one weekly status report per client as Markdown. Rank open items by Probability × Impact, flag overdue items against a `--date` argument, list actions due in the next 7 days and items closed. Standard library plus openpyxl only. Also accept two CSV files instead of the Excel file."
2. "Run it on the real tracker for 2026-11-13 and show me the Kavach report."
3. "It lists overdue items twice, once in an 'Overdue' section and again under 'Top risks'. Make it one ranked list with an OVERDUE flag, and add a 'Where we need you' section for actions owned by the client."
4. "Add a few smoke tests: the scoring, the overdue / this week / later buckets, and date parsing from Excel serial numbers."

### Mistakes it made, and what I did about them

**It thought my legend was a list of projects.** Under the table on the Summary tab I have a small legend explaining the RAG rule (a Red row, an Amber row, a Green row) and a "report date" cell. The first version only checked that column A wasn't empty, so it happily produced six reports: Kavach, Ledger, Red, Amber, Green, and one called "Report date (edit):". I noticed it in the console output. The fix was to say a row is a project only if its RAG status is actually Red, Amber or Green *and* it has a milestone date. The lesson for me was to describe what else is on the sheet, not just the table I care about.

**A formula pointed at the wrong column.** This one was in the tracker rather than the tool, but the tool reads the tracker so it would have carried through. The "open high-impact risks" count was written against the Probability column instead of Impact. It returned 4 and 3, which look perfectly reasonable, and that's precisely why I counted one of them by hand against the risk list (should have been 5 and 1). Changed the reference to the Impact column. A number that looks plausible is not the same as a number that's right.

## Files

- `status_report.py` – the tool
- `test_status_report.py` – smoke tests
- `sample_tracker.xlsx`, `sample_summary.csv`, `sample_risks.csv` – the Task 5 tracker as sample input
- `reports/` – example output for 2026-11-13
