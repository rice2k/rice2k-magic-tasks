# Rice2k Magic Tasks v3.3.0

Task-card drag-and-drop reordering.

![Rice2k Magic Tasks banner](https://raw.githubusercontent.com/rice2k/rice2k-magic-tasks/main/docs/screenshots/github-hero.png)

## Download

- [Windows EXE](https://github.com/rice2k/rice2k-magic-tasks/releases/download/v3.3.0/Rice2k-Magic-Tasks-v3.3.0.exe)
- [Release ZIP](https://github.com/rice2k/rice2k-magic-tasks/releases/download/v3.3.0/Rice2k-Magic-Tasks-v3.3.0.zip)
- [Source ZIP](https://github.com/rice2k/rice2k-magic-tasks/releases/download/v3.3.0/Rice2k-Magic-Tasks-Source-v3.3.0.zip)
- [SHA-256 checksums](https://github.com/rice2k/rice2k-magic-tasks/releases/download/v3.3.0/Rice2k-Magic-Tasks-v3.3.0.sha256)

## Highlights

- Added drag-and-drop reordering for task cards in the Tasks view.
- Top-level tasks can be dragged above or below other top-level tasks.
- Subtasks can be dragged within the same parent task.
- Added task-list autoscroll while dragging near the top or bottom.
- Kept **Move up** and **Move down** in the right-click menu for menu users.
- Added a visible **Drag task cards to reorder** hint on the Tasks page.
- Added tests for saved before/after reorder behavior.
- Kept the v3.2 cleaner task tabs, Options toggle, calendar month/year picker, themes, focus mode, templates, and reminders.

## Screenshots

| Tasks | Calendar |
| --- | --- |
| ![Tasks](https://raw.githubusercontent.com/rice2k/rice2k-magic-tasks/main/docs/screenshots/tasks.png) | ![Calendar](https://raw.githubusercontent.com/rice2k/rice2k-magic-tasks/main/docs/screenshots/calendar.png) |

| Dashboard | Settings |
| --- | --- |
| ![Dashboard](https://raw.githubusercontent.com/rice2k/rice2k-magic-tasks/main/docs/screenshots/dashboard.png) | ![Settings](https://raw.githubusercontent.com/rice2k/rice2k-magic-tasks/main/docs/screenshots/themes.png) |

## Quick Start

1. Open `Rice2k-Magic-Tasks-v3.3.0.exe`.
2. Pick a task-list tab.
3. Type one messy task.
4. Open **Options** only if you need dates, repeats, templates, or detail level.
5. Press **Add Task**.
6. Use **Steps**, **Edit**, **More**, or right-click to work with the task.
7. Drag task cards up or down to reorder them.

## Hotkeys And Mouse

| Shortcut or Action | Result |
| --- | --- |
| `Ctrl+K` | Quick add a task. |
| `Ctrl+T` | Open Tasks. |
| `Ctrl+D` | Open Dashboard. |
| `Ctrl+M` | Open Calendar. |
| `F1` | Open Help. |
| Drag a task card | Reorder it inside the list. |
| Drag a calendar task or event | Move it to another day. |

## Notes

The app stores data locally in `%APPDATA%\Rice2kMagicTasks\tasks.json`.
The Windows executable is unsigned, so Windows may show a SmartScreen warning on first launch.
