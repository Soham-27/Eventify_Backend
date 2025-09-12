from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.models.booking_seats import BookingSeat
from app.schemas.booking_seats import BookingSeatCreate
import uuid


async def create_booking_seat(db: AsyncSession, booking_seat: BookingSeatCreate):
    try:
        db_booking_seat = BookingSeat(
            id=uuid.uuid4(),
            booking_id=booking_seat.booking_id,
            event_seat_id=booking_seat.event_seat_id
        )
        db.add(db_booking_seat)
        await db.commit()
        await db.refresh(db_booking_seat)
        return db_booking_seat
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error creating booking seat: {str(e)}")


async def get_booking_seat_by_id(db: AsyncSession, booking_seat_id: str):
    try:
        result = await db.execute(select(BookingSeat).where(BookingSeat.id == booking_seat_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching booking seat: {str(e)}")


async def get_booking_seats_by_booking(db: AsyncSession, booking_id: str):
    try:
        result = await db.execute(select(BookingSeat).where(BookingSeat.booking_id == booking_id))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching booking seats: {str(e)}")


async def get_booking_seats(db: AsyncSession, skip: int = 0, limit: int = 10):
    try:
        result = await db.execute(select(BookingSeat).offset(skip).limit(limit))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching booking seats: {str(e)}")


async def delete_booking_seat(db: AsyncSession, booking_seat_id: str):
    try:
        result = await db.execute(select(BookingSeat).where(BookingSeat.id == booking_seat_id))
        db_booking_seat = result.scalars().first()
        if not db_booking_seat:
            return None
        
        await db.delete(db_booking_seat)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error deleting booking seat: {str(e)}")

