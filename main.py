from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, Depends
from sqlmodel import Session, select

from database import create_db_and_tables, get_session
from models import Task, TaskCreate, TaskUpdate, TaskRead, TaskStatus, TaskPriority


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Task Management API",
    description="A REST API for managing tasks with full CRUD operations",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"message": "Welcome to Task Management API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# CREATE - Add a new task
@app.post("/tasks", response_model=TaskRead, status_code=201)
async def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


# READ - Get all tasks with optional filtering
@app.get("/tasks", response_model=list[TaskRead])
async def get_tasks(
    session: Session = Depends(get_session),
    status: TaskStatus | None = Query(default=None, description="Filter by status"),
    priority: TaskPriority | None = Query(default=None, description="Filter by priority"),
    skip: int = Query(default=0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Number of tasks to return"),
):
    query = select(Task)

    if status:
        query = query.where(Task.status == status)

    if priority:
        query = query.where(Task.priority == priority)

    query = query.offset(skip).limit(limit)
    tasks = session.exec(query).all()
    return tasks


# READ - Get a single task by ID
@app.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# UPDATE - Update a task
@app.put("/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int, task_update: TaskUpdate, session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.now()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# DELETE - Delete a task
@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return None
