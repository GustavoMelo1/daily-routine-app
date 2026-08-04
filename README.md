# daily-routine-app

Personal digital agenda (calendar, tasks, goals and daily quote) with its own FastAPI API and SQLite database, replacing a paper notebook.

## Project structure

```
daily-routine-app/
├── backend/
│   ├── db/
│   │   ├── schema.sql       # table definitions (dias, tarefas, metas_semanais, conferencias)
│   │   └── init_db.py       # creates the database from schema.sql
│   ├── src/
│   │   └── main.py          # FastAPI API (dias and tarefas routes)
│   ├── tests/
│   │   └── test_main.py     # automated tests (pytest)
│   ├── .env.example         # environment variables template
│   └── requirements.txt     # Python dependencies
├── frontend/                # React + Vite + Tailwind app
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
