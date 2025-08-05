"""Action API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.timer_schemas import TimerAction, TimerActionResponse
from app.services import action_service

router = APIRouter(prefix="/actions", tags=["actions"])


@router.get("/", response_model=list[str])
async def get_actions():
    """Get the list of actions."""
    return await action_service.get_actions()

@router.post("/start", response_model=TimerActionResponse)
async def start_timer(
    timer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Start the timer."""
    return await action_service.start_timer(db, timer_id)

@router.post("/pause", response_model=TimerActionResponse)
async def pause_timer(timer_id: int):
    """Pause the timer."""
    return await action_service.pause_timer(timer_id)

@router.post("/resume", response_model=TimerActionResponse)
async def resume_timer(timer_id: int):
    """Resume the timer."""
    return await action_service.resume_timer(timer_id)

@router.post("/stop", response_model=TimerActionResponse)
async def stop_timer(timer_id: int):
    """Stop the timer."""
    return await action_service.stop_timer(timer_id)

@router.get("/status/{timer_id}", response_model=TimerActionResponse)
async def get_timer_status(timer_id: int):
    """Get the current status of a timer."""
    return await action_service.get_timer_status(timer_id)