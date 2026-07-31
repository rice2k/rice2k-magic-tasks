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
from tkinter import Menu, StringVar, Text, Tk, Toplevel, messagebox
from tkinter import ttk

APP_NAME = "Rice2k Magic Tasks"
VERSION = "2.2.0"
APP_DIR = Path(os.getenv("APPDATA", Path.home())) / "Rice2kMagicTasks"
DATA_FILE = APP_DIR / "tasks.json"


THEMES = {
    "Light": {
        "bg": "#f6f7fb",
        "panel": "#ffffff",
        "panel2": "#edf0f7",
        "text": "#1b1f2a",
        "muted": "#5f6878",
        "accent": "#3366ff",
        "accent2": "#e6ecff",
        "danger": "#bf2f45",
        "done": "#1d8f62",
    },
    "Dark": {
        "bg": "#141821",
        "panel": "#1d2330",
        "panel2": "#262e3f",
        "text": "#f3f6fb",
        "muted": "#aeb8c8",
        "accent": "#79a7ff",
        "accent2": "#223453",
        "danger": "#ff6b83",
        "done": "#70e0a3",
    },
    "Low Stimulation": {
        "bg": "#f2f3ef",
        "panel": "#fbfbf7",
        "panel2": "#e5e8df",
        "text": "#252820",
        "muted": "#687060",
        "accent": "#5d7561",
        "accent2": "#e1e8dc",
        "danger": "#9a4d4d",
        "done": "#4c7d55",
    },
    "Focus Contrast": {
        "bg": "#101215",
        "panel": "#f7f7f2",
        "panel2": "#deded7",
        "text": "#111318",
        "muted": "#333942",
        "accent": "#005fcc",
        "accent2": "#cfe2ff",
        "danger": "#a8182f",
        "done": "#006f45",
    },
    "Soft Pastel": {
        "bg": "#f7f1f5",
        "panel": "#fffafb",
        "panel2": "#efe4ee",
        "text": "#30252f",
        "muted": "#7a6778",
        "accent": "#7d6bc7",
        "accent2": "#ece8ff",
        "danger": "#bc536d",
        "done": "#4e936b",
    },
    "Black & Green": {
        "bg": "#020603",
        "panel": "#071208",
        "panel2": "#0e2713",
        "text": "#e7ffe7",
        "muted": "#91be91",
        "accent": "#18ff65",
        "accent2": "#123e1d",
        "danger": "#ff5d73",
        "done": "#35f482",
    },
    "Clean Blue": {
        "bg": "#eef5f8",
        "panel": "#ffffff",
        "panel2": "#dbe9ee",
        "text": "#17272e",
        "muted": "#58707a",
        "accent": "#06758f",
        "accent2": "#d8f2f8",
        "danger": "#b83a52",
        "done": "#277b59",
    },
}

