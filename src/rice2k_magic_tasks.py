"""Rice2k Magic Tasks.

A small Windows-first task planner with local storage, smart task rewriting,
recurring tasks, reminders, calendar views, focus mode, templates, and themes.
"""

from __future__ import annotations

import calendar
import copy
import json
import os
import re
import sys
import threading
import time
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from tkinter import Canvas, Menu, PhotoImage, StringVar, Text, Tk, Toplevel, filedialog, messagebox
from tkinter import ttk

APP_NAME = "Rice2k Magic Tasks"
VERSION = "2.9.0"
APP_DIR = Path(os.getenv("APPDATA", Path.home())) / "Rice2kMagicTasks"
DATA_FILE = APP_DIR / "tasks.json"


def resource_path(relative_path: str) -> Path:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return base_path / relative_path


ICON_PNG = resource_path("assets/rice2k_magic_tasks.png")
ICON_ICO = resource_path("assets/rice2k_magic_tasks.ico")
ACTION_ICON_DIR = resource_path("assets/actions")
TASK_PLACEHOLDER = "Add new item..."


THEMES = {
    "Classic Web": {
        "bg": "#f5f7fb",
        "panel": "#ffffff",
        "panel2": "#e9eef8",
        "card1": "#e8f0ff",
        "card2": "#fff4d6",
        "card3": "#e5f8ee",
        "high_bg": "#ffe7ec",
        "medium_bg": "#fff4d6",
        "done_bg": "#eef2f7",
        "text": "#162033",
        "muted": "#5d6678",
        "accent": "#3366ee",
        "accent2": "#dfe8ff",
        "accent3": "#24a87a",
        "danger": "#b6324f",
        "done": "#21885c",
        "button_text": "#ffffff",
        "hero": "#3157d5",
        "hero_text": "#ffffff",
        "card_text": "#162033",
        "description": "Closest to the simple web layout: white panels, blue actions, gentle highlights.",
    },
    "Candy Pop": {
        "bg": "#fff3fb",
        "panel": "#ffffff",
        "panel2": "#ffe1f3",
        "card1": "#ffe4f1",
        "card2": "#e5f5ff",
        "card3": "#e8ffe9",
        "high_bg": "#ffe2e9",
        "medium_bg": "#fff3c4",
        "done_bg": "#eff8f0",
        "text": "#261529",
        "muted": "#6d5871",
        "accent": "#e83f8f",
        "accent2": "#ffd2ea",
        "accent3": "#19a974",
        "danger": "#c82451",
        "done": "#1b8b5a",
        "button_text": "#ffffff",
        "hero": "#d6327f",
        "hero_text": "#ffffff",
        "card_text": "#261529",
        "description": "Bright pinks, sky blues, and green wins for a more playful task list.",
    },
    "Ocean Glow": {
        "bg": "#eafcff",
        "panel": "#ffffff",
        "panel2": "#cdf5f5",
        "card1": "#dcfaff",
        "card2": "#e7fff3",
        "card3": "#fff7dc",
        "high_bg": "#ffe3f0",
        "medium_bg": "#fff5ca",
        "done_bg": "#e5f8ee",
        "text": "#092d38",
        "muted": "#476c75",
        "accent": "#008bb8",
        "accent2": "#c8f4ff",
        "accent3": "#00a676",
        "danger": "#c93667",
        "done": "#18895f",
        "button_text": "#ffffff",
        "hero": "#007999",
        "hero_text": "#ffffff",
        "card_text": "#092d38",
        "description": "Clean water colors with punchy buttons and calm reading contrast.",
    },
    "Soft Blue": {
        "bg": "#edf7fb",
        "panel": "#ffffff",
        "panel2": "#d9edf5",
        "card1": "#dff3ff",
        "card2": "#e7f8f0",
        "card3": "#fff1db",
        "high_bg": "#ffe7e2",
        "medium_bg": "#fff1db",
        "done_bg": "#e8f4f0",
        "text": "#12313f",
        "muted": "#52707b",
        "accent": "#087aa8",
        "accent2": "#d7eef7",
        "accent3": "#1d9a73",
        "danger": "#b94a5e",
        "done": "#237a62",
        "button_text": "#ffffff",
        "hero": "#0b5f82",
        "hero_text": "#ffffff",
        "card_text": "#12313f",
        "description": "Cool, quiet colors for longer reading sessions.",
    },
    "Sunset Arcade": {
        "bg": "#fff2e8",
        "panel": "#fffefb",
        "panel2": "#ffe1c4",
        "card1": "#ffdac7",
        "card2": "#ffeaa8",
        "card3": "#dff4cc",
        "high_bg": "#ffd9dc",
        "medium_bg": "#ffeaa8",
        "done_bg": "#edf6dd",
        "text": "#2d1d12",
        "muted": "#745d4f",
        "accent": "#ef6b2e",
        "accent2": "#ffd4b8",
        "accent3": "#4b9d4d",
        "danger": "#c73c52",
        "done": "#4b8f38",
        "button_text": "#ffffff",
        "hero": "#d84a27",
        "hero_text": "#fffaf1",
        "card_text": "#2d1d12",
        "description": "Orange, peach, and gold for a bright desktop-app feel.",
    },
    "Warm Focus": {
        "bg": "#fff7ed",
        "panel": "#ffffff",
        "panel2": "#f4e7d5",
        "card1": "#ffe5c2",
        "card2": "#f9efd4",
        "card3": "#eaf3dc",
        "high_bg": "#ffe1d6",
        "medium_bg": "#f9efd4",
        "done_bg": "#edf3e4",
        "text": "#2d241c",
        "muted": "#756756",
        "accent": "#b85d17",
        "accent2": "#f3dcc0",
        "accent3": "#5d8f3c",
        "danger": "#b54848",
        "done": "#5d8f3c",
        "button_text": "#ffffff",
        "hero": "#9a4f16",
        "hero_text": "#fffaf1",
        "card_text": "#2d241c",
        "description": "Warm, readable, and low-glare without feeling plain.",
    },
    "Lavender Pop": {
        "bg": "#f7f1ff",
        "panel": "#ffffff",
        "panel2": "#eadcff",
        "card1": "#eee2ff",
        "card2": "#dff7ff",
        "card3": "#fff2ca",
        "high_bg": "#ffe0ef",
        "medium_bg": "#fff2ca",
        "done_bg": "#edf7f0",
        "text": "#25193c",
        "muted": "#625276",
        "accent": "#7b4ce3",
        "accent2": "#e3d5ff",
        "accent3": "#00a7a5",
        "danger": "#c93e75",
        "done": "#1f8f67",
        "button_text": "#ffffff",
        "hero": "#6539c9",
        "hero_text": "#ffffff",
        "card_text": "#25193c",
        "description": "Purple, teal, and soft gold with strong readable text.",
    },
    "Mint Fresh": {
        "bg": "#eefcf4",
        "panel": "#ffffff",
        "panel2": "#d8f5e6",
        "card1": "#daf9e8",
        "card2": "#e6f7ff",
        "card3": "#fff5d8",
        "high_bg": "#ffe3e8",
        "medium_bg": "#fff5d8",
        "done_bg": "#e4f6eb",
        "text": "#102d22",
        "muted": "#527366",
        "accent": "#129968",
        "accent2": "#c9f2df",
        "accent3": "#0b87a6",
        "danger": "#b93f5e",
        "done": "#168a5f",
        "button_text": "#ffffff",
        "hero": "#087a57",
        "hero_text": "#ffffff",
        "card_text": "#102d22",
        "description": "Fresh green, blue, and gold with crisp task-card contrast.",
    },
    "Graphite Calm": {
        "bg": "#111318",
        "panel": "#1b1f27",
        "panel2": "#2a303b",
        "card1": "#233248",
        "card2": "#3a3020",
        "card3": "#20362d",
        "high_bg": "#3a2029",
        "medium_bg": "#3a3020",
        "done_bg": "#202a25",
        "text": "#f4f7fb",
        "muted": "#b8c0cc",
        "accent": "#69a7ff",
        "accent2": "#2d4260",
        "accent3": "#65d6ad",
        "danger": "#ff7b91",
        "done": "#65d6ad",
        "button_text": "#10141b",
        "hero": "#203d66",
        "hero_text": "#f4f7fb",
        "card_text": "#f4f7fb",
        "description": "A dark gray theme with blue highlights and softer contrast than black.",
    },
    "Black & Green": {
        "bg": "#020504",
        "panel": "#07110b",
        "panel2": "#102118",
        "card1": "#102d1b",
        "card2": "#1c3115",
        "card3": "#0d3028",
        "high_bg": "#2b171b",
        "medium_bg": "#273017",
        "done_bg": "#0e2118",
        "text": "#e9ffe9",
        "muted": "#9bc59e",
        "accent": "#31e981",
        "accent2": "#173d24",
        "accent3": "#24cfa0",
        "danger": "#ff5d73",
        "done": "#58f2a0",
        "button_text": "#041006",
        "hero": "#0b351c",
        "hero_text": "#e9ffe9",
        "card_text": "#e9ffe9",
        "description": "Dark, green, high contrast, and easier on the eyes.",
    },
}

THEME_ALIASES = {
    "Easy Light": "Classic Web",
    "Light": "Classic Web",
    "Dark": "Black & Green",
    "Low Stimulation": "Classic Web",
    "Focus Contrast": "Black & Green",
    "Soft Pastel": "Candy Pop",
    "Clean Blue": "Ocean Glow",
    "Mint": "Mint Fresh",
    "Graphite": "Graphite Calm",
}

DEFAULT_SETTINGS = {
    "theme": "Classic Web",
    "compact_rows": False,
    "reduced_motion": False,
    "plain_background": False,
}

UI_FONT = ("Segoe UI", 11)
UI_FONT_BOLD = ("Segoe UI", 11, "bold")
TITLE_FONT = ("Segoe UI", 19, "bold")
APP_TITLE_FONT = ("Segoe UI", 20, "bold")
SMALL_FONT = ("Segoe UI", 10)

RECURRENCE_OPTIONS = ["None", "Daily", "Weekdays", "Weekly", "Monthly"]

BUILTIN_TEMPLATES = [
    {
        "name": "Morning Reset",
        "tasks": [
            "Drink water",
            "Check calendar",
            "Pick the first important task",
            "Clear the work surface",
            "Start a 15 minute focus session",
        ],
    },
    {
        "name": "Weekly Planning",
        "tasks": [
            "Review unfinished tasks",
            "Choose three priorities for the week",
            "Block time for important work",
            "Move low priority tasks out of the way",
            "Prepare one easy starter task",
        ],
    },
    {
        "name": "Appointment Prep",
        "tasks": [
            "Confirm appointment time",
            "Write down questions",
            "Gather documents",
            "Set travel reminder",
            "Prepare follow up task",
        ],
    },
    {
        "name": "Home Cleanup",
        "tasks": [
            "Collect trash",
            "Move dishes to kitchen",
            "Clear one surface",
            "Start laundry",
            "Reset the main room",
        ],
    },
    {
        "name": "Work Kickoff",
        "tasks": [
            "Open the needed files",
            "Read the latest notes",
            "Write the next concrete action",
            "Handle one blocker",
            "Send any needed update",
        ],
    },
]


def app_now() -> datetime:
    return datetime.now().replace(microsecond=0)


def make_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def default_data() -> dict:
    return {
        "version": VERSION,
        "settings": copy.deepcopy(DEFAULT_SETTINGS),
        "lists": [
            {
                "id": make_id("list"),
                "name": "Main List",
                "tasks": [],
            }
        ],
        "templates": copy.deepcopy(BUILTIN_TEMPLATES),
        "distractions": [],
        "events": [],
    }


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def normalize_theme_name(name: str | None) -> str:
    if name in THEMES:
        return name
    if name in THEME_ALIASES:
        return THEME_ALIASES[name]
    return DEFAULT_SETTINGS["theme"]


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    return None


def parse_datetime(due_date: str | None, due_time: str | None) -> datetime | None:
    day = parse_date(due_date)
    if not day:
        return None
    clock = due_time.strip() if due_time else "09:00"
    for fmt in ("%H:%M", "%I:%M %p", "%I %p"):
        try:
            parsed = datetime.strptime(clock, fmt).time()
            return datetime.combine(day, parsed)
        except ValueError:
            pass
    return datetime.combine(day, datetime.strptime("09:00", "%H:%M").time())


def due_label(task: dict) -> str:
    due_dt = parse_datetime(task.get("due_date"), task.get("due_time"))
    if not due_dt:
        return ""
    return due_dt.strftime("%Y-%m-%d %I:%M %p").replace(" 0", " ")


def event_time_label(event: dict) -> str:
    start = clean_text(event.get("start_time", ""))
    end = clean_text(event.get("end_time", ""))
    if start and end:
        return f"{start}-{end}"
    if start:
        return start
    return "Any time"


def event_occurs_on(event: dict, day: date) -> bool:
    start = parse_date(event.get("date"))
    if not start or day < start:
        return False
    recurrence = event.get("recurrence", "None")
    if recurrence == "None":
        return day == start
    if recurrence == "Daily":
        return True
    if recurrence == "Weekdays":
        return day.weekday() < 5
    if recurrence == "Weekly":
        return (day - start).days % 7 == 0
    if recurrence == "Monthly":
        return day.day == min(start.day, calendar.monthrange(day.year, day.month)[1])
    return day == start


def next_recurrence_date(current: date, recurrence: str) -> date | None:
    if recurrence == "Daily":
        return current + timedelta(days=1)
    if recurrence == "Weekdays":
        nxt = current + timedelta(days=1)
        while nxt.weekday() >= 5:
            nxt += timedelta(days=1)
        return nxt
    if recurrence == "Weekly":
        return current + timedelta(days=7)
    if recurrence == "Monthly":
        year = current.year + (1 if current.month == 12 else 0)
        month = 1 if current.month == 12 else current.month + 1
        last_day = calendar.monthrange(year, month)[1]
        return date(year, month, min(current.day, last_day))
    return None


