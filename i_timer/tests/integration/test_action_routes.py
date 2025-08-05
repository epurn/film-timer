"""Integration tests for action API routes."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.timer_models import Timer, TimerStep
from app.services.timer_state import timer_manager


@pytest.mark.asyncio
async def test_get_actions_endpoint(client: AsyncClient):
    """Test getting the list of actions via API."""
    response = await client.get("/api/v1/actions/")
    
    assert response.status_code == 200
    actions = response.json()
    assert isinstance(actions, list)
    assert len(actions) > 0
    assert all(isinstance(action, str) for action in actions)
    assert "start" in actions
    assert "pause" in actions
    assert "resume" in actions
    assert "stop" in actions


@pytest.mark.asyncio
async def test_start_timer_endpoint_success(client: AsyncClient, db_session: AsyncSession):
    """Test starting a timer via API."""
    # Create a timer with steps first
    timer_data = {
        "name": "Test Timer",
        "description": "Timer for action testing",
        "steps": [
            {
                "title": "Warm up",
                "duration_seconds": 300,
                "repetitions": 1,
                "order_index": 0,
                "notes": "Light warm up"
            },
            {
                "title": "Work",
                "duration_seconds": 1200,
                "repetitions": 2,
                "order_index": 1,
                "notes": "High intensity"
            }
        ]
    }
    create_response = await client.post("/api/v1/timers/", json=timer_data)
    timer_id = create_response.json()["id"]
    
    # Start the timer
    response = await client.post(f"/api/v1/actions/start?timer_id={timer_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Timer started"
    assert data["time_in_step"] >= 0
    assert data["time_in_timer"] >= 0
    assert data["total_time"] == 2700  # 300*1 + 1200*2
    assert data["state"] == "running"


@pytest.mark.asyncio
async def test_start_timer_not_found(client: AsyncClient):
    """Test starting a non-existent timer."""
    response = await client.post("/api/v1/actions/start?timer_id=999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Timer not found"


@pytest.mark.asyncio
async def test_pause_timer_endpoint_success(client: AsyncClient, db_session: AsyncSession):
    """Test pausing a timer via API."""
    # Create and start a timer
    timer_data = {
        "name": "Pause Test Timer",
        "steps": [
            {
                "title": "Step 1",
                "duration_seconds": 600,
                "repetitions": 1,
                "order_index": 0
            }
        ]
    }
    create_response = await client.post("/api/v1/timers/", json=timer_data)
    timer_id = create_response.json()["id"]
    
    # Start the timer
    await client.post(f"/api/v1/actions/start?timer_id={timer_id}")
    
    # Pause the timer
    response = await client.post(f"/api/v1/actions/pause?timer_id={timer_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Timer paused"
    assert data["state"] == "paused"
    assert data["time_in_step"] >= 0
    assert data["time_in_timer"] >= 0
    assert data["total_time"] == 600


@pytest.mark.asyncio
async def test_pause_timer_not_running(client: AsyncClient, db_session: AsyncSession):
    """Test pausing a timer that's not running."""
    # Create a timer but don't start it
    timer_data = {
        "name": "Not Running Timer",
        "steps": [
            {
                "title": "Step 1",
                "duration_seconds": 600,
                "repetitions": 1,
                "order_index": 0
            }
        ]
    }
    create_response = await client.post("/api/v1/timers/", json=timer_data)
    timer_id = create_response.json()["id"]
    
    # Try to pause without starting
    response = await client.post(f"/api/v1/actions/pause?timer_id={timer_id}")
    assert response.status_code == 404
    assert "not found or not running" in response.json()["detail"]


