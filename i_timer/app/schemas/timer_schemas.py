"""Pydantic schemas for timer operations."""

from datetime import datetime
from token import OP
from typing import Optional
from pydantic import BaseModel, Field
from app.enums import TimerAction


class TimerStepBase(BaseModel):
    """Base schema for timer steps."""
    
    title: str = Field(..., min_length=1, max_length=255)
    duration_seconds: int = Field(..., ge=1)
    repetitions: int = Field(default=1, ge=1)
    notes: Optional[str] = None


class TimerStepCreate(TimerStepBase):
    """Schema for creating timer steps."""
    
    order_index: int = Field(..., ge=0)


class TimerStepUpdate(BaseModel):
    """Schema for updating timer steps."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    duration_seconds: Optional[int] = Field(None, ge=1)
    repetitions: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = None
    order_index: Optional[int] = Field(None, ge=0)


class TimerStep(TimerStepBase):
    """Schema for timer step responses."""
    
    id: int
    timer_id: int
    order_index: int
    
    class Config:
        from_attributes = True


class TimerBase(BaseModel):
    """Base schema for timers."""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class TimerCreate(TimerBase):
    """Schema for creating timers."""
    
    steps: list[TimerStepCreate] = []


class TimerUpdate(BaseModel):
    """Schema for updating timers."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class Timer(TimerBase):
    """Schema for timer responses."""
    
    id: int
    created_at: datetime
    updated_at: datetime
    steps: list[TimerStep] = []
    
    class Config:
        from_attributes = True


class TimerExport(BaseModel):
    """Schema for timer export data."""
    
    timer_name: str
    timer_description: Optional[str]
    steps: list[TimerStep]
    
    class Config:
        from_attributes = True


class TimerAction(BaseModel):
    """Schema for timer actions."""
    action: TimerAction
    timer_id: int
    step_id: Optional[int] = None


class TimerActionResponse(BaseModel):
    """Schema for timer action responses."""
    message: str
    time_in_step: int
    time_in_timer: int
    total_time: int
    state: str  # "running", "paused", "stopped", "finished"