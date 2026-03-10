from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.crud import create_task, delete_task, get_task, get_tasks, update_task
from app.database import Base, engine, get_db, wait_for_db
from app.schemas import TaskCreate, TaskResponse, TaskUpdate

@asynccontextmanager
async def lifespan(application: FastAPI):
    wait_for_db()
    Base.metadata.create_all(bind=engine)
    print("[APP] Tables created, app is ready!")
    yield
    print("[APP] Shutting down...")
app = FastAPI(
    title="Lam Viec 360 - Task API",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/")
def root():
    return {"message": "Lam Viec 360 - Task CRUD API"}

@app.get("/tasks", response_model=list[TaskResponse])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_tasks(db, skip=skip, limit=limit)

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create(task_in: TaskCreate, db: Session = Depends(get_db)):
    return create_task(db, task_in)

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update(task_id: int, task_in: TaskUpdate, db: Session = Depends(get_db)):
    task = update_task(db, task_id, task_in)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.delete("/tasks/{task_id}")
def delete(task_id: int, db: Session = Depends(get_db)):
    success = delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted"}
