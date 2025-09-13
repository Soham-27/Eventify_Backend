from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.deps import get_db
from app.crud.analytics import (
    get_total_confirmed_bookings, 
    get_most_popular_events, 
    get_capacity_utilization
)
from app.schemas.analytics import PopularEvent, CapacityUtilization
from app.middleware.authenticated import get_current_user
from typing import List

router = APIRouter()


@router.get("/admin/total-bookings")
async def get_total_bookings_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get total number of confirmed bookings
    """
    try:
        if current_user['role'] != 'ADMIN':
            raise HTTPException(status_code=403, detail="Forbidden")
        
        total_bookings = await get_total_confirmed_bookings(db)
        return {"total_confirmed_bookings": total_bookings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/popular-events", response_model=List[PopularEvent])
async def get_popular_events_endpoint(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get most popular events (top N by seats booked)
    """
    try:
        if current_user['role'] != 'ADMIN':
            raise HTTPException(status_code=403, detail="Forbidden")
        
        popular_events = await get_most_popular_events(db, limit=limit)
        return popular_events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/capacity-utilization", response_model=List[CapacityUtilization])
async def get_capacity_utilization_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get capacity utilization for all events
    """
    try:
        if current_user['role'] != 'ADMIN':
            raise HTTPException(status_code=403, detail="Forbidden")
        
        capacity_utilization = await get_capacity_utilization(db)
        return capacity_utilization
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
