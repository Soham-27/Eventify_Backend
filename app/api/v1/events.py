from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from app.schemas.events import EventCreate, EventUpdate,EventOut
from app.crud.events import create_event, get_event_by_id, update_event, get_events
from app.db.deps import get_db
from app.middleware.authenticated import get_current_user   
from app.schemas.events import EventOut,EventCreate,EventUpdate

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
