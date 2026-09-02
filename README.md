# daily-routine-app

Personal digital agenda (calendar, tasks, goals and daily quote) with its own FastAPI API and SQLite database, replacing a paper notebook. Includes a pipeline that reads a photo of the physical notebook and loads it straight into the database via the API.

## Target project structure

```text
daily-routine-app/
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |   `-- routers/
|   |   |       |-- days.py
|   |   |       |-- tasks.py
|   |   |       `-- quarantine.py
|   |   |-- core/
|   |   |   |-- config.py
|   |   |   `-- logging_config.py
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
- Static mock for now (`frontend/src/App.jsx`) — real frontend in progress separately.

## How to run

Clone the repository:
   ```
   git clone https://github.com/GustavoMelo1/daily-routine-app.git
   cd daily-routine-app
   ```

### Backend

   ```
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   python db/init_db.py
   uvicorn app.main:app --reload
   ```

Run the tests:
   ```
   python -m pytest tests/ -v
   ```

Fill in `GEMINI_API_KEY` in `.env` (get one at [aistudio.google.com](https://aistudio.google.com)) to run the pipeline.

### Frontend

   ```
   cd frontend
   npm install
   npm run dev
   ```

### Pipeline

```
cd backend
python -m pipeline.publicar
```


