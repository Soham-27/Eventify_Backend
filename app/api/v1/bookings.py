"""Booking API endpoints

This module handles booking operations:
- Create bookings with payment flow (PENDING status)
- Cancel bookings
- Get user bookings
- Debug Redis locks

For payment processing, use /payments endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.deps import get_db
from app.middleware.authenticated import get_current_user
from app.schemas.bookings import SeatBookingRequest, CancelBookingRequest, BookingOut
from app.processor.booking_processor import BookingProcessor
from app.processor.payment_processor import PaymentProcessor
from app.core.redis import redis

router = APIRouter()

@router.post("/book", status_code=201)
async def book_seats_api(payload: SeatBookingRequest, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Book seats for an event with payment flow"""
    try:
        result = await PaymentProcessor.initiate_booking_with_payment(
            db, str(payload.event_id), current_user["user_id"], [str(s) for s in payload.seat_ids]
        )
        
        if not result["success"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/cancel", status_code=200)
async def cancel_booking_api(payload: CancelBookingRequest, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Cancel a pending booking and release seats"""
    try:
        result = await PaymentProcessor.cancel_booking(db, str(payload.booking_id))
        
        if not result["success"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/debug/redis-locks")
async def debug_redis_locks_api():
    """Debug endpoint to see all Redis lock keys"""
    try:
        # Test Redis connection
        await redis.ping()
        
        # Get all lock keys
        lock_keys = await redis.keys("lock:*")
        lock_details = []
        
        for key in lock_keys:
            value = await redis.get(key)
            ttl = await redis.ttl(key)
            lock_details.append({
                "key": key,
                "value": value,
                "ttl": ttl
            })
        
        return {
            "redis_connection": "OK",
            "total_locks": len(lock_keys),
            "lock_details": lock_details
        }
    except Exception as e:
        return {"redis_connection": "ERROR", "error": str(e)}


@router.post("/debug/create-test-lock")
async def create_test_lock():
    """Create a test lock for debugging"""
    try:
        test_key = "lock:test-event:test-seat"
        test_value = "test-user-123"
        await redis.set(test_key, test_value, ex=60)  # 60 seconds TTL
        return {"message": "Test lock created", "key": test_key, "value": test_value, "ttl": 60}
    except Exception as e:
        return {"error": str(e)}


@router.delete("/debug/clear-all-locks")
async def clear_all_locks():
    """Clear all Redis locks (for testing)"""
    try:
        lock_keys = await redis.keys("lock:*")
        if lock_keys:
            await redis.delete(*lock_keys)
            return {"message": f"Cleared {len(lock_keys)} locks", "cleared_keys": lock_keys}
        else:
            return {"message": "No locks found to clear"}
    except Exception as e:
        return {"error": str(e)}


@router.get("/get-bookings-by-user", response_model=List[BookingOut])
async def get_bookings_by_user_api(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Get all bookings for the current user"""
    try:
        return await BookingProcessor.get_bookings_by_user(db, current_user["user_id"])
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))