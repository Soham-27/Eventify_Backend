from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from app.schemas.events import EventCreate, EventUpdate, EventOut, EventStatusUpdate
from app.crud.events import create_event, get_event_by_id, update_event, get_events, update_event_status, delete_event
from app.db.deps import get_db
from app.middleware.authenticated import get_current_user

router = APIRouter()



@router.post("/", status_code=201, response_model=EventOut)
async def create_event_api(event: EventCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user))-> EventOut:
    if current_user['role'] != 'ADMIN':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create events")
    return await create_event(db, event, current_user['user_id'])

@router.get("/{event_id}", status_code=200)
async def get_event_api(event_id: str, db: AsyncSession = Depends(get_db)) -> EventOut:
    event = await get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.get("/", status_code=200)
async def get_events_api(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db))-> list[EventOut]:
    return await get_events(db, skip, limit)

@router.put("/{event_id}", status_code=200, response_model=EventOut)
async def update_event_api(
    event_id: str,
    event_update: EventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> EventOut:
    """Update event details (admin only)"""
    if current_user['role'] != 'ADMIN':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update events")
    
    event = await update_event(db, event_id, event_update)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.patch("/{event_id}/status", status_code=200, response_model=EventOut)
async def update_event_status_api(
    event_id: str, 
    status_update: EventStatusUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> EventOut:
    """Update event active status (admin only)"""
    if current_user['role'] != 'ADMIN':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update event status")
    
    event = await update_event_status(db, event_id, status_update)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.delete("/{event_id}", status_code=200)
async def delete_event_api(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete event (admin only)"""
    if current_user['role'] != 'ADMIN':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete events")
    
    success = await delete_event(db, event_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    
    return {"message": "Event deleted successfully"}


