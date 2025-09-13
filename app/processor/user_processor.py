"""User business logic processor"""

import re
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.users import UserCreate, UserLogin
from app.service.user_service import UserService


class UserProcessor:
    """Processor class for user business logic"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password strength"""
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):  # At least one uppercase
            return False
        if not re.search(r'[a-z]', password):  # At least one lowercase
            return False
        if not re.search(r'\d', password):  # At least one digit
            return False
        return True

    @staticmethod
    def validate_name(name: str) -> bool:
        """Validate name format"""
        if not name or len(name.strip()) < 2:
            return False
        if len(name) > 100:
            return False
        return True

    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate):
        """Process user creation with business logic"""
        # Business logic: Validate input data
        if not UserProcessor.validate_name(user.name):
            raise ValueError("Name must be between 2 and 100 characters")
        
        if not UserProcessor.validate_email(user.email):
            raise ValueError("Invalid email format")
        
        if not UserProcessor.validate_password(user.password):
            raise ValueError("Password must be at least 8 characters with uppercase, lowercase, and digit")
        
        if user.role not in ['ADMIN', 'USER']:
            raise ValueError("Role must be either 'ADMIN' or 'USER'")
        
        # Check if user already exists
        existing_user = await UserService.get_user_by_email(db, user.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Call service layer
        db_user = await UserService.create_user(db, user)
        
        # Generate JWT token
        token = UserService.generate_jwt_token(str(db_user.id), db_user.role)
        
        return {
            "user_id": str(db_user.id),
            "role": db_user.role,
            "email": db_user.email,
            "token": token
        }

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str):
        """Process user authentication with business logic"""
        # Business logic: Validate input data
        if not email or not password:
            raise ValueError("Email and password are required")
        
        if not UserProcessor.validate_email(email):
            raise ValueError("Invalid email format")
        
        # Get user from database
        user = await UserService.get_user_by_email(db, email)
        if not user:
            raise ValueError("Invalid email or password")
        
        # Verify password
        if not UserService.verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")
        
        # Generate JWT token
        token = UserService.generate_jwt_token(str(user.id), user.role)
        
        return {
            "user_id": str(user.id),
            "role": user.role,
            "email": user.email,
            "token": token
        }

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str):
        """Process getting user by ID with business logic"""
        # Business logic: Validate user ID format
        if not user_id or len(user_id) < 10:
            raise ValueError("Invalid user ID")
        
        # Call service layer
        return await UserService.get_user_by_id(db, user_id)

    @staticmethod
    async def get_users(db: AsyncSession):
        """Process getting all users with business logic"""
        # Business logic: Additional validation can be added here
        # For example: check if user has permission to view all users
        
        # Call service layer
        return await UserService.get_users(db)

    @staticmethod
    async def update_user(db: AsyncSession, user_id: str, user_data: dict):
        """Process user update with business logic"""
        # Business logic: Validate update data
        if 'email' in user_data and not UserProcessor.validate_email(user_data['email']):
            raise ValueError("Invalid email format")
        
        if 'name' in user_data and not UserProcessor.validate_name(user_data['name']):
            raise ValueError("Name must be between 2 and 100 characters")
        
        if 'role' in user_data and user_data['role'] not in ['ADMIN', 'USER']:
            raise ValueError("Role must be either 'ADMIN' or 'USER'")
        
        # Check if user exists
        existing_user = await UserService.get_user_by_id(db, user_id)
        if not existing_user:
            raise ValueError("User not found")
        
        # Check if email is already taken by another user
        if 'email' in user_data and user_data['email'] != existing_user.email:
            email_user = await UserService.get_user_by_email(db, user_data['email'])
            if email_user:
                raise ValueError("Email already taken by another user")
        
        # Call service layer
        return await UserService.update_user(db, user_id, user_data)

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: str):
        """Process user deletion with business logic"""
        # Business logic: Check if user exists
        existing_user = await UserService.get_user_by_id(db, user_id)
        if not existing_user:
            raise ValueError("User not found")
        
        # Additional business logic can be added here
        # For example: check if user has active bookings, prevent admin deletion, etc.
        
        # Call service layer
        return await UserService.delete_user(db, user_id)
