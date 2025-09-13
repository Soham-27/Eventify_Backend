from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.deps import get_db
from app.middleware.authenticated import get_current_user
from app.schemas.bookings import SeatBookingRequest, CancelBookingRequest, BookingOut
from app.crud.bookings import book_seats_with_lock, get_bookings_by_user

router = APIRouter()

@router.post("/book", status_code=201)
async def book_seats_api(payload: SeatBookingRequest, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        result = await book_seats_with_lock(db, str(payload.event_id), current_user["user_id"], [str(s) for s in payload.seat_ids])
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/cancel", status_code=200)
async def cancel_booking_api(payload: CancelBookingRequest, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    ok = await cancel_booking_and_release(db, str(payload.booking_id))
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return {"message": "Booking cancelled and seats released"}


# @router.get("/debug/redis-locks")
# async def debug_redis_locks_api():
#     """Debug endpoint to see all Redis lock keys"""
#     return await debug_redis_locks()


# @router.post("/debug/create-test-lock")
# async def create_test_lock():
#     """Create a test lock for debugging"""
#     from app.core.redis import redis
#     try:
#         test_key = "lock:test-event:test-seat"
#         test_value = "test-user-123"
#         await redis.set(test_key, test_value, ex=60)  # 60 seconds TTL
#         return {"message": "Test lock created", "key": test_key, "value": test_value}
#     except Exception as e:
#         return {"error": str(e)}


@router.get("/get-bookings-by-user", response_model=List[BookingOut])
async def get_bookings_by_user_api(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return await get_bookings_by_user(db, current_user["user_id"])