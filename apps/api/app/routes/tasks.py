from datetime import date, timedelta
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps.auth import get_user
from app.models.task import Task
from app.models.user import User
from app.schemas.task import CompletionOut, TaskCreate, TaskOut, TaskUpdate

# Create a router
router = APIRouter()


@router.get("/", response_model=List[TaskOut])
def get_tasks(
    start: Optional[date] = None,
    end: Optional[date] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_user),
):
    """
    Get tasks for the current user between the start and end dates.
    """
    user_id = user.id
    query = db.query(Task).filter(Task.user_id == user_id)
    if start and end:
        query = query.filter(Task.date.between(start, end))
    return query.order_by(Task.order).all()


@router.post("/", response_model=TaskOut)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_user),
):
    """
    Create a new task for the current user.
    """
    user_id = user.id

    # Shift existing tasks' order by 1
    db.query(Task).filter(Task.user_id == user_id, Task.date == task.date).update(
        {Task.order: Task.order + 1}
    )

    # Create the new task
    new_task = Task(
        user_id=user_id,
        date=task.date,
        title=task.title,
        note=task.note,
        is_completed=task.is_completed,
        order=1,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    updates: TaskUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_user),
):
    """
    Update a task for the current user.
    """
    user_id = user.id
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = updates.model_dump(exclude_unset=True)

    # Enforce only one type of update at a time
    update_fields = set(update_data.keys())
    groups = {
        "date": {"date"},
        "order": {"order"},
        "text": {"title", "note"},
        "completed": {"is_completed"},
    }

    matched_groups = [group for group, keys in groups.items() if update_fields & keys]
    if len(matched_groups) > 1:
        raise HTTPException(
            status_code=400,
            detail="Only one type of update is allowed per request (order, title/note, or is_completed).",
        )

    # Handle date update
    if "date" in update_fields:
        new_date = update_data["date"]
        old_date = task.date

        # Check if the new date is valid
        if new_date != old_date:
            task.date = new_date

            # Reorder tasks from the old date
            old_day_tasks = (
                db.query(Task)
                .filter(
                    Task.user_id == user_id, Task.date == old_date, Task.id != task.id
                )
                .order_by(Task.order)
                .all()
            )
            for idx, t in enumerate(old_day_tasks, start=1):
                setattr(t, "order", idx)

            # Shift other tasks on the new date
            new_day_tasks = (
                db.query(Task)
                .filter(
                    Task.user_id == user_id, Task.date == new_date, Task.id != task.id
                )
                .order_by(Task.order.desc())
                .all()
            )
            for t in new_day_tasks:
                setattr(t, "order", getattr(t, "order") + 1)

            # Put the moved task at the top
            setattr(task, "order", 1)

    # Handle order update
    elif "order" in update_fields:
        new_order = update_data.get("order")
        if new_order is None or new_order < 1:
            raise HTTPException(status_code=400, detail="Order must be 1 or greater")

        same_day_tasks = (
            db.query(Task)
            .filter(Task.user_id == user_id, Task.date == task.date, Task.id != task_id)
            .order_by(Task.order)
            .all()
        )

        # Ensure the new order is within the valid range
        max_order = len(same_day_tasks) + 1
        if new_order > max_order:
            new_order = max_order

        current_order = getattr(task, "order")
        for t in same_day_tasks:
            t_order = getattr(t, "order")
            # Shift tasks down
            if current_order < new_order:
                if current_order < t_order <= new_order:
                    setattr(t, "order", t_order - 1)
            # Shift tasks up
            else:
                if new_order <= t_order < current_order:
                    setattr(t, "order", t_order + 1)

        setattr(task, "order", new_order)

    # Handle title/note update
    elif {"title", "note"} & update_fields:
        update_title_or_note = any(k in update_data for k in ["title", "note"])
        for key, value in update_data.items():
            setattr(task, key, value)

    # Handle is_completed update
    elif "is_completed" in update_fields:
        new_status = update_data["is_completed"]
        task.is_completed = new_status

        # Get all tasks for the same day (excluding the current task)
        same_day_tasks = (
            db.query(Task)
            .filter(Task.user_id == user_id, Task.date == task.date, Task.id != task.id)
            .order_by(Task.order)
            .all()
        )

        if new_status:
            # If marking as completed, move the task to the last position.
            current_order = getattr(task, "order")
            for t in same_day_tasks:
                t_order = getattr(t, "order")
                if t_order > current_order:
                    setattr(t, "order", t_order - 1)
            setattr(task, "order", len(same_day_tasks) + 1)
        else:
            # If marking as incomplete, move the task to the first position.
            for t in same_day_tasks:
                setattr(t, "order", getattr(t, "order") + 1)
            setattr(task, "order", 1)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_user),
):
    """
    Delete a task for the current user.
    """
    user_id = user.id
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    affected_dates = []

    # Delete the single task
    affected_dates = [task.date]
    db.delete(task)

    db.commit()

    # Reorder the remaining tasks
    for d in affected_dates:
        remaining_tasks = (
            db.query(Task)
            .filter(Task.user_id == user_id, Task.date == d)
            .order_by(Task.order)
            .all()
        )

        for i, t in enumerate(remaining_tasks, start=1):
            setattr(t, "order", i)

    db.commit()
    return {"message": "Task(s) deleted and reordered"}


@router.get("/completion/", response_model=List[CompletionOut])
def get_completion_status(
    start: date,
    end: date,
    db: Session = Depends(get_db),
    user: User = Depends(get_user),
):
    user_id = user.id

    # Create an expression to sum up completed tasks (1 if completed, else 0)
    completed_sum = func.sum(case((Task.is_completed == True, 1), else_=0)).label(
        "completed"
    )

    # Query for each day: count total tasks and sum the completed tasks.
    results = (
        db.query(
            Task.date,
            func.count(Task.id).label("total"),
            completed_sum,
        )
        .filter(
            Task.user_id == user_id,
            Task.date.between(start, end),
        )
        .group_by(Task.date)
        .order_by(Task.date)
        .all()
    )

    # Format the results
    completions = [
        {
            "date": row.date,
            "total": row.total,
            "completed": row.completed or 0,
        }
        for row in results
    ]
    return completions
