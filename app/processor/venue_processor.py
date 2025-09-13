"""Venue business logic processor"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.venues import VenueCreate, VenueUpdate
from app.service.venue_service import VenueService


class VenueProcessor:
    """Processor class for venue business logic"""
    
    @staticmethod
    def validate_venue_name(name: str) -> bool:
        """Validate venue name"""
        if not name or len(name.strip()) < 2:
            return False
        if len(name) > 200:
            return False
        return True

    @staticmethod
    def validate_venue_capacity(total_rows: int, seats_per_row: int) -> bool:
        """Validate venue capacity"""
        if total_rows <= 0 or total_rows > 50:
            return False
        if seats_per_row <= 0 or seats_per_row > 100:
            return False
        if total_rows * seats_per_row > 5000:  # Max 5000 seats per venue
            return False
        return True

    @staticmethod
    async def create_venue(db: AsyncSession, venue: VenueCreate):
        """Process venue creation with business logic"""
        # Business logic: Validate input data
        if not VenueProcessor.validate_venue_name(venue.name):
            raise ValueError("Venue name must be between 2 and 200 characters")
        
        if not VenueProcessor.validate_venue_capacity(venue.total_rows, venue.seats_per_row):
            raise ValueError("Invalid venue capacity. Rows: 1-50, Seats per row: 1-100, Total seats: max 5000")
        
        # Call service layer
        return await VenueService.create_venue(db, venue)

    @staticmethod
    async def get_venue_by_id(db: AsyncSession, venue_id: str):
        """Process getting venue by ID with business logic"""
        # Business logic: Validate venue ID format
        if not venue_id or len(venue_id) < 10:
            raise ValueError("Invalid venue ID")
        
        # Call service layer
        return await VenueService.get_venue_by_id(db, venue_id)

    @staticmethod
    async def get_venues(db: AsyncSession, skip: int = 0, limit: int = 10):
        """Process getting venues with business logic"""
        # Business logic: Validate pagination parameters
        if skip < 0:
            raise ValueError("Skip must be non-negative")
        
        if limit <= 0 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        # Call service layer
        return await VenueService.get_venues(db, skip, limit)

    @staticmethod
    async def update_venue(db: AsyncSession, venue_id: str, venue_update: VenueUpdate):
        """Process venue update with business logic"""
        # Business logic: Validate update data
        if venue_update.name and not VenueProcessor.validate_venue_name(venue_update.name):
            raise ValueError("Venue name must be between 2 and 200 characters")
        
        
        # Check if venue exists
        existing_venue = await VenueService.get_venue_by_id(db, venue_id)
        if not existing_venue:
            raise ValueError("Venue not found")
        
        # Call service layer
        return await VenueService.update_venue(db, venue_id, venue_update)

    @staticmethod
    async def delete_venue(db: AsyncSession, venue_id: str):
        """Process venue deletion with business logic"""
        # Business logic: Check if venue exists
        existing_venue = await VenueService.get_venue_by_id(db, venue_id)
        if not existing_venue:
            raise ValueError("Venue not found")
        
        # Additional business logic can be added here
        # For example: check if venue has active events, prevent deletion if there are bookings, etc.
        
        # Call service layer
        return await VenueService.delete_venue(db, venue_id)
