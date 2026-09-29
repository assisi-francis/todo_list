import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import Todo

# Use a file-based SQLite for tests to avoid :memory: connection issues with FastAPI's threading
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_todos.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_todo():
    response = client.post("/api/todos/", json={"title": "Test Task"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["completed"] is False

def test_create_todo_empty_title():
    response = client.post("/api/todos/", json={"title": "  "})
    assert response.status_code == 422

def test_create_todo_too_long():
    response = client.post("/api/todos/", json={"title": "a" * 101})
    assert response.status_code == 422

def test_list_todos_order():
    client.post("/api/todos/", json={"title": "Task 1"})
    client.post("/api/todos/", json={"title": "Task 2"})
    response = client.get("/api/todos/")
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Task 2"

def test_filter_todos():
    client.post("/api/todos/", json={"title": "Active Task"})
    client.post("/api/todos/", json={"title": "Completed Task"})
    
    todos = client.get("/api/todos/").json()
    todo_id = todos[0]["id"]
    client.patch(f"/api/todos/{todo_id}", json={"completed": True})
    
    res_active = client.get("/api/todos/?status=active").json()
    assert len(res_active) == 1
    res_comp = client.get("/api/todos/?status=completed").json()
    assert len(res_comp) == 1

def test_update_todo():
    client.post("/api/todos/", json={"title": "Old Title"})
    todo_id = client.get("/api/todos/").json()[0]["id"]
    response = client.patch(f"/api/todos/{todo_id}", json={"title": "New Title"})
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"

def test_update_missing_todo():
    response = client.patch("/api/todos/999", json={"title": "Ghost"})
    assert response.status_code == 404

def test_delete_todo():
    client.post("/api/todos/", json={"title": "Delete Me"})
    todo_id = client.get("/api/todos/").json()[0]["id"]
    response = client.delete(f"/api/todos/{todo_id}")
    assert response.status_code == 204
    assert len(client.get("/api/todos/").json()) == 0

def test_clear_completed():
    client.post("/api/todos/", json={"title": "Task 1"})
    client.post("/api/todos/", json={"title": "Task 2"})
    todos = client.get("/api/todos/").json()
    for t in todos:
        client.patch(f"/api/todos/{t['id']}", json={"completed": True})
        
    response = client.delete("/api/todos/completed")
    assert response.status_code == 200
    assert response.json()["deleted"] == 2
    assert len(client.get("/api/todos/").json()) == 0