class SmartPlanner:
    category_words = {
        "Home": ["clean", "laundry", "dish", "kitchen", "room", "trash", "house", "closet", "garage", "bed"],
        "Work": ["email", "report", "meeting", "client", "project", "code", "invoice", "presentation", "manager"],
        "Health": ["doctor", "medicine", "exercise", "walk", "sleep", "appointment", "therapy", "meal", "water"],
        "Errands": ["buy", "store", "pickup", "call", "mail", "bank", "shop", "return", "post office"],
        "Admin": ["form", "file", "paper", "budget", "tax", "bill", "account", "renew", "password"],
        "School": ["study", "homework", "assignment", "class", "teacher", "exam", "quiz", "essay"],
        "Creative": ["draw", "write", "record", "music", "video", "design", "photo", "paint"],
    }

    starters = (
        "open",
        "write",
        "call",
        "send",
        "review",
        "clean",
        "buy",
        "schedule",
        "make",
        "check",
        "finish",
        "start",
        "prepare",
        "update",
    )

    @classmethod
    def categorize(cls, text: str) -> str:
        lower = text.lower()
        for category, words in cls.category_words.items():
            if any(word in lower for word in words):
                return category
        return "General"

    @classmethod
    def energy(cls, text: str) -> str:
        lower = text.lower()
        if any(word in lower for word in ["call", "meeting", "doctor", "deadline", "deep", "presentation", "tax"]):
            return "High"
        if any(word in lower for word in ["read", "sort", "check", "list", "collect", "water", "trash"]):
            return "Low"
        return "Medium"

    @classmethod
    def estimate(cls, text: str, spice: int = 3) -> int:
        lower = text.lower()
        words = max(3, len(text.split()))
        base = 8 + words * 3
        if any(word in lower for word in ["project", "house", "report", "tax", "plan", "presentation", "essay"]):
            base += 25
        if any(word in lower for word in ["quick", "text", "water", "trash", "check"]):
            base -= 8
        if any(word in lower for word in ["organize", "research", "deep", "budget", "clean"]):
            base += 12
        return min(240, max(5, base + (spice - 3) * 8))

    @classmethod
    def priority(cls, text: str, due_date: str | None = None) -> str:
        lower = text.lower()
        due = parse_date(due_date)
        if any(word in lower for word in ["urgent", "asap", "deadline", "today", "tonight", "overdue"]):
            return "High"
        if due and due <= date.today() + timedelta(days=1):
            return "High"
        if due and due <= date.today() + timedelta(days=7):
            return "Medium"
        if any(word in lower for word in ["soon", "this week", "tomorrow", "important"]):
            return "Medium"
        return "Normal"

    @classmethod
    def rewrite(cls, text: str) -> str:
        text = clean_text(text)
        if not text:
            return text
        lower = text.lower().strip(" .!?")
        replacements = [
            ("clean house", "Reset one small area of the house"),
            ("clean room", "Clear and reset one surface in the room"),
            ("do laundry", "Run one complete laundry cycle"),
            ("laundry", "Run one complete laundry cycle"),
            ("dishes", "Clear the dishes from the sink or counter"),
            ("work on project", "Finish one useful piece of the project"),
            ("get organized", "Sort the loose items into keep, move, and trash piles"),
            ("emails", "Clear the most important email action"),
            ("email", "Handle the most important email action"),
            ("make appointment", "Schedule the appointment and save the details"),
            ("study", "Study one focused section and capture what is still confusing"),
            ("budget", "Update the budget and flag the next money decision"),
            ("pack", "Pack the essentials first, then add nice-to-have items"),
        ]
        for needle, replacement in replacements:
            if needle in lower:
                return replacement
        if lower.startswith(cls.starters):
            return text[0].upper() + text[1:]
        category = cls.categorize(text)
        if category == "Home":
            return f"Reset one visible part of: {text[0].lower() + text[1:]}"
        if category == "Work":
            return f"Move this work forward: {text[0].lower() + text[1:]}"
        if category == "School":
            return f"Make one clear study step for: {text[0].lower() + text[1:]}"
        if category == "Creative":
            return f"Create a rough first pass of: {text[0].lower() + text[1:]}"
        return f"Start with one small action for: {text[0].lower() + text[1:]}"

    @classmethod
    def breakdown(cls, text: str, spice: int = 3) -> list[str]:
        text = clean_text(text)
        lower = text.lower()
        category = cls.categorize(text)
        first = cls.rewrite(text)
        general = [
            "Name the finished result in one sentence",
            "Clear a two-minute starter space",
            "Gather the one thing needed to begin",
            "Do the smallest visible action",
            "Check what changed",
            "Handle one blocker or decide who to ask",
            "Finish, save, or reset the area",
            "Write the next follow-up if one remains",
        ]
        if category == "Home":
            general = [
                "Pick the smallest visible area",
                "Remove trash and obvious clutter",
                "Group items by where they belong",
                "Put away the easiest group",
                "Reset one surface so progress is visible",
                "Start one timer if the task can keep going",
                "Stop when the chosen area is usable",
                "Write the next room or surface for later",
            ]
        elif category == "Work":
            general = [
                "Open the relevant files or notes",
                "Write the exact outcome needed",
                "List missing information",
                "Complete the first deliverable chunk",
                "Review for one obvious problem",
                "Send or save the update",
                "Create a follow-up task for anything blocked",
            ]
        elif category == "Health":
            general = [
                "Confirm the health-related goal",
                "Gather medicine, paperwork, or supplies",
                "Set a reminder or travel time",
                "Do the next physical action",
                "Record what was done",
                "Schedule the next check-in if needed",
            ]
        elif category == "Errands":
            general = [
                "Confirm the item or place",
                "Check hours, address, or phone number",
                "Prepare payment, bag, or documents",
                "Complete the errand",
                "Put away or record the result",
                "Save receipts or confirmation numbers",
            ]
        elif category == "Admin":
            general = [
                "Open the account, form, or folder",
                "Find the newest document or notice",
                "Write down the exact decision needed",
                "Complete the required field, payment, or upload",
                "Save proof or a confirmation number",
                "Set a follow-up reminder if there is a wait",
            ]
        elif category == "School":
            general = [
                "Open the assignment, notes, or study material",
                "Circle the exact question or section",
                "Work for one short focus block",
                "Write a rough answer before polishing",
                "Check instructions against the work",
                "Submit, save, or list what still needs help",
            ]
        elif category == "Creative":
            general = [
                "Open the blank file, page, or tool",
                "Make a rough version without judging it",
                "Pick one part to improve",
                "Save a version before changing more",
                "Add one finishing detail",
                "Write the next creative step",
            ]
        if "email" in lower:
            general = [
                "Open the inbox",
                "Search for the important thread",
                "Decide: reply, archive, schedule, or task",
                "Write the shortest useful response",
                "Add one clear next action if needed",
                "Send or save the draft",
            ]
        steps = [first] + general
        count_by_spice = {1: 3, 2: 4, 3: 5, 4: 7, 5: 9}
        count = min(len(steps), count_by_spice.get(max(1, min(5, spice)), 5))
        return steps[:count]

    @classmethod
    def coach_note(cls, text: str, due_date: str | None = None) -> str:
        priority = cls.priority(text, due_date)
        energy = cls.energy(text)
        if priority == "High":
            return "Start with the first visible action, then decide what can wait."
        if energy == "Low":
            return "This is a good low-energy task. Let the tiny first step count."
        if energy == "High":
            return "Make the start smaller than your brain thinks it should be."
        return "Aim for progress, not a perfect plan."

    @classmethod
    def minimum_win(cls, text: str) -> str:
        category = cls.categorize(text)
        if category == "Home":
            return "Make one small area look better than it did five minutes ago."
        if category == "Work":
            return "Create or send one useful piece, even if the whole job is not done."
        if category == "Health":
            return "Do the next caring action and record it so you do not have to remember."
        if category == "Errands":
            return "Confirm the place, item, or call, then do only that next step."
        if category == "Admin":
            return "Find the right page or document and complete one required field."
        if category == "School":
            return "Work one question, paragraph, or study section before polishing."
        if category == "Creative":
            return "Make a rough version that exists, then improve one part."
        return "Do one visible step that makes the task less stuck."

    @classmethod
    def finish_line(cls, text: str) -> str:
        category = cls.categorize(text)
        if category == "Home":
            return "The chosen area is usable enough to stop without guilt."
        if category == "Work":
            return "A useful update is saved, sent, or ready for the next person."
        if category == "Health":
            return "The caring action is done and the next reminder is captured."
        if category == "Errands":
            return "The item, call, pickup, or confirmation is handled."
        if category == "Admin":
            return "The form, payment, file, or proof is saved where you can find it."
        if category == "School":
            return "One answer, section, or study block is complete enough to review."
        if category == "Creative":
            return "A visible draft exists, even if it is not polished yet."
        return "The task has one clear result or one clear next action."

    @classmethod
    def blocker_check(cls, text: str) -> str:
        category = cls.categorize(text)
        if category == "Work":
            return "Check whether you need a file, decision, person, or deadline before going deep."
        if category == "Errands":
            return "Check hours, address, payment, and whether the item is actually available."
        if category == "Admin":
            return "Check login details, newest paperwork, account numbers, and proof before starting."
        if category == "Health":
            return "Check time, supplies, paperwork, travel, and any follow-up instructions."
        if category == "School":
            return "Check the instructions, rubric, due date, and what question you are answering."
        if category == "Creative":
            return "Check whether you are blocked by tools, references, or trying to polish too early."
        return "Check whether the next step needs a tool, place, person, decision, or document."

    @classmethod
    def preview(cls, text: str, due_date: str | None, spice: int) -> dict:
        steps = cls.breakdown(text, spice)
        return {
            "rewrite": cls.rewrite(text),
            "category": cls.categorize(text),
            "energy": cls.energy(text),
            "estimate": cls.estimate(text, spice),
            "priority": cls.priority(text, due_date),
            "steps": steps,
            "next_action": steps[0] if steps else clean_text(text),
            "coach_note": cls.coach_note(text, due_date),
            "minimum_win": cls.minimum_win(text),
            "finish_line": cls.finish_line(text),
            "blocker_check": cls.blocker_check(text),
        }


