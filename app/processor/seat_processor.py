"""Seat business logic processor"""

import re
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.seats import SeatCreate, SeatUpdate
from app.service.seat_service import SeatService


class SeatProcessor:
    """Processor class for seat business logic"""
    
    @staticmethod
    def validate_seat_label(label: str) -> bool:
        """Validate seat label format (e.g., A1, B2, etc.)"""
        if not label:
            return False
        pattern = r'^[A-Z]\d+$'
        return re.match(pattern, label) is not None

    @staticmethod
    def validate_row_number(row_no: str) -> bool:
        """Validate row number (A-Z)"""
        if not row_no or len(row_no) != 1:
            return False
        return row_no.isalpha() and row_no.isupper()

    @staticmethod
    def validate_seat_number(seat_no: int) -> bool:
        """Validate seat number"""
        return 1 <= seat_no <= 100

    @staticmethod
    async def create_seat(db: AsyncSession, seat: SeatCreate):
        """Process seat creation with business logic"""
        # Business logic: Validate input data
        if not SeatProcessor.validate_seat_label(seat.label):
            raise ValueError("Seat label must be in format like A1, B2, etc.")
        
        if not SeatProcessor.validate_row_number(seat.row_no):
            raise ValueError("Row number must be a single uppercase letter (A-Z)")
        
        if not SeatProcessor.validate_seat_number(seat.seat_no):
            raise ValueError("Seat number must be between 1 and 100")
        
        # Check if seat already exists for this venue
        existing_seats = await SeatService.get_seats_by_venue(db, str(seat.venue_id))
        for existing_seat in existing_seats:
            if existing_seat.label == seat.label:
                raise ValueError("Seat with this label already exists in the venue")
        
        # Call service layer
        return await SeatService.create_seat(db, seat)

    @staticmethod
    async def get_seat_by_id(db: AsyncSession, seat_id: str):
        """Process getting seat by ID with business logic"""
        # Business logic: Validate seat ID format
        if not seat_id or len(seat_id) < 10:
            raise ValueError("Invalid seat ID")
        
        # Call service layer
        return await SeatService.get_seat_by_id(db, seat_id)

    @staticmethod
    async def get_seats_by_venue(db: AsyncSession, venue_id: str):
        """Process getting seats by venue with business logic"""
        # Business logic: Validate venue ID format
        if not venue_id or len(venue_id) < 10:
            raise ValueError("Invalid venue ID")
        
        # Call service layer
        return await SeatService.get_seats_by_venue(db, venue_id)

    @staticmethod
    async def get_seats(db: AsyncSession, skip: int = 0, limit: int = 10):
        """Process getting seats with business logic"""
        # Business logic: Validate pagination parameters
        if skip < 0:
            raise ValueError("Skip must be non-negative")
        
        if limit <= 0 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        # Call service layer
        return await SeatService.get_seats(db, skip, limit)

    @staticmethod
    async def update_seat(db: AsyncSession, seat_id: str, seat_update: SeatUpdate):
        """Process seat update with business logic"""
        # Business logic: Validate update data
        if seat_update.label and not SeatProcessor.validate_seat_label(seat_update.label):
            raise ValueError("Seat label must be in format like A1, B2, etc.")
        
        if seat_update.row_no and not SeatProcessor.validate_row_number(seat_update.row_no):
            raise ValueError("Row number must be a single uppercase letter (A-Z)")
        
        if seat_update.seat_no and not SeatProcessor.validate_seat_number(seat_update.seat_no):
            raise ValueError("Seat number must be between 1 and 100")
        
        # Check if seat exists
        existing_seat = await SeatService.get_seat_by_id(db, seat_id)
        if not existing_seat:
            raise ValueError("Seat not found")
        
        # Check if new label conflicts with existing seats
        if seat_update.label and seat_update.label != existing_seat.label:
            existing_seats = await SeatService.get_seats_by_venue(db, str(existing_seat.venue_id))
            for seat in existing_seats:
                if seat.label == seat_update.label and seat.id != seat_id:
                    raise ValueError("Seat with this label already exists in the venue")
        
        # Call service layer
        return await SeatService.update_seat(db, seat_id, seat_update)

    @staticmethod
    async def delete_seat(db: AsyncSession, seat_id: str):
        """Process seat deletion with business logic"""
        # Business logic: Check if seat exists
        existing_seat = await SeatService.get_seat_by_id(db, seat_id)
        if not existing_seat:
            raise ValueError("Seat not found")
        
        # Additional business logic can be added here
        # For example: check if seat is booked in any events, prevent deletion if booked, etc.
        
        # Call service layer
        return await SeatService.delete_seat(db, seat_id)

    @staticmethod
    async def generate_seats(db: AsyncSession, venue_id: str, total_rows: int, seats_per_row: int):
        """Process seat generation with business logic"""
        # Business logic: Validate generation parameters
        if not venue_id or len(venue_id) < 10:
            raise ValueError("Invalid venue ID")
        
        if total_rows <= 0 or total_rows > 50:
            raise ValueError("Total rows must be between 1 and 50")
        
        if seats_per_row <= 0 or seats_per_row > 100:
            raise ValueError("Seats per row must be between 1 and 100")
        
        if total_rows * seats_per_row > 5000:
            raise ValueError("Total seats cannot exceed 5000")
        
        # Check if seats already exist for this venue
        existing_seats = await SeatService.get_seats_by_venue(db, venue_id)
        if existing_seats:
            raise ValueError("Seats already exist for this venue")
        
        # Call service layer
        return await SeatService.generate_seats(db, venue_id, total_rows, seats_per_row)
