from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from app.schemas.events import EventCreate, EventUpdate, EventOut, EventStatusUpdate
from app.processor.event_processor import EventProcessor
from app.db.deps import get_db
from app.middleware.authenticated import get_current_user

router = APIRouter()



@router.post("/", status_code=201, response_model=EventOut)
async def create_event_api(event: EventCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user))-> EventOut:
    """Create a new event (admin only)"""
    if current_user['role'] != 'ADMIN':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create events")
    
    try:
        return await EventProcessor.create_event(db, event, current_user['user_id'])
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/upcoming", status_code=200)
async def get_upcoming_events_api(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Get upcoming events with capacity details"""
    try:
        return await EventProcessor.get_upcoming_events_with_capacity(db, skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{event_id}", status_code=200)
async def get_event_api(event_id: str, db: AsyncSession = Depends(get_db)) -> EventOut:
    """Get event by ID"""
    try:
        event = await EventProcessor.get_event_by_id(db, event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        return event
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", status_code=200)
async def get_events_api(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db))-> list[EventOut]:
    """Get all events"""
    try:
        return await EventProcessor.get_events(db, skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

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
    
    try:
        event = await EventProcessor.update_event(db, event_id, event_update)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        return event
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
    
    try:
        event = await EventProcessor.update_event_status(db, event_id, status_update)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        return event
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{event_id}", status_code=200)
async def delete_event_api(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete event (admin only)"""
    if current_user['role'] != 'ADMIN':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete events")
    
    try:
        success = await EventProcessor.delete_event(db, event_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        
        return {"message": "Event deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


