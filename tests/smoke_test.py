import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rice2k_magic_tasks import (
    ICON_ICO,
    ICON_PNG,
    SmartPlanner,
    THEMES,
    calendar_event_text,
    calendar_task_text,
    default_data,
    event_occurs_on,
    next_recurrence_date,
    normalize_theme_name,
    parse_date,
    reorder_item,
    safe_display_text,
)


def test_planner_preview():
    plan = SmartPlanner.preview("clean house", "2026-08-01", 4)
    assert plan["rewrite"]
    assert plan["category"] == "Home"
    assert len(plan["steps"]) >= 4
    assert plan["estimate"] >= 5
    assert plan["next_action"]
    assert plan["coach_note"]
    assert plan["minimum_win"]
    assert plan["finish_line"]
    assert plan["blocker_check"]
    assert plan["if_stuck"]
    assert plan["clarifying_question"]


def test_planner_preview_for_digital_tasks():
    plan = SmartPlanner.preview("fix cluttered app ui", "", 4)
    assert plan["category"] == "Digital"
    assert any("primary" in step for step in plan["steps"])
    assert "readable" in plan["finish_line"]


def test_recurrence_weekdays():
    assert str(next_recurrence_date(parse_date("2026-07-31"), "Weekdays")) == "2026-08-03"


def test_default_data_shape():
    data = default_data()
    assert data["lists"]
    assert data["templates"]
    assert data["events"] == []
    assert data["settings"]["theme"] == "Classic Web"
    assert data["settings"]["text_size"] == "Comfort"


def test_theme_count_and_names():
    assert list(THEMES) == [
        "Classic Web",
        "Candy Pop",
        "Ocean Glow",
        "Soft Blue",
        "Sunset Arcade",
        "Warm Focus",
        "Lavender Pop",
        "Mint Fresh",
        "Graphite Calm",
        "Black & Green",
    ]


def test_old_theme_names_migrate():
    assert normalize_theme_name("Easy Light") == "Classic Web"
    assert normalize_theme_name("Candy Pop") == "Candy Pop"
    assert normalize_theme_name("Ocean Glow") == "Ocean Glow"
    assert normalize_theme_name("Sunset Arcade") == "Sunset Arcade"
    assert normalize_theme_name("Soft Pastel") == "Candy Pop"
    assert normalize_theme_name("Clean Blue") == "Ocean Glow"
    assert normalize_theme_name("Mint") == "Mint Fresh"
    assert normalize_theme_name("Graphite") == "Graphite Calm"


def test_recurring_event_occurrences():
    event = {"date": "2026-08-01", "recurrence": "Weekly"}
    assert event_occurs_on(event, parse_date("2026-08-01"))
    assert event_occurs_on(event, parse_date("2026-08-08"))
    assert not event_occurs_on(event, parse_date("2026-08-09"))


def test_calendar_labels_stay_short():
    assert calendar_event_text({"start_time": "08:30", "title": "Planning block that has a long name"}) == "8:30 Planning..."
    assert calendar_task_text({"text": "Write a very long project update email"}) == "Write a very lo..."


def test_safe_display_text_breaks_long_words():
    value = safe_display_text("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", chunk=8)
    assert value == "aaaaaaaa aaaaaaaa aaaaaaaa aaaaaaaa"


def test_reorder_item_before_and_after():
    items = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    assert reorder_item(items, "a", "c", after=True)
    assert [item["id"] for item in items] == ["b", "c", "a"]
    assert reorder_item(items, "a", "b", after=False)
    assert [item["id"] for item in items] == ["a", "b", "c"]
    assert not reorder_item(items, "a", "a", after=True)


def test_icon_assets_exist():
    assert ICON_PNG.exists()
    assert ICON_ICO.exists()
    assert (ROOT / "assets" / "actions" / "magic.png").exists()
    assert (ROOT / "assets" / "actions" / "edit.png").exists()
