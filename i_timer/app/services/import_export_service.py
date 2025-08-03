"""Import/Export service for timer data."""

import csv
import io
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.timer_models import Timer
from app.schemas.timer_schemas import TimerCreate, TimerStepCreate, TimerExport
from app.services.timer_service import get_timer_by_id, create_timer


async def export_timer_to_csv(db: AsyncSession, timer_id: int) -> str:
    """Export a timer to CSV format."""
    timer = await get_timer_by_id(db, timer_id)
    if not timer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timer not found"
        )
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "timer_name",
        "timer_description", 
        "step_order",
        "step_title",
        "duration_seconds",
        "repetitions",
        "notes"
    ])
    
    # Write timer steps
    for step in sorted(timer.steps, key=lambda s: s.order_index):
        writer.writerow([
            timer.name,
            timer.description or "",
            step.order_index,
            step.title,
            step.duration_seconds,
            step.repetitions,
            step.notes or ""
        ])
    
    return output.getvalue()


async def import_timer_from_csv(db: AsyncSession, csv_content: str) -> Timer:
    """Import a timer from CSV format."""
    try:
        # Parse CSV content
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(csv_reader)
        
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV file is empty"
            )
        
        # Extract timer info from first row
        first_row = rows[0]
        timer_name = first_row.get("timer_name", "").strip()
        timer_description = first_row.get("timer_description", "").strip()
        
        if not timer_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Timer name is required"
            )
        
        # Parse steps
        steps = []
        for row in rows:
            try:
                step = TimerStepCreate(
                    title=row.get("step_title", "").strip(),
                    duration_seconds=int(row.get("duration_seconds", 0)),
                    repetitions=int(row.get("repetitions", 1)),
                    notes=row.get("notes", "").strip() or None,
                    order_index=int(row.get("step_order", 0))
                )
                steps.append(step)
            except (ValueError, TypeError) as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid step data: {str(e)}"
                )
        
        if not steps:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one timer step is required"
            )
        
        # Create timer
        timer_data = TimerCreate(
            name=timer_name,
            description=timer_description or None,
            steps=steps
        )
        
        return await create_timer(db, timer_data)
        
    except csv.Error as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid CSV format: {str(e)}"
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing timer: {str(e)}"
        )