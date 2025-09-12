from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.models.event_seats import EventSeat
from app.schemas.event_seats import EventSeatCreate, EventSeatUpdate
import uuid


async def create_event_seat(db: AsyncSession, event_seat: EventSeatCreate):
    try:
        db_event_seat = EventSeat(
            id=uuid.uuid4(),
            event_id=event_seat.event_id,
            seat_id=event_seat.seat_id,
            price=event_seat.price,
            status=event_seat.status
        )
        db.add(db_event_seat)
        await db.commit()
        await db.refresh(db_event_seat)
        return db_event_seat
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error creating event seat: {str(e)}")


async def get_event_seat_by_id(db: AsyncSession, event_seat_id: str):
    try:
        result = await db.execute(select(EventSeat).where(EventSeat.id == event_seat_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching event seat: {str(e)}")


async def get_event_seats_by_event(db: AsyncSession, event_id: str):

    """
    get all event seats with row/seat details (label, row_no, seat_no)
    """
    try:
        from app.models.seats import Seat
        # Join with Seat to fetch label/row_no/seat_no
        result = await db.execute(
            select(
                EventSeat.id,
                EventSeat.event_id,
                EventSeat.seat_id,
                EventSeat.price,
                EventSeat.status,
                Seat.label,
                Seat.row_no,
                Seat.seat_no,
            ).join(Seat, EventSeat.seat_id == Seat.id).where(
                EventSeat.event_id == event_id
            )
        )

        rows = result.all()
        # Build serializable dicts compatible with response schema
        return [
            {
                "id": r.id,
                "event_id": r.event_id,
                "seat_id": r.seat_id,
                "price": r.price,
                "status": r.status,
                "label": r.label,
                "row_no": r.row_no,
                "seat_no": r.seat_no,
            }
            for r in rows
        ]
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching event seats: {str(e)}")


async def get_available_event_seats(db: AsyncSession, event_id: str):
    try:
        from app.models.seats import Seat
        # Join with Seat to include label/row_no/seat_no and filter AVAILABLE
        result = await db.execute(
            select(
                EventSeat.id,
                EventSeat.event_id,
                EventSeat.seat_id,
                EventSeat.price,
                EventSeat.status,
                Seat.label,
                Seat.row_no,
                Seat.seat_no,
            ).join(Seat, EventSeat.seat_id == Seat.id).where(
                EventSeat.event_id == event_id,
                EventSeat.status == "AVAILABLE"
            )
        )

        rows = result.all()
        return [
            {
                "id": r.id,
                "event_id": r.event_id,
                "seat_id": r.seat_id,
                "price": r.price,
                "status": r.status,
                "label": r.label,
                "row_no": r.row_no,
                "seat_no": r.seat_no,
            }
            for r in rows
        ]
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching available event seats: {str(e)}")


async def update_event_seat(db: AsyncSession, event_seat_id: str, event_seat_update: EventSeatUpdate):
    try:
        result = await db.execute(select(EventSeat).where(EventSeat.id == event_seat_id))
        db_event_seat = result.scalars().first()
        if not db_event_seat:
            return None
        
        for var, value in vars(event_seat_update).items():
            if value is not None:
                setattr(db_event_seat, var, value)
        
        db.add(db_event_seat)
        await db.commit()
        await db.refresh(db_event_seat)
        return db_event_seat
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error updating event seat: {str(e)}")


async def delete_event_seat(db: AsyncSession, event_seat_id: str):
    try:
        result = await db.execute(select(EventSeat).where(EventSeat.id == event_seat_id))
        db_event_seat = result.scalars().first()
        if not db_event_seat:
            return None
        
        await db.delete(db_event_seat)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error deleting event seat: {str(e)}")


async def generate_event_seats(db: AsyncSession, event_id: str, venue_id: str, default_price: float):
    """Generate event seats for an event by copying all seats from the venue"""
    try:
        from app.crud.seats import get_seats_by_venue
        
        # Get all seats for the venue
        venue_seats = await get_seats_by_venue(db, venue_id)
        
        if not venue_seats:
            raise Exception(f"No seats found for venue {venue_id}")
        
        # Create event seats for each venue seat
        event_seats = []
        for seat in venue_seats:
            event_seat = EventSeat(
                id=uuid.uuid4(),
                event_id=event_id,
                seat_id=seat.id,
                price=default_price,
                status="AVAILABLE"
            )
            event_seats.append(event_seat)
        
        # Add all event seats to the database
        db.add_all(event_seats)
        await db.flush()  # Flush to get the event seats in the database
        
        return event_seats
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error generating event seats: {str(e)}")


async def update_event_seats_price_by_row(db: AsyncSession, event_id: str, row_no: str, new_price: float):
    """Update price for all event seats in a specific row"""
    try:
        from sqlalchemy import and_
        from app.models.seats import Seat
        
        # Get all event seats for the event and row using a join
        result = await db.execute(
            select(EventSeat).join(Seat, EventSeat.seat_id == Seat.id).where(
                and_(
                    EventSeat.event_id == event_id,
                    Seat.row_no == row_no
                )
            )
        )
        event_seats = result.scalars().all()
        
        if not event_seats:
            raise Exception(f"No event seats found for event {event_id} and row {row_no}")
        
        # Update price for all seats in the row
        updated_count = 0
        for event_seat in event_seats:
            event_seat.price = new_price
            updated_count += 1
        
        db.add_all(event_seats)
        await db.commit()
        
        return {
            "message": f"Updated price for {updated_count} seats in row {row_no}",
            "row": row_no,
            "new_price": new_price,
            "updated_count": updated_count
        }
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error updating event seats price by row: {str(e)}")


async def get_event_seats_by_row(db: AsyncSession, event_id: str, row_no: str):
    """Get all event seats for a specific event and row"""
    try:
        from sqlalchemy import and_
        from app.models.seats import Seat
        
        result = await db.execute(
            select(EventSeat).join(Seat, EventSeat.seat_id == Seat.id).where(
                and_(
                    EventSeat.event_id == event_id,
                    Seat.row_no == row_no
                )
            )
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching event seats by row: {str(e)}")