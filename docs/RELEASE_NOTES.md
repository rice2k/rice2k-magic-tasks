# Rice2k Magic Tasks v3.0.1

Readability and font polish update for the v3 interface.

## Highlights

- Added a multi-font UI setup with display, body, compact badge, and mono fallbacks.
- Uses strong heading fonts where available, while keeping body text on readable Windows UI fonts.
- Added responsive task-title wrapping so long task names stay inside the card.
- Changed task badges from one long row into a small wrapping grid.
- Shortened category, energy, task, and calendar labels before they can hit an edge.
- Made calendar event times shorter, such as **8:30 Planning...**, so cells stay readable.
- Reduced navigation padding and renamed Dashboard to **Home** in the top bar so all tabs fit at the minimum window size.
- Updated Help copy to match the cleaner v3 task-card flow.
- Refreshed README screenshots with longer sample text to verify wrapping.

## Notes

The app stores data locally in `%APPDATA%\Rice2kMagicTasks\tasks.json`.
The Windows executable is unsigned, so Windows may show a SmartScreen warning on first launch.
