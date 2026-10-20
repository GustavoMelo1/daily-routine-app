# daily-routine-app

[![Backend tests](https://github.com/GustavoMelo1/daily-routine-app/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/GustavoMelo1/daily-routine-app/actions/workflows/backend-tests.yml)

I plan my days and keep track of my studies in a notebook. I started this project
because I wanted to bring those notes into a calendar without giving up writing
on paper.

There was another reason too: after a week of studying, it can feel like I haven't
done much. Keeping my weekly reports in one place and comparing them helps me
look back at what I actually worked on.

The app has grown around those two habits. It now includes daily planning, photo
imports, weekly comparisons and a learning tree for the subjects I want to study.
It's also a project I'm using to learn and improve as I build it.

## What I can do with it

- **Plan tomorrow:** write one task per line, save the day and check things off
  as I finish them. Study minutes can be filled in afterward.
- **Browse my routine:** month, week and day views, plus a monthly panel with
  study time, completed tasks and my longest sequence of study days.
- **Import notebook pages:** Gemini reads the photos and the app saves each
  entry under the date written on the page, including past days.
- **Compare weeks:** import the Markdown reports I prepare outside the app and
  ask Gemini to compare two of them, with excerpts from both texts.
- **Organize what to learn:** build a tree such as Data Engineering → Python →
  Functions, mark topics and keep Markdown notes, examples and links beside them.

The interface is in Portuguese and has light and dark themes. Planning, tasks
and learning notes work without AI. OCR and report comparisons use Gemini.

## Stack

Python, FastAPI and SQLite on the backend. React, Vite and Tailwind on the
frontend. Gemini handles OCR and weekly comparisons. Tests use pytest and Vitest,
with checks running through GitHub Actions.

## Running locally

### Backend

From the repository root:

```powershell
cd backend
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your settings:

```env
DB_URL=db/rotina.db
GEMINI_API_KEY=your-gemini-api-key
GEMINI_OCR_MODEL=gemini-3.6-flash
GEMINI_COMPARISON_MODEL=gemini-3.6-flash
API_BASE_URL=http://localhost:8000
```

Use models available to your Gemini project. Keep the key in the backend `.env`.

Before starting the API, create or update the database:

```powershell
python db/migrate.py
python -m uvicorn app.main:app --reload
```

The migration command backs up an existing database before changing it. Stop the
API and any running import before migrating. API docs are at
`http://localhost:8000/docs`.

### Frontend

Open another terminal at the repository root:

```powershell
cd frontend
npm ci
npm run dev
```

Open **http://localhost:5173** and leave both terminals running.
This app is meant for personal use on my computer. It has no login, so don't
expose the API to the internet.

## Using it

### Planning a day

Choose a date in the calendar, including future dates. Add one task per
line and click **Salvar dia e tarefas**. Everything starts unchecked, with zero
study minutes. During the day, check off tasks and use **Salvar minutos** to
record the time you actually studied. The quote and other details are optional.

### Importing the notebook

Create `backend/images/` and put your `.jpg`, `.jpeg` or `.png` photos directly
inside it. From `backend`, run:

```powershell
python -m pipeline.batch
```

For example, a page with entries dated `12/10/2026` and `13/10/2026` produces
records for those two dates, even if I send the photo a week later. Write the
complete dates clearly, including the year.

The batch skips photos it has already finished. If a record has an invalid date,
study time or task, it goes to quarantine with the reason. Logs are saved in
`backend/logs/batch.log`.

On Windows, I can schedule the import for every day at 20:00:

```powershell
.\scripts\install_schedule.ps1 -PythonPath (Get-Command python).Source -Time '20:00'
```

Run that from `backend`. The computer must be on and the user signed in. The task
starts a temporary local API if needed. More on [scheduling and recovery](docs/import-operations.md).

### Looking back at the week

In **Evolução**, import a UTF-8 `.md` report and check its date before saving.
With two reports available, choose an earlier week and click
**Gerar comparação com IA**. That sends both texts to Gemini and may consume your
quota. The comparison is saved so you can read it again without generating it again.

The reports are prepared outside the app; it doesn't scan GitHub repositories.
See [weekly evolution](docs/weekly-evolution.md) for the full workflow.

### Building a learning tree

In **Aprendizado**, create an area and use **+** to add topics and subtopics.
Each checkbox is independent: marking Python doesn't mark everything inside it.

Open **Nota** on a topic to write Markdown, preview it or download a `.md` copy.
Search works across topic titles and saved notes. Save before switching topics;
there's no autosave. These notes stay local and aren't sent to Gemini.

## How the code is organized

Routes handle HTTP, schemas validate inputs, repositories hold the SQL, and
services handle operations that need several steps. The image pipeline uses the
API rather than opening the database itself.

Main folders and entry points:

```text
daily-routine-app/
├── .github/workflows/
├── backend/
│   ├── app/
│   │   ├── api/routers/
│   │   ├── core/
│   │   ├── database/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── db/
│   │   ├── migrations/
│   │   ├── migrate.py
│   │   └── schema.sql
│   ├── pipeline/
│   │   ├── batch.py
│   │   ├── ocr.py
│   │   ├── payloads.py
│   │   └── validation.py
│   ├── scripts/
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   │   ├── evolution/
│   │   │   └── learning/
│   │   ├── hooks/
│   │   ├── utils/
│   │   └── App.jsx
│   └── package.json
├── docs/
├── pytest.ini
└── README.md
```

## Tests

From the repository root:

```powershell
python -m pytest -q
cd frontend
npm test
npm run lint
npm run build
```

Tests use temporary databases and simulated external responses. They don't call Gemini.

## Still to work on

The main workflows are there, but a few things still need attention:

- Quarantine has storage and error reasons, but no screen to correct and republish entries.
- A photo for a date already in the calendar isn't merged with that day. The import stops on the conflict.
- Study minutes are editable; quotes, author and day type don't have an edit form yet.
- There's no trash or undo. Deleting a day removes its tasks through separate requests, so an interrupted deletion can be partial.
- Learning notes don't have a version history, topic connections or a graph view yet.

Backups are created before migrations, not after every edit. Keep regular copies
of the database with the API and batch stopped. I've recorded the other practical
limits in [the local-use review](docs/local-use-review.md).

Next is [M11](docs/m11-refactor.md): organize the code and tests while using the
app enough to find out what actually needs improving.
