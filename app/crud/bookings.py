from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.models.bookings import Booking
from app.models.booking_seats import BookingSeat
from app.models.event_seats import EventSeat
from app.schemas.bookings import BookingCreate, BookingUpdate
from app.core.redis import redis
from decimal import Decimal
import uuid

LOCK_TTL_SECONDS = 180

async def create_booking(db: AsyncSession, booking: BookingCreate):
    try:
        db_booking = Booking(
            id=uuid.uuid4(),
            event_id=booking.event_id,
            user_id=booking.user_id,
            total_amount=booking.total_amount,
            status=booking.status
        )
        db.add(db_booking)
        await db.commit()
        await db.refresh(db_booking)
        return db_booking
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error creating booking: {str(e)}")


async def get_booking_by_id(db: AsyncSession, booking_id: str):
    try:
        result = await db.execute(select(Booking).where(Booking.id == booking_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching booking: {str(e)}")


async def get_bookings_by_user(db: AsyncSession, user_id: str):
    try:
        result = await db.execute(select(Booking).where(Booking.user_id == user_id))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching user bookings: {str(e)}")


async def get_bookings_by_event(db: AsyncSession, event_id: str):
    try:
        result = await db.execute(select(Booking).where(Booking.event_id == event_id))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching event bookings: {str(e)}")


async def get_bookings(db: AsyncSession, skip: int = 0, limit: int = 10):
    try:
        result = await db.execute(select(Booking).offset(skip).limit(limit))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching bookings: {str(e)}")


async def update_booking(db: AsyncSession, booking_id: str, booking_update: BookingUpdate):
    try:
        result = await db.execute(select(Booking).where(Booking.id == booking_id))
        db_booking = result.scalars().first()
        if not db_booking:
            return None
        
        for var, value in vars(booking_update).items():
            if value is not None:
                setattr(db_booking, var, value)
        
        db.add(db_booking)
        await db.commit()
        await db.refresh(db_booking)
        return db_booking
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error updating booking: {str(e)}")


async def delete_booking(db: AsyncSession, booking_id: str):
    try:
        result = await db.execute(select(Booking).where(Booking.id == booking_id))
        db_booking = result.scalars().first()
        if not db_booking:
            return None
        
        await db.delete(db_booking)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error deleting booking: {str(e)}")


async def book_seats_with_lock(db: AsyncSession, event_id: str, user_id: str, seat_ids: list[str]) -> dict:
    """Attempt to book seats using Redis locks to avoid race conditions."""
    # Step 1: Validate all seats are AVAILABLE
    result = await db.execute(select(EventSeat).where(EventSeat.event_id == event_id, EventSeat.seat_id.in_(seat_ids)))
    seats = result.scalars().all()
    if len(seats) != len(seat_ids):
        raise Exception("One or more seats do not exist for this event")
    if any(s.status != "AVAILABLE" for s in seats):
        raise Exception("One or more selected seats are not available")

    # Step 2: Acquire locks in Redis
    acquired_keys: list[str] = []
    try:
        for seat_id in seat_ids:
            lock_key = f"lock:{event_id}:{seat_id}"
            ok = await redis.set(lock_key, user_id, ex=LOCK_TTL_SECONDS, nx=True)
            if not ok:
                raise Exception("Seat not available")
            acquired_keys.append(lock_key)

        # Step 3: Compute total amount from event_seats price
        total_amount = sum(Decimal(str(s.price)) for s in seats)
        time.sleep(2000)

        # Step 4: Create Booking and BookingSeat rows; mark event seats as BOOKED
        booking = Booking(
            id=uuid.uuid4(),
            event_id=event_id,
            user_id=user_id,
            total_amount=total_amount,
            status="CONFIRMED",
        )
        db.add(booking)
        await db.flush()

        for s in seats:
            db.add(BookingSeat(id=uuid.uuid4(), booking_id=booking.id, event_seat_id=s.id))
            s.status = "BOOKED"
            db.add(s)

        await db.commit()
        return {"booking_id": str(booking.id), "total_amount": str(total_amount)}
    except Exception as e:
        await db.rollback()
        # Release any acquired locks
        if acquired_keys:
            await redis.delete(*acquired_keys)
        raise
    finally:
        # Release locks after success as well
        if acquired_keys:
            await redis.delete(*acquired_keys)


async def cancel_booking_and_release(db: AsyncSession, booking_id: str) -> bool:
    """Cancel a booking and mark seats AVAILABLE again."""
    try:
        result = await db.execute(select(Booking).where(Booking.id == booking_id))
        booking = result.scalars().first()
        if not booking:
            return False

        # Fetch booking seats
        bs_result = await db.execute(select(BookingSeat).where(BookingSeat.booking_id == booking_id))
        bs_list = bs_result.scalars().all()

        # Mark event seats AVAILABLE
        es_ids = [bs.event_seat_id for bs in bs_list]
        if es_ids:
            es_result = await db.execute(select(EventSeat).where(EventSeat.id.in_(es_ids)))
            for es in es_result.scalars().all():
                es.status = "AVAILABLE"
                db.add(es)

        # Delete booking and booking_seats
        for bs in bs_list:
            await db.delete(bs)
        await db.delete(booking)

        await db.commit()
        return True
    except SQLAlchemyError:
        await db.rollback()
        raise

