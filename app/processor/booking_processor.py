"""Booking business logic processor"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.bookings import BookingCreate, BookingUpdate
from app.service.booking_service import BookingService


class BookingProcessor:
    """Processor class for booking business logic"""
    
    @staticmethod
    def validate_booking_amount(total_amount: float) -> bool:
        """Validate booking total amount"""
        return total_amount >= 0 and total_amount <= 100000  # Max 100,000 per booking

    @staticmethod
    def validate_booking_status(status: str) -> bool:
        """Validate booking status"""
        valid_statuses = ["PENDING", "CONFIRMED", "CANCELLED", "REFUNDED"]
        return status in valid_statuses

    @staticmethod
    def validate_seat_ids(seat_ids: list[str]) -> bool:
        """Validate seat IDs list"""
        if not seat_ids or len(seat_ids) == 0:
            return False
        if len(seat_ids) > 20:  # Max 20 seats per booking
            return False
        return True

    @staticmethod
    async def create_booking(db: AsyncSession, booking: BookingCreate):
        """Process booking creation with business logic"""
        # Business logic: Validate input data
        if not BookingProcessor.validate_booking_amount(float(booking.total_amount)):
            raise ValueError("Booking amount must be between 0 and 100,000")
        
        if not BookingProcessor.validate_booking_status(booking.status):
            raise ValueError("Invalid booking status. Must be PENDING, CONFIRMED, CANCELLED, or REFUNDED")
        
        # Call service layer
        return await BookingService.create_booking(db, booking)

    @staticmethod
    async def get_booking_by_id(db: AsyncSession, booking_id: str):
        """Process getting booking by ID with business logic"""
        # Business logic: Validate booking ID format
        if not booking_id or len(booking_id) < 10:
            raise ValueError("Invalid booking ID")
        
        # Call service layer
        return await BookingService.get_booking_by_id(db, booking_id)

    @staticmethod
    async def get_bookings_by_user(db: AsyncSession, user_id: str):
        """Process getting bookings by user with business logic"""
        # Business logic: Validate user ID format
        if not user_id or len(user_id) < 10:
            raise ValueError("Invalid user ID")
        
        # Call service layer
        return await BookingService.get_bookings_by_user(db, user_id)

    @staticmethod
    async def get_bookings_by_event(db: AsyncSession, event_id: str):
        """Process getting bookings by event with business logic"""
        # Business logic: Validate event ID format
        if not event_id or len(event_id) < 10:
            raise ValueError("Invalid event ID")
        
        # Call service layer
        return await BookingService.get_bookings_by_event(db, event_id)

    @staticmethod
    async def get_bookings(db: AsyncSession, skip: int = 0, limit: int = 10):
        """Process getting bookings with business logic"""
        # Business logic: Validate pagination parameters
        if skip < 0:
            raise ValueError("Skip must be non-negative")
        
        if limit <= 0 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        # Call service layer
        return await BookingService.get_bookings(db, skip, limit)

    @staticmethod
    async def update_booking(db: AsyncSession, booking_id: str, booking_update: BookingUpdate):
        """Process booking update with business logic"""
        # Business logic: Validate update data
        if booking_update.total_amount and not BookingProcessor.validate_booking_amount(float(booking_update.total_amount)):
            raise ValueError("Booking amount must be between 0 and 100,000")
        
        if booking_update.status and not BookingProcessor.validate_booking_status(booking_update.status):
            raise ValueError("Invalid booking status. Must be PENDING, CONFIRMED, CANCELLED, or REFUNDED")
        
        # Check if booking exists
        existing_booking = await BookingService.get_booking_by_id(db, booking_id)
        if not existing_booking:
            raise ValueError("Booking not found")
        
        # Call service layer
        return await BookingService.update_booking(db, booking_id, booking_update)

    @staticmethod
    async def delete_booking(db: AsyncSession, booking_id: str):
        """Process booking deletion with business logic"""
        # Business logic: Check if booking exists
        existing_booking = await BookingService.get_booking_by_id(db, booking_id)
        if not existing_booking:
            raise ValueError("Booking not found")
        
        # Additional business logic can be added here
        # For example: prevent deletion of confirmed bookings, check refund policies, etc.
        
        # Call service layer
        return await BookingService.delete_booking(db, booking_id)

    @staticmethod
    async def book_seats_with_lock(db: AsyncSession, event_id: str, user_id: str, seat_ids: list[str]) -> dict:
        """Process seat booking with business logic"""
        # Business logic: Validate input parameters
        if not event_id or len(event_id) < 10:
            raise ValueError("Invalid event ID")
        
        if not user_id or len(user_id) < 10:
            raise ValueError("Invalid user ID")
        
        if not BookingProcessor.validate_seat_ids(seat_ids):
            raise ValueError("Invalid seat selection. Must select 1-20 seats")
        
        # Call service layer
        return await BookingService.book_seats_with_lock(db, event_id, user_id, seat_ids)

    @staticmethod
    async def cancel_booking_and_release(db: AsyncSession, booking_id: str) -> bool:
        """Process booking cancellation with business logic"""
        # Business logic: Validate booking ID format
        if not booking_id or len(booking_id) < 10:
            raise ValueError("Invalid booking ID")
        
        # Check if booking exists
        existing_booking = await BookingService.get_booking_by_id(db, booking_id)
        if not existing_booking:
            raise ValueError("Booking not found")
        
        # Additional business logic can be added here
        # For example: check cancellation policies, refund rules, time limits, etc.
        
        # Call service layer
        return await BookingService.cancel_booking_and_release(db, booking_id)

    @staticmethod
    async def debug_redis_locks():
        """Process Redis debug operation with business logic"""
        # Business logic: This is a debug function, minimal validation
        # Could add admin-only checks in the future
        
        # Call service layer
        return await BookingService.debug_redis_locks()
