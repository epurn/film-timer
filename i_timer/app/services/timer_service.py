"""Timer business logic service."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.timer_models import Timer, TimerStep
from app.schemas.timer_schemas import TimerCreate, TimerUpdate, TimerStepCreate


async def get_timer_by_id(db: AsyncSession, timer_id: int) -> Optional[Timer]:
    """Get timer by ID with all steps."""
    result = await db.execute(
        select(Timer)
        .options(selectinload(Timer.steps))
        .where(Timer.id == timer_id)
    )
    return result.scalar_one_or_none()


async def get_timers(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Timer]:
    """Get list of timers with basic info."""
    result = await db.execute(
        select(Timer)
        .options(selectinload(Timer.steps))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def create_timer(db: AsyncSession, timer_data: TimerCreate) -> Timer:
    """Create a new timer with steps."""
    # Create timer
    db_timer = Timer(
        name=timer_data.name,
        description=timer_data.description
    )
    db.add(db_timer)
    await db.flush()  # Get the timer ID
    
    # Create steps
    for step_data in timer_data.steps:
        db_step = TimerStep(
            timer_id=db_timer.id,
            title=step_data.title,
            duration_seconds=step_data.duration_seconds,
            repetitions=step_data.repetitions,
            notes=step_data.notes,
            order_index=step_data.order_index
        )
        db.add(db_step)
    
    await db.commit()
    await db.refresh(db_timer)
    
    # Return timer with steps
    return await get_timer_by_id(db, db_timer.id)


async def update_timer(db: AsyncSession, timer_id: int, timer_data: TimerUpdate) -> Optional[Timer]:
    """Update an existing timer."""
    db_timer = await get_timer_by_id(db, timer_id)
    if not db_timer:
        return None
    
    # Update timer fields
    if timer_data.name is not None:
        db_timer.name = timer_data.name
    if timer_data.description is not None:
        db_timer.description = timer_data.description
    
    await db.commit()
    await db.refresh(db_timer)
    return db_timer


async def delete_timer(db: AsyncSession, timer_id: int) -> bool:
    """Delete a timer and all its steps."""
    db_timer = await get_timer_by_id(db, timer_id)
    if not db_timer:
        return False
    
    await db.delete(db_timer)
    await db.commit()
    return True


async def add_timer_step(db: AsyncSession, timer_id: int, step_data: TimerStepCreate) -> Optional[TimerStep]:
    """Add a new step to an existing timer."""
    # Verify timer exists
    db_timer = await get_timer_by_id(db, timer_id)
    if not db_timer:
        return None
    
    # Create step
    db_step = TimerStep(
        timer_id=timer_id,
        title=step_data.title,
        duration_seconds=step_data.duration_seconds,
        repetitions=step_data.repetitions,
        notes=step_data.notes,
        order_index=step_data.order_index
    )
    
    db.add(db_step)
    await db.commit()
    await db.refresh(db_step)
    return db_step


async def delete_timer_step(db: AsyncSession, timer_id: int, step_id: int) -> bool:
    """Delete a specific timer step."""
    result = await db.execute(
        select(TimerStep).where(
            TimerStep.id == step_id,
            TimerStep.timer_id == timer_id
        )
    )
    db_step = result.scalar_one_or_none()
    
    if not db_step:
        return False
    
    await db.delete(db_step)
    await db.commit()
    return True