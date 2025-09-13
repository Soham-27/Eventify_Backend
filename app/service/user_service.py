"""User database service operations"""

import bcrypt
import jwt
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.models.users import User
from app.schemas.users import UserCreate

SECRET_KEY = "your_secret_key"  # Use a secure key and keep it secret


class UserService:
    """Service class for user database operations"""
    
    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate):
        """Create user in database"""
        try:
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
            return db_user
        except SQLAlchemyError as e:
            await db.rollback()
            raise Exception(f"Error creating user: {str(e)}")

    @staticmethod
    async def get_users(db: AsyncSession):
        """Get all users from database"""
        try:
            result = await db.execute(select(User))
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching users: {str(e)}")

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str):
        """Get user by email from database"""
        try:
            result = await db.execute(select(User).where(User.email == email))
            return result.scalars().first()
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching user: {str(e)}")

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str):
        """Get user by ID from database"""
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            return result.scalars().first()
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching user: {str(e)}")

    @staticmethod
    async def update_user(db: AsyncSession, user_id: str, user_data: dict):
        """Update user in database"""
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            db_user = result.scalars().first()
            if not db_user:
                return None
            
            for key, value in user_data.items():
                if hasattr(db_user, key) and value is not None:
                    setattr(db_user, key, value)
            
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            return db_user
        except SQLAlchemyError as e:
            await db.rollback()
            raise Exception(f"Error updating user: {str(e)}")

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: str):
        """Delete user from database"""
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            db_user = result.scalars().first()
            if not db_user:
                return None
            
            await db.delete(db_user)
            await db.commit()
            return True
        except SQLAlchemyError as e:
            await db.rollback()
            raise Exception(f"Error deleting user: {str(e)}")

    @staticmethod
    def generate_jwt_token(user_id: str, role: str) -> str:
        """Generate JWT token for user"""
        payload = {
            "user_id": user_id,
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify user password"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