class MagicTasksApp:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("1200x840")
        self.root.minsize(1040, 680)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        self.app_icon_image = None
        self.action_icons: dict[str, PhotoImage] = {}
        self.set_window_icon()
        self.load_action_icons()

        self.data = self.load_data()
        self.active_list_id = self.data["lists"][0]["id"]
        self.current_view = "Tasks"
        self.selected_task_id: str | None = None
        self.task_card_widgets: dict[str, dict[str, ttk.Widget]] = {}
        self.reminder_seen: set[str] = set()
        self.focus_task_id: str | None = None
        self.focus_remaining = 0
        self.focus_running = False
        self.calendar_month = date.today().replace(day=1)
        self.drag_calendar_item: tuple[str, str, date] | None = None
        self.tray_icon = None
        self.pending_settings = copy.deepcopy(self.data["settings"])

        self.configure_style()
        self.build_shell()
        self.apply_theme(self.data["settings"]["theme"])
        self.register_shortcuts()
        self.show_tasks()
        self.setup_tray()
        self.root.after(1000, self.check_reminders)

    def run(self) -> None:
        self.root.mainloop()

    def load_data(self) -> dict:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        if not DATA_FILE.exists():
            data = default_data()
            self.save_payload(data)
            return data
        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            backup = DATA_FILE.with_suffix(f".broken-{int(time.time())}.json")
            try:
                DATA_FILE.replace(backup)
            except OSError:
                pass
            data = default_data()
            self.save_payload(data)
            return data
        data.setdefault("version", VERSION)
        data.setdefault("settings", copy.deepcopy(DEFAULT_SETTINGS))
        data.setdefault("templates", copy.deepcopy(BUILTIN_TEMPLATES))
        data.setdefault("distractions", [])
        data.setdefault("events", [])
        if not data.get("lists"):
            data["lists"] = default_data()["lists"]
        for key, value in DEFAULT_SETTINGS.items():
            data["settings"].setdefault(key, value)
        data["settings"]["theme"] = normalize_theme_name(data["settings"].get("theme"))
        data["events"] = [self.normalize_event(event) for event in data.get("events", []) if isinstance(event, dict)]
        return data

    def save_payload(self, payload: dict) -> None:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def save_data(self) -> None:
        self.data["version"] = VERSION
        self.save_payload(self.data)

    def configure_style(self) -> None:
        self.root.option_add("*Font", UI_FONT)
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

    def set_window_icon(self) -> None:
        try:
            if ICON_ICO.exists():
                self.root.iconbitmap(str(ICON_ICO))
            if ICON_PNG.exists():
                self.app_icon_image = PhotoImage(file=str(ICON_PNG))
                self.root.iconphoto(True, self.app_icon_image)
        except Exception:
            self.app_icon_image = None

    def load_action_icons(self) -> None:
        for name in ["check", "magic", "edit", "subtask", "estimate", "delete", "menu"]:
            path = ACTION_ICON_DIR / f"{name}.png"
            if path.exists():
                try:
                    self.action_icons[name] = PhotoImage(file=str(path)).subsample(3, 3)
                except Exception:
                    pass

    def normalize_event(self, event: dict) -> dict:
        today = date.today().isoformat()
        title = clean_text(str(event.get("title", ""))) or "Untitled event"
        event_date = event.get("date") if parse_date(event.get("date")) else today
        recurrence = event.get("recurrence", "None")
        if recurrence not in RECURRENCE_OPTIONS:
            recurrence = "None"
        try:
            reminder_minutes = max(0, int(event.get("reminder_minutes", 15) or 15))
        except (TypeError, ValueError):
            reminder_minutes = 15
        return {
            "id": event.get("id") or make_id("event"),
            "title": title,
            "date": event_date,
            "start_time": clean_text(str(event.get("start_time", "09:00"))) or "09:00",
            "end_time": clean_text(str(event.get("end_time", "10:00"))) or "10:00",
            "recurrence": recurrence,
            "reminder_minutes": reminder_minutes,
            "notes": str(event.get("notes", "")),
            "created_at": event.get("created_at") or app_now().isoformat(),
            "updated_at": event.get("updated_at") or app_now().isoformat(),
        }

    def theme_popup(self, win: Toplevel) -> None:
        colors = self.colors()
        win.configure(bg=colors["bg"])
        try:
            if self.app_icon_image:
                win.iconphoto(True, self.app_icon_image)
        except Exception:
            pass

    def make_menu(self, parent=None) -> Menu:
        colors = self.colors()
        return Menu(
            parent or self.root,
            tearoff=False,
            bg=colors["panel"],
            fg=colors["text"],
            activebackground=colors["accent2"],
            activeforeground=colors["text"],
        )

    def add_menu_command(self, menu: Menu, label: str, icon: str | None, command) -> None:
        icon_image = self.action_icons.get(icon or "")
        if icon_image:
            menu.add_command(label=label, image=icon_image, compound="left", command=command)
        else:
            menu.add_command(label=label, command=command)

    def colors(self) -> dict:
        return THEMES[normalize_theme_name(self.data["settings"].get("theme"))]

    def apply_theme(self, theme_name: str) -> None:
        theme_name = normalize_theme_name(theme_name)
        self.data["settings"]["theme"] = theme_name
        colors = self.colors()
        display_bg = colors["panel"] if self.data["settings"].get("plain_background") else colors["bg"]
        row_height = 30 if self.data["settings"].get("compact_rows") else 40
        self.root.configure(bg=display_bg)
        self.style.configure(".", background=display_bg, foreground=colors["text"], fieldbackground=colors["panel"], font=UI_FONT)
        self.style.configure("TFrame", background=display_bg)
        self.style.configure("Panel.TFrame", background=colors["panel"])
        self.style.configure("TaskCard.TFrame", background=colors["panel"])
        self.style.configure("SelectedTask.TFrame", background=colors["accent2"])
        self.style.configure("DoneTask.TFrame", background=colors["done_bg"])
        self.style.configure("Hero.TFrame", background=colors["hero"])
        self.style.configure("CardOne.TFrame", background=colors["card1"])
        self.style.configure("CardTwo.TFrame", background=colors["card2"])
        self.style.configure("CardThree.TFrame", background=colors["card3"])
        self.style.configure("TLabel", background=display_bg, foreground=colors["text"], font=UI_FONT)
        self.style.configure("Panel.TLabel", background=colors["panel"], foreground=colors["text"])
        self.style.configure("Muted.TLabel", background=colors["panel"], foreground=colors["muted"])
        self.style.configure("TaskCard.TLabel", background=colors["panel"], foreground=colors["text"])
        self.style.configure("SelectedTask.TLabel", background=colors["accent2"], foreground=colors["text"])
        self.style.configure("DoneTask.TLabel", background=colors["done_bg"], foreground=colors["muted"])
        self.style.configure("TaskMeta.TLabel", background=colors["panel"], foreground=colors["muted"], font=SMALL_FONT)
        self.style.configure("SelectedMeta.TLabel", background=colors["accent2"], foreground=colors["muted"], font=SMALL_FONT)
        self.style.configure("DoneMeta.TLabel", background=colors["done_bg"], foreground=colors["muted"], font=SMALL_FONT)
        self.style.configure("Event.TLabel", background=colors["card1"], foreground=colors["card_text"], font=SMALL_FONT, padding=(4, 2))
        self.style.configure("CalendarTask.TLabel", background=colors["card2"], foreground=colors["card_text"], font=SMALL_FONT, padding=(4, 2))
        self.style.configure("Hero.TLabel", background=colors["hero"], foreground=colors["hero_text"])
        self.style.configure("CardOne.TLabel", background=colors["card1"], foreground=colors["card_text"])
        self.style.configure("CardTwo.TLabel", background=colors["card2"], foreground=colors["card_text"])
        self.style.configure("CardThree.TLabel", background=colors["card3"], foreground=colors["card_text"])
        self.style.configure("Title.TLabel", background=display_bg, foreground=colors["text"], font=TITLE_FONT)
        self.style.configure("Section.TLabel", background=colors["panel"], foreground=colors["text"], font=UI_FONT_BOLD)
        self.style.configure("AppTitle.TLabel", background=colors["hero"], foreground=colors["hero_text"], font=APP_TITLE_FONT)
        self.style.configure("Accent.TButton", background=colors["accent"], foreground=colors["button_text"], padding=(14, 8), font=UI_FONT_BOLD)
        self.style.configure("TButton", padding=(10, 7), background=colors["panel2"], foreground=colors["text"], font=UI_FONT)
        self.style.configure("Nav.TButton", padding=(10, 7), background=colors["accent2"], foreground=colors["text"], font=SMALL_FONT)
        self.style.map("TButton", background=[("active", colors["accent2"])], foreground=[("active", colors["text"])])
        self.style.configure("TCheckbutton", background=display_bg, foreground=colors["text"], font=UI_FONT)
        self.style.configure("TRadiobutton", background=display_bg, foreground=colors["text"], font=UI_FONT)
        self.style.configure("TEntry", fieldbackground=colors["panel"], foreground=colors["text"], padding=7)
        self.style.configure("TCombobox", fieldbackground=colors["panel"], foreground=colors["text"], padding=5)
        self.style.configure("Treeview", rowheight=row_height, fieldbackground=colors["panel"], background=colors["panel"], foreground=colors["text"], font=UI_FONT)
        self.style.configure("Treeview.Heading", background=colors["panel2"], foreground=colors["text"], font=UI_FONT_BOLD)
        self.style.map("Treeview", background=[("selected", colors["accent2"])], foreground=[("selected", colors["text"])])

    def build_shell(self) -> None:
        self.shell = ttk.Frame(self.root, padding=16)
        self.shell.pack(fill="both", expand=True)
        self.header = ttk.Frame(self.shell)
        self.header.pack(fill="x", pady=(0, 8))
        ttk.Label(self.header, text=APP_NAME, style="Title.TLabel").pack(side="left")
        self.nav = ttk.Frame(self.header)
        self.nav.pack(side="right")
        for name in ["Dashboard", "Tasks", "Calendar", "Focus", "Templates", "Settings", "Help"]:
            ttk.Button(self.nav, text=name, style="Nav.TButton", command=lambda n=name: self.route(n)).pack(side="left", padx=3)
        self.content = ttk.Frame(self.shell)
        self.content.pack(fill="both", expand=True)

    def register_shortcuts(self) -> None:
        self.root.bind_all("<Control-k>", lambda _event: self.quick_add_dialog())
        self.root.bind_all("<Control-t>", lambda _event: self.route("Tasks"))
        self.root.bind_all("<Control-d>", lambda _event: self.route("Dashboard"))
        self.root.bind_all("<Control-m>", lambda _event: self.route("Calendar"))
        self.root.bind_all("<F1>", lambda _event: self.route("Help"))

    def clear_content(self) -> None:
        self.root.unbind("<Escape>")
        for child in self.content.winfo_children():
            child.destroy()

    def route(self, name: str) -> None:
        self.current_view = name
        {
            "Dashboard": self.show_dashboard,
            "Tasks": self.show_tasks,
            "Calendar": self.show_calendar,
            "Focus": self.show_focus,
            "Templates": self.show_templates,
            "Settings": self.show_settings,
            "Help": self.show_help,
        }[name]()

    def panel(self, parent, padding: int = 12, style: str = "Panel.TFrame"):
        frame = ttk.Frame(parent, style=style, padding=padding)
        return frame

    def active_list(self) -> dict:
        for item in self.data["lists"]:
            if item["id"] == self.active_list_id:
                return item
        self.active_list_id = self.data["lists"][0]["id"]
        return self.data["lists"][0]

    def all_task_refs(self, include_completed: bool = True) -> list[tuple[dict, dict, dict | None]]:
        refs = []
        for task_list in self.data["lists"]:
            for task in task_list.get("tasks", []):
                if include_completed or not task.get("completed"):
                    refs.append((task, task_list, None))
                for subtask in task.get("subtasks", []):
                    if include_completed or not subtask.get("completed"):
                        refs.append((subtask, task_list, task))
        return refs

    def find_task(self, task_id: str) -> tuple[dict | None, dict | None, dict | None]:
        for task_list in self.data["lists"]:
            for task in task_list.get("tasks", []):
                if task["id"] == task_id:
                    return task, task_list, None
                for subtask in task.get("subtasks", []):
                    if subtask["id"] == task_id:
                        return subtask, task_list, task
        return None, None, None

    def build_task(self, text: str, due_date: str = "", due_time: str = "", recurrence: str = "None", spice: int = 3) -> dict:
        plan = SmartPlanner.preview(text, due_date, spice)
        notes = "\n".join(
            [
                f"Quick start: {plan['next_action']}",
                f"Minimum win: {plan['minimum_win']}",
                f"Done when: {plan['finish_line']}",
                f"Watch for: {plan['blocker_check']}",
                f"Coach note: {plan['coach_note']}",
            ]
        )
        return {
            "id": make_id("task"),
            "text": plan["rewrite"],
            "original_text": clean_text(text),
            "notes": notes,
            "completed": False,
            "category": plan["category"],
            "energy": plan["energy"],
            "priority": plan["priority"],
            "estimate": plan["estimate"],
            "due_date": due_date.strip(),
            "due_time": due_time.strip(),
            "reminder_minutes": 15,
            "recurrence": recurrence,
            "created_at": app_now().isoformat(),
            "updated_at": app_now().isoformat(),
            "subtasks": [],
        }

    def build_event(
        self,
        title: str,
        event_date: str,
        start_time: str = "09:00",
        end_time: str = "10:00",
        recurrence: str = "None",
        notes: str = "",
    ) -> dict:
        return self.normalize_event(
            {
                "id": make_id("event"),
                "title": title,
                "date": event_date,
                "start_time": start_time,
                "end_time": end_time,
                "recurrence": recurrence,
                "reminder_minutes": 15,
                "notes": notes,
                "created_at": app_now().isoformat(),
                "updated_at": app_now().isoformat(),
            }
        )

    def find_event(self, event_id: str) -> dict | None:
        for event in self.data.get("events", []):
            if event.get("id") == event_id:
                return event
        return None

    def show_dashboard(self) -> None:
        self.clear_content()
        colors = self.colors()
        tasks = self.all_task_refs()
        open_tasks = [ref for ref in tasks if not ref[0].get("completed")]
        done_tasks = [ref for ref in tasks if ref[0].get("completed")]
        today = date.today()
        overdue = []
        due_today = []
        upcoming = []
        for task, task_list, parent in open_tasks:
            due = parse_date(task.get("due_date"))
            if not due:
                continue
            if due < today:
                overdue.append((task, task_list, parent))
            elif due == today:
                due_today.append((task, task_list, parent))
            elif due <= today + timedelta(days=7):
                upcoming.append((task, task_list, parent))

        top = ttk.Frame(self.content)
        top.pack(fill="x")
        ttk.Label(top, text="Dashboard", style="Title.TLabel").pack(side="left")
        ttk.Button(top, text="Add Task", style="Accent.TButton", command=self.quick_add_dialog).pack(side="right")

        stats = ttk.Frame(self.content)
        stats.pack(fill="x", pady=10)
        for label, value, frame_style, label_style in [
            ("Open", len(open_tasks), "CardOne.TFrame", "CardOne.TLabel"),
            ("Done", len(done_tasks), "CardThree.TFrame", "CardThree.TLabel"),
            ("Today", len(due_today), "CardTwo.TFrame", "CardTwo.TLabel"),
            ("Late", len(overdue), "Panel.TFrame", "Panel.TLabel"),
            ("Lists", len(self.data["lists"]), "Panel.TFrame", "Panel.TLabel"),
        ]:
            card = self.panel(stats, style=frame_style)
            card.pack(side="left", fill="x", expand=True, padx=4)
            ttk.Label(card, text=str(value), style=label_style, font=("Segoe UI", 20, "bold")).pack(anchor="w")
            ttk.Label(card, text=label, style=label_style).pack(anchor="w")

        body = ttk.PanedWindow(self.content, orient="horizontal")
        body.pack(fill="both", expand=True, pady=(4, 0))
        left = self.panel(body)
        right = self.panel(body)
        body.add(left, weight=3)
        body.add(right, weight=2)

        ttk.Label(left, text="Needs Attention", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        tree = ttk.Treeview(left, columns=("list", "due", "priority"), show="tree headings")
        tree.heading("#0", text="Task")
        tree.column("#0", width=390, anchor="w")
        for col, width in [("list", 150), ("due", 160), ("priority", 90)]:
            tree.heading(col, text=col.title())
            tree.column(col, width=width, anchor="w")
        tree.tag_configure("high", background=colors["high_bg"], foreground=colors["text"])
        tree.tag_configure("medium", background=colors["medium_bg"], foreground=colors["text"])
        tree.pack(fill="both", expand=True)
        for task, task_list, _ in overdue + due_today + upcoming:
            prefix = "Late: " if parse_date(task.get("due_date")) and parse_date(task.get("due_date")) < today else ""
            tag = "high" if task["priority"] == "High" else "medium" if task["priority"] == "Medium" else ""
            tree.insert("", "end", text=task["text"], values=(task_list["name"], f"{prefix}{due_label(task)}", task["priority"]), tags=(tag,))
        if not overdue and not due_today and not upcoming:
            tree.insert("", "end", text="No dated tasks need attention.", values=("", "", ""))

        ttk.Label(right, text="Next Actions", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        next_box = ttk.Frame(right, style="Panel.TFrame")
        next_box.pack(fill="both", expand=True)
        for task, task_list, parent in open_tasks[:8]:
            row = ttk.Frame(next_box, style="Panel.TFrame")
            row.pack(fill="x", pady=5)
            mark = "Subtask" if parent else task_list["name"]
            ttk.Label(row, text=task["text"], style="Panel.TLabel", font=UI_FONT_BOLD, wraplength=300).pack(anchor="w")
            ttk.Label(row, text=f"{mark} | {task.get('estimate', 10)} min | {task.get('energy', 'Medium')} energy", style="Muted.TLabel").pack(anchor="w")
        if not open_tasks:
            ttk.Label(next_box, text="Everything is complete.", style="Panel.TLabel").pack(anchor="w")
        self.content.configure(style="TFrame")

    def show_tasks(self) -> None:
        self.clear_content()
        page = ttk.Frame(self.content)
        page.pack(fill="both", expand=True, padx=72)

        title_area = ttk.Frame(page)
        title_area.pack(fill="x", pady=(4, 14))
        ttk.Label(title_area, text="Rice2k Magic ToDo", style="Title.TLabel", font=("Segoe UI", 24, "bold")).pack(anchor="center")
        ttk.Label(title_area, text="Break tasks into calm next steps.", foreground=self.colors()["muted"]).pack(anchor="center", pady=(2, 0))

        list_bar = ttk.Frame(page)
        list_bar.pack(fill="x", pady=(0, 8))
        ttk.Label(list_bar, text="List").pack(side="left", padx=(0, 4))
        list_names = [item["name"] for item in self.data["lists"]]
        self.list_var = StringVar(value=self.active_list()["name"])
        selector = ttk.Combobox(list_bar, textvariable=self.list_var, values=list_names, state="readonly", width=24)
        selector.pack(side="left")
        selector.bind("<<ComboboxSelected>>", self.on_list_selected)
        ttk.Button(list_bar, text="New tab", command=self.new_list_dialog).pack(side="left", padx=4)
        ttk.Button(list_bar, text="Rename tab", command=self.rename_list_dialog).pack(side="left", padx=4)
        ttk.Label(list_bar, text="Theme").pack(side="left", padx=(18, 4))
        self.quick_theme_var = StringVar(value=self.data["settings"].get("theme", DEFAULT_SETTINGS["theme"]))
        theme_selector = ttk.Combobox(list_bar, textvariable=self.quick_theme_var, values=list(THEMES.keys()), state="readonly", width=16)
        theme_selector.pack(side="left")
        theme_selector.bind("<<ComboboxSelected>>", self.switch_task_theme)

        filter_bar = ttk.Frame(page)
        filter_bar.pack(fill="x", pady=(0, 8))
        ttk.Label(filter_bar, text="Search").pack(side="left", padx=(0, 4))
        self.search_text = StringVar()
        search_entry = ttk.Entry(filter_bar, textvariable=self.search_text, width=34)
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        search_entry.bind("<KeyRelease>", lambda _event: self.populate_task_tree())
        self.show_done_var = StringVar(value="True")
        ttk.Checkbutton(
            filter_bar,
            text="Show completed",
            variable=self.show_done_var,
            onvalue="True",
            offvalue="False",
            command=self.populate_task_tree,
        ).pack(side="left")

        add_panel = self.panel(page, padding=14)
        add_panel.pack(fill="x", pady=(0, 10))
        self.task_text = StringVar()
        self.due_date = StringVar()
        self.due_time = StringVar(value="09:00")
        self.recurrence = StringVar(value="None")
        add_panel.columnconfigure(0, weight=1)
        self.task_entry = ttk.Entry(add_panel, textvariable=self.task_text, width=70)
        self.task_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.task_entry.insert(0, TASK_PLACEHOLDER)
        self.task_entry.configure(foreground=self.colors()["muted"])
        self.task_entry.bind("<FocusIn>", self.clear_task_placeholder)
        self.task_entry.bind("<FocusOut>", self.restore_task_placeholder)
        self.task_entry.bind("<Return>", lambda _event: self.add_task())
        ttk.Button(add_panel, text="Add", style="Accent.TButton", command=self.add_task).grid(row=0, column=1, sticky="ew")

        spice_panel = ttk.Frame(add_panel, style="Panel.TFrame")
        spice_panel.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        spice_panel.columnconfigure(1, weight=1)
        ttk.Label(spice_panel, text="Spiciness level:", style="Panel.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.spice = ttk.Scale(spice_panel, from_=1, to=5, orient="horizontal", length=220)
        self.spice.set(3)
        self.spice.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        ttk.Label(spice_panel, text="More spice means more smaller steps.", style="Muted.TLabel").grid(row=0, column=2, sticky="e")

        details = ttk.Frame(add_panel, style="Panel.TFrame")
        details.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        for idx in range(4):
            details.columnconfigure(idx, weight=1 if idx == 0 else 0)
        ttk.Label(details, text="Due date", style="Panel.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(details, textvariable=self.due_date, width=14).grid(row=1, column=0, sticky="ew", padx=(0, 8))
        ttk.Label(details, text="Time", style="Panel.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Entry(details, textvariable=self.due_time, width=10).grid(row=1, column=1, sticky="ew", padx=(0, 8))
        ttk.Label(details, text="Repeats", style="Panel.TLabel").grid(row=0, column=2, sticky="w")
        ttk.Combobox(details, textvariable=self.recurrence, values=RECURRENCE_OPTIONS, state="readonly", width=12).grid(row=1, column=2, sticky="ew", padx=(0, 8))
        ttk.Button(details, text="Templates", command=self.show_templates).grid(row=1, column=3, sticky="ew")

        list_shell = self.panel(page, padding=0)
        list_shell.pack(fill="both", expand=True)
        self.task_canvas = Canvas(list_shell, highlightthickness=0, bg=self.colors()["panel"])
        task_scroll = ttk.Scrollbar(list_shell, orient="vertical", command=self.task_canvas.yview)
        self.task_canvas.configure(yscrollcommand=task_scroll.set)
        self.task_list_frame = ttk.Frame(self.task_canvas, style="Panel.TFrame", padding=8)
        self.task_canvas_window = self.task_canvas.create_window((0, 0), window=self.task_list_frame, anchor="nw")
        self.task_canvas.pack(side="left", fill="both", expand=True)
        task_scroll.pack(side="right", fill="y")
        self.task_list_frame.bind("<Configure>", self.update_task_scroll_region)
        self.task_canvas.bind("<Configure>", self.resize_task_canvas_window)
        self.task_canvas.bind_all("<MouseWheel>", self.on_task_mousewheel)
        self.populate_task_tree()

        item_actions = ttk.Frame(page)
        item_actions.pack(fill="x", pady=(10, 6))
        for label, command in [
            ("Complete", self.toggle_selected_complete),
            ("Edit", self.edit_selected),
            ("Break down", self.breakdown_selected),
            ("Make easier", self.rewrite_selected),
            ("Add subtask", self.add_subtask_dialog),
            ("Remove", self.delete_selected),
        ]:
            ttk.Button(item_actions, text=label, command=command).pack(side="left", padx=(0, 6))

        list_actions = ttk.Frame(page)
        list_actions.pack(fill="x", pady=(4, 0))
        for label, command in [
            ("Estimate", self.estimate_current_list),
            ("Prioritize", self.prioritize_current_list),
            ("Save to file", self.save_current_list_to_file),
            ("Load from file", self.load_current_list_from_file),
            ("Copy Markdown", self.copy_markdown_to_clipboard),
            ("Clear completed", self.clear_completed_tasks),
        ]:
            ttk.Button(list_actions, text=label, command=command).pack(side="left", padx=(0, 6), pady=2)

    def clear_task_placeholder(self, _event=None) -> None:
        if hasattr(self, "task_entry") and self.task_text.get() == TASK_PLACEHOLDER:
            self.task_entry.delete(0, "end")
            self.task_entry.configure(foreground=self.colors()["text"])

    def restore_task_placeholder(self, _event=None) -> None:
        if hasattr(self, "task_entry") and not self.task_text.get().strip():
            self.task_entry.insert(0, TASK_PLACEHOLDER)
            self.task_entry.configure(foreground=self.colors()["muted"])

    def populate_task_tree(self) -> None:
        if not hasattr(self, "task_list_frame"):
            return
        self.task_card_widgets = {}
        for child in self.task_list_frame.winfo_children():
            child.destroy()
        shown = 0
        query = clean_text(self.search_text.get()).lower() if hasattr(self, "search_text") else ""
        show_done = self.show_done_var.get() == "True" if hasattr(self, "show_done_var") else True
        for task in self.active_list().get("tasks", []):
            parent_visible = self.task_visible(task, query, show_done)
            if parent_visible:
                self.render_task_card(task, depth=0)
                shown += 1
            for subtask in task.get("subtasks", []):
                if self.task_visible(subtask, query, show_done):
                    self.render_task_card(subtask, depth=1 if parent_visible else 0)
                    shown += 1
        if not self.active_list().get("tasks"):
            empty = ttk.Frame(self.task_list_frame, style="Panel.TFrame", padding=22)
            empty.pack(fill="x")
            ttk.Label(empty, text="No tasks yet. Add one above and break it down when it feels too big.", style="Muted.TLabel", wraplength=720).pack(anchor="center")
        elif shown == 0:
            empty = ttk.Frame(self.task_list_frame, style="Panel.TFrame", padding=22)
            empty.pack(fill="x")
            ttk.Label(empty, text="No matching tasks. Clear the search or turn on completed tasks.", style="Muted.TLabel", wraplength=720).pack(anchor="center")

    def task_visible(self, task: dict, query: str, show_done: bool) -> bool:
        if task.get("completed") and not show_done:
            return False
        if not query:
            return True
        fields = [
            task.get("text", ""),
            task.get("notes", ""),
            task.get("category", ""),
            task.get("energy", ""),
            task.get("priority", ""),
            task.get("due_date", ""),
        ]
        return query in " ".join(fields).lower()

    def task_styles(self, task: dict, is_selected: bool) -> tuple[str, str, str]:
        if task.get("completed"):
            return "DoneTask.TFrame", "DoneTask.TLabel", "DoneMeta.TLabel"
        if is_selected:
            return "SelectedTask.TFrame", "SelectedTask.TLabel", "SelectedMeta.TLabel"
        return "TaskCard.TFrame", "TaskCard.TLabel", "TaskMeta.TLabel"

    def task_accent_color(self, task: dict) -> str:
        colors = self.colors()
        if task.get("completed"):
            return colors["done"]
        if task.get("priority") == "High":
            return colors["danger"]
        if task.get("priority") == "Medium":
            return colors["accent3"]
        return colors["accent"]

    def render_task_card(self, task: dict, depth: int = 0) -> None:
        is_selected = task["id"] == self.selected_task_id
        frame_style, title_style, meta_style = self.task_styles(task, is_selected)
        outer = ttk.Frame(self.task_list_frame, style="Panel.TFrame")
        outer.pack(fill="x", padx=(depth * 28, 0), pady=5)
        card = ttk.Frame(outer, style=frame_style, padding=(12, 10))
        card.pack(fill="x")
        self.bind_task_clicks(card, task["id"])

        rail = Canvas(card, width=7, height=58, bg=self.task_accent_color(task), highlightthickness=0)
        rail.pack(side="left", fill="y", padx=(0, 10))
        self.bind_task_clicks(rail, task["id"])

        check_text = "[x]" if task.get("completed") else "[ ]"
        check = ttk.Button(card, text=check_text, width=4, command=lambda tid=task["id"]: self.toggle_task_by_id(tid))
        check.pack(side="left", padx=(0, 10))
        check.bind("<Button-3>", lambda event, tid=task["id"]: self.show_task_menu(event, tid))

        text_area = ttk.Frame(card, style=frame_style)
        text_area.pack(side="left", fill="x", expand=True)
        title = ttk.Label(text_area, text=task["text"], style=title_style, font=("Segoe UI", 13, "bold"), wraplength=760)
        title.pack(anchor="w")
        self.bind_task_clicks(text_area, task["id"])
        self.bind_task_clicks(title, task["id"])
        title.bind("<Double-1>", lambda event, tid=task["id"]: (self.select_task_card(tid), self.edit_selected()))
        meta_parts = []
        if due_label(task):
            meta_parts.append(f"Due {due_label(task)}")
        meta_parts.append(f"{task.get('estimate', 10)} min")
        meta_parts.append(task.get("priority", "Normal"))
        meta_parts.append(task.get("category", "General"))
        meta = ttk.Label(text_area, text="  |  ".join(meta_parts), style=meta_style)
        meta.pack(anchor="w", pady=(3, 0))
        self.bind_task_clicks(meta, task["id"])

        actions = ttk.Frame(text_area, style=frame_style)
        actions.pack(anchor="w", pady=(8, 0))
        for icon_name, text, command in [
            ("magic", "Steps", lambda tid=task["id"]: self.run_task_action(tid, self.breakdown_selected)),
            ("edit", "Edit", lambda tid=task["id"]: self.run_task_action(tid, self.edit_selected)),
            ("subtask", "Add", lambda tid=task["id"]: self.run_task_action(tid, self.add_subtask_dialog)),
            ("delete", "Del", lambda tid=task["id"]: self.run_task_action(tid, self.delete_selected)),
        ]:
            button = self.icon_button(actions, icon_name, text, command)
            button.bind("<Button-3>", lambda event, tid=task["id"]: self.show_task_menu(event, tid))
            button.pack(side="left", padx=(0, 6))
        self.bind_task_clicks(actions, task["id"])

        self.task_card_widgets[task["id"]] = {
            "card": card,
            "text_area": text_area,
            "title": title,
            "meta": meta,
            "actions": actions,
        }

    def bind_task_clicks(self, widget, task_id: str) -> None:
        widget.bind("<Button-1>", lambda event, tid=task_id: self.select_task_card(tid))
        widget.bind("<Button-3>", lambda event, tid=task_id: self.show_task_menu(event, tid))

    def icon_button(self, parent, icon_name: str, text: str, command):
        icon = self.action_icons.get(icon_name)
        if icon:
            return ttk.Button(parent, text=text, image=icon, compound="left", command=command)
        return ttk.Button(parent, text=text, command=command)

    def select_task_card(self, task_id: str) -> None:
        self.selected_task_id = task_id
        for current_id, widgets in self.task_card_widgets.items():
            task, _, _ = self.find_task(current_id)
            if not task:
                continue
            frame_style, title_style, meta_style = self.task_styles(task, current_id == task_id)
            for key in ["card", "text_area", "actions"]:
                widgets[key].configure(style=frame_style)
            widgets["title"].configure(style=title_style)
            widgets["meta"].configure(style=meta_style)

    def run_task_action(self, task_id: str, action) -> None:
        self.selected_task_id = task_id
        action()

    def toggle_task_by_id(self, task_id: str) -> None:
        self.selected_task_id = task_id
        self.toggle_selected_complete()

    def update_task_scroll_region(self, _event=None) -> None:
        if hasattr(self, "task_canvas"):
            self.task_canvas.configure(scrollregion=self.task_canvas.bbox("all"))

    def resize_task_canvas_window(self, event) -> None:
        if hasattr(self, "task_canvas"):
            self.task_canvas.itemconfigure(self.task_canvas_window, width=event.width)

    def on_task_mousewheel(self, event) -> None:
        if hasattr(self, "task_canvas") and self.current_view == "Tasks":
            self.task_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_list_selected(self, _event=None) -> None:
        selected = self.list_var.get()
        for task_list in self.data["lists"]:
            if task_list["name"] == selected:
                self.active_list_id = task_list["id"]
                break
        self.selected_task_id = None
        self.show_tasks()

    def switch_task_theme(self, _event=None) -> None:
        selected = normalize_theme_name(self.quick_theme_var.get() if hasattr(self, "quick_theme_var") else None)
        self.data["settings"]["theme"] = selected
        self.save_data()
        self.apply_theme(selected)
        self.show_tasks()

    def add_task(self) -> None:
        text = clean_text(self.task_text.get())
        if text == TASK_PLACEHOLDER:
            text = ""
        if not text:
            messagebox.showinfo(APP_NAME, "Enter a task first.")
            return
        due_date = self.due_date.get().strip()
        if due_date and not parse_date(due_date):
            messagebox.showwarning(APP_NAME, "Use a date like 2026-08-01.")
            return
        task = self.build_task(text, due_date, self.due_time.get(), self.recurrence.get(), int(round(float(self.spice.get()))))
        self.active_list()["tasks"].append(task)
        self.task_text.set("")
        self.save_data()
        self.populate_task_tree()
        if hasattr(self, "task_entry"):
            self.task_entry.focus_set()

    def selected_task(self) -> tuple[dict | None, dict | None, dict | None]:
        if not self.selected_task_id:
            return None, None, None
        return self.find_task(self.selected_task_id)

    def show_task_menu(self, event, task_id: str | None = None) -> None:
        if task_id:
            self.selected_task_id = task_id
        menu = self.make_menu()
        self.add_menu_command(menu, "Complete / reopen", "check", self.toggle_selected_complete)
        self.add_menu_command(menu, "Edit task", "edit", self.edit_selected)
        self.add_menu_command(menu, "Add note", "edit", self.add_note_dialog)
        self.add_menu_command(menu, "Add subtask", "subtask", self.add_subtask_dialog)
        menu.add_separator()
        self.add_menu_command(menu, "Break down into steps", "magic", self.breakdown_selected)
        self.add_menu_command(menu, "Make easier", "magic", self.rewrite_selected)
        self.add_menu_command(menu, "Estimate", "estimate", self.estimate_selected_task)

        schedule_menu = self.make_menu(menu)
        for label, days in [("Today", 0), ("Tomorrow", 1), ("Next week", 7)]:
            schedule_menu.add_command(label=label, command=lambda d=days: self.set_selected_due_in_days(d))
        schedule_menu.add_command(label="Custom schedule...", command=self.schedule_selected_dialog)
        menu.add_cascade(label="Schedule", menu=schedule_menu)

        recurrence_menu = self.make_menu(menu)
        for recurrence in RECURRENCE_OPTIONS:
            recurrence_menu.add_command(label=recurrence, command=lambda value=recurrence: self.set_selected_recurrence(value))
        menu.add_cascade(label="Repeats", menu=recurrence_menu)

        priority_menu = self.make_menu(menu)
        for priority in ["High", "Medium", "Normal"]:
            priority_menu.add_command(label=priority, command=lambda value=priority: self.set_selected_priority(value))
        menu.add_cascade(label="Priority", menu=priority_menu)

        category_menu = self.make_menu(menu)
        for category in ["General", *SmartPlanner.category_words.keys()]:
            category_menu.add_command(label=category, command=lambda value=category: self.set_selected_category(value))
        menu.add_cascade(label="Category", menu=category_menu)

        menu.add_separator()
        self.add_menu_command(menu, "Create calendar event", "estimate", self.create_event_from_selected)
        self.add_menu_command(menu, "Show on calendar", "menu", self.show_selected_on_calendar)
        self.add_menu_command(menu, "Copy Markdown", "menu", self.copy_selected_task_markdown)
        self.add_menu_command(menu, "Duplicate", "subtask", self.duplicate_selected)
        self.add_menu_command(menu, "Move up", "menu", lambda: self.move_selected(-1))
        self.add_menu_command(menu, "Move down", "menu", lambda: self.move_selected(1))
        self.add_menu_command(menu, "Start Focus", "check", self.focus_selected)
        menu.add_separator()
        self.add_menu_command(menu, "Delete", "delete", self.delete_selected)
        menu.tk_popup(event.x_root, event.y_root)

    def set_selected_due_in_days(self, days: int) -> None:
        task, _, _ = self.selected_task()
        if not task:
            return
        target = date.today() + timedelta(days=days)
        task["due_date"] = target.isoformat()
        task["due_time"] = task.get("due_time") or "09:00"
        task["priority"] = SmartPlanner.priority(task["text"], task.get("due_date"))
        task["updated_at"] = app_now().isoformat()
        self.save_data()
        self.refresh_current_view()

    def schedule_selected_dialog(self) -> None:
        task, _, _ = self.selected_task()
        if not task:
            return
        win = Toplevel(self.root)
        win.title("Schedule Task")
        win.geometry("430x260")
        win.transient(self.root)
        win.grab_set()
        self.theme_popup(win)
        frame = ttk.Frame(win, padding=14)
        frame.pack(fill="both", expand=True)
        due_var = StringVar(value=task.get("due_date", ""))
        time_var = StringVar(value=task.get("due_time", "09:00"))
        repeat_var = StringVar(value=task.get("recurrence", "None"))
        reminder_var = StringVar(value=str(task.get("reminder_minutes", 15)))
        for label, var in [("Due date", due_var), ("Time", time_var), ("Reminder minutes", reminder_var)]:
            ttk.Label(frame, text=label).pack(anchor="w")
            ttk.Entry(frame, textvariable=var).pack(fill="x", pady=(0, 8))
        ttk.Label(frame, text="Repeats").pack(anchor="w")
        ttk.Combobox(frame, textvariable=repeat_var, values=RECURRENCE_OPTIONS, state="readonly").pack(fill="x")

        def save_schedule() -> None:
            if due_var.get() and not parse_date(due_var.get()):
                messagebox.showwarning(APP_NAME, "Use a date like 2026-08-01.")
                return
            task["due_date"] = due_var.get().strip()
            task["due_time"] = time_var.get().strip()
            task["recurrence"] = repeat_var.get()
            try:
                task["reminder_minutes"] = max(0, int(reminder_var.get()))
            except ValueError:
                task["reminder_minutes"] = 15
            task["priority"] = SmartPlanner.priority(task["text"], task.get("due_date"))
            task["updated_at"] = app_now().isoformat()
            self.save_data()
            win.destroy()
            self.refresh_current_view()

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=(12, 0))
        ttk.Button(buttons, text="Save", command=save_schedule).pack(side="right")
        ttk.Button(buttons, text="Cancel", command=win.destroy).pack(side="right", padx=4)

    def set_selected_recurrence(self, recurrence: str) -> None:
        task, _, _ = self.selected_task()
        if not task:
            return
        task["recurrence"] = recurrence
        task["updated_at"] = app_now().isoformat()
        self.save_data()
        self.refresh_current_view()

    def set_selected_priority(self, priority: str) -> None:
        task, _, _ = self.selected_task()
        if not task:
            return
        task["priority"] = priority
        task["updated_at"] = app_now().isoformat()
        self.save_data()
        self.refresh_current_view()

    def set_selected_category(self, category: str) -> None:
        task, _, _ = self.selected_task()
        if not task:
            return
        task["category"] = category
        task["updated_at"] = app_now().isoformat()
        self.save_data()
        self.refresh_current_view()

    def add_note_dialog(self) -> None:
        task, _, _ = self.selected_task()
        if not task:
            return
        self.simple_input("Add Note", "Note", lambda value: self.append_note_to_selected(value))

    def append_note_to_selected(self, value: str) -> None:
        task, _, _ = self.selected_task()
        value = clean_text(value)
        if not task or not value:
            return
        task["notes"] = f"{task.get('notes', '').strip()}\n\nNote: {value}".strip()
        task["updated_at"] = app_now().isoformat()
        self.save_data()
        self.refresh_current_view()

    def copy_selected_task_markdown(self) -> None:
        task, _, _ = self.selected_task()
        if not task:
            return
        checked = "x" if task.get("completed") else " "
        due = f" due {due_label(task)}" if due_label(task) else ""
        self.root.clipboard_clear()
        self.root.clipboard_append(f"- [{checked}] {task.get('text', 'Untitled task')}{due}")
        messagebox.showinfo(APP_NAME, "Task copied as Markdown.")

    def create_event_from_selected(self) -> None:
        task, _, _ = self.selected_task()
        if not task:
            return
        event = self.build_event(
            title=task.get("text", "Task"),
            event_date=task.get("due_date") or date.today().isoformat(),
            start_time=task.get("due_time") or "09:00",
            recurrence=task.get("recurrence", "None"),
            notes=task.get("notes", ""),
        )
        self.data.setdefault("events", []).append(event)
        self.save_data()
        self.calendar_month = parse_date(event["date"]).replace(day=1)
        self.show_calendar()

    def show_selected_on_calendar(self) -> None:
        task, _, _ = self.selected_task()
        if not task:
            return
        due = parse_date(task.get("due_date"))
        if due:
            self.calendar_month = due.replace(day=1)
        self.show_calendar()

    def refresh_current_view(self) -> None:
        if self.current_view == "Calendar":
            self.show_calendar()
        elif self.current_view == "Tasks":
            self.populate_task_tree()
        else:
            self.route(self.current_view)

    def toggle_selected_complete(self) -> None:
        task, task_list, parent = self.selected_task()
        if not task:
            return
        task["completed"] = not task.get("completed")
        task["updated_at"] = app_now().isoformat()
        if task["completed"] and not parent:
            self.create_next_recurring(task, task_list)
        self.save_data()
        self.populate_task_tree()

    def create_next_recurring(self, task: dict, task_list: dict) -> None:
        recurrence = task.get("recurrence", "None")
        due = parse_date(task.get("due_date"))
        if recurrence == "None" or not due:
            return
        next_date = next_recurrence_date(due, recurrence)
        if not next_date:
            return
        clone = copy.deepcopy(task)
        clone["id"] = make_id("task")
        clone["completed"] = False
        clone["due_date"] = next_date.isoformat()
        clone["created_at"] = app_now().isoformat()
        clone["updated_at"] = app_now().isoformat()
        for subtask in clone.get("subtasks", []):
            subtask["id"] = make_id("task")
            subtask["completed"] = False
        task_list["tasks"].append(clone)

    def rewrite_selected(self) -> None:
        task, _, _ = self.selected_task()
        if not task:
            return
        previous = task["text"]
        source = task.get("original_text") or task["text"]
        plan = SmartPlanner.preview(source, task.get("due_date", ""), 2)
        task["text"] = plan["rewrite"]
        helper_note = "\n".join(
            [
                f"Made easier from: {previous}",
                f"Quick start: {plan['next_action']}",
                f"Minimum win: {plan['minimum_win']}",
                f"Done when: {plan['finish_line']}",
                f"Watch for: {plan['blocker_check']}",
                f"Coach note: {plan['coach_note']}",
            ]
        )
        task["notes"] = f"{helper_note}\n\n{task.get('notes', '')}".strip()
        task["updated_at"] = app_now().isoformat()
        self.save_data()
        self.populate_task_tree()

    def breakdown_selected(self) -> None:
        task, _, _ = self.selected_task()
        if not task:
            return
        spice = 4
        steps = SmartPlanner.breakdown(task["text"], spice)
        task["subtasks"] = [
            {
                "id": make_id("task"),
                "text": step,
                "original_text": step,
                "notes": "",
                "completed": False,
                "category": task.get("category", "General"),
                "energy": SmartPlanner.energy(step),
                "priority": task.get("priority", "Normal"),
                "estimate": max(5, task.get("estimate", 30) // max(1, len(steps))),
                "due_date": task.get("due_date", ""),
                "due_time": task.get("due_time", ""),
                "reminder_minutes": task.get("reminder_minutes", 15),
                "recurrence": "None",
                "created_at": app_now().isoformat(),
                "updated_at": app_now().isoformat(),
                "subtasks": [],
            }
            for step in steps
        ]
        task["updated_at"] = app_now().isoformat()
        self.save_data()
        self.populate_task_tree()

    def delete_selected(self) -> None:
        task, task_list, parent = self.selected_task()
        if not task:
            return
        if not messagebox.askyesno(APP_NAME, "Delete the selected task?"):
            return
        if parent:
            parent["subtasks"] = [item for item in parent.get("subtasks", []) if item["id"] != task["id"]]
        else:
            task_list["tasks"] = [item for item in task_list.get("tasks", []) if item["id"] != task["id"]]
        self.selected_task_id = None
        self.save_data()
        self.populate_task_tree()

    def duplicate_selected(self) -> None:
        task, task_list, parent = self.selected_task()
        if not task:
            return
        clone = copy.deepcopy(task)
        clone["id"] = make_id("task")
        clone["text"] = f"{clone['text']} copy"
        clone["completed"] = False
        for subtask in clone.get("subtasks", []):
            subtask["id"] = make_id("task")
            subtask["completed"] = False
        if parent:
            parent.setdefault("subtasks", []).append(clone)
        else:
            task_list.setdefault("tasks", []).append(clone)
        self.save_data()
        self.populate_task_tree()

    def add_subtask_dialog(self) -> None:
        task, _, parent = self.selected_task()
        if not task:
            return
        host = parent if parent else task
        self.simple_input("Add Subtask", "Subtask", lambda value: self.add_subtask(host, value))

    def add_subtask(self, parent: dict, text: str) -> None:
        text = clean_text(text)
        if not text:
            return
        subtask = self.build_task(text, parent.get("due_date", ""), parent.get("due_time", ""), "None", 2)
        parent.setdefault("subtasks", []).append(subtask)
        self.save_data()
        self.populate_task_tree()

    def edit_selected(self) -> None:
        task, _, _ = self.selected_task()
        if not task:
            return
        win = Toplevel(self.root)
        win.title("Edit Task")
        win.geometry("520x470")
        win.transient(self.root)
        win.grab_set()
        self.theme_popup(win)
        frame = ttk.Frame(win, padding=14)
        frame.pack(fill="both", expand=True)
        text_var = StringVar(value=task.get("text", ""))
        due_var = StringVar(value=task.get("due_date", ""))
        time_var = StringVar(value=task.get("due_time", ""))
        repeat_var = StringVar(value=task.get("recurrence", "None"))
        reminder_var = StringVar(value=str(task.get("reminder_minutes", 15)))
        ttk.Label(frame, text="Task").pack(anchor="w")
        ttk.Entry(frame, textvariable=text_var).pack(fill="x", pady=(0, 8))
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=(0, 8))
        for label, var, width in [("Due Date", due_var, 14), ("Time", time_var, 10), ("Reminder", reminder_var, 8)]:
            box = ttk.Frame(row)
            box.pack(side="left", padx=(0, 8))
            ttk.Label(box, text=label).pack(anchor="w")
            ttk.Entry(box, textvariable=var, width=width).pack()
        ttk.Label(frame, text="Repeats").pack(anchor="w")
        ttk.Combobox(frame, textvariable=repeat_var, values=RECURRENCE_OPTIONS, state="readonly").pack(fill="x", pady=(0, 8))
        ttk.Label(frame, text="Notes").pack(anchor="w")
        colors = self.colors()
        notes = Text(frame, height=8, wrap="word", font=UI_FONT, bg=colors["panel"], fg=colors["text"], insertbackground=colors["text"], relief="solid", borderwidth=1)
        notes.insert("1.0", task.get("notes", ""))
        notes.pack(fill="both", expand=True)

        def save_edit() -> None:
            if due_var.get() and not parse_date(due_var.get()):
                messagebox.showwarning(APP_NAME, "Use a date like 2026-08-01.")
                return
            task["text"] = clean_text(text_var.get())
            task["due_date"] = due_var.get().strip()
            task["due_time"] = time_var.get().strip()
            task["recurrence"] = repeat_var.get()
            try:
                task["reminder_minutes"] = max(0, int(reminder_var.get()))
            except ValueError:
                task["reminder_minutes"] = 15
            task["notes"] = notes.get("1.0", "end").strip()
            task["priority"] = SmartPlanner.priority(task["text"], task.get("due_date"))
            task["updated_at"] = app_now().isoformat()
            self.save_data()
            win.destroy()
            self.populate_task_tree()

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=(10, 0))
        ttk.Button(buttons, text="Save", command=save_edit).pack(side="right")
        ttk.Button(buttons, text="Cancel", command=win.destroy).pack(side="right", padx=4)

    def move_selected(self, delta: int) -> None:
        task, task_list, parent = self.selected_task()
        if not task:
            return
        items = parent.setdefault("subtasks", []) if parent else task_list.setdefault("tasks", [])
        idx = next((i for i, item in enumerate(items) if item["id"] == task["id"]), -1)
        target = idx + delta
        if idx < 0 or target < 0 or target >= len(items):
            return
        items[idx], items[target] = items[target], items[idx]
        self.save_data()
        self.populate_task_tree()

    def estimate_current_list(self) -> None:
        for task in self.active_list().get("tasks", []):
            self.refresh_task_planning(task)
            for subtask in task.get("subtasks", []):
                self.refresh_task_planning(subtask)
        self.save_data()
        self.populate_task_tree()

    def estimate_selected_task(self) -> None:
        task, _, _ = self.selected_task()
        if not task:
            return
        self.refresh_task_planning(task)
        self.save_data()
        self.populate_task_tree()

    def prioritize_current_list(self) -> None:
        priority_order = {"High": 0, "Medium": 1, "Normal": 2}
        for task in self.active_list().get("tasks", []):
            self.refresh_task_planning(task)
            for subtask in task.get("subtasks", []):
                self.refresh_task_planning(subtask)
            task["subtasks"] = sorted(task.get("subtasks", []), key=lambda item: priority_order.get(item.get("priority", "Normal"), 3))
        self.active_list()["tasks"] = sorted(self.active_list().get("tasks", []), key=lambda item: priority_order.get(item.get("priority", "Normal"), 3))
        self.save_data()
        self.populate_task_tree()

    def refresh_task_planning(self, task: dict) -> None:
        text = task.get("original_text") or task.get("text", "")
        task["category"] = SmartPlanner.categorize(text)
        task["energy"] = SmartPlanner.energy(text)
        task["estimate"] = SmartPlanner.estimate(text, 3)
        task["priority"] = SmartPlanner.priority(text, task.get("due_date"))
        task["updated_at"] = app_now().isoformat()

    def save_current_list_to_file(self) -> None:
        filename = filedialog.asksaveasfilename(
            title="Save list",
            defaultextension=".json",
            filetypes=[("Rice2k task list", "*.json"), ("All files", "*.*")],
            initialfile=f"{self.active_list()['name']}.json",
        )
        if not filename:
            return
        Path(filename).write_text(json.dumps(self.active_list(), indent=2), encoding="utf-8")
        messagebox.showinfo(APP_NAME, "List saved.")

    def load_current_list_from_file(self) -> None:
        filename = filedialog.askopenfilename(
            title="Load list",
            filetypes=[("Rice2k task list", "*.json"), ("All files", "*.*")],
        )
        if not filename:
            return
        try:
            loaded = json.loads(Path(filename).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            messagebox.showwarning(APP_NAME, "That file could not be loaded.")
            return
        if not isinstance(loaded, dict) or not isinstance(loaded.get("tasks"), list):
            messagebox.showwarning(APP_NAME, "That file does not look like a saved task list.")
            return
        current = self.active_list()
        current["name"] = clean_text(loaded.get("name", current["name"])) or current["name"]
        current["tasks"] = [self.normalize_loaded_task(task) for task in loaded.get("tasks", []) if isinstance(task, dict)]
        self.selected_task_id = None
        self.save_data()
        self.show_tasks()

    def normalize_loaded_task(self, task: dict) -> dict:
        normalized = self.build_task(task.get("original_text") or task.get("text", "Untitled task"))
        for key in [
            "id",
            "text",
            "original_text",
            "notes",
            "completed",
            "category",
            "energy",
            "priority",
            "estimate",
            "due_date",
            "due_time",
            "reminder_minutes",
            "recurrence",
            "created_at",
            "updated_at",
        ]:
            if key in task:
                normalized[key] = task[key]
        normalized["id"] = normalized.get("id") or make_id("task")
        normalized["subtasks"] = [self.normalize_loaded_task(item) for item in task.get("subtasks", []) if isinstance(item, dict)]
        return normalized

    def copy_markdown_to_clipboard(self) -> None:
        markdown = "\n".join(self.markdown_lines(self.active_list().get("tasks", []))) or "- [ ] No tasks yet"
        self.root.clipboard_clear()
        self.root.clipboard_append(markdown)
        messagebox.showinfo(APP_NAME, "Markdown copied to clipboard.")

    def markdown_lines(self, tasks: list[dict], indent: int = 0) -> list[str]:
        lines = []
        prefix = "  " * indent
        for task in tasks:
            checked = "x" if task.get("completed") else " "
            estimate = f" ({task.get('estimate')} min)" if task.get("estimate") else ""
            lines.append(f"{prefix}- [{checked}] {task.get('text', 'Untitled task')}{estimate}")
            lines.extend(self.markdown_lines(task.get("subtasks", []), indent + 1))
        return lines

    def clear_completed_tasks(self) -> None:
        def keep_open(tasks: list[dict]) -> list[dict]:
            kept = []
            for task in tasks:
                if task.get("completed"):
                    continue
                task["subtasks"] = keep_open(task.get("subtasks", []))
                kept.append(task)
            return kept

        self.active_list()["tasks"] = keep_open(self.active_list().get("tasks", []))
        self.selected_task_id = None
        self.save_data()
        self.populate_task_tree()

    def quick_add_dialog(self) -> None:
        self.simple_input("Quick Add", "Task", lambda value: self.quick_add(value))

    def quick_add(self, value: str) -> None:
        value = clean_text(value)
        if value:
            self.active_list()["tasks"].append(self.build_task(value))
            self.save_data()
            self.route(self.current_view)

    def simple_input(self, title: str, label: str, callback) -> None:
        win = Toplevel(self.root)
        win.title(title)
        win.geometry("420x130")
        win.transient(self.root)
        win.grab_set()
        self.theme_popup(win)
        frame = ttk.Frame(win, padding=14)
        frame.pack(fill="both", expand=True)
        value = StringVar()
        ttk.Label(frame, text=label).pack(anchor="w")
        entry = ttk.Entry(frame, textvariable=value)
        entry.pack(fill="x", pady=8)
        entry.focus_set()

        def done() -> None:
            callback(value.get())
            win.destroy()

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Add", command=done).pack(side="right")
        ttk.Button(buttons, text="Cancel", command=win.destroy).pack(side="right", padx=4)
        win.bind("<Return>", lambda _event: done())

    def new_list_dialog(self) -> None:
        self.simple_input("New List", "List Name", self.create_list)

    def create_list(self, name: str) -> None:
        name = clean_text(name)
        if not name:
            return
        task_list = {"id": make_id("list"), "name": name, "tasks": []}
        self.data["lists"].append(task_list)
        self.active_list_id = task_list["id"]
        self.save_data()
        self.show_tasks()

    def rename_list_dialog(self) -> None:
        self.simple_input("Rename List", "New Name", self.rename_list)

    def rename_list(self, name: str) -> None:
        name = clean_text(name)
        if not name:
            return
        self.active_list()["name"] = name
        self.save_data()
        self.show_tasks()

    def show_calendar(self) -> None:
        self.clear_content()
        top = ttk.Frame(self.content)
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(top, text="Calendar", style="Title.TLabel").pack(side="left")
        ttk.Button(top, text="Add Event", style="Accent.TButton", command=lambda: self.show_event_dialog(date.today())).pack(side="right", padx=3)
        ttk.Button(top, text="Today", command=self.show_current_month).pack(side="right", padx=3)
        ttk.Button(top, text="Previous", command=lambda: self.change_month(-1)).pack(side="right", padx=3)
        ttk.Button(top, text="Next", command=lambda: self.change_month(1)).pack(side="right", padx=3)
        ttk.Label(top, text=self.calendar_month.strftime("%B %Y"), font=("Segoe UI", 13, "bold")).pack(side="right", padx=16)

        month = calendar.Calendar(firstweekday=6)
        weeks = month.monthdatescalendar(self.calendar_month.year, self.calendar_month.month)
        visible_days = [day for week in weeks for day in week]
        grid = ttk.Frame(self.content)
        grid.pack(fill="both", expand=True)
        for i, name in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
            ttk.Label(grid, text=name, anchor="center", font=("Segoe UI", 10, "bold")).grid(row=0, column=i, sticky="ew", padx=2, pady=2)
            grid.columnconfigure(i, weight=1)

        tasks_by_day: dict[date, list[dict]] = {}
        for task, _, _ in self.all_task_refs(include_completed=False):
            due = parse_date(task.get("due_date"))
            if due:
                tasks_by_day.setdefault(due, []).append(task)

        events_by_day: dict[date, list[dict]] = {}
        for event in self.data.get("events", []):
            for day in visible_days:
                if event_occurs_on(event, day):
                    events_by_day.setdefault(day, []).append(event)

        for row_idx, week in enumerate(weeks, start=1):
            grid.rowconfigure(row_idx, weight=1)
            for col_idx, day in enumerate(week):
                cell = self.panel(grid, padding=8)
                cell.grid(row=row_idx, column=col_idx, sticky="nsew", padx=2, pady=2)
                self.bind_calendar_target(cell, day)
                label_style = "Panel.TLabel"
                day_text = str(day.day)
                if day.month != self.calendar_month.month:
                    day_text = f"({day.day})"
                day_label = ttk.Label(cell, text=day_text, style=label_style, font=("Segoe UI", 10, "bold"))
                day_label.pack(anchor="w")
                self.bind_calendar_target(day_label, day)

                shown = 0
                for event_item in events_by_day.get(day, [])[:3]:
                    label = ttk.Label(cell, text=f"{event_time_label(event_item)}  {event_item['title']}", style="Event.TLabel", wraplength=135)
                    label.pack(anchor="w", fill="x", pady=1)
                    self.bind_calendar_item(label, "event", event_item["id"], day)
                    shown += 1
                for task in tasks_by_day.get(day, [])[: max(0, 5 - shown)]:
                    label = ttk.Label(cell, text=f"Task: {task['text']}", style="CalendarTask.TLabel", wraplength=135)
                    label.pack(anchor="w", fill="x", pady=1)
                    self.bind_calendar_item(label, "task", task["id"], day)
                    shown += 1
                extra = len(events_by_day.get(day, [])) + len(tasks_by_day.get(day, [])) - shown
                if extra > 0:
                    ttk.Label(cell, text=f"+{extra} more", style="Muted.TLabel").pack(anchor="w")

    def show_current_month(self) -> None:
        self.calendar_month = date.today().replace(day=1)
        self.show_calendar()

    def change_month(self, delta: int) -> None:
        month = self.calendar_month.month + delta
        year = self.calendar_month.year
        if month < 1:
            month = 12
            year -= 1
        if month > 12:
            month = 1
            year += 1
        self.calendar_month = date(year, month, 1)
        self.show_calendar()

    def bind_calendar_target(self, widget, day: date) -> None:
        widget.bind("<Double-1>", lambda _event, d=day: self.show_event_dialog(d))
        widget.bind("<Button-3>", lambda event, d=day: self.show_calendar_day_menu(event, d))
        widget.bind("<ButtonRelease-1>", lambda _event, d=day: self.drop_calendar_item(d))

    def bind_calendar_item(self, widget, kind: str, item_id: str, day: date) -> None:
        widget.bind("<ButtonPress-1>", lambda _event, k=kind, iid=item_id, d=day: self.start_calendar_drag(k, iid, d))
        widget.bind("<ButtonRelease-1>", lambda _event, d=day: self.drop_calendar_item(d))
        widget.bind("<Double-1>", lambda _event, k=kind, iid=item_id, d=day: self.open_calendar_item(k, iid, d))
        widget.bind("<Button-3>", lambda event, k=kind, iid=item_id, d=day: self.show_calendar_item_menu(event, k, iid, d))

    def start_calendar_drag(self, kind: str, item_id: str, origin_day: date) -> None:
        self.drag_calendar_item = (kind, item_id, origin_day)

    def drop_calendar_item(self, target_day: date) -> None:
        if not self.drag_calendar_item:
            return
        kind, item_id, origin_day = self.drag_calendar_item
        self.drag_calendar_item = None
        if target_day == origin_day:
            return
        if kind == "task":
            task, _, _ = self.find_task(item_id)
            if task:
                task["due_date"] = target_day.isoformat()
                task["due_time"] = task.get("due_time") or "09:00"
                task["updated_at"] = app_now().isoformat()
                self.save_data()
                self.show_calendar()
        elif kind == "event":
            event = self.find_event(item_id)
            if event:
                event["date"] = target_day.isoformat()
                event["updated_at"] = app_now().isoformat()
                self.save_data()
                self.show_calendar()

    def open_calendar_item(self, kind: str, item_id: str, day: date) -> None:
        if kind == "event":
            self.show_event_dialog(day, item_id)
            return
        self.selected_task_id = item_id
        self.edit_selected()

    def show_calendar_day_menu(self, event, day: date) -> None:
        menu = self.make_menu()
        menu.add_command(label=f"Add event on {day.isoformat()}", command=lambda d=day: self.show_event_dialog(d))
        menu.add_command(label=f"Add task due {day.isoformat()}", command=lambda d=day: self.quick_add_due_dialog(d))
        menu.add_command(label="Jump to today", command=self.show_current_month)
        menu.tk_popup(event.x_root, event.y_root)

    def show_calendar_item_menu(self, event, kind: str, item_id: str, day: date) -> None:
        if kind == "task":
            self.selected_task_id = item_id
            self.show_task_menu(event, item_id)
            return
        self.show_event_menu(event, item_id, day)

    def quick_add_due_dialog(self, day: date) -> None:
        self.simple_input("Add Task", f"Task due {day.isoformat()}", lambda value, d=day: self.quick_add_due(value, d))

    def quick_add_due(self, value: str, day: date) -> None:
        value = clean_text(value)
        if not value:
            return
        self.active_list()["tasks"].append(self.build_task(value, day.isoformat(), "09:00"))
        self.save_data()
        self.show_calendar()

    def show_event_menu(self, event, event_id: str, day: date) -> None:
        menu = self.make_menu()
        self.add_menu_command(menu, "Edit event", "edit", lambda eid=event_id, d=day: self.show_event_dialog(d, eid))
        self.add_menu_command(menu, "Duplicate event", "subtask", lambda eid=event_id: self.duplicate_event(eid))
        self.add_menu_command(menu, "Create task from event", "check", lambda eid=event_id: self.create_task_from_event(eid))
        repeats = self.make_menu(menu)
        for recurrence in RECURRENCE_OPTIONS:
            repeats.add_command(label=recurrence, command=lambda value=recurrence, eid=event_id: self.set_event_recurrence(eid, value))
        menu.add_cascade(label="Repeats", menu=repeats)
        menu.add_separator()
        self.add_menu_command(menu, "Delete event", "delete", lambda eid=event_id: self.delete_event(eid))
        menu.tk_popup(event.x_root, event.y_root)

    def show_event_dialog(self, event_date: date | None = None, event_id: str | None = None) -> None:
        existing = self.find_event(event_id) if event_id else None
        win = Toplevel(self.root)
        win.title("Edit Event" if existing else "Add Event")
        win.geometry("520x430")
        win.transient(self.root)
        win.grab_set()
        self.theme_popup(win)
        frame = ttk.Frame(win, padding=14)
        frame.pack(fill="both", expand=True)
        title_var = StringVar(value=existing.get("title", "") if existing else "")
        date_var = StringVar(value=existing.get("date", "") if existing else (event_date or date.today()).isoformat())
        start_var = StringVar(value=existing.get("start_time", "09:00") if existing else "09:00")
        end_var = StringVar(value=existing.get("end_time", "10:00") if existing else "10:00")
        repeat_var = StringVar(value=existing.get("recurrence", "None") if existing else "None")
        reminder_var = StringVar(value=str(existing.get("reminder_minutes", 15)) if existing else "15")

        ttk.Label(frame, text="Title").pack(anchor="w")
        ttk.Entry(frame, textvariable=title_var).pack(fill="x", pady=(0, 8))
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=(0, 8))
        for label, var, width in [("Date", date_var, 14), ("Start", start_var, 10), ("End", end_var, 10), ("Reminder", reminder_var, 8)]:
            box = ttk.Frame(row)
            box.pack(side="left", padx=(0, 8))
            ttk.Label(box, text=label).pack(anchor="w")
            ttk.Entry(box, textvariable=var, width=width).pack()
        ttk.Label(frame, text="Repeats").pack(anchor="w")
        ttk.Combobox(frame, textvariable=repeat_var, values=RECURRENCE_OPTIONS, state="readonly").pack(fill="x", pady=(0, 8))
        ttk.Label(frame, text="Notes").pack(anchor="w")
        colors = self.colors()
        notes = Text(frame, height=8, wrap="word", font=UI_FONT, bg=colors["panel"], fg=colors["text"], insertbackground=colors["text"], relief="solid", borderwidth=1)
        notes.insert("1.0", existing.get("notes", "") if existing else "")
        notes.pack(fill="both", expand=True)

        def save_event() -> None:
            title = clean_text(title_var.get())
            if not title:
                messagebox.showinfo(APP_NAME, "Enter an event title.")
                return
            if not parse_date(date_var.get()):
                messagebox.showwarning(APP_NAME, "Use a date like 2026-08-01.")
                return
            try:
                reminder = max(0, int(reminder_var.get()))
            except ValueError:
                reminder = 15
            payload = self.normalize_event(
                {
                    "id": existing.get("id") if existing else make_id("event"),
                    "title": title,
                    "date": parse_date(date_var.get()).isoformat(),
                    "start_time": start_var.get(),
                    "end_time": end_var.get(),
                    "recurrence": repeat_var.get(),
                    "reminder_minutes": reminder,
                    "notes": notes.get("1.0", "end").strip(),
                    "created_at": existing.get("created_at") if existing else app_now().isoformat(),
                    "updated_at": app_now().isoformat(),
                }
            )
            if existing:
                existing.update(payload)
            else:
                self.data.setdefault("events", []).append(payload)
            self.calendar_month = parse_date(payload["date"]).replace(day=1)
            self.save_data()
            win.destroy()
            self.show_calendar()

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=(10, 0))
        ttk.Button(buttons, text="Save Event", command=save_event).pack(side="right")
        ttk.Button(buttons, text="Cancel", command=win.destroy).pack(side="right", padx=4)

    def duplicate_event(self, event_id: str) -> None:
        event = self.find_event(event_id)
        if not event:
            return
        clone = copy.deepcopy(event)
        clone["id"] = make_id("event")
        clone["title"] = f"{clone.get('title', 'Event')} copy"
        clone["created_at"] = app_now().isoformat()
        clone["updated_at"] = app_now().isoformat()
        self.data.setdefault("events", []).append(clone)
        self.save_data()
        self.show_calendar()

    def set_event_recurrence(self, event_id: str, recurrence: str) -> None:
        event = self.find_event(event_id)
        if not event:
            return
        event["recurrence"] = recurrence
        event["updated_at"] = app_now().isoformat()
        self.save_data()
        self.show_calendar()

    def create_task_from_event(self, event_id: str) -> None:
        event = self.find_event(event_id)
        if not event:
            return
        self.active_list()["tasks"].append(self.build_task(event.get("title", "Event"), event.get("date", ""), event.get("start_time", "09:00"), event.get("recurrence", "None")))
        self.save_data()
        self.show_calendar()

    def delete_event(self, event_id: str) -> None:
        event = self.find_event(event_id)
        if not event:
            return
        if not messagebox.askyesno(APP_NAME, "Delete this calendar event?"):
            return
        self.data["events"] = [item for item in self.data.get("events", []) if item.get("id") != event_id]
        self.save_data()
        self.show_calendar()

    def show_focus(self) -> None:
        self.clear_content()
        ttk.Label(self.content, text="Focus Mode", style="Title.TLabel").pack(anchor="w", pady=(0, 10))
        layout = ttk.PanedWindow(self.content, orient="horizontal")
        layout.pack(fill="both", expand=True)
        left = self.panel(layout)
        right = self.panel(layout)
        layout.add(left, weight=3)
        layout.add(right, weight=2)

        open_refs = self.all_task_refs(include_completed=False)
        current = None
        if self.focus_task_id:
            current = self.find_task(self.focus_task_id)[0]
        if not current and open_refs:
            current = open_refs[0][0]
            self.focus_task_id = current["id"]
        if current:
            ttk.Label(left, text=current["text"], style="Panel.TLabel", font=("Segoe UI", 20, "bold"), wraplength=620).pack(anchor="w")
            details = f"{current.get('estimate', 10)} min | {current.get('energy', 'Medium')} energy | {current.get('priority', 'Normal')}"
            ttk.Label(left, text=details, style="Muted.TLabel").pack(anchor="w", pady=(4, 20))
        else:
            ttk.Label(left, text="No open tasks.", style="Panel.TLabel", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        timer_text = self.format_remaining()
        self.timer_label = ttk.Label(left, text=timer_text, style="Panel.TLabel", font=("Segoe UI", 46, "bold"))
        self.timer_label.pack(anchor="center", pady=20)
        controls = ttk.Frame(left, style="Panel.TFrame")
        controls.pack(anchor="center")
        for label, minutes in [("5", 5), ("15", 15), ("25", 25)]:
            ttk.Button(controls, text=f"{label} min", command=lambda m=minutes: self.start_focus_timer(m)).pack(side="left", padx=3)
        ttk.Button(controls, text="Pause", command=self.pause_focus_timer).pack(side="left", padx=3)
        ttk.Button(controls, text="Complete", command=self.complete_focus_task).pack(side="left", padx=3)
        ttk.Button(controls, text="Next", command=self.next_focus_task).pack(side="left", padx=3)

        ttk.Label(right, text="Distraction Capture", style="Panel.TLabel", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 8))
        colors = self.colors()
        self.distraction_text = Text(right, height=5, wrap="word", font=UI_FONT, bg=colors["panel"], fg=colors["text"], insertbackground=colors["text"], relief="solid", borderwidth=1)
        self.distraction_text.pack(fill="x")
        ttk.Button(right, text="Capture", command=self.capture_distraction).pack(anchor="e", pady=6)
        ttk.Label(right, text="Open Tasks", style="Panel.TLabel", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(12, 8))
        for task, task_list, parent in open_refs[:12]:
            label = f"{task['text']} ({task_list['name']})"
            ttk.Button(right, text=label, command=lambda tid=task["id"]: self.select_focus_task(tid)).pack(fill="x", pady=2)

    def focus_selected(self) -> None:
        task, _, _ = self.selected_task()
        if task:
            self.focus_task_id = task["id"]
            self.show_focus()

    def select_focus_task(self, task_id: str) -> None:
        self.focus_task_id = task_id
        self.focus_remaining = 0
        self.focus_running = False
        self.show_focus()

    def start_focus_timer(self, minutes: int) -> None:
        self.focus_remaining = minutes * 60
        self.focus_running = True
        self.tick_focus_timer()

    def pause_focus_timer(self) -> None:
        self.focus_running = False

    def tick_focus_timer(self) -> None:
        if not self.focus_running:
            return
        if self.focus_remaining <= 0:
            self.focus_running = False
            self.root.bell()
            messagebox.showinfo(APP_NAME, "Focus session complete.")
            return
        self.focus_remaining -= 1
        if hasattr(self, "timer_label"):
            self.timer_label.configure(text=self.format_remaining())
        self.root.after(1000, self.tick_focus_timer)

    def format_remaining(self) -> str:
        minutes, seconds = divmod(max(0, self.focus_remaining), 60)
        return f"{minutes:02d}:{seconds:02d}"

    def complete_focus_task(self) -> None:
        if not self.focus_task_id:
            return
        task, task_list, parent = self.find_task(self.focus_task_id)
        if not task:
            return
        task["completed"] = True
        if not parent:
            self.create_next_recurring(task, task_list)
        self.save_data()
        self.next_focus_task()

    def next_focus_task(self) -> None:
        open_refs = self.all_task_refs(include_completed=False)
        self.focus_task_id = open_refs[0][0]["id"] if open_refs else None
        self.show_focus()

    def capture_distraction(self) -> None:
        text = self.distraction_text.get("1.0", "end").strip()
        if not text:
            return
        self.data.setdefault("distractions", []).append({"text": text, "created_at": app_now().isoformat()})
        self.distraction_text.delete("1.0", "end")
        self.save_data()

    def show_templates(self) -> None:
        self.clear_content()
        ttk.Label(self.content, text="Templates", style="Title.TLabel").pack(anchor="w", pady=(0, 10))
        layout = ttk.PanedWindow(self.content, orient="horizontal")
        layout.pack(fill="both", expand=True)
        left = self.panel(layout)
        right = self.panel(layout)
        layout.add(left, weight=1)
        layout.add(right, weight=2)
        self.template_list = ttk.Treeview(left, columns=("count",), show="tree headings")
        self.template_list.heading("#0", text="Template")
        self.template_list.heading("count", text="Tasks")
        self.template_list.column("#0", width=240)
        self.template_list.column("count", width=70)
        self.template_list.pack(fill="both", expand=True)
        for index, template in enumerate(self.data.get("templates", [])):
            self.template_list.insert("", "end", iid=str(index), text=template["name"], values=(len(template["tasks"]),))
        self.template_list.bind("<<TreeviewSelect>>", lambda _event: self.show_template_preview(right))
        buttons = ttk.Frame(left, style="Panel.TFrame")
        buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(buttons, text="Apply", command=self.apply_template).pack(side="left")
        ttk.Button(buttons, text="Save Current List", command=self.save_template_from_list).pack(side="left", padx=4)
        ttk.Label(right, text="Select a template.", style="Panel.TLabel").pack(anchor="w")

    def show_template_preview(self, parent) -> None:
        for child in parent.winfo_children():
            child.destroy()
        index = self.selected_template_index()
        if index is None:
            return
        template = self.data["templates"][index]
        ttk.Label(parent, text=template["name"], style="Panel.TLabel", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 8))
        for task in template.get("tasks", []):
            ttk.Label(parent, text=f"- {task}", style="Panel.TLabel", wraplength=600).pack(anchor="w", pady=2)

    def selected_template_index(self) -> int | None:
        selected = self.template_list.selection() if hasattr(self, "template_list") else ()
        if not selected:
            return None
        try:
            return int(selected[0])
        except ValueError:
            return None

    def apply_template(self) -> None:
        index = self.selected_template_index()
        if index is None:
            return
        template = self.data["templates"][index]
        new_list = {"id": make_id("list"), "name": template["name"], "tasks": [self.build_task(text) for text in template.get("tasks", [])]}
        self.data["lists"].append(new_list)
        self.active_list_id = new_list["id"]
        self.save_data()
        self.show_tasks()

    def save_template_from_list(self) -> None:
        current = self.active_list()
        tasks = [task["text"] for task in current.get("tasks", [])]
        if not tasks:
            messagebox.showinfo(APP_NAME, "The current list has no tasks.")
            return
        self.data.setdefault("templates", []).append({"name": f"{current['name']} Template", "tasks": tasks})
        self.save_data()
        self.show_templates()

    def show_help(self) -> None:
        self.clear_content()
        ttk.Label(self.content, text="Help", style="Title.TLabel").pack(anchor="w", pady=(0, 10))
        layout = ttk.PanedWindow(self.content, orient="horizontal")
        layout.pack(fill="both", expand=True)
        left = self.panel(layout)
        right = self.panel(layout)
        layout.add(left, weight=3)
        layout.add(right, weight=2)

        ttk.Label(left, text="Quick Start", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        steps = [
            "Type one messy task into Add new item.",
            "Use Spiciness level to choose how many steps you want.",
            "Add a due date, time, or repeat if the task needs one.",
            "Press Add. The planner rewrites the task and adds helpful notes.",
            "Use Steps for a breakdown, Edit for details, Add for subtasks, and Del to remove.",
            "Right-click any task for more tools like simplify, duplicate, move, focus, and estimate.",
        ]
        for index, text in enumerate(steps, start=1):
            row = ttk.Frame(left, style="Panel.TFrame")
            row.pack(fill="x", pady=3)
            ttk.Label(row, text=f"{index}.", style="Panel.TLabel", font=UI_FONT_BOLD, width=3).pack(side="left", anchor="n")
            ttk.Label(row, text=text, style="Panel.TLabel", wraplength=620).pack(side="left", fill="x", expand=True)

        ttk.Label(left, text="Reading Tips", style="Section.TLabel").pack(anchor="w", pady=(16, 8))
        tips = [
            "Use Search to narrow a long list.",
            "Turn off Show completed when finished tasks are distracting.",
            "Use the Theme picker on the task page for instant color changes.",
            "Try Focus when you want the app to show only one next task.",
        ]
        for tip in tips:
            ttk.Label(left, text=f"- {tip}", style="Panel.TLabel", wraplength=650).pack(anchor="w", pady=2)

        ttk.Label(right, text="Keyboard Shortcuts", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        shortcuts = [
            ("Ctrl+K", "Quick add a task"),
            ("Ctrl+T", "Open Tasks"),
            ("Ctrl+D", "Open Dashboard"),
            ("Ctrl+M", "Open Calendar"),
            ("F1", "Open Help"),
            ("Enter", "Add from the main task box"),
            ("Double-click task", "Edit selected task"),
            ("Right-click task", "Open task tools"),
        ]
        for keys, action in shortcuts:
            row = ttk.Frame(right, style="Panel.TFrame")
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=keys, style="Panel.TLabel", font=UI_FONT_BOLD, width=16).pack(side="left")
            ttk.Label(row, text=action, style="Muted.TLabel", wraplength=320).pack(side="left", fill="x", expand=True)

        ttk.Label(right, text="Good Starter Tasks", style="Section.TLabel").pack(anchor="w", pady=(18, 8))
        examples = ["clean kitchen", "send project update", "prepare appointment", "organize paperwork"]
        for example in examples:
            ttk.Button(right, text=example, command=lambda value=example: self.quick_add(value)).pack(fill="x", pady=3)

    def show_settings(self) -> None:
        self.clear_content()
        self.pending_settings = copy.deepcopy(self.data["settings"])
        ttk.Label(self.content, text="Settings", style="Title.TLabel").pack(anchor="w", pady=(0, 10))
        panel = self.panel(self.content)
        panel.pack(fill="x")
        theme_var = StringVar(value=self.data["settings"].get("theme", DEFAULT_SETTINGS["theme"]))
        compact_var = StringVar(value=str(self.data["settings"].get("compact_rows", False)))
        plain_var = StringVar(value=str(self.data["settings"].get("plain_background", False)))
        ttk.Label(panel, text="Theme", style="Section.TLabel").pack(anchor="w")
        ttk.Label(panel, text="Themes preview right away. Save keeps the change; Cancel restores the old look.", style="Muted.TLabel").pack(anchor="w", pady=(2, 8))
        theme_grid = ttk.Frame(panel, style="Panel.TFrame")
        theme_grid.pack(fill="x", pady=(4, 12))
        for idx, name in enumerate(THEMES.keys()):
            option = ttk.Frame(theme_grid, style="Panel.TFrame", padding=(0, 4))
            option.grid(row=idx // 2, column=idx % 2, sticky="ew", padx=8, pady=4)
            ttk.Radiobutton(option, text=name, value=name, variable=theme_var, command=lambda: self.preview_theme(theme_var.get())).pack(anchor="w")
            ttk.Label(option, text=THEMES[name]["description"], style="Muted.TLabel", wraplength=390).pack(anchor="w", padx=(22, 0))
            theme_grid.columnconfigure(idx % 2, weight=1)
        ttk.Label(panel, text="Reading Comfort", style="Section.TLabel").pack(anchor="w")
        for label, var, key in [
            ("Smaller task rows", compact_var, "compact_rows"),
            ("Plain background", plain_var, "plain_background"),
        ]:
            ttk.Checkbutton(panel, text=label, variable=var, onvalue="True", offvalue="False", command=lambda k=key, v=var: self.preview_setting(k, v.get() == "True")).pack(anchor="w", pady=2)
        buttons = ttk.Frame(panel, style="Panel.TFrame")
        buttons.pack(fill="x", pady=(14, 0))
        ttk.Button(buttons, text="Save Settings", command=self.save_settings).pack(side="right")
        ttk.Button(buttons, text="Cancel", command=self.cancel_settings).pack(side="right", padx=4)
        self.root.bind("<Escape>", lambda _event: self.cancel_settings())

    def preview_theme(self, name: str) -> None:
        self.apply_theme(name)

    def preview_setting(self, key: str, value: bool) -> None:
        self.data["settings"][key] = value
        self.apply_theme(self.data["settings"].get("theme", DEFAULT_SETTINGS["theme"]))

    def save_settings(self) -> None:
        self.save_data()
        self.show_dashboard()

    def cancel_settings(self) -> None:
        self.data["settings"] = copy.deepcopy(self.pending_settings)
        self.apply_theme(self.data["settings"].get("theme", DEFAULT_SETTINGS["theme"]))
        self.show_dashboard()

    def check_reminders(self) -> None:
        now = app_now()
        for task, task_list, _ in self.all_task_refs(include_completed=False):
            due_dt = parse_datetime(task.get("due_date"), task.get("due_time"))
            if not due_dt:
                continue
            reminder = int(task.get("reminder_minutes", 15))
            alert_at = due_dt - timedelta(minutes=reminder)
            key = f"{task['id']}:{task.get('due_date')}:{task.get('due_time')}"
            if key in self.reminder_seen:
                continue
            if alert_at <= now <= due_dt + timedelta(hours=12):
                self.reminder_seen.add(key)
                self.show_reminder(task, task_list, due_dt)
        for event in self.data.get("events", []):
            event_day = now.date() if event_occurs_on(event, now.date()) else parse_date(event.get("date"))
            event_dt = parse_datetime(event_day.isoformat() if event_day else "", event.get("start_time"))
            if not event_dt:
                continue
            reminder = int(event.get("reminder_minutes", 15))
            alert_at = event_dt - timedelta(minutes=reminder)
            key = f"event:{event['id']}:{event_day}:{event.get('start_time')}"
            if key in self.reminder_seen:
                continue
            if alert_at <= now <= event_dt + timedelta(hours=12):
                self.reminder_seen.add(key)
                self.show_event_reminder(event, event_dt)
        self.root.after(30000, self.check_reminders)

    def show_reminder(self, task: dict, task_list: dict, due_dt: datetime) -> None:
        self.root.bell()
        win = Toplevel(self.root)
        win.title("Reminder")
        win.geometry("420x180")
        win.attributes("-topmost", True)
        self.theme_popup(win)
        frame = ttk.Frame(win, padding=14)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Reminder", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(frame, text=task["text"], wraplength=380).pack(anchor="w", pady=8)
        ttk.Label(frame, text=f"{task_list['name']} | {due_dt.strftime('%Y-%m-%d %I:%M %p').replace(' 0', ' ')}").pack(anchor="w")
        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=(12, 0))
        ttk.Button(buttons, text="Open", command=lambda: (win.destroy(), self.root.deiconify(), self.select_focus_task(task["id"]))).pack(side="right")
        ttk.Button(buttons, text="Dismiss", command=win.destroy).pack(side="right", padx=4)

    def show_event_reminder(self, event: dict, event_dt: datetime) -> None:
        self.root.bell()
        win = Toplevel(self.root)
        win.title("Event Reminder")
        win.geometry("430x190")
        win.attributes("-topmost", True)
        self.theme_popup(win)
        frame = ttk.Frame(win, padding=14)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Event Reminder", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(frame, text=event["title"], wraplength=390).pack(anchor="w", pady=8)
        ttk.Label(frame, text=f"{event_dt.strftime('%Y-%m-%d %I:%M %p').replace(' 0', ' ')} | {event.get('recurrence', 'None')}").pack(anchor="w")
        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=(12, 0))
        ttk.Button(buttons, text="Open Calendar", command=lambda: (win.destroy(), self.root.deiconify(), self.show_calendar())).pack(side="right")
        ttk.Button(buttons, text="Dismiss", command=win.destroy).pack(side="right", padx=4)

    def setup_tray(self) -> None:
        try:
            import pystray
            from PIL import Image, ImageDraw
        except Exception:
            return
        if ICON_PNG.exists():
            image = Image.open(ICON_PNG).resize((64, 64))
        else:
            image = Image.new("RGB", (64, 64), "#6c5ce7")
            draw = ImageDraw.Draw(image)
            draw.rounded_rectangle((8, 8, 56, 56), radius=12, fill="#ffffff")
            draw.rounded_rectangle((16, 18, 48, 26), radius=4, fill="#ff3d95")
            draw.rounded_rectangle((16, 30, 48, 38), radius=4, fill="#ffca3a")
            draw.rounded_rectangle((16, 42, 48, 50), radius=4, fill="#22cfc0")

        def open_window(_icon=None, _item=None) -> None:
            self.root.after(0, self.show_window)

        def open_focus(_icon=None, _item=None) -> None:
            self.root.after(0, lambda: (self.show_window(), self.show_focus()))

        def quit_app(_icon=None, _item=None) -> None:
            self.root.after(0, self.quit_app)

        menu = pystray.Menu(
            pystray.MenuItem("Open", open_window),
            pystray.MenuItem("Focus Mode", open_focus),
            pystray.MenuItem("Exit", quit_app),
        )
        self.tray_icon = pystray.Icon("Rice2kMagicTasks", image, APP_NAME, menu)
        thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        thread.start()

    def hide_to_tray(self) -> None:
        if self.tray_icon:
            self.root.withdraw()
        else:
            self.quit_app()

    def show_window(self) -> None:
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def quit_app(self) -> None:
        self.save_data()
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        self.root.destroy()


def main() -> int:
    app = MagicTasksApp()
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
