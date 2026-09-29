# Todo Web App

A simple, full-stack todo application built with FastAPI and Bootstrap.

## Features
- Add, edit, toggle, and delete tasks.
- Filter tasks by All, Active, or Completed.
- Persists data in a SQLite database.
- Responsive design for mobile and desktop.

## Prerequisites
- Python 3.11+

## Setup and Run
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or venv\Scripts\activate on Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```
4. Open your browser at: `http://127.0.0.1:8000`

## Running Tests
```bash
export PYTHONPATH=.
pytest -v tests/test_api.py
```

## API Endpoints
| Method | Path | Description |
|---|---|---|
| GET | `/api/todos/` | List all todos (Optional query `status=all\|active\|completed`) |
| POST | `/api/todos/` | Create a new todo |
| PATCH | `/api/todos/{id}` | Update a todo's title or status |
| DELETE | `/api/todos/completed` | Remove all completed tasks |
| DELETE | `/api/todos/{id}` | Remove a specific task |

## Project Structure
```
todo-app/
├── requirements.txt
├── README.md
├── app/
│   ├── main.py          # FastAPI app, static files, routers
│   ├── database.py      # Engine and session setup
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   └── routes.py        # API endpoints
├── static/
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
└── tests/
    └── test_api.py
```
