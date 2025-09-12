from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.models.venues import Venue
from app.schemas.venues import VenueCreate, VenueUpdate
from app.crud.seats import generate_seats
import uuid


async def create_venue(db: AsyncSession, venue: VenueCreate):
    try:
        db_venue = Venue(
            id=uuid.uuid4(),
            name=venue.name,
            address=venue.address,
            total_rows=venue.total_rows,
            seats_per_row=venue.seats_per_row
        )
        db.add(db_venue)
        await db.flush()  # Flush to get the venue ID

        await generate_seats(db, db_venue.id, db_venue.total_rows, db_venue.seats_per_row)
        await db.commit()
        await db.refresh(db_venue)

        return db_venue
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error creating venue: {str(e)}")


async def get_venue_by_id(db: AsyncSession, venue_id: str):
    try:
        result = await db.execute(select(Venue).where(Venue.id == venue_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching venue: {str(e)}")


async def get_venues(db: AsyncSession, skip: int = 0, limit: int = 10):
    try:
        result = await db.execute(select(Venue).offset(skip).limit(limit))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching venues: {str(e)}")


async def update_venue(db: AsyncSession, venue_id: str, venue_update: VenueUpdate):
    try:
        result = await db.execute(select(Venue).where(Venue.id == venue_id))
        db_venue = result.scalars().first()
        if not db_venue:
            return None
        
        for var, value in vars(venue_update).items():
            if value is not None:
                setattr(db_venue, var, value)
        
        db.add(db_venue)
        await db.commit()
        await db.refresh(db_venue)
        return db_venue
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error updating venue: {str(e)}")


async def delete_venue(db: AsyncSession, venue_id: str):
    try:
        result = await db.execute(select(Venue).where(Venue.id == venue_id))
        db_venue = result.scalars().first()
        if not db_venue:
            return None
        
        await db.delete(db_venue)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error deleting venue: {str(e)}")
