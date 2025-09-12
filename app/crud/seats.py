from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.models.seats import Seat
from app.schemas.seats import SeatCreate, SeatUpdate
import uuid
import string


async def create_seat(db: AsyncSession, seat: SeatCreate):
    try:
        db_seat = Seat(
            id=uuid.uuid4(),
            venue_id=seat.venue_id,
            label=seat.label,
            row_no=seat.row_no,
            seat_no=seat.seat_no
        )
        db.add(db_seat)
        await db.commit()
        await db.refresh(db_seat)
        return db_seat
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error creating seat: {str(e)}")


async def get_seat_by_id(db: AsyncSession, seat_id: str):
    try:
        result = await db.execute(select(Seat).where(Seat.id == seat_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching seat: {str(e)}")


async def get_seats_by_venue(db: AsyncSession, venue_id: str):
    try:
        result = await db.execute(select(Seat).where(Seat.venue_id == venue_id))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching seats: {str(e)}")


async def get_seats(db: AsyncSession, skip: int = 0, limit: int = 10):
    try:
        result = await db.execute(select(Seat).offset(skip).limit(limit))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching seats: {str(e)}")


async def update_seat(db: AsyncSession, seat_id: str, seat_update: SeatUpdate):
    try:
        result = await db.execute(select(Seat).where(Seat.id == seat_id))
        db_seat = result.scalars().first()
        if not db_seat:
            return None
        
        for var, value in vars(seat_update).items():
            if value is not None:
                setattr(db_seat, var, value)
        
        db.add(db_seat)
        await db.commit()
        await db.refresh(db_seat)
        return db_seat
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error updating seat: {str(e)}")


async def delete_seat(db: AsyncSession, seat_id: str):
    try:
        result = await db.execute(select(Seat).where(Seat.id == seat_id))
        db_seat = result.scalars().first()
        if not db_seat:
            return None
        
        await db.delete(db_seat)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error deleting seat: {str(e)}")


async def generate_seats(db: AsyncSession, venue_id: str, total_rows: int, seats_per_row: int):
    """Generate seats for a venue based on total_rows and seats_per_row"""
    try:
        seats = []
        
        # Generate row letters (A, B, C, etc.)
        row_letters = string.ascii_uppercase[:total_rows]
        
        for row_idx, row_letter in enumerate(row_letters):
            for seat_num in range(1, seats_per_row + 1):
                seat = Seat(
                    id=uuid.uuid4(),
                    venue_id=venue_id,
                    label=f"{row_letter}{seat_num}",
                    row_no=row_letter,
                    seat_no=seat_num
                )
                seats.append(seat)
        
        # Add all seats to the database
        db.add_all(seats)
        await db.flush()  # Flush to get the seats in the database
        
        return seats
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error generating seats: {str(e)}")