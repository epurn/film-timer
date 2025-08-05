"""Action API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.timer_schemas import TimerAction, TimerActionResponse
from app.services import action_service

router = APIRouter(prefix="/actions", tags=["actions"])


@router.get("/", response_model=TimerActionResponse)
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

@router.get("/pause", response_model=TimerActionResponse)
async def pause_timer():
    pass