"""Event seat business logic processor"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.event_seats import EventSeatCreate, EventSeatUpdate
from app.service.event_seat_service import EventSeatService


class EventSeatProcessor:
    """Processor class for event seat business logic"""
    
    @staticmethod
    def validate_event_seat_price(price: float) -> bool:
        """Validate event seat price"""
        return price >= 0 and price <= 10000  # Max 10,000 per seat

    @staticmethod
    def validate_event_seat_status(status: str) -> bool:
        """Validate event seat status"""
        valid_statuses = ["AVAILABLE", "BOOKED", "RESERVED", "BLOCKED"]
        return status in valid_statuses

    @staticmethod
    async def create_event_seat(db: AsyncSession, event_seat: EventSeatCreate):
        """Process event seat creation with business logic"""
        # Business logic: Validate input data
        if not EventSeatProcessor.validate_event_seat_price(event_seat.price):
            raise ValueError("Event seat price must be between 0 and 10,000")
        
        if not EventSeatProcessor.validate_event_seat_status(event_seat.status):
            raise ValueError("Invalid event seat status. Must be AVAILABLE, BOOKED, RESERVED, or BLOCKED")
        
        # Check if event exists
        from app.service.event_service import EventService
        existing_event = await EventService.get_event_by_id(db, str(event_seat.event_id))
        if not existing_event:
            raise ValueError("Event not found")
        
        # Check if seat already exists for this event
        existing_seats = await EventSeatService.get_event_seats_by_event(db, str(event_seat.event_id))
        for existing_seat in existing_seats:
            if existing_seat['seat_id'] == str(event_seat.seat_id):
                raise ValueError("Seat already exists for this event")
        
        # Call service layer
        return await EventSeatService.create_event_seat(db, event_seat)

    @staticmethod
    async def get_event_seat_by_id(db: AsyncSession, event_seat_id: str):
        """Process getting event seat by ID with business logic"""
        # Business logic: Validate event seat ID format
        if not event_seat_id or len(event_seat_id) < 10:
            raise ValueError("Invalid event seat ID")
        
        # Call service layer
        return await EventSeatService.get_event_seat_by_id(db, event_seat_id)

    @staticmethod
    async def get_event_seats_by_event(db: AsyncSession, event_id: str):
        """Process getting event seats by event with business logic"""
        # Business logic: Validate event ID format
        if not event_id or len(event_id) < 10:
            raise ValueError("Invalid event ID")
        
        # Call service layer
        return await EventSeatService.get_event_seats_by_event(db, event_id)

    @staticmethod
    async def get_available_event_seats(db: AsyncSession, event_id: str):
        """Process getting available event seats with business logic"""
        # Business logic: Validate event ID format
        if not event_id or len(event_id) < 10:
            raise ValueError("Invalid event ID")
        
        # Call service layer
        return await EventSeatService.get_available_event_seats(db, event_id)

    @staticmethod
    async def update_event_seat(db: AsyncSession, event_seat_id: str, event_seat_update: EventSeatUpdate):
        """Process event seat update with business logic"""
        # Business logic: Validate update data
        if event_seat_update.price is not None and not EventSeatProcessor.validate_event_seat_price(event_seat_update.price):
            raise ValueError("Event seat price must be between 0 and 10,000")
        
        if event_seat_update.status and not EventSeatProcessor.validate_event_seat_status(event_seat_update.status):
            raise ValueError("Invalid event seat status. Must be AVAILABLE, BOOKED, RESERVED, or BLOCKED")
        
        # Check if event seat exists
        existing_seat = await EventSeatService.get_event_seat_by_id(db, event_seat_id)
        if not existing_seat:
            raise ValueError("Event seat not found")
        
        # Call service layer
        return await EventSeatService.update_event_seat(db, event_seat_id, event_seat_update)

    @staticmethod
    async def delete_event_seat(db: AsyncSession, event_seat_id: str):
        """Process event seat deletion with business logic"""
        # Business logic: Check if event seat exists
        existing_seat = await EventSeatService.get_event_seat_by_id(db, event_seat_id)
        if not existing_seat:
            raise ValueError("Event seat not found")
        
        # Additional business logic can be added here
        # For example: prevent deletion if seat is booked
        
        # Call service layer
        return await EventSeatService.delete_event_seat(db, event_seat_id)

    @staticmethod
    async def generate_event_seats(db: AsyncSession, event_id: str, venue_id: str, default_price: float):
        """Process event seat generation with business logic"""
        # Business logic: Validate generation parameters
        if not event_id or len(event_id) < 10:
            raise ValueError("Invalid event ID")
        
        if not venue_id or len(venue_id) < 10:
            raise ValueError("Invalid venue ID")
        
        if not EventSeatProcessor.validate_event_seat_price(default_price):
            raise ValueError("Default price must be between 0 and 10,000")
        
        # Check if event exists
        from app.service.event_service import EventService
        existing_event = await EventService.get_event_by_id(db, event_id)
        if not existing_event:
            raise ValueError("Event not found")
        
        # Check if seats already exist for this event
        existing_seats = await EventSeatService.get_event_seats_by_event(db, event_id)
        if existing_seats:
            raise ValueError("Event seats already exist for this event")
        
        # Call service layer
        return await EventSeatService.generate_event_seats(db, event_id, venue_id, default_price)

    @staticmethod
    async def update_event_seats_price_by_row(db: AsyncSession, event_id: str, row_no: str, new_price: float):
        """Process updating event seats price by row with business logic"""
        # Business logic: Validate parameters
        if not event_id or len(event_id) < 10:
            raise ValueError("Invalid event ID")
        
        if not row_no or len(row_no) != 1 or not row_no.isalpha():
            raise ValueError("Row number must be a single letter (A-Z)")
        
        if not EventSeatProcessor.validate_event_seat_price(new_price):
            raise ValueError("Price must be between 0 and 10,000")
        
        # Check if event exists
        from app.service.event_service import EventService
        existing_event = await EventService.get_event_by_id(db, event_id)
        if not existing_event:
            raise ValueError("Event not found")
        
        # Call service layer
        return await EventSeatService.update_event_seats_price_by_row(db, event_id, row_no, new_price)

    @staticmethod
    async def get_event_seats_by_row(db: AsyncSession, event_id: str, row_no: str):
        """Process getting event seats by row with business logic"""
        # Business logic: Validate parameters
        if not event_id or len(event_id) < 10:
            raise ValueError("Invalid event ID")
        
        if not row_no or len(row_no) != 1 or not row_no.isalpha():
            raise ValueError("Row number must be a single letter (A-Z)")
        
        # Call service layer
        return await EventSeatService.get_event_seats_by_row(db, event_id, row_no)
