"""Timer state management for tracking running timers."""

from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
from typing import List
import asyncio
from contextlib import asynccontextmanager

from app.schemas.timer_schemas import TimerStep, Timer


class TimerStatus(Enum):
    """Timer status enumeration."""
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    FINISHED = "finished"

@dataclass
class TimerStepData:
    """Represents the current state of a step in a timer."""
    step_index: int
    duration_seconds: int
    repetitions: int


@dataclass
class TimerState:
    """Represents the current state of a running timer."""
    timer_id: int
    status: TimerStatus
    current_step_index: int
    current_repetition: int
    time_in_step: int  # seconds
    time_in_timer: int  # total seconds elapsed
    start_time: datetime
    total_duration: int
    steps: List[TimerStepData] = field(default_factory=list)
    pause_time: Optional[datetime] = None
    total_time_paused: timedelta = timedelta(0)


class TimerStateManager:
    """Manages the state of running timers."""
    
    def __init__(self):
        self._timers: Dict[int, TimerState] = {}
        self._tasks: Dict[int, asyncio.Task] = {}

    def _calculate_total_duration(self, steps: List[TimerStepData]) -> int:
        """Calculate the total duration of a timer."""
        return sum(step.duration_seconds * step.repetitions for step in steps)
    
    
    def _update_timer_state(self, timer_id: int):
        """Update the state of a timer."""
        if timer_id not in self._timers:
            return
            
        state = self._timers[timer_id]
        
        # Calculate elapsed time accounting for pauses
        current_time = datetime.now()
        elapsed_time = current_time - state.start_time
        total_elapsed = int(elapsed_time.total_seconds())
        paused_seconds = int(state.total_time_paused.total_seconds())
        state.time_in_timer = total_elapsed - paused_seconds
        
        # Check if timer is finished
        if state.time_in_timer >= state.total_duration:
            state.status = TimerStatus.FINISHED
            state.current_step_index = len(state.steps) - 1
            state.current_repetition = state.steps[-1].repetitions
            state.time_in_step = state.steps[-1].duration_seconds
            self._timers[timer_id] = state
            return
        
        # Simple while loop to advance through steps
        step_time = 0
        step_idx = 0
        repetition = 1
        
        while step_idx < len(state.steps):
            step = state.steps[step_idx]
            step_duration = step.duration_seconds
            
            # Check if we've moved past this step
            if state.time_in_timer >= step_time + (step_duration * step.repetitions):
                step_time += step_duration * step.repetitions
                step_idx += 1
                repetition = 1
            else:
                # We're in this step
                remaining_time = state.time_in_timer - step_time
                repetition = (remaining_time // step_duration) + 1
                repetition = min(repetition, step.repetitions)
                
                time_in_step = remaining_time % step_duration
                if time_in_step == 0 and repetition > 1:
                    time_in_step = step_duration
                
                # Update state
                state.current_step_index = step_idx
                state.current_repetition = repetition
                state.time_in_step = time_in_step
                break
            
    def get_timer_state(self, timer_id: int) -> Optional[TimerState]:
        """Get the current state of a timer."""
        self._update_timer_state(timer_id)
        return self._timers.get(timer_id)
    
    def is_timer_running(self, timer_id: int) -> bool:
        """Check if a timer is currently running."""
        self._update_timer_state(timer_id)
        return timer_id in self._timers and self._timers[timer_id].status == TimerStatus.RUNNING
    
    def start_timer(self, timer_id: int, steps: List[TimerStepData]) -> TimerState:
        """Start a new timer."""
        state = TimerState(
            timer_id=timer_id,
            status=TimerStatus.RUNNING,
            steps=steps,
            current_step_index=0,
            current_repetition=1,
            time_in_step=0,
            time_in_timer=0,
            start_time=datetime.now(),
            total_duration=self._calculate_total_duration(steps)
        )
        self._timers[timer_id] = state
        return state
    
    def pause_timer(self, timer_id: int) -> Optional[TimerState]:
        """Pause a running timer."""
        if timer_id not in self._timers:
            return None
        
        state = self._timers[timer_id]
        if state.status == TimerStatus.RUNNING:
            state.status = TimerStatus.PAUSED
            state.pause_time = datetime.now()
        return state
    
    def resume_timer(self, timer_id: int) -> Optional[TimerState]:
        """Resume a paused timer."""
        if timer_id not in self._timers:
            return None
        
        state = self._timers[timer_id]
        if state.status == TimerStatus.PAUSED:
            state.status = TimerStatus.RUNNING
            # Adjust pause time to account for pause duration
            if state.pause_time:
                pause_duration = datetime.now() - state.pause_time
                state.total_time_paused += pause_duration
            state.pause_time = None
        return state
    
    def stop_timer(self, timer_id: int) -> Optional[TimerState]:
        """Stop a timer."""
        if timer_id not in self._timers:
            return None
        
        state = self._timers[timer_id]
        state.status = TimerStatus.STOPPED
        self._update_timer_state(timer_id)
        return state
    
    def remove_timer(self, timer_id: int):
        """Remove a timer from tracking."""
        self._timers.pop(timer_id, None)
        if timer_id in self._tasks:
            self._tasks[timer_id].cancel()
            del self._tasks[timer_id]


# Global timer state manager
timer_manager = TimerStateManager() 