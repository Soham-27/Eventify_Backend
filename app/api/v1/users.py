from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.users import UserCreate, UserLogin, UserOut, UserWithToken, UserMe
from app.processor.user_processor import UserProcessor
from app.db.deps import get_db
from app.middleware.authenticated import get_current_user

router = APIRouter()

@router.post("/", status_code=201, response_model=UserWithToken)
async def create_user_api(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user"""
    try:
        return await UserProcessor.create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/me", status_code=200, response_model=UserMe)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/login", status_code=200, response_model=UserWithToken)
async def login_user_api(user: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return token"""
    try:
        return await UserProcessor.authenticate_user(db, user.email, user.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


