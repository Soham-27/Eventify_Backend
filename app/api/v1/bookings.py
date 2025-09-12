from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.deps import get_db
from app.middleware.authenticated import get_current_user
from app.schemas.bookings import SeatBookingRequest, CancelBookingRequest
from app.crud.bookings import book_seats_with_lock, cancel_booking_and_release

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
