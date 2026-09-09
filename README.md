# daily-routine-app

[![Backend tests](https://github.com/GustavoMelo1/daily-routine-app/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/GustavoMelo1/daily-routine-app/actions/workflows/backend-tests.yml)

I created this project to turn my handwritten notebook entries into a digital agenda. I wanted a way to follow my tasks and study time over the weeks while keeping the habit of writing on paper.

The app brings those records into a calendar, with daily tasks, quotes and monthly study totals. A photo of the notebook starts the import: Gemini reads the page, the pipeline checks the data, and the API saves the records.

## Current project structure

The main parts of the project:

```text
daily-routine-app/
├── .github/workflows/backend-tests.yml
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routers/
│   │   │       ├── days.py
│   │   │       ├── tasks.py
│   │   │       └── quarantine.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── database/
│   │   │   └── connection.py
│   │   ├── repositories/
│   │   │   ├── day.py
│   │   │   ├── task.py
│   │   │   └── quarantine.py
│   │   ├── schemas/
│   │   │   ├── day.py
│   │   │   ├── task.py
│   │   │   └── quarantine.py
│   │   └── main.py
│   ├── db/
│   │   ├── init_db.py
│   │   └── schema.sql
│   ├── pipeline/
│   │   ├── batch.py
│   │   ├── ocr.py
│   │   ├── publisher.py
│   │   ├── validation.py
│   │   └── vocabulary.py
│   ├── tests/
│   │   ├── api/
│   │   │   ├── conftest.py
│   │   │   ├── test_days.py
│   │   │   ├── test_tasks.py
│   │   │   └── test_quarantine.py
│   │   ├── pipeline/
│   │   │   ├── test_publisher.py
│   │   │   └── test_validation.py
│   │   └── conftest.py
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   └── index.css
│   ├── package.json
│   └── README.md
├── pytest.ini
└── README.md
```

## Stack

**Backend**

- Python + FastAPI
- SQLite
- pytest
- python-dotenv

**Pipeline**

- Google Gemini API (`google-genai`)
- difflib (stdlib)

**Frontend**

- React + Vite + Tailwind
- Calendar (month/week/day), day creation/deletion, task management and monthly metrics connected to the API.
- Light/dark themes with the selected preference saved in the browser.

## Layered architecture

```text
React frontend / pipeline publisher
                |
                v
FastAPI routers -> repositories -> SQLite
       |
       +-- Pydantic schemas: request types
       +-- Database dependency: connection lifecycle
```

## Quarantine flow

Handwriting can produce incomplete or incorrect data. Before publishing a day,
the pipeline checks its date, study minutes and tasks. A valid day goes to the
agenda; a day with validation errors goes to quarantine along with its tasks
and the reasons it was rejected.

The API stores these records through `POST /erros-quarentena` and
`POST /tarefas-quarentena`, with status `pendente` and a `motivo_erro`.
For example, negative study minutes produce the error `minutos_invalidos`.

Reviewing, correcting and republishing quarantined records is still pending.
There is no review screen or automatic reprocessing yet.

## How to run

Clone the repository:
   ```
   git clone https://github.com/GustavoMelo1/daily-routine-app.git
   cd daily-routine-app
   ```

### Backend

   ```
   cd backend
   python -m pip install -r requirements.txt
   ```

Copy `backend/.env.example` to `backend/.env` and use uppercase `DB_URL`:

```env
DB_URL=db/rotina.db
GEMINI_API_KEY=your-gemini-api-key
```

From `backend`, initialize a new database once, then start the API:

   ```
   python db/init_db.py
   python -m uvicorn app.main:app --reload
   ```

If the database already exists, skip initialization. API documentation is at
`http://localhost:8000/docs`.

Fill in `GEMINI_API_KEY` in `.env` (get one at [aistudio.google.com](https://aistudio.google.com)) to run the pipeline.

### Frontend

In a separate terminal, starting from the repository root:

   ```
   cd frontend
   npm install
   npm run dev
   ```

Open `http://localhost:5173`. Keep the backend running at `http://localhost:8000`.
See [frontend/README.md](frontend/README.md) for frontend configuration and checks.

### Pipeline

Start the backend and configure a valid `GEMINI_API_KEY` first. Place the image
at `backend/exemplo.jpeg` (or change the image path in `pipeline/batch.py`).

From the repository root:

```
cd backend
python -m pipeline.batch
```

The command reads the photo with Gemini and publishes the validated records.

### Tests and CI

Run from the repository root or from `backend`:

```bash
python -m pytest -q
```

Tests cover the API, validation and publication flow without calling Gemini.
GitHub Actions runs them on every push and pull request; click the badge above
to see the results.
