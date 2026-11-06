#!/usr/bin/env python3
"""
Weekly status report generator for a TPM.

Reads the project tracker (Excel with 'Summary' and 'Risks & Issues' tabs,
or two CSV files) and writes one Markdown status report per client.

Usage:
    python status_report.py --tracker T5_Project_Tracker.xlsx
    python status_report.py --tracker T5_Project_Tracker.xlsx --date 2026-11-14 --out reports
    python status_report.py --summary summary.csv --risks risks.csv

Only dependency outside the standard library: openpyxl (for .xlsx input).
"""
import argparse
import csv
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

SCORE = {"Low": 1, "Medium": 2, "High": 3}
RAG_ICON = {"Red": "🔴", "Amber": "🟠", "Green": "🟢"}


# ---------- reading ----------
def _to_date(v):
    """Accept date, datetime, Excel serial, or 'YYYY-MM-DD' / 'DD-Mon-YYYY' strings."""
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    if isinstance(v, (int, float)):  # Excel serial number
        return (datetime(1899, 12, 30) + timedelta(days=float(v))).date()
    s = str(v).strip()
    for fmt in ("%Y-%m-%d", "%d-%b-%Y", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Cannot read date: {v!r}")


def _rows_from_sheet(ws):
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    header = [str(h).strip() if h is not None else "" for h in rows[0]]
    out = []
    for r in rows[1:]:
        if r[0] is None or str(r[0]).strip() == "":
            continue  # skip blank rows and the legend below the table
        out.append({header[i]: r[i] for i in range(len(header)) if header[i]})
    return out


def read_xlsx(path):
    try:
        from openpyxl import load_workbook
    except ImportError:
        sys.exit("openpyxl is required for .xlsx input: pip install openpyxl")
    wb = load_workbook(path, data_only=True)
    missing = [t for t in ("Summary", "Risks & Issues") if t not in wb.sheetnames]
    if missing:
        sys.exit(f"Tracker is missing tab(s): {missing}. Found: {wb.sheetnames}")
    # A real project row has a RAG status AND a milestone date. This drops the
    # legend / "report date" cells that sit under the table on the Summary tab.
    summary = [r for r in _rows_from_sheet(wb["Summary"])
               if str(r.get("Status (RAG)", "")).strip() in RAG_ICON and r.get("Milestone date")]
    risks = [r for r in _rows_from_sheet(wb["Risks & Issues"]) if r.get("Project") and r.get("Description")]
    return summary, risks


def read_csv(summary_path, risks_path):
    with open(summary_path, newline="", encoding="utf-8") as f:
        summary = [r for r in csv.DictReader(f) if r.get("Project")]
    with open(risks_path, newline="", encoding="utf-8") as f:
        risks = [r for r in csv.DictReader(f) if r.get("Project")]
    return summary, risks


# ---------- logic ----------
def score(item):
    """Probability x Impact. Recomputed here so CSV input without a Score column works."""
    return SCORE.get(str(item.get("Probability", "")).strip(), 0) * SCORE.get(str(item.get("Impact", "")).strip(), 0)


def classify(items, report_date):
    open_items = [i for i in items if str(i.get("Status", "Open")).strip() != "Closed"]
    closed = [i for i in items if str(i.get("Status", "")).strip() == "Closed"]
    overdue, this_week, later = [], [], []
    for i in open_items:
        due = _to_date(i.get("Due date"))
        if due is None:
            later.append(i)
        elif due < report_date:
            overdue.append(i)
        elif due <= report_date + timedelta(days=7):
            this_week.append(i)
        else:
            later.append(i)
    key = lambda i: (-score(i), _to_date(i.get("Due date")) or date.max)
    return sorted(overdue, key=key), sorted(this_week, key=key), sorted(later, key=key), closed


def fmt_date(d):
    d = _to_date(d)
    return d.strftime("%a %d %b %Y") if d else "TBD"


def render_item(i, overdue=False):
    flag = " ⚠️ OVERDUE" if overdue else ""
    line = (f"- **{i.get('ID', '')} – {i.get('Type', 'Item')} "
            f"(P: {i.get('Probability')}, I: {i.get('Impact')}){flag}**: {str(i.get('Description', '')).strip()}")
    line += (f"\n  - *Action:* {str(i.get('Action', '')).strip()} — owner **{i.get('Owner', '?')}**, "
             f"due {fmt_date(i.get('Due date'))}")
    return line


def build_report(project, risks, report_date):
    name = project["Project"]
    rag = str(project.get("Status (RAG)", project.get("Status", ""))).strip()
    overdue, this_week, later, closed = classify(risks, report_date)
    week_end = report_date
    week_start = report_date - timedelta(days=4)

    lines = [
        f"# Weekly status – {name}",
        f"**To:** {project.get('Client', '')}  ",
        f"**From:** {project.get('Owner', 'TPM')}, PanScience Innovations  ",
        f"**Week:** {week_start.strftime('%d %b')} – {week_end.strftime('%d %b %Y')}  ",
        "",
        f"## Overall status: {RAG_ICON.get(rag, '')} {rag}",
        f"**Next milestone:** {project.get('Next milestone', '')} – **{fmt_date(project.get('Milestone date'))}**  ",
        f"**Main point this week:** {str(project.get('Main problem', '')).strip()}",
        "",
    ]
    lines += ["## Open risks and issues (highest score first, max 6)"]
    ranked = sorted(overdue + this_week + later, key=lambda i: -score(i))[:6]
    lines += [render_item(i, overdue=(i in overdue)) for i in ranked] or ["- None open."]
    lines += ["", "## Actions due in the next 7 days"]
    lines += [f"- {fmt_date(i.get('Due date'))}: {str(i.get('Action', '')).strip()} (**{i.get('Owner')}**)"
              for i in sorted(this_week, key=lambda i: _to_date(i.get('Due date')))] or ["- None."]
    lines += ["", "## Closed since last report"]
    lines += [f"- {i.get('ID')}: {str(i.get('Description', '')).strip()}" for i in closed] or ["- None."]
    lines += ["", "## Where we need you"]
    client_side = [i for i in overdue + this_week if str(i.get('Owner', '')).strip().lower() in ("client", "nirmal", "sagar")]
    lines += ([f"- {i.get('ID')}: {str(i.get('Action', '')).strip()}" for i in client_side]
              or ["- No action pending on your side this week; please reply if anything above is a surprise."])
    lines += [
        "",
        f"_Open items: {len(overdue) + len(this_week) + len(later)} · Overdue: {len(overdue)} · Generated {report_date.isoformat()} from the project tracker._",
    ]
    return "\n".join(lines)


# ---------- main ----------
def main():
    ap = argparse.ArgumentParser(description="Generate weekly client status reports from the project tracker.")
    ap.add_argument("--tracker", help="Excel tracker with 'Summary' and 'Risks & Issues' tabs")
    ap.add_argument("--summary", help="CSV export of the Summary tab (alternative to --tracker)")
    ap.add_argument("--risks", help="CSV export of the Risks & Issues tab (alternative to --tracker)")
    ap.add_argument("--date", help="Report date YYYY-MM-DD (default: today)")
    ap.add_argument("--out", default="reports", help="Output folder (default: reports)")
    args = ap.parse_args()

    if args.tracker:
        summary, risks = read_xlsx(args.tracker)
    elif args.summary and args.risks:
        summary, risks = read_csv(args.summary, args.risks)
    else:
        ap.error("Give --tracker FILE.xlsx, or both --summary and --risks CSV files.")

    report_date = _to_date(args.date) if args.date else date.today()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    for p in summary:
        project_risks = [r for r in risks if str(r.get("Project", "")).strip() == str(p["Project"]).strip()]
        text = build_report(p, project_risks, report_date)
        fn = out / f"{report_date.isoformat()}_{p['Project']}_status.md"
        fn.write_text(text, encoding="utf-8")
        overdue = classify(project_risks, report_date)[0]
        print(f"wrote {fn}  ({p.get('Status (RAG)', '')}, {len(project_risks)} items, {len(overdue)} overdue)")


if __name__ == "__main__":
    main()
