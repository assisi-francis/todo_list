from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .database import get_db
from .models import Todo
from .schemas import TodoCreate, TodoUpdate, TodoOut

router = APIRouter(prefix="/api/todos", tags=["todos"])

@router.get("/", response_model=List[TodoOut])
def list_todos(status: Optional[str] = "all", db: Session = Depends(get_db)):
    query = db.query(Todo)
    if status == "active":
        query = query.filter(Todo.completed == False)
    elif status == "completed":
        query = query.filter(Todo.completed == True)
    
    return query.order_by(Todo.created_at.desc()).all()

@router.post("/", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
def create_todo(todo_in: TodoCreate, db: Session = Depends(get_db)):
    db_todo = Todo(title=todo_in.title)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@router.patch("/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, todo_in: TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if todo_in.title is not None:
        db_todo.title = todo_in.title
    if todo_in.completed is not None:
        db_todo.completed = todo_in.completed
        
    db.commit()
    db.refresh(db_todo)
    return db_todo

@router.delete("/completed", status_code=status.HTTP_200_OK)
def clear_completed(db: Session = Depends(get_db)):
    deleted_count = db.query(Todo).filter(Todo.completed == True).delete()
    db.commit()
    return {"deleted": deleted_count}

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(db_todo)
    db.commit()
    return None
