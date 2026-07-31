import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rice2k_magic_tasks import SmartPlanner, default_data, next_recurrence_date, parse_date


def test_planner_preview():
    plan = SmartPlanner.preview("clean house", "2026-08-01", 4)
    assert plan["rewrite"]
    assert plan["category"] == "Home"
    assert len(plan["steps"]) >= 4
    assert plan["estimate"] >= 5


def test_recurrence_weekdays():
    assert str(next_recurrence_date(parse_date("2026-07-31"), "Weekdays")) == "2026-08-03"


def test_default_data_shape():
    data = default_data()
    assert data["lists"]
    assert data["templates"]
    assert data["settings"]["theme"] == "Light"
