"""Payment service operations"""

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.models.payments import Payment
from app.models.bookings import Booking
from app.models.event_seats import EventSeat
from app.models.booking_seats import BookingSeat
from app.schemas.payments import PaymentCreate, PaymentUpdate
from app.core.redis import redis
from decimal import Decimal
import uuid
import asyncio

LOCK_TTL_SECONDS = 180  # 3 minutes

class PaymentService:
    """Service class for payment operations"""
    
    @staticmethod
    async def create_pending_booking_with_locks(db: AsyncSession, event_id: str, user_id: str, seat_ids: list[str]) -> dict:
        """Create pending booking with Redis locks for seats"""
        # Step 1: Acquire locks in Redis for all seats (optional)
        acquired_keys: list[str] = []
        try:
            # Test Redis connection first
            await redis.ping()
            print(f"Redis connection successful")
            
            for seat_id in seat_ids:
                lock_key = f"lock:{event_id}:{seat_id}"
                print(f"Attempting to lock: {lock_key}")
                ok = await redis.set(lock_key, user_id, ex=LOCK_TTL_SECONDS, nx=True)
                if not ok:
                    raise Exception(f"Seat {seat_id} is not available")
                acquired_keys.append(lock_key)
                print(f"Successfully locked: {lock_key}")
        except Exception as e:
            print(f"Redis not available, continuing without locks: {e}")
            # Continue without Redis locks for testing
            acquired_keys = []

        # Step 2: Validate all seats are AVAILABLE
        result = await db.execute(select(EventSeat).where(EventSeat.event_id == event_id, EventSeat.seat_id.in_(seat_ids)))
        seats = result.scalars().all()
        if len(seats) != len(seat_ids):
            raise Exception("One or more seats do not exist for this event")
        if any(s.status != "AVAILABLE" for s in seats):
            raise Exception("One or more selected seats are not available")

        # Step 3: Compute total amount
        total_amount = sum(Decimal(str(s.price)) for s in seats)

        # Step 4: Create PENDING booking
        booking = Booking(
            id=uuid.uuid4(),
            event_id=event_id,
            user_id=user_id,
            total_amount=total_amount,
            status="PENDING",
        )
        db.add(booking)
        await db.flush()

        # Step 5: Create BookingSeat entries and mark event seats as LOCKED
        for s in seats:
            db.add(BookingSeat(id=uuid.uuid4(), booking_id=booking.id, event_seat_id=s.id))
            s.status = "LOCKED"
            db.add(s)

        await db.commit()
        
        return {
            "booking_id": str(booking.id), 
            "total_amount": str(total_amount),
            "status": "PENDING",
            "lock_keys": acquired_keys
        }

    @staticmethod
    async def confirm_payment_and_booking(db: AsyncSession, booking_id: str, transaction_ref: str = None) -> dict:
        """Confirm payment and update booking status to CONFIRMED"""
        try:
            # Get the booking
            result = await db.execute(select(Booking).where(Booking.id == booking_id))
            booking = result.scalars().first()
            if not booking:
                raise Exception("Booking not found")
            
            if booking.status != "PENDING":
                raise Exception("Booking is not in PENDING status")

            # Create payment record
            payment = Payment(
                id=uuid.uuid4(),
                booking_id=booking.id,
                user_id=booking.user_id,
                amount=booking.total_amount,
                status="SUCCESS",
                transaction_ref=transaction_ref or f"TXN_{uuid.uuid4().hex[:12].upper()}"
            )
            db.add(payment)

            # Update booking status to CONFIRMED
            booking.status = "CONFIRMED"
            db.add(booking)

            # Update event seats to BOOKED
            bs_result = await db.execute(select(BookingSeat).where(BookingSeat.booking_id == booking_id))
            bs_list = bs_result.scalars().all()
            
            es_ids = [bs.event_seat_id for bs in bs_list]
            if es_ids:
                es_result = await db.execute(select(EventSeat).where(EventSeat.id.in_(es_ids)))
                for es in es_result.scalars().all():
                    es.status = "BOOKED"
                    db.add(es)

            await db.commit()

            # Release Redis locks
            await PaymentService._release_booking_locks(db, booking_id, booking.event_id, bs_list)

            return {
                "booking_id": str(booking.id),
                "payment_id": str(payment.id),
                "status": "CONFIRMED",
                "transaction_ref": payment.transaction_ref
            }
        except SQLAlchemyError as e:
            await db.rollback()
            raise Exception(f"Error confirming payment: {str(e)}")

    @staticmethod
    async def fail_payment_and_cancel_booking(db: AsyncSession, booking_id: str, transaction_ref: str = None) -> dict:
        """Fail payment and cancel booking"""
        try:
            # Get the booking
            result = await db.execute(select(Booking).where(Booking.id == booking_id))
            booking = result.scalars().first()
            if not booking:
                raise Exception("Booking not found")
            
            if booking.status != "PENDING":
                raise Exception("Booking is not in PENDING status")

            # Create failed payment record
            payment = Payment(
                id=uuid.uuid4(),
                booking_id=booking.id,
                user_id=booking.user_id,
                amount=booking.total_amount,
                status="FAILED",
                transaction_ref=transaction_ref
            )
            db.add(payment)

            # Update booking status to CANCELLED
            booking.status = "CANCELLED"
            db.add(booking)

            # Update event seats back to AVAILABLE
            bs_result = await db.execute(select(BookingSeat).where(BookingSeat.booking_id == booking_id))
            bs_list = bs_result.scalars().all()
            
            es_ids = [bs.event_seat_id for bs in bs_list]
            if es_ids:
                es_result = await db.execute(select(EventSeat).where(EventSeat.id.in_(es_ids)))
                for es in es_result.scalars().all():
                    es.status = "AVAILABLE"
                    db.add(es)

            await db.commit()

            # Release Redis locks
            await PaymentService._release_booking_locks(db, booking_id, booking.event_id, bs_list)

            return {
                "booking_id": str(booking.id),
                "payment_id": str(payment.id),
                "status": "CANCELLED",
                "transaction_ref": payment.transaction_ref
            }
        except SQLAlchemyError as e:
            await db.rollback()
            raise Exception(f"Error failing payment: {str(e)}")

    @staticmethod
    async def _release_booking_locks(db: AsyncSession, booking_id: str, event_id: str, booking_seats: list):
        """Release Redis locks for a booking"""
        try:
            # Get seat IDs from booking seats
            seat_ids = []
            for bs in booking_seats:
                # Get seat_id from event_seat
                es_result = await db.execute(select(EventSeat).where(EventSeat.id == bs.event_seat_id))
                es = es_result.scalars().first()
                if es:
                    seat_ids.append(str(es.seat_id))
            
            # Release locks
            if seat_ids:
                lock_keys = [f"lock:{event_id}:{seat_id}" for seat_id in seat_ids]
                await redis.delete(*lock_keys)
        except Exception as e:
            print(f"Error releasing locks: {e}")

    @staticmethod
    async def cleanup_expired_locks(db: AsyncSession):
        """Clean up expired locks and cancel pending bookings"""
        try:
            # Get all lock keys
            lock_keys = await redis.keys("lock:*")
            expired_bookings = []
            
            for lock_key in lock_keys:
                ttl = await redis.ttl(lock_key)
                if ttl <= 0:  # Lock has expired
                    # Extract event_id and seat_id from lock key
                    parts = lock_key.split(":")
                    if len(parts) >= 3:
                        event_id = parts[1]
                        seat_id = parts[2]
                        
                        # Find pending bookings for this seat
                        result = await db.execute(
                            select(Booking)
                            .join(BookingSeat, Booking.id == BookingSeat.booking_id)
                            .join(EventSeat, BookingSeat.event_seat_id == EventSeat.id)
                            .where(
                                Booking.status == "PENDING",
                                EventSeat.event_id == event_id,
                                EventSeat.seat_id == seat_id
                            )
                        )
                        bookings = result.scalars().all()
                        
                        for booking in bookings:
                            if booking.id not in expired_bookings:
                                expired_bookings.append(booking.id)
            
            # Cancel expired bookings
            for booking_id in expired_bookings:
                try:
                    await PaymentService.fail_payment_and_cancel_booking(db, booking_id, "EXPIRED")
                except Exception as e:
                    print(f"Error canceling expired booking {booking_id}: {e}")
            
            return {"expired_bookings": len(expired_bookings)}
        except Exception as e:
            print(f"Error cleaning up expired locks: {e}")
            return {"expired_bookings": 0}

    @staticmethod
    async def get_booking_status(db: AsyncSession, booking_id: str):
        """Get booking status and payment info"""
        try:
            # Get booking with payment info
            result = await db.execute(
                select(Booking, Payment)
                .outerjoin(Payment, Booking.id == Payment.booking_id)
                .where(Booking.id == booking_id)
            )
            booking_payment = result.first()
            
            if not booking_payment:
                return None
            
            booking, payment = booking_payment
            return {
                "booking_id": str(booking.id),
                "status": booking.status,
                "total_amount": str(booking.total_amount),
                "payment_status": payment.status if payment else None,
                "transaction_ref": payment.transaction_ref if payment else None,
                "created_at": booking.created_at
            }
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching booking status: {str(e)}")
