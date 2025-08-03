"""Timer API routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.timer_schemas import Timer, TimerCreate, TimerUpdate, TimerStep, TimerStepCreate
from app.services import timer_service

router = APIRouter(prefix="/timers", tags=["timers"])


@router.get("/", response_model=List[Timer])
async def get_timers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get list of timers."""
    timers = await timer_service.get_timers(db, skip=skip, limit=limit)
    return timers


@router.get("/{timer_id}", response_model=Timer)
async def get_timer(
    timer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific timer by ID."""
    timer = await timer_service.get_timer_by_id(db, timer_id)
    if not timer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timer not found"
        )
    return timer


@router.post("/", response_model=Timer, status_code=status.HTTP_201_CREATED)
async def create_timer(
    timer_data: TimerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new timer."""
    return await timer_service.create_timer(db, timer_data)


@router.put("/{timer_id}", response_model=Timer)
async def update_timer(
    timer_id: int,
    timer_data: TimerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing timer."""
    timer = await timer_service.update_timer(db, timer_id, timer_data)
    if not timer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timer not found"
        )
    return timer


@router.delete("/{timer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timer(
    timer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a timer."""
    success = await timer_service.delete_timer(db, timer_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timer not found"
        )


@router.post("/{timer_id}/steps", response_model=TimerStep, status_code=status.HTTP_201_CREATED)
async def add_timer_step(
    timer_id: int,
    step_data: TimerStepCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a new step to a timer."""
    step = await timer_service.add_timer_step(db, timer_id, step_data)
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timer not found"
        )
    return step


@router.delete("/{timer_id}/steps/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timer_step(
    timer_id: int,
    step_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a timer step."""
    success = await timer_service.delete_timer_step(db, timer_id, step_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timer or step not found"
        )