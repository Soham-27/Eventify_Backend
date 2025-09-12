from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from app.schemas.venues import VenueCreate, VenueUpdate, VenueOut
from app.crud.venues import create_venue, get_venue_by_id, update_venue, get_venues, delete_venue
from app.db.deps import get_db
from app.middleware.authenticated import get_current_user

router = APIRouter()


@router.post("/", status_code=201, response_model=VenueOut)
async def create_venue_api(venue: VenueCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)) -> VenueOut:
    if current_user['role'] != 'ADMIN':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create venues")
    return await create_venue(db, venue)


@router.get("/{venue_id}", status_code=200, response_model=VenueOut)
async def get_venue_api(venue_id: str, db: AsyncSession = Depends(get_db)):
    venue = await get_venue_by_id(db, venue_id)
    if not venue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue not found")
    return venue


@router.get("/", status_code=200, response_model=list[VenueOut])
async def get_venues_api(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await get_venues(db, skip, limit)


@router.put("/{venue_id}", status_code=200, response_model=VenueOut)
async def update_venue_api(venue_id: str, venue_update: VenueUpdate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)) -> VenueOut:
    if current_user['role'] != 'ADMIN':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update venues")
    
    venue = await update_venue(db, venue_id, venue_update)
    if not venue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue not found")
    return venue


@router.delete("/{venue_id}", status_code=200, response_model=dict)
async def delete_venue_api(venue_id: str, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'ADMIN':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete venues")
    
    result = await delete_venue(db, venue_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue not found")
    return {"message": "Venue deleted successfully"}
