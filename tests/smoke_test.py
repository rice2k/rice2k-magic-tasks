import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rice2k_magic_tasks import ICON_ICO, ICON_PNG, SmartPlanner, THEMES, default_data, next_recurrence_date, parse_date


def test_planner_preview():
    plan = SmartPlanner.preview("clean house", "2026-08-01", 4)
    assert plan["rewrite"]
    assert plan["category"] == "Home"
    assert len(plan["steps"]) >= 4
    assert plan["estimate"] >= 5
    assert plan["next_action"]
    assert plan["coach_note"]


def test_recurrence_weekdays():
    assert str(next_recurrence_date(parse_date("2026-07-31"), "Weekdays")) == "2026-08-03"


def test_default_data_shape():
    data = default_data()
    assert data["lists"]
    assert data["templates"]
    assert data["settings"]["theme"] == "Candy Pop"


def test_theme_count_and_names():
    assert list(THEMES) == ["Candy Pop", "Ocean Glow", "Sunset Arcade", "Black & Green"]


def test_icon_assets_exist():
    assert ICON_PNG.exists()
    assert ICON_ICO.exists()
