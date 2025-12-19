from datetime import date, timedelta
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps.auth import get_subscribed_user
from app.models.backlog import Backlog
from app.models.user import User
from app.schemas.backlog import BacklogCreate, BacklogOut, BacklogUpdate

# Create a router
router = APIRouter()


@router.get("/", response_model=List[BacklogOut])
def get_backlogs(
    db: Session = Depends(get_db),
    user: User = Depends(get_subscribed_user),
):
    """
    Get backlogs for the current user.
    """
    user_id = user.id
    query = db.query(Backlog).filter(Backlog.user_id == user_id)
    return query.order_by(Backlog.order).all()


@router.post("/", response_model=BacklogOut)
def create_backlog(
    backlog: BacklogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_subscribed_user),
):
    """
    Create a new backlog for the current user.
    """
    user_id = user.id

    # Shift existing backlogs' order by 1
    db.query(Backlog).filter(Backlog.user_id == user_id).update(
        {"order": Backlog.order + 1}
    )

    # Create the new backlog
    new_backlog = Backlog(
        user_id=user_id,
        date=date.today(),
        detail=backlog.detail,
        order=1,
    )

    db.add(new_backlog)
    db.commit()
    db.refresh(new_backlog)

    return new_backlog


@router.patch("/{backlog_id}", response_model=BacklogOut)
def update_backlog(
    backlog_id: int,
    updates: BacklogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_subscribed_user),
):
    """
    Update a backlog for the current user.
    """
    user_id = user.id
    backlog = (
        db.query(Backlog)
        .filter(Backlog.id == backlog_id, Backlog.user_id == user_id)
        .first()
    )
    if not backlog:
        raise HTTPException(status_code=404, detail="Backlog not found")

    update_data = updates.model_dump(exclude_unset=True)

    # Enforce only one type of update at a time
    update_fields = set(update_data.keys())
    groups = {
        "order": {"order"},
        "detail": {"detail"},
    }

    matched_groups = [group for group, keys in groups.items() if update_fields & keys]
    if len(matched_groups) > 1:
        raise HTTPException(
            status_code=400,
            detail="Only one type of update is allowed per request (order or detail).",
        )

    # Handle order update
    if "order" in update_fields:
        new_order = update_data.get("order")
        if new_order is None or new_order < 1:
            raise HTTPException(status_code=400, detail="Order must be 1 or greater")

        other_backlogs = (
            db.query(Backlog)
            .filter(Backlog.user_id == user_id, Backlog.id != backlog_id)
            .order_by(Backlog.order)
            .all()
        )

        # Ensure the new order is within the valid range
        max_order = len(other_backlogs) + 1
        if new_order > max_order:
            new_order = max_order

        current_order = getattr(backlog, "order")
        for t in other_backlogs:
            t_order = getattr(t, "order")
            # Shift backlogs down
            if current_order < new_order:
                if current_order < t_order <= new_order:
                    setattr(t, "order", t_order - 1)
            # Shift backlogs up
            else:
                if new_order <= t_order < current_order:
                    setattr(t, "order", t_order + 1)

        setattr(backlog, "order", new_order)

    # Handle detail and date update
    elif {"detail"} & update_fields:
        setattr(backlog, "detail", update_data.get("detail"))
        setattr(backlog, "date", date.today())

    db.commit()
    db.refresh(backlog)
    return backlog


@router.delete("/{backlog_id}")
def delete_backlog(
    backlog_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_subscribed_user),
):
    """
    Delete a backlog for the current user.
    """
    user_id = user.id
    backlog = (
        db.query(Backlog)
        .filter(Backlog.id == backlog_id, Backlog.user_id == user_id)
        .first()
    )
    if not backlog:
        raise HTTPException(status_code=404, detail="Backlog not found")

    backlog_order = backlog.order

    db.delete(backlog)
    db.commit()

    # Reorder the remaining backlogs
    remaining_backlogs = (
        db.query(Backlog)
        .filter(Backlog.user_id == user_id, Backlog.order > backlog_order)
        .order_by(Backlog.order)
        .all()
    )

    for t in remaining_backlogs:
        setattr(t, "order", getattr(t, "order") - 1)

    db.commit()
    return {"message": "Backlog deleted and remaining reordered"}
