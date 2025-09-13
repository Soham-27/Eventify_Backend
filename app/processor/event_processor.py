"""Event business logic processor"""

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.events import EventCreate, EventUpdate, EventStatusUpdate
from app.service.event_service import EventService


class EventProcessor:
    """Processor class for event business logic"""
    
    @staticmethod
    def validate_event_title(title: str) -> bool:
        """Validate event title"""
        if not title or len(title.strip()) < 2:
            return False
        if len(title) > 200:
            return False
        return True

    @staticmethod
    def validate_event_description(description: str) -> bool:
        """Validate event description"""
        if description and len(description) > 1000:
            return False
        return True

    @staticmethod
    def validate_event_price(price: float) -> bool:
        """Validate event price"""
        return price >= 0 and price <= 10000  # Max 10,000 per seat

    @staticmethod
    def validate_event_times(start_time: datetime, end_time: datetime) -> bool:
        """Validate event start and end times"""
        if start_time >= end_time:
            return False
        
        return True

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
    async def check_event_overlap(db: AsyncSession, venue_id: str, start_time: datetime, end_time: datetime, exclude_event_id: str = None) -> bool:
        """Check if event overlaps with other events at the same venue"""
        try:
            from app.service.event_service import EventService
            
            # Get all events for the venue
            events = await EventService.get_events(db, skip=0, limit=1000, active_only=False)
            
            for event in events:
                # Skip the current event if we're updating
                if exclude_event_id and str(event.id) == exclude_event_id:
                    continue
                
                # Skip events at different venues
                if str(event.venue_id) != venue_id:
                    continue
                
                # Check for overlap
                # Two events overlap if: new_start < existing_end AND new_end > existing_start
                # Normalize all datetimes to UTC for comparison
                norm_start_time = EventProcessor.normalize_datetime(start_time)
                norm_end_time = EventProcessor.normalize_datetime(end_time)
                norm_event_start = EventProcessor.normalize_datetime(event.start_time)
                norm_event_end = EventProcessor.normalize_datetime(event.end_time)
                
                if norm_start_time < norm_event_end and norm_end_time > norm_event_start:
                    return True  # Overlap found
            
            return False  # No overlap
        except Exception as e:
            raise Exception(f"Error checking event overlap: {str(e)}")

    @staticmethod
    def validate_event_future_time(start_time: datetime) -> bool:
        """Validate that event starts in the future"""
        current_time = datetime.now(timezone.utc)
        norm_start_time = EventProcessor.normalize_datetime(start_time)
        return norm_start_time > current_time

    @staticmethod
    async def create_event(db: AsyncSession, event: EventCreate, created_by: str):
        """Process event creation with business logic"""
        # Business logic: Validate input data
        if not EventProcessor.validate_event_title(event.title):
            raise ValueError("Event title must be between 2 and 200 characters")
        
        if not EventProcessor.validate_event_description(event.description):
            raise ValueError("Event description cannot exceed 1000 characters")
        
        if not EventProcessor.validate_event_price(float(event.default_price)):
            raise ValueError("Event price must be between 0 and 10,000")
        
        # if not EventProcessor.validate_event_times(event.start_time, event.end_time):
        #     raise ValueError("Invalid event times. Start time must be before end time")
        
        if not EventProcessor.validate_event_future_time(event.start_time):
            raise ValueError("Event start time must be in the future")
        
        # Check for event overlap at the same venue
        has_overlap = await EventProcessor.check_event_overlap(db, str(event.venue_id), event.start_time, event.end_time)
        if has_overlap:
            raise ValueError("Event overlaps with another event at the same venue")
        
        # Call service layer
        return await EventService.create_event(db, event, created_by)

    @staticmethod
    async def get_event_by_id(db: AsyncSession, event_id: str):
        """Process getting event by ID with business logic"""
        # Business logic: Validate event ID format
        if not event_id or len(event_id) < 10:
            raise ValueError("Invalid event ID")
        
        # Call service layer
        return await EventService.get_event_by_id(db, event_id)

    @staticmethod
    async def get_events(db: AsyncSession, skip: int = 0, limit: int = 10, active_only: bool = True):
        """Process getting events with business logic"""
        # Business logic: Validate pagination parameters
        if skip < 0:
            raise ValueError("Skip must be non-negative")
        
        if limit <= 0 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        # Call service layer
        return await EventService.get_events(db, skip, limit, active_only)

    @staticmethod
    async def update_event(db: AsyncSession, event_id: str, event_update: EventUpdate):
        """Process event update with business logic"""
        # Business logic: Validate update data
        if event_update.title and not EventProcessor.validate_event_title(event_update.title):
            raise ValueError("Event title must be between 2 and 200 characters")
        
        if event_update.description and not EventProcessor.validate_event_description(event_update.description):
            raise ValueError("Event description cannot exceed 1000 characters")
        
        if event_update.default_price and not EventProcessor.validate_event_price(float(event_update.default_price)):
            raise ValueError("Event price must be between 0 and 10,000")
        
        if event_update.start_time and event_update.end_time:
            # if not EventProcessor.validate_event_times(event_update.start_time, event_update.end_time):
            #     raise ValueError("Invalid event times. Start time must be before end time")
            pass
        
        if event_update.start_time and not EventProcessor.validate_event_future_time(event_update.start_time):
            raise ValueError("Event start time must be in the future")
        
        # Check if event exists
        existing_event = await EventService.get_event_by_id(db, event_id)
        if not existing_event:
            raise ValueError("Event not found")
        
        # Check for event overlap at the same venue (after getting existing event)
        if event_update.start_time and event_update.end_time:
            has_overlap = await EventProcessor.check_event_overlap(db, str(existing_event.venue_id), event_update.start_time, event_update.end_time, exclude_event_id=event_id)
            if has_overlap:
                raise ValueError("Event overlaps with another event at the same venue")
        
        # Call service layer
        return await EventService.update_event(db, event_id, event_update)

    @staticmethod
    async def update_event_status(db: AsyncSession, event_id: str, status_update: EventStatusUpdate):
        """Process event status update with business logic"""
        # Check if event exists
        existing_event = await EventService.get_event_by_id(db, event_id)
        if not existing_event:
            raise ValueError("Event not found")
        
        # Additional business logic can be added here
        # For example: prevent deactivating events with confirmed bookings
        
        # Call service layer
        return await EventService.update_event_status(db, event_id, status_update)

    @staticmethod
    async def is_event_bookable(db: AsyncSession, event_id: str) -> bool:
        """Process event bookability check with business logic"""
        # Business logic: Validate event ID format
        if not event_id or len(event_id) < 10:
            raise ValueError("Invalid event ID")
        
        # Call service layer
        return await EventService.is_event_bookable(db, event_id)

    @staticmethod
    async def get_upcoming_events_with_capacity(db: AsyncSession, skip: int = 0, limit: int = 10):
        """Process getting upcoming events with capacity with business logic"""
        # Business logic: Validate pagination parameters
        if skip < 0:
            raise ValueError("Skip must be non-negative")
        
        if limit <= 0 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        # Call service layer
        return await EventService.get_upcoming_events_with_capacity(db, skip, limit)

    @staticmethod
    async def delete_event(db: AsyncSession, event_id: str):
        """Process event deletion with business logic"""
        # Business logic: Check if event exists
        existing_event = await EventService.get_event_by_id(db, event_id)
        if not existing_event:
            raise ValueError("Event not found")
        
        # Additional business logic can be added here
        # For example: check if event has confirmed bookings, prevent deletion if there are bookings, etc.
        
        # Call service layer
        return await EventService.delete_event(db, event_id)
