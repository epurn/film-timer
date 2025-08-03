"""Integration tests for import/export API routes."""

import pytest
from httpx import AsyncClient
import io


@pytest.mark.asyncio
async def test_export_timer_endpoint(client: AsyncClient):
    """Test exporting a timer to CSV via API."""
    # Create a timer with steps first
    timer_data = {
        "name": "Export Test Timer",
        "description": "Timer for export testing",
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
                "order_index": 1,
                "notes": "High intensity"
            }
        ]
    }
    create_response = await client.post("/api/v1/timers/", json=timer_data)
    timer_id = create_response.json()["id"]
    
    # Export the timer
    response = await client.get(f"/api/v1/import-export/timers/{timer_id}/export")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment" in response.headers["content-disposition"]
    
    # Verify CSV content
    csv_content = response.text
    lines = csv_content.strip().split('\n')
    assert len(lines) == 3  # Header + 2 steps
    
    # Check header
    header = lines[0]
    assert "timer_name" in header
    assert "step_title" in header
    assert "duration_seconds" in header


@pytest.mark.asyncio
async def test_export_timer_not_found(client: AsyncClient):
    """Test exporting a non-existent timer."""
    response = await client.get("/api/v1/import-export/timers/999/export")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_import_timer_endpoint(client: AsyncClient):
    """Test importing a timer from CSV via API."""
    # Create CSV content
    csv_content = """timer_name,timer_description,step_order,step_title,duration_seconds,repetitions,notes
Import Test Timer,Imported timer,0,Warm up,300,1,Light warm up
Import Test Timer,Imported timer,1,Work,1200,3,High intensity"""
    
    # Create file-like object
    csv_file = io.BytesIO(csv_content.encode('utf-8'))
    
    # Import the timer
    files = {"file": ("test_timer.csv", csv_file, "text/csv")}
    response = await client.post("/api/v1/import-export/timers/import", files=files)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Import Test Timer"
    assert data["description"] == "Imported timer"
    assert len(data["steps"]) == 2
    assert data["steps"][0]["title"] == "Warm up"
    assert data["steps"][1]["repetitions"] == 3


@pytest.mark.asyncio
async def test_import_timer_invalid_file(client: AsyncClient):
    """Test importing with invalid file format."""
    # Create non-CSV file
    txt_file = io.BytesIO(b"This is not a CSV file")
    
    files = {"file": ("test.txt", txt_file, "text/plain")}
    response = await client.post("/api/v1/import-export/timers/import", files=files)
    
    assert response.status_code == 400
    assert "CSV file" in response.json()["detail"]


@pytest.mark.asyncio
async def test_import_timer_empty_csv(client: AsyncClient):
    """Test importing an empty CSV file."""
    csv_content = "timer_name,timer_description,step_order,step_title,duration_seconds,repetitions,notes"
    csv_file = io.BytesIO(csv_content.encode('utf-8'))
    
    files = {"file": ("empty.csv", csv_file, "text/csv")}
    response = await client.post("/api/v1/import-export/timers/import", files=files)
    
    assert response.status_code == 400
    assert "empty" in response.json()["detail"]


@pytest.mark.asyncio
async def test_import_timer_invalid_csv_data(client: AsyncClient):
    """Test importing CSV with invalid data."""
    csv_content = """timer_name,timer_description,step_order,step_title,duration_seconds,repetitions,notes
Test Timer,Description,0,Step 1,invalid_duration,1,Notes"""
    csv_file = io.BytesIO(csv_content.encode('utf-8'))
    
    files = {"file": ("invalid.csv", csv_file, "text/csv")}
    response = await client.post("/api/v1/import-export/timers/import", files=files)
    
    assert response.status_code == 400
    assert "Invalid step data" in response.json()["detail"]