"""Event database service operations"""

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from app.models.events import Event
from app.models.event_seats import EventSeat
from app.schemas.events import EventCreate, EventUpdate, EventStatusUpdate
from app.service.event_seat_service import EventSeatService
from app.models.venues import Venue
import uuid


class EventService:
    """Service class for event database operations"""
    
    @staticmethod
    def normalize_datetime(dt: datetime) -> datetime:
        """Normalize datetime to UTC timezone-aware"""
        if dt.tzinfo is None:
            # If naive, assume it's UTC
            return dt.replace(tzinfo=timezone.utc)
        else:
            # If timezone-aware, convert to UTC
            return dt.astimezone(timezone.utc)
    
    @staticmethod
    async def create_event(db: AsyncSession, event: EventCreate, created_by: str):
        """Create event in database"""
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
            await EventSeatService.generate_event_seats(db, db_event.id, event.venue_id, float(event.default_price))
            
            await db.commit()
            await db.refresh(db_event)
            return db_event
        except SQLAlchemyError as e:
            await db.rollback()
            raise Exception(f"Error creating event: {str(e)}")

    @staticmethod
    async def get_event_by_id(db: AsyncSession, event_id: str):
        """Get event by ID from database with venue name"""
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

    @staticmethod
    async def get_events(db: AsyncSession, skip: int = 0, limit: int = 10, active_only: bool = True):
        """Get events from database with venue names"""
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

    @staticmethod
    async def update_event(db: AsyncSession, event_id: str, event_update: EventUpdate):
        """Update event in database"""
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

    @staticmethod
    async def update_event_status(db: AsyncSession, event_id: str, status_update: EventStatusUpdate):
        """Update event active status in database"""
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

    @staticmethod
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
            current_time = datetime.now(timezone.utc)
            norm_end_time = EventService.normalize_datetime(event.end_time)
            if norm_end_time <= current_time:
                return False
            
            return True
        except SQLAlchemyError as e:
            raise Exception(f"Error checking event bookability: {str(e)}")

    @staticmethod
    async def get_upcoming_events_with_capacity(db: AsyncSession, skip: int = 0, limit: int = 10):
        """Get upcoming events with capacity details from database"""
        try:
            from datetime import datetime, timezone
            from sqlalchemy import case
            
            # Query to get upcoming events with venue names and capacity
            query = (
                select(
                    Event.id,
                    Event.title,
                    Event.start_time,
                    Event.end_time,
                    Event.default_price,
                    Venue.name.label('venue_name'),
                    func.count(EventSeat.id).label('total_capacity'),
                    func.sum(
                        case(
                            (EventSeat.status == 'AVAILABLE', 1),
                            else_=0
                        )
                    ).label('available_seats')
                )
                .select_from(Event)
                .join(Venue, Event.venue_id == Venue.id)
                .join(EventSeat, Event.id == EventSeat.event_id)
                .where(Event.is_active == True)
                .group_by(
                    Event.id, 
                    Event.title, 
                    Event.start_time, 
                    Event.end_time, 
                    Event.default_price, 
                    Venue.name
                )
                .order_by(Event.start_time)
            )
            
            result = await db.execute(query.offset(skip).limit(limit))
            rows = result.all()
            
            # Format the response
            upcoming_events = []
            for row in rows:
                upcoming_events.append({
                    "id": str(row.id),
                    "title": row.title,
                    "venue_name": row.venue_name,
                    "start_time": row.start_time,
                    "end_time": row.end_time,
                    "default_price": row.default_price,
                    "total_capacity": row.total_capacity,
                    "available_seats": row.available_seats,
                    "booked_seats": row.total_capacity - row.available_seats
                })
            
            return upcoming_events
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching upcoming events: {str(e)}")

    @staticmethod
    async def delete_event(db: AsyncSession, event_id: str):
        """Delete event from database"""
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
