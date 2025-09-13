from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.event_seats import EventSeatOut, EventSeatWithSeatOut, RowPriceUpdate, RowPriceUpdateResponse
from app.processor.event_seat_processor import EventSeatProcessor
from app.db.deps import get_db
from app.middleware.authenticated import get_current_user

router = APIRouter()


@router.get("/event/{event_id}", response_model=list[EventSeatWithSeatOut])
async def get_event_seats_api(
    event_id: str, 
    db: AsyncSession = Depends(get_db)
):
    """Get all event seats for an event"""
    try:
        return await EventSeatProcessor.get_event_seats_by_event(db, event_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/event/{event_id}/available", response_model=list[EventSeatOut])
async def get_available_event_seats_api(
    event_id: str, 
    db: AsyncSession = Depends(get_db)
):
    """Get all available event seats for an event"""
    try:
        return await EventSeatProcessor.get_available_event_seats(db, event_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/event/{event_id}/row/{row_no}", response_model=list[EventSeatOut])
async def get_event_seats_by_row_api(
    event_id: str, 
    row_no: str, 
    db: AsyncSession = Depends(get_db)
):
    """Get all event seats for a specific row in an event"""
    try:
        return await EventSeatProcessor.get_event_seats_by_row(db, event_id, row_no)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/event/{event_id}/row/price", response_model=RowPriceUpdateResponse)
async def update_row_price_api(
    event_id: str,
    price_update: RowPriceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update price for all seats in a specific row (admin only)"""
    if current_user['role'] != 'ADMIN':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to update seat prices"
        )
    
    try:
        result = await EventSeatProcessor.update_event_seats_price_by_row(
            db, 
            event_id, 
            price_update.row_no, 
            float(price_update.new_price)
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
