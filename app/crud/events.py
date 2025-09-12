from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.models.events import Event
from app.schemas.events import EventCreate, EventUpdate
from app.crud.event_seats import generate_event_seats
import uuid


async def create_event(db: AsyncSession, event: EventCreate, created_by: str):
    try:
        db_event = Event(
            id=uuid.uuid4(),
            venue_id=event.venue_id,
            title=event.title,
            description=event.description,
            default_price=event.default_price,
            start_time=event.start_time,
            end_time=event.end_time,
            created_by=created_by
        )
        db.add(db_event)
        await db.flush()  # Flush to get the event ID

        # Generate event seats automatically
        await generate_event_seats(db, db_event.id, event.venue_id, float(event.default_price))
        
        await db.commit()
        await db.refresh(db_event)
        return db_event
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error creating event: {str(e)}")
    

async def get_event_by_id(db: AsyncSession, event_id: str):
    try:
        result = await db.execute(select(Event).where(Event.id == event_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching event: {str(e)}")
    
    
async def get_events(db: AsyncSession, skip: int = 0, limit: int = 10):
    try:
        result = await db.execute(select(Event).offset(skip).limit(limit))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching events: {str(e)}")
    
    
async def update_event(db: AsyncSession, event_id: str, event_update: EventUpdate):
    try:
        result = await db.execute(select(Event).where(Event.id == event_id))
        db_event = result.scalars().first()
        if not db_event:
            return None
        
        for var, value in vars(event_update).items():
            if value is not None:
                setattr(db_event, var, value)
        
        db.add(db_event)
        await db.commit()
        await db.refresh(db_event)
        return db_event
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error updating event: {str(e)}")


async def delete_event(db: AsyncSession, event_id: str):
    try:
        result = await db.execute(select(Event).where(Event.id == event_id))
        db_event = result.scalars().first()
        if not db_event:
            return None
        
        await db.delete(db_event)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error deleting event: {str(e)}")  