DEFAULT_SETTINGS = {
    "theme": "Light",
    "compact_rows": False,
    "reduced_motion": False,
    "plain_background": False,
}

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
    }


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


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
        "Home": ["clean", "laundry", "dish", "kitchen", "room", "trash", "house"],
        "Work": ["email", "report", "meeting", "client", "project", "code", "invoice"],
        "Health": ["doctor", "medicine", "exercise", "walk", "sleep", "appointment"],
        "Errands": ["buy", "store", "pickup", "call", "mail", "bank", "shop"],
        "Admin": ["form", "file", "paper", "budget", "tax", "bill", "account"],
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
        if any(word in lower for word in ["call", "meeting", "doctor", "deadline", "deep"]):
            return "High"
        if any(word in lower for word in ["read", "sort", "check", "list", "collect"]):
            return "Low"
        return "Medium"

    @classmethod
    def estimate(cls, text: str, spice: int = 3) -> int:
        words = max(3, len(text.split()))
        base = 10 + words * 2
        if any(word in text.lower() for word in ["project", "house", "report", "tax", "plan"]):
            base += 20
        return min(240, max(5, base + (spice - 3) * 10))

    @classmethod
    def priority(cls, text: str, due_date: str | None = None) -> str:
        lower = text.lower()
        due = parse_date(due_date)
        if any(word in lower for word in ["urgent", "asap", "deadline", "today"]):
            return "High"
        if due and due <= date.today() + timedelta(days=1):
            return "High"
        if due and due <= date.today() + timedelta(days=7):
            return "Medium"
        return "Normal"

    @classmethod
    def rewrite(cls, text: str) -> str:
        text = clean_text(text)
        if not text:
            return text
        lower = text.lower()
        replacements = [
            ("clean house", "Reset the house one small area at a time"),
            ("clean room", "Clear and reset the room one surface at a time"),
            ("do laundry", "Run one complete laundry cycle"),
            ("work on project", "Move the project forward with one finished step"),
            ("get organized", "Sort the loose items into keep, move, and trash piles"),
            ("emails", "Clear the most important email actions"),
            ("make appointment", "Schedule the appointment and save the details"),
        ]
        for needle, replacement in replacements:
            if needle in lower:
                return replacement
        if lower.startswith(cls.starters):
            return text[0].upper() + text[1:]
        return f"Start: {text[0].lower() + text[1:]}"

    @classmethod
    def breakdown(cls, text: str, spice: int = 3) -> list[str]:
        text = clean_text(text)
        lower = text.lower()
        category = cls.categorize(text)
        first = cls.rewrite(text)
        general = [
            f"Define what done means for: {text}",
            "Gather anything needed",
            "Do the smallest first action",
            "Check what remains",
            "Finish, save, or clean up",
        ]
        if category == "Home":
            general = [
                "Pick one visible area",
                "Remove trash and obvious clutter",
                "Group items by where they belong",
                "Put away the easiest group",
                "Wipe or reset the main surface",
                "Stop when the chosen area is usable",
            ]
        elif category == "Work":
            general = [
                "Open the relevant files or notes",
                "Write the exact outcome needed",
                "List missing information",
                "Complete the first deliverable chunk",
                "Review for one obvious problem",
                "Send or save the update",
            ]
        elif category == "Health":
            general = [
                "Confirm the health-related goal",
                "Gather medicine, paperwork, or supplies",
                "Set a reminder or travel time",
                "Do the next physical action",
                "Record what was done",
            ]
        elif category == "Errands":
            general = [
                "Confirm the item or place",
                "Check hours, address, or phone number",
                "Prepare payment, bag, or documents",
                "Complete the errand",
                "Put away or record the result",
            ]
        if "email" in lower:
            general = [
                "Open the inbox",
                "Search for the important thread",
                "Decide: reply, archive, schedule, or task",
                "Write the shortest useful response",
                "Send or save the draft",
            ]
        steps = [first] + general
        count = min(len(steps), max(3, spice + 3))
        return steps[:count]

    @classmethod
    def preview(cls, text: str, due_date: str | None, spice: int) -> dict:
        return {
            "rewrite": cls.rewrite(text),
            "category": cls.categorize(text),
            "energy": cls.energy(text),
            "estimate": cls.estimate(text, spice),
            "priority": cls.priority(text, due_date),
            "steps": cls.breakdown(text, spice),
        }


