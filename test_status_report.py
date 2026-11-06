"""Smoke tests: python -m pytest -q  (or: python test_status_report.py)"""
from datetime import date
import status_report as sr


def _item(id_, due, prob="High", imp="High", status="Open"):
    return {"ID": id_, "Project": "X", "Type": "Risk", "Description": "d", "Probability": prob,
            "Impact": imp, "Owner": "me", "Action": "a", "Due date": due, "Status": status}


def test_score():
    assert sr.score(_item("1", "2026-11-10")) == 9
    assert sr.score(_item("1", "2026-11-10", "Low", "Medium")) == 2


def test_classify_buckets():
    today = date(2026, 11, 13)
    overdue, week, later, closed = sr.classify([
        _item("a", "2026-11-11"), _item("b", "2026-11-15"), _item("c", "2026-12-01"),
        _item("d", "2026-11-01", status="Closed")], today)
    assert [i["ID"] for i in overdue] == ["a"]
    assert [i["ID"] for i in week] == ["b"]
    assert [i["ID"] for i in later] == ["c"]
    assert [i["ID"] for i in closed] == ["d"]


def test_dates_from_excel_serial_and_strings():
    assert sr._to_date(46000) == date(2025, 12, 9)
    assert sr._to_date("13-Nov-2026") == date(2026, 11, 13)


def test_report_mentions_overdue():
    p = {"Project": "X", "Client": "C", "Status (RAG)": "Red", "Next milestone": "m",
         "Milestone date": "2026-11-20", "Main problem": "p", "Owner": "o"}
    txt = sr.build_report(p, [_item("a", "2026-11-11")], date(2026, 11, 13))
    assert "OVERDUE" in txt and "🔴 Red" in txt


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f(); print("ok", n)
