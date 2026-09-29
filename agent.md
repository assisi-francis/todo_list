# agent.md: Build a Todo Web App (FastAPI + Bootstrap)

## Role
You are a senior full-stack engineer. Build a complete, working todo web app by following the steps below **in order**. Do not skip steps. After each step, run its **Verify** check. If a check fails, fix it before moving on.

## Goal
A web app where a user can add, complete, edit, delete, and filter tasks. Data is stored in a database on the server and survives restarts.

## Tech Stack (do not substitute without asking)
- **Backend:** Python 3.11+, FastAPI, Uvicorn, SQLAlchemy 2.x, Pydantic v2
- **Database:** SQLite (file: `todos.db`)
- **Frontend:** HTML5, CSS3, vanilla JavaScript (ES6+, `fetch` API), Bootstrap 5.3 via CDN
- **Testing:** pytest + FastAPI `TestClient`
- No frontend frameworks (no React/Vue/jQuery), no build tools, no Node required

## Features (MVP)
1. Add a task (title required, 1-100 characters)
2. Toggle a task complete / incomplete
3. Edit a task title
4. Delete a task (with confirmation)
5. Filter: All / Active / Completed
6. Show count of remaining active tasks
7. "Clear completed" button
8. Empty-state message when there are no tasks
9. Inline error messages if the API fails

## Out of Scope
User accounts, authentication, due dates, categories, drag-and-drop, deployment config. Do not add these unless asked.

---

## Project Structure (create exactly this)
```
todo-app/
├── requirements.txt
├── README.md
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, static files, routers
│   ├── database.py      # engine, session, Base, get_db
│   ├── models.py        # SQLAlchemy Todo model
│   ├── schemas.py       # Pydantic schemas
│   └── routes.py        # /api/todos endpoints
├── static/
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
└── tests/
    └── test_api.py
```

---

## Step-by-Step Instructions

### Step 1: Environment setup
1. Create the folder `todo-app` and `cd` into it.
2. Create and activate a virtual environment: `python -m venv venv`
   - macOS/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`
3. Create `requirements.txt` with: `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `pytest`, `httpx`
4. Run: `pip install -r requirements.txt`
5. Create the folders and empty files from the Project Structure above.

**Verify:** `python -c "import fastapi, sqlalchemy; print('ok')"` prints `ok`.

### Step 2: Database layer
In `app/database.py`:
1. Create the engine with `sqlite:///./todos.db` and `connect_args={"check_same_thread": False}`.
2. Create `SessionLocal` (`autoflush=False`) and a declarative `Base`.
3. Write a `get_db()` generator dependency that yields a session and always closes it.

In `app/models.py`, define `Todo`:
- `id`: Integer, primary key
- `title`: String(100), not null
- `completed`: Boolean, default `False`
- `created_at`: DateTime, default current UTC time

**Verify:** Importing both modules raises no errors.

### Step 3: Schemas
In `app/schemas.py` (Pydantic v2):
1. `TodoCreate`: `title: str` (strip whitespace; length 1-100)
2. `TodoUpdate`: `title: str | None` (same rules), `completed: bool | None`
3. `TodoOut`: `id`, `title`, `completed`, `created_at`, with `model_config = ConfigDict(from_attributes=True)`

Reject whitespace-only titles with a validation error.

**Verify:** `TodoCreate(title="  ")` raises a validation error; `TodoCreate(title=" hi ")` gives `"hi"`.

### Step 4: API routes
In `app/routes.py`, use `APIRouter(prefix="/api/todos", tags=["todos"])`:

| Method | Path | Behavior | Success code |
|---|---|---|---|
| GET | `/` | List todos, newest first. Optional query `status` = `all` (default) / `active` / `completed` | 200 |
| POST | `/` | Create from `TodoCreate` | 201 |
| PATCH | `/{todo_id}` | Partial update from `TodoUpdate`; 404 if not found | 200 |
| DELETE | `/completed` | Delete all completed todos; return `{"deleted": <count>}` | 200 |
| DELETE | `/{todo_id}` | Delete one; 404 if not found | 204 |

Rules:
- Define `DELETE /completed` **before** `DELETE /{todo_id}` so the route is not shadowed.
- Use `Depends(get_db)` in every endpoint.
- Use `response_model=TodoOut` (or `list[TodoOut]`) where applicable.
- Raise `HTTPException(status_code=404, detail="Todo not found")` for missing IDs.

**Verify:** Covered in Step 5 and Step 9.

### Step 5: App entry point
In `app/main.py`:
1. Create the `FastAPI(title="Todo App")` instance.
2. Create tables on startup: `Base.metadata.create_all(bind=engine)`.
3. Include the router from `routes.py`.
4. Mount `static/` at `/static` using `StaticFiles`.
5. Add `GET /` that returns `FileResponse("static/index.html")`.
6. Use absolute paths built from `pathlib.Path(__file__)` so the app runs from any working directory.

Run: `uvicorn app.main:app --reload`

**Verify:**
- `http://127.0.0.1:8000/docs` shows all 5 endpoints.
- In the docs UI, create, list, update, and delete a todo successfully.

