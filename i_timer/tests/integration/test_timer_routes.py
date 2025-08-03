"""Integration tests for timer API routes."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_timer_endpoint(client: AsyncClient):
    """Test creating a timer via API."""
    timer_data = {
        "name": "Test Timer",
        "description": "A test timer",
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
                "repetitions": 3,
                "order_index": 1
            }
        ]
    }
    
    response = await client.post("/api/v1/timers/", json=timer_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Timer"
    assert data["description"] == "A test timer"
    assert len(data["steps"]) == 2
    assert data["steps"][0]["title"] == "Warm up"


@pytest.mark.asyncio
async def test_get_timers_endpoint(client: AsyncClient):
    """Test getting timers via API."""
    # Create a timer first
    timer_data = {
        "name": "Test Timer",
        "steps": []
    }
    await client.post("/api/v1/timers/", json=timer_data)
    
    # Get timers
    response = await client.get("/api/v1/timers/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Test Timer"


@pytest.mark.asyncio
async def test_get_timer_by_id_endpoint(client: AsyncClient):
    """Test getting a specific timer via API."""
    # Create a timer first
    timer_data = {
        "name": "Test Timer",
        "steps": [
            {
                "title": "Step 1",
                "duration_seconds": 60,
                "order_index": 0
            }
        ]
    }
    create_response = await client.post("/api/v1/timers/", json=timer_data)
    timer_id = create_response.json()["id"]
    
    # Get the timer
    response = await client.get(f"/api/v1/timers/{timer_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == timer_id
    assert data["name"] == "Test Timer"
    assert len(data["steps"]) == 1


@pytest.mark.asyncio
async def test_get_timer_not_found(client: AsyncClient):
    """Test getting a non-existent timer."""
    response = await client.get("/api/v1/timers/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_timer_endpoint(client: AsyncClient):
    """Test updating a timer via API."""
    # Create a timer first
    timer_data = {
        "name": "Original Timer",
        "steps": []
    }
    create_response = await client.post("/api/v1/timers/", json=timer_data)
    timer_id = create_response.json()["id"]
    
    # Update the timer
    update_data = {
        "name": "Updated Timer",
        "description": "Updated description"
    }
    response = await client.put(f"/api/v1/timers/{timer_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Timer"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_timer_endpoint(client: AsyncClient):
    """Test deleting a timer via API."""
    # Create a timer first
    timer_data = {
        "name": "Timer to delete",
        "steps": []
    }
    create_response = await client.post("/api/v1/timers/", json=timer_data)
    timer_id = create_response.json()["id"]
    
    # Delete the timer
    response = await client.delete(f"/api/v1/timers/{timer_id}")
    
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = await client.get(f"/api/v1/timers/{timer_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_add_timer_step_endpoint(client: AsyncClient):
    """Test adding a step to a timer via API."""
    # Create a timer first
    timer_data = {
        "name": "Test Timer",
        "steps": []
    }
    create_response = await client.post("/api/v1/timers/", json=timer_data)
    timer_id = create_response.json()["id"]
    
    # Add a step
    step_data = {
        "title": "New Step",
        "duration_seconds": 120,
        "order_index": 0
    }
    response = await client.post(f"/api/v1/timers/{timer_id}/steps", json=step_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Step"
    assert data["timer_id"] == timer_id


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Interval Timer API" in data["message"]