"""Enums for the timer application."""

from enum import Enum


class TimerAction(Enum):
    """Available timer actions."""
    
    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    STOP = "stop"
    RESET = "reset"
    NEXT_STEP = "next_step"
    PREVIOUS_STEP = "previous_step"