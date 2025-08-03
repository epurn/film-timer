"""Unit tests for timer service."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.timer_service import (
    create_timer,
    get_timer_by_id,
    get_timers,
    update_timer,
    delete_timer,
    add_timer_step,
    delete_timer_step
)
from app.schemas.timer_schemas import TimerCreate, TimerUpdate, TimerStepCreate


@pytest.mark.asyncio
async def test_create_timer(db_session: AsyncSession):
    """Test creating a timer with steps."""
    timer_data = TimerCreate(
        name="Test Timer",
        description="A test timer",
        steps=[
            TimerStepCreate(
                title="Warm up",
                duration_seconds=300,
                repetitions=1,
                order_index=0,
                notes="Light warm up"
            ),
            TimerStepCreate(
                title="Work",
                duration_seconds=1200,
                repetitions=3,
                order_index=1,
                notes="High intensity"
            )
        ]
    )
    
    timer = await create_timer(db_session, timer_data)
    
    assert timer.id is not None
    assert timer.name == "Test Timer"
    assert timer.description == "A test timer"
    assert len(timer.steps) == 2
    assert timer.steps[0].title == "Warm up"
    assert timer.steps[0].duration_seconds == 300
    assert timer.steps[1].repetitions == 3


@pytest.mark.asyncio
async def test_get_timer_by_id(db_session: AsyncSession):
    """Test getting a timer by ID."""
    # Create a timer first
    timer_data = TimerCreate(
        name="Test Timer",
        steps=[
            TimerStepCreate(
                title="Step 1",
                duration_seconds=60,
                order_index=0
            )
        ]
    )
    created_timer = await create_timer(db_session, timer_data)
    
    # Get the timer
    retrieved_timer = await get_timer_by_id(db_session, created_timer.id)
    
    assert retrieved_timer is not None
    assert retrieved_timer.id == created_timer.id
    assert retrieved_timer.name == "Test Timer"
    assert len(retrieved_timer.steps) == 1


@pytest.mark.asyncio
async def test_get_timer_by_id_not_found(db_session: AsyncSession):
    """Test getting a non-existent timer."""
    timer = await get_timer_by_id(db_session, 999)
    assert timer is None


@pytest.mark.asyncio
async def test_get_timers(db_session: AsyncSession):
    """Test getting list of timers."""
    # Create multiple timers
    for i in range(3):
        timer_data = TimerCreate(
            name=f"Timer {i}",
            steps=[]
        )
        await create_timer(db_session, timer_data)
    
    timers = await get_timers(db_session)
    assert len(timers) == 3


@pytest.mark.asyncio
async def test_update_timer(db_session: AsyncSession):
    """Test updating a timer."""
    # Create a timer
    timer_data = TimerCreate(name="Original Timer", steps=[])
    timer = await create_timer(db_session, timer_data)
    
    # Update the timer
    update_data = TimerUpdate(
        name="Updated Timer",
        description="Updated description"
    )
    updated_timer = await update_timer(db_session, timer.id, update_data)
    
    assert updated_timer is not None
    assert updated_timer.name == "Updated Timer"
    assert updated_timer.description == "Updated description"


@pytest.mark.asyncio
async def test_delete_timer(db_session: AsyncSession):
    """Test deleting a timer."""
    # Create a timer
    timer_data = TimerCreate(name="Timer to delete", steps=[])
    timer = await create_timer(db_session, timer_data)
    
    # Delete the timer
    success = await delete_timer(db_session, timer.id)
    assert success is True
    
    # Verify it's gone
    deleted_timer = await get_timer_by_id(db_session, timer.id)
    assert deleted_timer is None


@pytest.mark.asyncio
async def test_add_timer_step(db_session: AsyncSession):
    """Test adding a step to an existing timer."""
    # Create a timer
    timer_data = TimerCreate(name="Test Timer", steps=[])
    timer = await create_timer(db_session, timer_data)
    
    # Add a step
    step_data = TimerStepCreate(
        title="New Step",
        duration_seconds=120,
        order_index=0
    )
    step = await add_timer_step(db_session, timer.id, step_data)
    
    assert step is not None
    assert step.title == "New Step"
    assert step.timer_id == timer.id


@pytest.mark.asyncio
async def test_delete_timer_step(db_session: AsyncSession):
    """Test deleting a timer step."""
    # Create a timer with a step
    timer_data = TimerCreate(
        name="Test Timer",
        steps=[
            TimerStepCreate(
                title="Step to delete",
                duration_seconds=60,
                order_index=0
            )
        ]
    )
    timer = await create_timer(db_session, timer_data)
    step_id = timer.steps[0].id
    
    # Delete the step
    success = await delete_timer_step(db_session, timer.id, step_id)
    assert success is True
    
    # Verify it's gone
    updated_timer = await get_timer_by_id(db_session, timer.id)
    assert len(updated_timer.steps) == 0