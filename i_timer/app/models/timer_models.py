"""Timer database models."""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Timer(Base):
    """Timer model representing a complete interval timer."""
    
    __tablename__ = "timers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship to timer steps
    steps = relationship("TimerStep", back_populates="timer", cascade="all, delete-orphan")


class TimerStep(Base):
    """TimerStep model representing individual steps within a timer."""
    
    __tablename__ = "timer_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    timer_id = Column(Integer, ForeignKey("timers.id"), nullable=False)
    order_index = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    repetitions = Column(Integer, nullable=False, default=1)
    notes = Column(Text, nullable=True)
    
    # Relationship to timer
    timer = relationship("Timer", back_populates="steps")