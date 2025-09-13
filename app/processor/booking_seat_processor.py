"""Booking seat business logic processor"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.booking_seats import BookingSeatCreate
from app.service.booking_seat_service import BookingSeatService


class BookingSeatProcessor:
    """Processor class for booking seat business logic"""
    
    @staticmethod
    async def create_booking_seat(db: AsyncSession, booking_seat: BookingSeatCreate):
        """Process booking seat creation with business logic"""
        # Business logic: Validate input data
        if not booking_seat.booking_id or len(booking_seat.booking_id) < 10:
            raise ValueError("Invalid booking ID")
        
        if not booking_seat.event_seat_id or len(booking_seat.event_seat_id) < 10:
            raise ValueError("Invalid event seat ID")
        
        # Check if booking exists
        from app.service.booking_service import BookingService
        existing_booking = await BookingService.get_booking_by_id(db, str(booking_seat.booking_id))
        if not existing_booking:
            raise ValueError("Booking not found")
        
        # Check if event seat exists
        from app.service.event_seat_service import EventSeatService
        existing_event_seat = await EventSeatService.get_event_seat_by_id(db, str(booking_seat.event_seat_id))
        if not existing_event_seat:
            raise ValueError("Event seat not found")
        
        # Check if seat is already booked for this booking
        existing_booking_seats = await BookingSeatService.get_booking_seats_by_booking(db, str(booking_seat.booking_id))
        for existing_bs in existing_booking_seats:
            if str(existing_bs.event_seat_id) == str(booking_seat.event_seat_id):
                raise ValueError("Seat already booked for this booking")
        
        # Call service layer
        return await BookingSeatService.create_booking_seat(db, booking_seat)

    @staticmethod
    async def get_booking_seat_by_id(db: AsyncSession, booking_seat_id: str):
        """Process getting booking seat by ID with business logic"""
        # Business logic: Validate booking seat ID format
        if not booking_seat_id or len(booking_seat_id) < 10:
            raise ValueError("Invalid booking seat ID")
        
        # Call service layer
        return await BookingSeatService.get_booking_seat_by_id(db, booking_seat_id)

    @staticmethod
    async def get_booking_seats_by_booking(db: AsyncSession, booking_id: str):
        """Process getting booking seats by booking with business logic"""
        # Business logic: Validate booking ID format
        if not booking_id or len(booking_id) < 10:
            raise ValueError("Invalid booking ID")
        
        # Call service layer
        return await BookingSeatService.get_booking_seats_by_booking(db, booking_id)

    @staticmethod
    async def get_booking_seats(db: AsyncSession, skip: int = 0, limit: int = 10):
        """Process getting booking seats with business logic"""
        # Business logic: Validate pagination parameters
        if skip < 0:
            raise ValueError("Skip must be non-negative")
        
        if limit <= 0 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        # Call service layer
        return await BookingSeatService.get_booking_seats(db, skip, limit)

    @staticmethod
    async def delete_booking_seat(db: AsyncSession, booking_seat_id: str):
        """Process booking seat deletion with business logic"""
        # Business logic: Check if booking seat exists
        existing_booking_seat = await BookingSeatService.get_booking_seat_by_id(db, booking_seat_id)
        if not existing_booking_seat:
            raise ValueError("Booking seat not found")
        
        # Additional business logic can be added here
        # For example: prevent deletion if booking is confirmed, check refund policies, etc.
        
        # Call service layer
        return await BookingSeatService.delete_booking_seat(db, booking_seat_id)