### Step 6: Frontend HTML
In `static/index.html`:
1. Use the HTML5 doctype, `lang="en"`, and the viewport meta tag.
2. Load Bootstrap 5.3 CSS from the jsDelivr CDN in `<head>`, then `css/style.css`.
3. Load the Bootstrap JS bundle and `js/app.js` (with `defer`) before `</body>`.
4. Layout, inside `<main class="container">` with a centered column (`col-md-8 col-lg-6`):
   - Page heading "My Todos"
   - An `<form id="todo-form">` with a Bootstrap `input-group`: text input (`id="todo-input"`, `maxlength="100"`, `required`) and an "Add" button
   - An alert container `<div id="error-box">` (hidden by default)
   - Filter buttons in a `btn-group`: All / Active / Completed (use `data-filter` attributes)
   - `<ul id="todo-list" class="list-group">`
   - A footer row with `<span id="remaining-count">` and a "Clear completed" button (`id="clear-completed"`)
5. Add ARIA labels to icon-only buttons.

**Verify:** Page loads at `/` and looks like a clean Bootstrap card layout with no console errors.

### Step 7: Frontend JavaScript
In `static/js/app.js`:
1. Keep state in a module-level object: `{ todos: [], filter: "all" }`.
2. Write an `api` helper wrapping `fetch` that:
   - Sends/accepts JSON
   - Throws an `Error` with a readable message on non-2xx responses (use the `detail` field when present)
   - Handles the 204 (no body) case
3. Write these functions:
   - `loadTodos()`: GET with the current filter, store in state, call `render()`
   - `addTodo(title)`, `toggleTodo(id, completed)`, `editTodo(id, title)`, `deleteTodo(id)`, `clearCompleted()`
   - `render()`: rebuild the list, update the remaining count, highlight the active filter button, show the empty state when the list is empty, show/hide "Clear completed"
   - `showError(message)`: display in `#error-box`, auto-hide after 4 seconds
4. Rendering rules:
   - Each item: checkbox, title (strikethrough + muted if completed), Edit and Delete buttons
   - Edit swaps the title for an inline input; Enter or blur saves, Escape cancels
   - Delete uses `confirm()` before calling the API
5. **Security:** never insert user text with `innerHTML`. Use `textContent` or `createElement` so titles cannot inject HTML/scripts.
6. Use **event delegation** on `#todo-list` (one listener, not one per item).
7. Wrap every API call in try/catch and route errors to `showError`.
8. Call `loadTodos()` on `DOMContentLoaded`.
9. Compute the remaining count from all active todos, not just the filtered list. Fetch counts separately or load all todos and filter on the client (choose one approach and keep it consistent).

**Verify:** In the browser you can add, toggle, edit, delete, filter, and clear completed. Reloading the page keeps the data.

### Step 8: Styling
In `static/css/style.css`, keep it minimal and let Bootstrap do the work:
- Light background on `body`, top margin on the container
- `.completed` style: line-through, reduced opacity
- Smooth hover and transition on list items
- Long titles wrap (`word-break: break-word`)
- Buttons remain tappable on mobile (min-height 38px)

**Verify:** Layout works at 360px width (mobile) and at desktop width.

### Step 9: Tests
In `tests/test_api.py`:
1. Use an in-memory or temporary SQLite database via a dependency override of `get_db`, so tests never touch `todos.db`.
2. Write tests for:
   - Create a todo (201, correct fields)
   - Reject empty and whitespace-only titles (422)
   - Reject titles over 100 characters (422)
   - List returns newest first
   - Filter by `active` and `completed`
   - Toggle completed via PATCH
   - Edit title via PATCH
   - PATCH and DELETE on a missing ID return 404
   - Delete one todo (204)
   - `DELETE /api/todos/completed` removes only completed items and returns the count

Run: `pytest -v`

**Verify:** All tests pass.

### Step 10: Documentation
Create `README.md` with: description, prerequisites, setup and run commands (venv, `pip install -r requirements.txt`, `uvicorn app.main:app --reload`), how to run tests, API endpoint table, and folder structure.

---

## Code Standards
- Python: type hints everywhere, PEP 8, small functions, no dead code
- JavaScript: `const`/`let` only (no `var`), no globals except the state object, async/await over `.then` chains
- Comment only the "why", not the "what"
- No hardcoded absolute paths
- Do not commit `venv/` or `todos.db` (add a `.gitignore`)

## Working Rules for the Agent
1. Work through the steps in order and state which step you are on.
2. After each step, run its **Verify** check and report the result in one line.
3. If a requirement is ambiguous, choose the simplest reasonable option, note the assumption, and continue. Only ask the user if you are blocked.
4. Do not install packages beyond those listed without explaining why.
5. Never leave the project in a broken state at the end of a step.

## Definition of Done
- [ ] All 9 MVP features work in the browser
- [ ] Data persists after restarting the server
- [ ] `pytest` passes with no failures
- [ ] No errors in the browser console or server logs
- [ ] User-entered text is never rendered as HTML
- [ ] Layout is responsive on mobile and desktop
- [ ] Folder structure matches the spec and README is complete
- [ ] Final message summarizes what was built, how to run it, and any assumptions made
