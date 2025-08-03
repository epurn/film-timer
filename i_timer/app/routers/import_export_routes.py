"""Import/Export API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.timer_schemas import Timer
from app.services import import_export_service

router = APIRouter(prefix="/import-export", tags=["import-export"])


@router.get("/timers/{timer_id}/export")
async def export_timer(
    timer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Export a timer to CSV format."""
    csv_content = await import_export_service.export_timer_to_csv(db, timer_id)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=timer_{timer_id}.csv"}
    )


@router.post("/timers/import", response_model=Timer, status_code=status.HTTP_201_CREATED)
async def import_timer(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Import a timer from CSV file."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    try:
        content = await file.read()
        csv_content = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be UTF-8 encoded"
        )
    
    return await import_export_service.import_timer_from_csv(db, csv_content)