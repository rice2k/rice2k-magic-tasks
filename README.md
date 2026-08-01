# Rice2k Magic Tasks

Rice2k Magic Tasks is a Windows-first task planner for turning rough ideas into smaller, calmer next actions. It runs locally, saves your lists on your computer, and includes smart planning tools for due dates, recurring tasks, reminders, focus sessions, templates, calendar views, and low-distraction themes.

![Version](https://img.shields.io/badge/version-2.6.0-3366ee)
![Platform](https://img.shields.io/badge/platform-Windows-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Download

Get the latest Windows build from the [Releases](../../releases) page.

The v2.6.0 release includes:

- `Rice2k-Magic-Tasks-v2.6.0.exe` - single-file Windows app
- `Rice2k-Magic-Tasks-v2.6.0.zip` - release package
- `Rice2k-Magic-Tasks-v2.6.0.sha256` - checksum file
- `Rice2k-Magic-Tasks-Source-v2.6.0.zip` - source archive

## Features

### Smart planning

- Rewrites vague tasks into clearer action wording.
- Breaks tasks into smaller steps.
- Estimates task size in minutes.
- Adds categories, energy levels, and priority hints.
- Adds quick-start, minimum-win, done-when, blocker, and coaching notes to new tasks.
- Keeps the planning engine local and private.

### Task management

- Multiple named task lists.
- Nested subtasks.
- Completion tracking.
- Large clickable task cards with checkbox controls and icon action buttons.
- Right-click menu with complete, breakdown, simplify, edit, subtask, estimate, duplicate, move, focus, and delete actions.
- Built-in planner notes that explain the finish line and common blockers for vague tasks.
- Manual task editing with notes, due date, due time, reminder timing, and recurrence.
- Move tasks up or down inside a list.

### Dates, reminders, and recurrence

- Due dates and due times.
- In-app reminders while the app is running.
- Daily, weekday, weekly, and monthly recurring tasks.
- Automatic creation of the next recurring task after completion.
- Monthly calendar view for upcoming work.

### Dashboard

- Counts open tasks, completed tasks, due-today tasks, overdue tasks, and lists.
- Shows overdue, today, and upcoming tasks.
- Surfaces next actions across all lists.

### Focus Mode

- Shows one task at a time.
- 5, 15, and 25 minute focus timers.
- One-click complete and next-task controls.
- Distraction capture box for parking unrelated thoughts.

### Templates

- Built-in templates for morning reset, weekly planning, appointments, home cleanup, and work kickoff.
- Save your current list as a reusable template.
- Apply a template into a new list.

### Themes

Settings preview themes immediately before you save. v2.6.0 keeps the theme list focused to four readable choices:

Included themes:

- Classic Web
- Soft Blue
- Warm Focus
- Black & Green

Settings also include smaller rows and plain background options for reading comfort.

### Windows system tray

The packaged release includes tray support with quick access to:

- Open
- Focus Mode
- Exit

Closing the window hides the app to the tray when tray support is available.

## Run From Source

Requirements:

- Windows 10 or Windows 11
- Python 3.11 or newer

```powershell
python -m pip install -r requirements.txt
python src\rice2k_magic_tasks.py
```

You can also double-click `run_app.bat`.

## Build The EXE

```powershell
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Rice2kMagicTasks --icon assets\rice2k_magic_tasks.ico --add-data "assets;assets" src\rice2k_magic_tasks.py
```

The executable will be created at:

```text
dist\Rice2kMagicTasks.exe
```

Or run:

```powershell
build_exe.bat
```

## Data Storage

Tasks and settings are stored locally at:

```text
%APPDATA%\Rice2kMagicTasks\tasks.json
```

No account is required. The app does not upload task data by default.

## Verify Downloads

After downloading the EXE or ZIP, compare its SHA-256 hash with the release checksum file.

```powershell
Get-FileHash .\Rice2k-Magic-Tasks-v2.6.0.exe -Algorithm SHA256
```

## Project Layout

```text
src/
  rice2k_magic_tasks.py
assets/
  rice2k_magic_tasks.ico
  rice2k_magic_tasks.png
tests/
  smoke_test.py
docs/
  RELEASE_NOTES.md
build_exe.bat
run_app.bat
requirements.txt
```

## License

MIT License. See [LICENSE](LICENSE).