class MagicTasksApp:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("1180x760")
        self.root.minsize(980, 620)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

        self.data = self.load_data()
        self.active_list_id = self.data["lists"][0]["id"]
        self.current_view = "Dashboard"
        self.tree_item_map: dict[str, str] = {}
        self.reminder_seen: set[str] = set()
        self.focus_task_id: str | None = None
        self.focus_remaining = 0
        self.focus_running = False
        self.calendar_month = date.today().replace(day=1)
        self.tray_icon = None
        self.pending_settings = copy.deepcopy(self.data["settings"])

        self.configure_style()
        self.build_shell()
        self.apply_theme(self.data["settings"]["theme"])
        self.show_dashboard()
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
        if not data.get("lists"):
            data["lists"] = default_data()["lists"]
        for key, value in DEFAULT_SETTINGS.items():
            data["settings"].setdefault(key, value)
        return data

    def save_payload(self, payload: dict) -> None:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def save_data(self) -> None:
        self.data["version"] = VERSION
        self.save_payload(self.data)

    def configure_style(self) -> None:
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

    def colors(self) -> dict:
        return THEMES.get(self.data["settings"].get("theme", "Light"), THEMES["Light"])

    def apply_theme(self, theme_name: str) -> None:
        self.data["settings"]["theme"] = theme_name
        colors = self.colors()
        row_height = 24 if self.data["settings"].get("compact_rows") else 32
        self.root.configure(bg=colors["bg"])
        self.style.configure(".", background=colors["bg"], foreground=colors["text"], fieldbackground=colors["panel"])
        self.style.configure("TFrame", background=colors["bg"])
        self.style.configure("Panel.TFrame", background=colors["panel"])
        self.style.configure("TLabel", background=colors["bg"], foreground=colors["text"])
        self.style.configure("Panel.TLabel", background=colors["panel"], foreground=colors["text"])
        self.style.configure("Muted.TLabel", background=colors["panel"], foreground=colors["muted"])
        self.style.configure("Title.TLabel", background=colors["bg"], foreground=colors["text"], font=("Segoe UI", 18, "bold"))
        self.style.configure("Accent.TButton", background=colors["accent"], foreground=colors["text"])
        self.style.configure("TButton", padding=6)
        self.style.map("TButton", background=[("active", colors["accent2"])])
        self.style.configure("TEntry", fieldbackground=colors["panel"], foreground=colors["text"])
        self.style.configure("TCombobox", fieldbackground=colors["panel"], foreground=colors["text"])
        self.style.configure("Treeview", rowheight=row_height, fieldbackground=colors["panel"], background=colors["panel"], foreground=colors["text"])
        self.style.configure("Treeview.Heading", background=colors["panel2"], foreground=colors["text"], font=("Segoe UI", 10, "bold"))
        self.style.map("Treeview", background=[("selected", colors["accent2"])], foreground=[("selected", colors["text"])])

    def build_shell(self) -> None:
        self.shell = ttk.Frame(self.root, padding=14)
        self.shell.pack(fill="both", expand=True)
        self.header = ttk.Frame(self.shell)
        self.header.pack(fill="x", pady=(0, 10))
        ttk.Label(self.header, text=APP_NAME, style="Title.TLabel").pack(side="left")
        self.nav = ttk.Frame(self.header)
        self.nav.pack(side="right")
        for name in ["Dashboard", "Tasks", "Calendar", "Focus", "Templates", "Settings"]:
            ttk.Button(self.nav, text=name, command=lambda n=name: self.route(n)).pack(side="left", padx=3)
        self.content = ttk.Frame(self.shell)
        self.content.pack(fill="both", expand=True)

    def clear_content(self) -> None:
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
        }[name]()

    def panel(self, parent, padding: int = 12):
        frame = ttk.Frame(parent, style="Panel.TFrame", padding=padding)
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
        return {
            "id": make_id("task"),
            "text": plan["rewrite"],
            "original_text": clean_text(text),
            "notes": "",
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
        ttk.Button(top, text="Quick Add", command=self.quick_add_dialog).pack(side="right")

        stats = ttk.Frame(self.content)
        stats.pack(fill="x", pady=10)
        for label, value in [
            ("Open", len(open_tasks)),
            ("Done", len(done_tasks)),
            ("Due Today", len(due_today)),
            ("Overdue", len(overdue)),
            ("Lists", len(self.data["lists"])),
        ]:
            card = self.panel(stats)
            card.pack(side="left", fill="x", expand=True, padx=4)
            ttk.Label(card, text=str(value), style="Panel.TLabel", font=("Segoe UI", 20, "bold")).pack(anchor="w")
            ttk.Label(card, text=label, style="Muted.TLabel").pack(anchor="w")

        body = ttk.PanedWindow(self.content, orient="horizontal")
        body.pack(fill="both", expand=True, pady=(4, 0))
        left = self.panel(body)
        right = self.panel(body)
        body.add(left, weight=3)
        body.add(right, weight=2)

        ttk.Label(left, text="Needs Attention", style="Panel.TLabel", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 8))
        tree = ttk.Treeview(left, columns=("list", "due", "priority"), show="tree headings")
        tree.heading("#0", text="Task")
        tree.column("#0", width=330, anchor="w")
        for col, width in [("list", 160), ("due", 160), ("priority", 80)]:
            tree.heading(col, text=col.title())
            tree.column(col, width=width, anchor="w")
        tree.pack(fill="both", expand=True)
        for task, task_list, _ in overdue + due_today + upcoming:
            prefix = "!" if parse_date(task.get("due_date")) and parse_date(task.get("due_date")) < today else ""
            tree.insert("", "end", text=task["text"], values=(task_list["name"], f"{prefix}{due_label(task)}", task["priority"]))

        ttk.Label(right, text="Next Actions", style="Panel.TLabel", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 8))
        next_box = ttk.Frame(right, style="Panel.TFrame")
        next_box.pack(fill="both", expand=True)
        for task, task_list, parent in open_tasks[:8]:
            row = ttk.Frame(next_box, style="Panel.TFrame")
            row.pack(fill="x", pady=3)
            mark = "Subtask" if parent else task_list["name"]
            ttk.Label(row, text=task["text"], style="Panel.TLabel", wraplength=360).pack(anchor="w")
            ttk.Label(row, text=f"{mark} | {task.get('estimate', 10)} min | {task.get('energy', 'Medium')} energy", style="Muted.TLabel").pack(anchor="w")
        if not open_tasks:
            ttk.Label(next_box, text="Everything is complete.", style="Panel.TLabel").pack(anchor="w")
        self.content.configure(style="TFrame")
        self.root.configure(bg=colors["bg"])

    def show_tasks(self) -> None:
        self.clear_content()
        top = ttk.Frame(self.content)
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(top, text="Tasks", style="Title.TLabel").pack(side="left")
        ttk.Label(top, text="List:").pack(side="left", padx=(20, 4))
        list_names = [item["name"] for item in self.data["lists"]]
        self.list_var = StringVar(value=self.active_list()["name"])
        selector = ttk.Combobox(top, textvariable=self.list_var, values=list_names, state="readonly", width=24)
        selector.pack(side="left")
        selector.bind("<<ComboboxSelected>>", self.on_list_selected)
        ttk.Button(top, text="New List", command=self.new_list_dialog).pack(side="left", padx=4)
        ttk.Button(top, text="Rename", command=self.rename_list_dialog).pack(side="left", padx=4)

        add_panel = self.panel(self.content)
        add_panel.pack(fill="x", pady=(0, 8))
        self.task_text = StringVar()
        self.due_date = StringVar()
        self.due_time = StringVar(value="09:00")
        self.recurrence = StringVar(value="None")
        ttk.Label(add_panel, text="Task", style="Panel.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(add_panel, textvariable=self.task_text, width=42).grid(row=1, column=0, sticky="ew", padx=(0, 8))
        ttk.Label(add_panel, text="Due Date", style="Panel.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Entry(add_panel, textvariable=self.due_date, width=14).grid(row=1, column=1, sticky="ew", padx=(0, 8))
        ttk.Label(add_panel, text="Time", style="Panel.TLabel").grid(row=0, column=2, sticky="w")
        ttk.Entry(add_panel, textvariable=self.due_time, width=10).grid(row=1, column=2, sticky="ew", padx=(0, 8))
        ttk.Label(add_panel, text="Repeats", style="Panel.TLabel").grid(row=0, column=3, sticky="w")
        ttk.Combobox(add_panel, textvariable=self.recurrence, values=RECURRENCE_OPTIONS, state="readonly", width=12).grid(row=1, column=3, sticky="ew", padx=(0, 8))
        ttk.Label(add_panel, text="Spice", style="Panel.TLabel").grid(row=0, column=4, sticky="w")
        self.spice = ttk.Scale(add_panel, from_=1, to=5, orient="horizontal", length=110)
        self.spice.set(3)
        self.spice.grid(row=1, column=4, sticky="ew", padx=(0, 8))
        ttk.Button(add_panel, text="Add", command=self.add_task).grid(row=1, column=5, sticky="ew")
        add_panel.columnconfigure(0, weight=1)

        toolbar = ttk.Frame(self.content)
        toolbar.pack(fill="x", pady=(0, 8))
        for label, command in [
            ("Complete", self.toggle_selected_complete),
            ("Rewrite", self.rewrite_selected),
            ("Break Down", self.breakdown_selected),
            ("Move Up", lambda: self.move_selected(-1)),
            ("Move Down", lambda: self.move_selected(1)),
            ("Delete", self.delete_selected),
        ]:
            ttk.Button(toolbar, text=label, command=command).pack(side="left", padx=3)

        self.tree = ttk.Treeview(
            self.content,
            columns=("status", "due", "priority", "estimate", "category", "repeat"),
            show="tree headings",
            selectmode="browse",
        )
        self.tree.heading("#0", text="Task")
        self.tree.column("#0", width=430, anchor="w")
        for col, title, width in [
            ("status", "Status", 90),
            ("due", "Due", 160),
            ("priority", "Priority", 90),
            ("estimate", "Estimate", 90),
            ("category", "Category", 100),
            ("repeat", "Repeats", 90),
        ]:
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda event: self.edit_selected())
        self.tree.bind("<Button-3>", self.show_task_menu)
        self.populate_task_tree()

    def populate_task_tree(self) -> None:
        self.tree_item_map = {}
        for item in self.tree.get_children():
            self.tree.delete(item)
        for task in self.active_list().get("tasks", []):
            iid = self.tree.insert("", "end", text=task["text"], values=self.task_values(task), open=True)
            self.tree_item_map[iid] = task["id"]
            for subtask in task.get("subtasks", []):
                sid = self.tree.insert(iid, "end", text=subtask["text"], values=self.task_values(subtask), open=True)
                self.tree_item_map[sid] = subtask["id"]

    def task_values(self, task: dict) -> tuple:
        return (
            "Done" if task.get("completed") else "Open",
            due_label(task),
            task.get("priority", "Normal"),
            f"{task.get('estimate', 10)} min",
            task.get("category", "General"),
            task.get("recurrence", "None"),
        )

    def on_list_selected(self, _event=None) -> None:
        selected = self.list_var.get()
        for task_list in self.data["lists"]:
            if task_list["name"] == selected:
                self.active_list_id = task_list["id"]
                break
        self.show_tasks()

    def add_task(self) -> None:
        text = clean_text(self.task_text.get())
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

    def selected_task(self) -> tuple[dict | None, dict | None, dict | None]:
        selected = self.tree.selection() if hasattr(self, "tree") else ()
        if not selected:
            return None, None, None
        task_id = self.tree_item_map.get(selected[0])
        if not task_id:
            return None, None, None
        return self.find_task(task_id)

    def show_task_menu(self, event) -> None:
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
        menu = Menu(self.root, tearoff=False)
        for label, command in [
            ("Edit", self.edit_selected),
            ("Duplicate", self.duplicate_selected),
            ("Add Subtask", self.add_subtask_dialog),
            ("Smart Rewrite", self.rewrite_selected),
            ("Break Down", self.breakdown_selected),
            ("Start Focus", self.focus_selected),
            ("Complete", self.toggle_selected_complete),
            ("Delete", self.delete_selected),
        ]:
            menu.add_command(label=label, command=command)
        menu.tk_popup(event.x_root, event.y_root)

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
        task["text"] = SmartPlanner.rewrite(task.get("original_text") or task["text"])
        task["notes"] = f"Previous wording: {previous}\n{task.get('notes', '')}".strip()
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
        notes = Text(frame, height=8, wrap="word")
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
        ttk.Button(top, text="Previous", command=lambda: self.change_month(-1)).pack(side="right", padx=3)
        ttk.Button(top, text="Next", command=lambda: self.change_month(1)).pack(side="right", padx=3)
        ttk.Label(top, text=self.calendar_month.strftime("%B %Y"), font=("Segoe UI", 13, "bold")).pack(side="right", padx=16)

        month = calendar.Calendar(firstweekday=6)
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
        for row_idx, week in enumerate(month.monthdatescalendar(self.calendar_month.year, self.calendar_month.month), start=1):
            grid.rowconfigure(row_idx, weight=1)
            for col_idx, day in enumerate(week):
                cell = self.panel(grid, padding=8)
                cell.grid(row=row_idx, column=col_idx, sticky="nsew", padx=2, pady=2)
                label_style = "Panel.TLabel"
                day_text = str(day.day)
                if day.month != self.calendar_month.month:
                    day_text = f"({day.day})"
                ttk.Label(cell, text=day_text, style=label_style, font=("Segoe UI", 10, "bold")).pack(anchor="w")
                for task in tasks_by_day.get(day, [])[:4]:
                    ttk.Label(cell, text=task["text"], style="Muted.TLabel", wraplength=130).pack(anchor="w")
                extra = len(tasks_by_day.get(day, [])) - 4
                if extra > 0:
                    ttk.Label(cell, text=f"+{extra} more", style="Muted.TLabel").pack(anchor="w")

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
        self.distraction_text = Text(right, height=5, wrap="word")
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

    def show_settings(self) -> None:
        self.clear_content()
        self.pending_settings = copy.deepcopy(self.data["settings"])
        ttk.Label(self.content, text="Settings", style="Title.TLabel").pack(anchor="w", pady=(0, 10))
        panel = self.panel(self.content)
        panel.pack(fill="x")
        theme_var = StringVar(value=self.data["settings"].get("theme", "Light"))
        compact_var = StringVar(value=str(self.data["settings"].get("compact_rows", False)))
        motion_var = StringVar(value=str(self.data["settings"].get("reduced_motion", False)))
        plain_var = StringVar(value=str(self.data["settings"].get("plain_background", False)))
        ttk.Label(panel, text="Theme", style="Panel.TLabel", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        theme_grid = ttk.Frame(panel, style="Panel.TFrame")
        theme_grid.pack(fill="x", pady=(4, 12))
        for idx, name in enumerate(THEMES.keys()):
            ttk.Radiobutton(theme_grid, text=name, value=name, variable=theme_var, command=lambda: self.preview_theme(theme_var.get())).grid(row=idx // 3, column=idx % 3, sticky="w", padx=8, pady=4)
        ttk.Label(panel, text="Display", style="Panel.TLabel", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        for label, var, key in [
            ("Compact rows", compact_var, "compact_rows"),
            ("Reduced motion", motion_var, "reduced_motion"),
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
        self.apply_theme(self.data["settings"].get("theme", "Light"))

    def save_settings(self) -> None:
        self.save_data()
        self.show_dashboard()

    def cancel_settings(self) -> None:
        self.data["settings"] = copy.deepcopy(self.pending_settings)
        self.apply_theme(self.data["settings"].get("theme", "Light"))
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
        self.root.after(30000, self.check_reminders)

    def show_reminder(self, task: dict, task_list: dict, due_dt: datetime) -> None:
        self.root.bell()
        win = Toplevel(self.root)
        win.title("Reminder")
        win.geometry("420x180")
        win.attributes("-topmost", True)
        frame = ttk.Frame(win, padding=14)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Reminder", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(frame, text=task["text"], wraplength=380).pack(anchor="w", pady=8)
        ttk.Label(frame, text=f"{task_list['name']} | {due_dt.strftime('%Y-%m-%d %I:%M %p').replace(' 0', ' ')}").pack(anchor="w")
        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=(12, 0))
        ttk.Button(buttons, text="Open", command=lambda: (win.destroy(), self.root.deiconify(), self.select_focus_task(task["id"]))).pack(side="right")
        ttk.Button(buttons, text="Dismiss", command=win.destroy).pack(side="right", padx=4)

    def setup_tray(self) -> None:
        try:
            import pystray
            from PIL import Image, ImageDraw
        except Exception:
            return
        image = Image.new("RGB", (64, 64), "#071208")
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((8, 8, 56, 56), radius=12, fill="#18ff65")
        draw.rectangle((18, 20, 46, 26), fill="#071208")
        draw.rectangle((18, 32, 40, 38), fill="#071208")
        draw.rectangle((18, 44, 34, 50), fill="#071208")

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
