# daily-routine-app

[![Backend tests](https://github.com/GustavoMelo1/daily-routine-app/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/GustavoMelo1/daily-routine-app/actions/workflows/backend-tests.yml)

Personal digital agenda for daily records, tasks, study minutes and quotes, with a React frontend, FastAPI API and SQLite database. A manual pipeline extracts records from notebook photos using Gemini and publishes them through the API.

## Current project structure

Main files are shown below; generated files and package markers are omitted.

```text
daily-routine-app/
|-- .github/workflows/backend-tests.yml
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |   `-- routers/
|   |   |       |-- days.py
|   |   |       |-- tasks.py
|   |   |       `-- quarantine.py
|   |   |-- core/
|   |   |   `-- config.py
|   |   |-- database/
|   |   |   `-- connection.py
|   |   |-- repositories/
|   |   |   |-- day.py
|   |   |   |-- task.py
|   |   |   `-- quarantine.py
|   |   |-- schemas/
|   |   |   |-- day.py
|   |   |   |-- task.py
|   |   |   `-- quarantine.py
|   |   `-- main.py
|   |-- db/
|   |   |-- init_db.py
|   |   `-- schema.sql
|   |-- pipeline/
|   |   |-- batch.py
|   |   |-- ocr.py
|   |   |-- publisher.py
|   |   |-- validation.py
|   |   `-- vocabulary.py
|   |-- tests/
|   |   |-- api/
|   |   |   |-- conftest.py
|   |   |   |-- test_days.py
|   |   |   |-- test_tasks.py
|   |   |   `-- test_quarantine.py
|   |   |-- pipeline/
|   |   |   |-- test_publisher.py
|   |   |   `-- test_validation.py
|   |   `-- conftest.py
|   |-- .env.example
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |   |-- api/
|   |   |-- components/
|   |   |-- hooks/
|   |   |-- utils/
|   |   |-- App.jsx
|   |   `-- index.css
|   |-- package.json
|   `-- README.md
|-- pytest.ini
`-- README.md
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

`pipeline/batch.py` calls `extract` and passes the result to `publish_days`.
The publisher normalizes date separators and calls `validate_day` for each day.
The validator returns a list of error codes, such as `data_invalida`,
`minutos_invalidos` or `tarefa_sem_descricao`.

- An empty error list allows normal publication through `/dias` and `/tarefas`.
- Validation errors send the day to `/erros-quarentena`. Its returned ID links
  task records sent to `/tarefas-quarentena`; the publisher then skips normal
  publication for that day.

| Method and path | Storage | Successful response |
|---|---|---|
| `POST /erros-quarentena` | `erros_quarentena` | HTTP 201 with `id` and `Status`. |
| `POST /tarefas-quarentena` | `tarefas_quarentena`, linked by `erro_quarentena_id` | HTTP 201 with `id` and `Status`. |

Both tables default `status` to `pendente` and store validation reasons in
`motivo_erro`. Quarantine schemas allow several fields to be null so incomplete
records can be retained. They still enforce types: arbitrary malformed payloads
are not guaranteed to be accepted. Day and task inserts are separate HTTP
requests, so the operation is not atomic across the whole day.

Quarantine currently provides storage only. There are no API routes or frontend
screens for listing, editing or reprocessing these records. Correcting a database
record manually does not trigger automatic publication.

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

Copy `backend/.env.example` to `backend/.env` and set the database variable with
this exact spelling (the current example uses lowercase `db_url`):

```env
DB_URL=db/rotina.db
GEMINI_API_KEY=your-gemini-api-key
```

From `backend`, initialize a new database once, then start the API:

   ```
   python db/init_db.py
   python -m uvicorn app.main:app --reload
   ```

If the database already exists, skip initialization: the schema uses plain
`CREATE TABLE` statements. API documentation is available at
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
The current image path is relative to the working directory.

From the repository root:

```
cd backend
python -m pipeline.batch
```

This command calls Gemini to extract the image, validates the returned days and
sends them to the local API. Valid days follow the normal publication path;
invalid days and their tasks are stored in quarantine. This is a manual run
that calls an external service and writes records; it is not a test command.

### Tests and CI

Run from the repository root or from `backend`:

```bash
python -m pytest -q
```

`pytest.ini` configures the backend import path. API tests use a temporary SQLite
database through `backend/tests/conftest.py`; shared API data fixtures live in
`backend/tests/api/conftest.py`. Publisher tests replace HTTP calls, and validation tests
check the returned error lists. These tests do not call Gemini or exercise OCR
end to end.

GitHub Actions installs the backend requirements and runs the suite with Python
3.14 on every push and pull request. The [workflow](.github/workflows/backend-tests.yml)
uses an Ubuntu runner, pip caching and read-only repository permissions. The badge
at the top shows the workflow status and links to its runs; it is not a coverage
measurement or proof of a successful live OCR run.
