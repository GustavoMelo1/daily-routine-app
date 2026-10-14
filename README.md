# daily-routine-app

[![Backend tests](https://github.com/GustavoMelo1/daily-routine-app/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/GustavoMelo1/daily-routine-app/actions/workflows/backend-tests.yml)

I created this project to turn my handwritten notebook entries into a digital
agenda. I wanted to follow my tasks and study time over the weeks while keeping
the habit of writing on paper.

A photo starts the import: Gemini reads the page, the pipeline validates the
result, and the API saves days and tasks or sends incomplete records to quarantine.
The calendar shows month, week and day views, alongside monthly study metrics.

The **Evolução** area also keeps the weekly Markdown reports I prepare outside
the app. Comparing two reports helps me see what changed, with excerpts from
both weeks instead of a productivity score.

## Stack

- Backend: Python, FastAPI, Pydantic and SQLite.
- Pipeline and weekly comparisons: Google Gemini (`google-genai`).
- Frontend: React, Vite and Tailwind, with light/dark themes.
- Tests: pytest and Vitest; GitHub Actions runs backend and frontend checks.

## Structure

```text
daily-routine-app/
├── .github/workflows/
│   ├── backend-tests.yml
│   └── frontend-tests.yml
├── backend/
│   ├── app/
│   │   ├── api/routers/
│   │   │   ├── days.py
│   │   │   ├── tasks.py
│   │   │   ├── quarantine.py
│   │   │   ├── image_imports.py
│   │   │   └── weekly_reports.py
│   │   ├── core/
│   │   ├── database/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── db/
│   │   ├── migrations/
│   │   ├── init_db.py
│   │   ├── migrate.py
│   │   └── schema.sql
│   ├── pipeline/
│   │   ├── batch.py
│   │   ├── import_client.py
│   │   ├── ocr.py
│   │   ├── payloads.py
│   │   ├── publisher.py
│   │   ├── tracking.py
│   │   ├── validation.py
│   │   └── vocabulary.py
│   ├── scripts/
│   │   ├── install_schedule.ps1
│   │   └── run_batch.ps1
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   │   └── evolution/
│   │   ├── hooks/
│   │   ├── utils/
│   │   └── App.jsx
│   └── package.json
├── docs/
│   ├── import-operations.md
│   ├── weekly-evolution.md
│   └── m11-refactor.md
├── pytest.ini
└── README.md
```

Routes handle HTTP, schemas validate requests, repositories contain SQL, and
services coordinate transactions and comparisons. The pipeline talks to the API;
it does not open the application database directly.

## Run locally

### Backend

From the repository root:

```powershell
cd backend
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and configure:

```env
DB_URL=db/rotina.db
GEMINI_API_KEY=your-gemini-api-key
GEMINI_OCR_MODEL=gemini-3.6-flash
GEMINI_COMPARISON_MODEL=gemini-3.6-flash
API_BASE_URL=http://localhost:8000
```

Then initialize or migrate the database and start the API:

```powershell
python db/migrate.py
python -m uvicorn app.main:app --reload
```

The migrator backs up existing databases before changing their structure.
Stop active writers before migrating. API docs: `http://localhost:8000/docs`.
Choose models available to your Gemini account; the API key stays in the backend.

### Frontend

In a separate terminal, from the repository root:

```powershell
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. Keep the API at `http://localhost:8000`.
This is a local, single-user app without authentication; do not expose the API
directly to the internet.

### Images and daily import

Put `.jpg`, `.jpeg` or `.png` files directly in `backend/images/`, then run from
`backend`:

```powershell
python -m pipeline.batch
```

Completed images are skipped by content hash. A publication failure rolls back
that image's records; a saved OCR payload is reused on retry. Existing dates are
not silently overwritten. Logs are written to `backend/logs/batch.log`.

To install the Windows task for **every day at 20:00**, from `backend`:

```powershell
.\scripts\install_schedule.ps1 -PythonPath (Get-Command python).Source -Time '20:00'
```

The task requires the computer on and the user signed in. It starts a temporary
local API if needed. [Recovery, backups and scheduling details](docs/import-operations.md).

### Weekly evolution

Open **Evolução**, import a UTF-8 `.md`, check its date/title and save. Importing
does not call AI. With two reports available, select an earlier week and choose
**Gerar comparação com IA**. This explicitly sends both texts to Gemini and may
consume your quota. Saved comparisons are reused until a source report changes.

The app does not scan repositories: you prepare those reports outside it.
[Workflow, API and comparison limits](docs/weekly-evolution.md).

## Quarantine

Invalid dates, study minutes or tasks are stored with the reason for rejection
and status `pendente`. They are not published as normal days. Reviewing,
correcting and republishing quarantine still needs a dedicated workflow; there
is no quarantine review screen yet.

## Tests

From the repository root:

```powershell
python -m pytest -q
cd frontend
npm test
npm run lint
npm run build
```

Tests cover the API, import/retry flow and weekly comparisons using temporary
databases and simulated external responses. They do not call Gemini.

M9 delivers reliable scheduled imports; M10 adds weekly reports and comparisons.
The next block is [M11: focused refactoring](docs/m11-refactor.md), keeping these
behaviors covered while organizing names, folders and tests.
