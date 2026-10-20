# Daily Routine frontend

React and Tailwind interface for the Daily Routine API. It provides month,
week and day calendar views, day/task management and period metrics without
mocked application data.

The Evolution section imports weekly Markdown reports, supports editing and
deletion, and displays saved AI comparisons with evidence from both reports.
Generating a comparison requires an explicit click and sends the two texts to
Gemini through the backend. Importing or reading reports does not call AI.

## Run locally

Start the backend at `http://localhost:8000`, then run:

```bash
npm install
npm run dev
```

The frontend is available at `http://localhost:5173`.

To use a different backend URL, create `.env.local`:

```env
VITE_API_URL=http://localhost:8000
```

## Checks

```bash
npm test
npm run lint
npm run build
```

## Current API constraints

- Choose a date in the calendar to save the day and its initial pending tasks together.
- Study minutes can be updated afterward; quote, author and type remain read-only.
- Deleting a day removes its tasks first because the database relationship has no cascade delete.
- Dashboard totals are calculated client-side from the month and day endpoints.
- The streak requires study minutes above zero and at least one completed task.
- Weekly report edits invalidate comparisons that use the changed text.
- Markdown preview skips raw HTML and external images.
- Learning topics have nested checkboxes and local Markdown notes, with search and `.md` download.
- Notes require explicit saving and reject edits from a stale version without replacing the draft.

See [weekly evolution](../docs/weekly-evolution.md) for configuration and limits.
