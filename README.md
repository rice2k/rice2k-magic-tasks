# Rice2k Magic Tasks

<p align="center">
  <img src="assets/rice2k_magic_tasks.png" alt="Rice2k Magic Tasks icon" width="96" height="96">
</p>

<p align="center">
  A colorful Windows task planner that turns messy to-dos into smaller, calmer next actions.
</p>

<p align="center">
  <img alt="Version" src="https://img.shields.io/badge/version-2.7.0-e83f8f">
  <img alt="Platform" src="https://img.shields.io/badge/platform-Windows-008bb8">
  <img alt="Themes" src="https://img.shields.io/badge/themes-8-7b4ce3">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-19a974">
</p>

## Screenshots

![Task list with colorful cards](docs/screenshots/tasks.png)

![Dashboard view](docs/screenshots/dashboard.png)

![Theme settings](docs/screenshots/themes.png)

## Download

Get the latest Windows build from the [Releases](../../releases) page.

The v2.7.0 release includes:

- `Rice2k-Magic-Tasks-v2.7.0.exe` - single-file Windows app.
- `Rice2k-Magic-Tasks-v2.7.0.zip` - release package.
- `Rice2k-Magic-Tasks-v2.7.0.sha256` - checksum file.
- `Rice2k-Magic-Tasks-Source-v2.7.0.zip` - source archive.

Windows may show a SmartScreen warning because the app is unsigned.

## What It Does

- Rewrites vague tasks into clearer action wording.
- Breaks large tasks into smaller steps.
- Adds estimates, priority hints, categories, and energy levels.
- Saves helpful notes with a quick start, minimum win, finish line, blocker check, and coach note.
- Keeps your task data local on your computer.
- Supports due dates, reminders, recurring tasks, templates, a dashboard, calendar view, focus mode, and tray access.

## How To Use

1. Open `Rice2k-Magic-Tasks-v2.7.0.exe`.
2. Type a task into **Add new item**.
3. Use **Spiciness level** to choose how detailed the breakdown should be.
4. Add a due date, time, or repeat setting if you want one.
5. Press **Add**.
6. Use the task buttons:
   - **Steps** breaks the task into subtasks.
   - **Edit** changes the task text, notes, due date, reminders, and recurrence.
   - **Add** adds a subtask.
   - **Del** removes the task.
7. Right-click a task for more actions, including simplify, duplicate, move, estimate, focus, and complete.
8. Change themes instantly from the task screen or from **Settings**.

## Themes

Rice2k Magic Tasks now includes eight themes:

- Classic Web
- Candy Pop
- Ocean Glow
- Soft Blue
- Sunset Arcade
- Warm Focus
- Lavender Pop
- Black & Green

Settings also includes smaller task rows and a plain background option for reading comfort.

## Features

### Smart Planning

- Local planner for task rewriting, breakdowns, estimates, categories, energy levels, and priorities.
- Richer guidance for vague tasks with **Done when** and **Watch for** notes.
- More useful subtasks for home, work, health, errands, admin, school, creative, and email tasks.

### Task Management

- Multiple named task lists.
- Nested subtasks.
- Large clickable task cards.
- Colored priority stripes.
- Checkbox controls.
- Labeled icon buttons.
- Right-click task menu.
- Manual editing with notes, due date, due time, reminder timing, and recurrence.
- Move tasks up or down inside a list.

### Scheduling

- Due dates and due times.
- In-app reminders while the app is running.
- Daily, weekday, weekly, and monthly recurring tasks.
- Automatic creation of the next recurring task after completion.
- Monthly calendar view.

### Focus

- One-task focus mode.
- 5, 15, and 25 minute timers.
- One-click complete and next-task controls.
- Distraction capture box.

### Templates

- Built-in templates for morning reset, weekly planning, appointments, home cleanup, and work kickoff.
- Save your current list as a reusable template.
- Apply a template into a new list.

### Windows Tray

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
Get-FileHash .\Rice2k-Magic-Tasks-v2.7.0.exe -Algorithm SHA256
```

## Project Layout

```text
src/
  rice2k_magic_tasks.py
assets/
  rice2k_magic_tasks.ico
  rice2k_magic_tasks.png
  actions/
docs/
  RELEASE_NOTES.md
  screenshots/
tests/
  smoke_test.py
build_exe.bat
run_app.bat
requirements.txt
```

## License

MIT License. See [LICENSE](LICENSE).
