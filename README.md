# daily-routine-app

Personal digital agenda (calendar, tasks, goals and daily quote) with its own FastAPI API and SQLite database, replacing a paper notebook. Includes a pipeline that reads a photo of the physical notebook and loads it straight into the database via the API.

## Project structure

```
daily-routine-app/
├── backend/
│   ├── db/
│   │   ├── schema.sql
│   │   └── init_db.py
│   ├── pipeline/
│   │   ├── ocr.py
│   │   ├── vocabulary.py
│   │   └── publicar.py
│   ├── src/
│   │   └── main.py
│   ├── tests/
│   │   └── test_main.py
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   ├── favicon.svg
│   │   └── icons.svg
│   ├── src/
│   │   ├── assets/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Stack

**Backend**
- **Python** + **FastAPI**
- **SQLite** (database)
- **pytest** (automated tests)
- **python-dotenv** (configuration via environment variable)

**Pipeline**
- **Google Gemini API** (`google-genai`) — vision model reading a photo of the notebook and extracting structured data
- **difflib** (stdlib) — fuzzy-matches recurring task names against a known vocabulary

**Frontend**
- **React** + **Vite**
- **Tailwind CSS**
- Currently a **static, non-functional mock** (`frontend/src/App.jsx`) — the real frontend is being built separately.

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
   uvicorn src.main:app --reload
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

## Pipeline

The pipeline replaces manual data entry: take a photo of the physical notebook page, and it loads the day and its tasks straight into the database through the existing API — no typing.

```
pipeline/
├── ocr.py         # sends the photo to Gemini, gets back structured JSON
├── vocabulary.py  # known recurring task names, used for fuzzy-matching
└── publicar.py    # loads the JSON into the API (POST /dias, POST /tarefas)
```

Run it with:
```
cd backend/pipeline
python publicar.py
```

It's idempotent — running the same photo twice does not duplicate the day or its tasks.

### Why Gemini instead of classic OCR

The first attempt used Tesseract (`pytesseract`), a traditional OCR engine. It failed outright on the notebook's handwriting, and — more fundamentally — a checkbox that's filled in, crossed out, or left empty isn't something character-recognition OCR can interpret; it needs actual visual understanding of the mark, not just character shapes. Switching to the Gemini vision API solved both problems: it reads the handwriting reliably and can tell filled/crossed/empty checkboxes apart based on a prompt describing the three states.

