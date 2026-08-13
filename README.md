# daily-routine-app

Personal digital agenda (calendar, tasks, goals and daily quote) with its own FastAPI API and SQLite database, replacing a paper notebook.

## Project structure

```
daily-routine-app/
├── backend/
│   ├── db/
│   │   ├── schema.sql
│   │   └── init_db.py
│   ├── pipeline/
│   │   ├── ocr.py
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

**Frontend**
- **React** + **Vite**
- **Tailwind CSS**

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

### Frontend

   ```
   cd frontend
   npm install
   npm run dev
   ```

