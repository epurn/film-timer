"""Action business logic service."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from fastapi import HTTPException

from app.models.timer_models import Timer
from app.schemas.timer_schemas import TimerActionResponse
from app.enums import TimerAction
from app.services.timer_state import timer_manager, TimerState, TimerStatus


def calculate_total_duration(timer: Timer) -> int:
    """Calculate the total duration of a timer."""
    duration = 0
    for step in timer.steps:
        duration += step.duration_seconds * step.repetitions
    return duration

def calculate_timer_progress(timer: Timer, state: TimerState) -> float:
    """Calculate the progress of a timer."""
    
    if state.status == TimerStatus.RUNNING:
        cur_total_time = datetime.now() - (state.start_time + state.pause_time)
        return cur_total_time / calculate_total_duration(timer)
    elif state.status == TimerStatus.PAUSED:
        return state.time_in_timer / calculate_total_duration(timer)
    elif state.status == TimerStatus.STOPPED:
        return state.time_in_timer / calculate_total_duration(timer)
    elif state.status == TimerStatus.FINISHED:
        return 1
    else:
        return 0

async def get_actions() -> list[TimerAction]:
    """Get the list of actions."""
    return [action.value for action in TimerAction]

async def start_timer(db: AsyncSession, timer_id: int) -> TimerActionResponse:
    """Start the timer."""
    timer = await db.get(Timer, timer_id)
    if not timer:
        raise HTTPException(status_code=404, detail="Timer not found")
    
    total_duration = calculate_total_duration(timer)
    timer_state = timer_manager.start_timer(timer_id, total_duration)
    return TimerActionResponse(
        message="Timer started",
        time_in_step=timer_state.time_in_step,
        time_in_timer=timer_state.time_in_timer,
        total_time=timer_state.total_duration,
        is_finished=timer_state.is_finished,
        is_paused=timer_state.is_paused,
        is_running=timer_state.is_running,
        is_stopped=timer_state.is_stopped)