"""Action business logic service."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from fastapi import HTTPException

from app.models.timer_models import Timer
from app.schemas.timer_schemas import TimerActionResponse
from app.enums import TimerAction
from app.services.timer_state import timer_manager, TimerStepData


async def get_actions() -> list[TimerAction]:
    """Get the list of actions."""
    return [action.value for action in TimerAction]


async def start_timer(db: AsyncSession, timer_id: int) -> TimerActionResponse:
    """Start the timer."""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    # Use select with eager loading to avoid lazy loading issues
    stmt = select(Timer).options(selectinload(Timer.steps)).where(Timer.id == timer_id)
    result = await db.execute(stmt)
    timer = result.scalar_one_or_none()
    
    if not timer:
        raise HTTPException(status_code=404, detail="Timer not found")
    
    steps = []
    i = 0
    for step in timer.steps:
        steps.append(TimerStepData(step_index=i, duration_seconds=step.duration_seconds, repetitions=step.repetitions))
        i += 1

    timer_state = timer_manager.start_timer(timer_id, steps)
    return TimerActionResponse(
        message="Timer started",
        time_in_step=timer_state.time_in_step,
        time_in_timer=timer_state.time_in_timer,
        total_time=timer_state.total_duration,
        state=timer_state.status.value)


async def pause_timer(timer_id: int) -> TimerActionResponse:
    """Pause the timer."""
    timer_state = timer_manager.pause_timer(timer_id)
    if not timer_state:
        raise HTTPException(status_code=404, detail="Timer not found or not running")
    return TimerActionResponse(
        message="Timer paused",
        time_in_step=timer_state.time_in_step,
        time_in_timer=timer_state.time_in_timer,
        total_time=timer_state.total_duration,
        state=timer_state.status.value)


async def resume_timer(timer_id: int) -> TimerActionResponse:
    """Resume the timer."""
    timer_state = timer_manager.resume_timer(timer_id)
    if not timer_state:
        raise HTTPException(status_code=404, detail="Timer not found or not paused")
    return TimerActionResponse(
        message="Timer resumed",
        time_in_step=timer_state.time_in_step,
        time_in_timer=timer_state.time_in_timer,
        total_time=timer_state.total_duration,
        state=timer_state.status.value)


async def stop_timer(timer_id: int) -> TimerActionResponse:
    """Stop the timer."""
    timer_state = timer_manager.stop_timer(timer_id)
    if not timer_state:
        raise HTTPException(status_code=404, detail="Timer not found")
    return TimerActionResponse(
        message="Timer stopped",
        time_in_step=timer_state.time_in_step,
        time_in_timer=timer_state.time_in_timer,
        total_time=timer_state.total_duration,
        state=timer_state.status.value)


async def get_timer_status(timer_id: int) -> TimerActionResponse:
    """Get the current status of a timer."""
    timer_state = timer_manager.get_timer_state(timer_id)
    if not timer_state:
        raise HTTPException(status_code=404, detail="Timer not found")
    return TimerActionResponse(
        message="Timer status retrieved",
        time_in_step=timer_state.time_in_step,
        time_in_timer=timer_state.time_in_timer,
        total_time=timer_state.total_duration,
        state=timer_state.status.value)