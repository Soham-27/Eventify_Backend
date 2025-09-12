import bcrypt
import jwt
from datetime import datetime, timedelta
from app.models.users import User
from app.schemas.users import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

SECRET_KEY = "your_secret_key"  # Use a secure key and keep it secret

async def create_user(db: AsyncSession, user: UserCreate):
    try:
        existing_user = await get_user_by_email(db, user.email)
        if existing_user:
            raise Exception("User already exists")
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db_user = User(
            name=user.name, 
            email=user.email, 
            password_hash=hashed_password, 
            role=user.role
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        # Generate JWT token
        payload = {
            "user_id": str(db_user.id),
            "role": db_user.role,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return {
            "user_id": str(db_user.id),
            "role": db_user.role,
            "email": db_user.email,
            "token": token
        }
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error creating user: {str(e)}")

async def get_users(db: AsyncSession):
    try:
        result = await db.execute(select(User))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise


async def get_user_by_email(db: AsyncSession, email: str):
    try:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching user: {str(e)}")
    
async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        payload = {
            "user_id": str(user.id),
            "role": user.role,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return {
            "user_id": str(user.id),
            "role": user.role,
            "email": user.email,
            "token": token
        }
    return None

