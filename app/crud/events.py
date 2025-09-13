from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.models.events import Event
from app.schemas.events import EventCreate, EventUpdate, EventStatusUpdate
from app.crud.event_seats import generate_event_seats
from app.models.venues import Venue
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
        # Query to get event with venue name
        query = (
            select(
                Event,
                Venue.name.label('venue_name')
            )
            .select_from(Event)
            .join(Venue, Event.venue_id == Venue.id)
            .where(Event.id == event_id)
        )
        
        result = await db.execute(query)
        row = result.first()
        
        if not row:
            return None
        
        event = row.Event
        # Add venue_name as an attribute to the event object
        event.venue_name = row.venue_name
        return event
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching event: {str(e)}")
    
    
async def get_events(db: AsyncSession, skip: int = 0, limit: int = 10, active_only: bool = True):
    try:
        # Query to get events with venue names
        query = (
            select(
                Event,
                Venue.name.label('venue_name')
            )
            .select_from(Event)
            .join(Venue, Event.venue_id == Venue.id)
        )
        
        if active_only:
            query = query.where(Event.is_active == True)
        
        result = await db.execute(query.offset(skip).limit(limit))
        rows = result.all()
        
        # Format the response to include venue name
        events_with_venue = []
        for row in rows:
            event = row.Event
            # Add venue_name as an attribute to the event object
            event.venue_name = row.venue_name
            events_with_venue.append(event)
        
        return events_with_venue
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


async def update_event_status(db: AsyncSession, event_id: str, status_update: EventStatusUpdate):
    """Update event active status (admin only)"""
    try:
        result = await db.execute(select(Event).where(Event.id == event_id))
        db_event = result.scalars().first()
        if not db_event:
            return None
        
        db_event.is_active = status_update.is_active
        db.add(db_event)
        await db.commit()
        await db.refresh(db_event)
        return db_event
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error updating event status: {str(e)}")


async def is_event_bookable(db: AsyncSession, event_id: str) -> bool:
    """Check if an event is bookable (active and not finished)"""
    try:
        result = await db.execute(select(Event).where(Event.id == event_id))
        event = result.scalars().first()
        if not event:
            return False
        
        # Check if event is active
        if not event.is_active:
            return False
        
        # Check if event has finished
        current_time = datetime.utcnow()
        if event.end_time <= current_time:
            return False
        
        return True
    except SQLAlchemyError as e:
        raise Exception(f"Error checking event bookability: {str(e)}")


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