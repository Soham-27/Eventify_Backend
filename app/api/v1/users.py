from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.users import UserCreate, UserLogin, UserOut, UserWithToken, UserMe
from app.crud.users import create_user, authenticate_user
from app.db.deps import get_db
from app.middleware.authenticated import get_current_user

router = APIRouter()

@router.post("/", status_code=201,response_model=UserWithToken)
async def create_user_api(user: UserCreate, db: AsyncSession = Depends(get_db)):
    print(user)
    return await create_user(db, user)

@router.get("/me", status_code=200,response_model=UserMe)
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.post("/login",status_code=200,response_model=UserWithToken)
async def login_user_api(user: UserLogin, db: AsyncSession = Depends(get_db)):
    return await authenticate_user(db, user.email, user.password)