@pytest.mark.asyncio
async def test_resume_timer_endpoint_success(client: AsyncClient, db_session: AsyncSession):
    """Test resuming a timer via API."""
    # Create and start a timer
    timer_data = {
        "name": "Resume Test Timer",
        "steps": [
            {
                "title": "Step 1",
                "duration_seconds": 600,
                "repetitions": 1,
                "order_index": 0
            }
        ]
    }
    create_response = await client.post("/api/v1/timers/", json=timer_data)
    timer_id = create_response.json()["id"]
    
    # Start the timer
    await client.post(f"/api/v1/actions/start?timer_id={timer_id}")
    
    # Pause the timer
    await client.post(f"/api/v1/actions/pause?timer_id={timer_id}")
    
    # Resume the timer
    response = await client.post(f"/api/v1/actions/resume?timer_id={timer_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Timer resumed"
    assert data["state"] == "running"
    assert data["time_in_step"] >= 0
    assert data["time_in_timer"] >= 0
    assert data["total_time"] == 600


@pytest.mark.asyncio
async def test_resume_timer_not_paused(client: AsyncClient, db_session: AsyncSession):
    """Test resuming a timer that's not paused."""
    # Create and start a timer
    timer_data = {
        "name": "Not Paused Timer",
        "steps": [
            {
                "title": "Step 1",
                "duration_seconds": 600,
                "repetitions": 1,
                "order_index": 0
            }
        ]
    }
    create_response = await client.post("/api/v1/timers/", json=timer_data)
    timer_id = create_response.json()["id"]
    
    # Start the timer
    await client.post(f"/api/v1/actions/start?timer_id={timer_id}")
    
    # Try to resume without pausing
    response = await client.post(f"/api/v1/actions/resume?timer_id={timer_id}")
    assert response.status_code == 404
    assert "not found or not paused" in response.json()["detail"]


@pytest.mark.asyncio
async def test_stop_timer_endpoint_success(client: AsyncClient, db_session: AsyncSession):
    """Test stopping a timer via API."""
    # Create and start a timer
    timer_data = {
        "name": "Stop Test Timer",
        "steps": [
            {
                "title": "Step 1",
                "duration_seconds": 600,
                "repetitions": 1,
                "order_index": 0
            }
        ]
    }
    create_response = await client.post("/api/v1/timers/", json=timer_data)
    timer_id = create_response.json()["id"]
    
    # Start the timer
    await client.post(f"/api/v1/actions/start?timer_id={timer_id}")
    
    # Stop the timer
    response = await client.post(f"/api/v1/actions/stop?timer_id={timer_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Timer stopped"
    assert data["state"] == "stopped"
    assert data["time_in_step"] >= 0
    assert data["time_in_timer"] >= 0
    assert data["total_time"] == 600


@pytest.mark.asyncio
async def test_stop_timer_not_running(client: AsyncClient, db_session: AsyncSession):
    """Test stopping a timer that's not running."""
    # Create a timer but don't start it
    timer_data = {
        "name": "Not Running Timer",
        "steps": [
            {
                "title": "Step 1",
                "duration_seconds": 600,
                "repetitions": 1,
                "order_index": 0
            }
        ]
    }
    create_response = await client.post("/api/v1/timers/", json=timer_data)
    timer_id = create_response.json()["id"]
    
    # Try to stop without starting
    response = await client.post(f"/api/v1/actions/stop?timer_id={timer_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_timer_status_endpoint_success(client: AsyncClient, db_session: AsyncSession):
    """Test getting timer status via API."""
    # Create and start a timer
    timer_data = {
        "name": "Status Test Timer",
        "steps": [
            {
                "title": "Step 1",
                "duration_seconds": 600,
                "repetitions": 1,
                "order_index": 0
            }
        ]
    }
    create_response = await client.post("/api/v1/timers/", json=timer_data)
    timer_id = create_response.json()["id"]
    
    # Start the timer
    await client.post(f"/api/v1/actions/start?timer_id={timer_id}")
    
    # Get timer status
    response = await client.get(f"/api/v1/actions/status/{timer_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Timer status retrieved"
    assert data["state"] == "running"
    assert data["time_in_step"] >= 0
    assert data["time_in_timer"] >= 0
    assert data["total_time"] == 600


@pytest.mark.asyncio
async def test_get_timer_status_not_found(client: AsyncClient):
    """Test getting status of a non-existent timer."""
    response = await client.get("/api/v1/actions/status/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Timer not found"


@pytest.mark.asyncio
async def test_timer_lifecycle_complete(client: AsyncClient, db_session: AsyncSession):
    """Test complete timer lifecycle: start -> pause -> resume -> stop."""
    # Create a timer
    timer_data = {
        "name": "Lifecycle Test Timer",
        "steps": [
            {
                "title": "Step 1",
                "duration_seconds": 300,
                "repetitions": 1,
                "order_index": 0
            },
            {
                "title": "Step 2",
                "duration_seconds": 600,
                "repetitions": 2,
                "order_index": 1
            }
        ]
    }
    create_response = await client.post("/api/v1/timers/", json=timer_data)
    timer_id = create_response.json()["id"]
    
    # 1. Start the timer
    start_response = await client.post(f"/api/v1/actions/start?timer_id={timer_id}")
    assert start_response.status_code == 200
    start_data = start_response.json()
    assert start_data["state"] == "running"
    assert start_data["total_time"] == 1500  # 300*1 + 600*2
    
    # 2. Pause the timer
    pause_response = await client.post(f"/api/v1/actions/pause?timer_id={timer_id}")
    assert pause_response.status_code == 200
    pause_data = pause_response.json()
    assert pause_data["state"] == "paused"
    
    # 3. Resume the timer
    resume_response = await client.post(f"/api/v1/actions/resume?timer_id={timer_id}")
    assert resume_response.status_code == 200
    resume_data = resume_response.json()
    assert resume_data["state"] == "running"
    
    # 4. Stop the timer
    stop_response = await client.post(f"/api/v1/actions/stop?timer_id={timer_id}")
    assert stop_response.status_code == 200
    stop_data = stop_response.json()
    assert stop_data["state"] == "stopped"


@pytest.mark.asyncio
async def test_multiple_timers_independent(client: AsyncClient, db_session: AsyncSession):
    """Test that multiple timers can be managed independently."""
    # Create two timers
    timer1_data = {
        "name": "Timer 1",
        "steps": [{"title": "Step 1", "duration_seconds": 300, "repetitions": 1, "order_index": 0}]
    }
    timer2_data = {
        "name": "Timer 2",
        "steps": [{"title": "Step 1", "duration_seconds": 600, "repetitions": 1, "order_index": 0}]
    }
    
    create1_response = await client.post("/api/v1/timers/", json=timer1_data)
    create2_response = await client.post("/api/v1/timers/", json=timer2_data)
    timer1_id = create1_response.json()["id"]
    timer2_id = create2_response.json()["id"]
    
    # Start both timers
    await client.post(f"/api/v1/actions/start?timer_id={timer1_id}")
    await client.post(f"/api/v1/actions/start?timer_id={timer2_id}")
    
    # Pause only timer 1
    pause_response = await client.post(f"/api/v1/actions/pause?timer_id={timer1_id}")
    assert pause_response.status_code == 200
    assert pause_response.json()["state"] == "paused"
    
    # Check timer 2 is still running
    status_response = await client.get(f"/api/v1/actions/status/{timer2_id}")
    assert status_response.status_code == 200
    assert status_response.json()["state"] == "running"


@pytest.mark.asyncio
async def test_timer_with_empty_steps(client: AsyncClient, db_session: AsyncSession):
    """Test starting a timer with no steps."""
    # Create a timer with no steps
    timer_data = {
        "name": "Empty Timer",
        "steps": []
    }
    create_response = await client.post("/api/v1/timers/", json=timer_data)
    timer_id = create_response.json()["id"]
    
    # Start the timer
    response = await client.post(f"/api/v1/actions/start?timer_id={timer_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Timer started"
    assert data["state"] == "running"
    assert data["total_time"] == 0


@pytest.mark.asyncio
async def test_timer_with_multiple_steps_and_repetitions(client: AsyncClient, db_session: AsyncSession):
    """Test timer with multiple steps and repetitions."""
    # Create a complex timer
    timer_data = {
        "name": "Complex Timer",
        "steps": [
            {
                "title": "Warm up",
                "duration_seconds": 300,
                "repetitions": 2,
                "order_index": 0
            },
            {
                "title": "Work",
                "duration_seconds": 1200,
                "repetitions": 3,
                "order_index": 1
            },
            {
                "title": "Cool down",
                "duration_seconds": 180,
                "repetitions": 1,
                "order_index": 2
            }
        ]
    }
    create_response = await client.post("/api/v1/timers/", json=timer_data)
    timer_id = create_response.json()["id"]
    
    # Start the timer
    response = await client.post(f"/api/v1/actions/start?timer_id={timer_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Timer started"
    assert data["state"] == "running"
    # Total time: 300*2 + 1200*3 + 180*1 = 600 + 3600 + 180 = 4380
    assert data["total_time"] == 4380


@pytest.mark.asyncio
async def test_invalid_timer_id_format(client: AsyncClient):
    """Test handling of invalid timer ID format."""
    response = await client.post("/api/v1/actions/start?timer_id=invalid")
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_missing_timer_id_parameter(client: AsyncClient):
    """Test handling of missing timer ID parameter."""
    response = await client.post("/api/v1/actions/start")
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_negative_timer_id(client: AsyncClient):
    """Test handling of negative timer ID."""
    response = await client.post("/api/v1/actions/start?timer_id=-1")
    assert response.status_code == 404
    assert response.json()["detail"] == "Timer not found" 