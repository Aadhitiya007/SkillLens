"""
User Authentication Service
JWT-based authentication with user registration and login.
Updated to use PostgreSQL with SQLAlchemy.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
import jwt
import uuid

from app.config import settings
from app.database import User as UserModel, create_session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, Field

logger = logging.getLogger(__name__)


class UserCreate(BaseModel):
    """User registration model."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    role: str = "student"  # student, admin, placement_cell, faculty
    department: Optional[str] = None
    register_number: Optional[str] = None


class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str


class User(BaseModel):
    """User response model."""
    user_id: str
    email: str
    full_name: str
    role: str
    department: Optional[str] = None
    register_number: Optional[str] = None
    created_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: User


def get_password_hash(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


class AuthService:
    """Authentication service with JWT and PostgreSQL."""
    
    def __init__(self):
        """Initialize auth service."""
        self.secret_key = settings.secret_key if hasattr(settings, 'secret_key') else settings.jwt_secret
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.jwt_expiration_minutes
    
    def _create_access_token(self, data: dict) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    async def register_user(self, user_data: UserCreate, db: AsyncSession) -> Token:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            db: Database session
            
        Returns:
            JWT token and user info
        """
        try:
            # Check if user already exists
            result = await db.execute(
                select(UserModel).where(UserModel.email == user_data.email)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                raise ValueError("Email already registered")
            
            # Create new user
            new_user = UserModel(
                email=user_data.email,
                hashed_password=get_password_hash(user_data.password),
                full_name=user_data.full_name,
                role=user_data.role,
                department=user_data.department,
                register_number=user_data.register_number,
                is_active=True
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            # Create access token
            access_token = self._create_access_token({
                "sub": str(new_user.id),
                "email": new_user.email
            })
            
            # Return token and user
            user = User(
                user_id=str(new_user.id),
                email=new_user.email,
                full_name=new_user.full_name,
                role=new_user.role,
                department=new_user.department,
                register_number=new_user.register_number,
                created_at=new_user.created_at,
                is_active=new_user.is_active
            )
            
            return Token(access_token=access_token, user=user)
            
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            raise Exception("Failed to register user")
    
    async def login_user(self, login_data: UserLogin, db: AsyncSession) -> Token:
        """
        Authenticate user and return token.
        
        Args:
            login_data: User login credentials
            db: Database session
            
        Returns:
            JWT token and user info
        """
        try:
            # Find user
            result = await db.execute(
                select(UserModel).where(UserModel.email == login_data.email)
            )
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                raise ValueError("Invalid email or password")
            
            # Verify password
            if not verify_password(login_data.password, user_model.hashed_password):
                raise ValueError("Invalid email or password")
            
            # Check if user is active
            if not user_model.is_active:
                raise ValueError("Account is deactivated")
            
            # Create access token
            access_token = self._create_access_token({
                "sub": str(user_model.id),
                "email": user_model.email
            })
            
            # Return token and user
            user = User(
                user_id=str(user_model.id),
                email=user_model.email,
                full_name=user_model.full_name,
                role=user_model.role,
                department=user_model.department,
                register_number=user_model.register_number,
                created_at=user_model.created_at,
                is_active=user_model.is_active
            )
            
            return Token(access_token=access_token, user=user)
            
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error logging in user: {e}")
            raise Exception("Failed to login")
    
    async def verify_token(self, token: str, db: AsyncSession) -> Optional[User]:
        """
        Verify JWT token and return user.
        
        Args:
            token: JWT access token
            db: Database session
            
        Returns:
            User if valid, None otherwise
        """
        try:
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id_str = payload.get("sub")
            
            if user_id_str is None:
                return None
            
            # Convert to UUID
            try:
                user_id = uuid.UUID(user_id_str)
            except ValueError:
                return None
            
            # Get user from database
            result = await db.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                return None
            
            return User(
                user_id=str(user_model.id),
                email=user_model.email,
                full_name=user_model.full_name,
                role=user_model.role,
                department=user_model.department,
                register_number=user_model.register_number,
                created_at=user_model.created_at,
                is_active=user_model.is_active
            )
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.JWTError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str, db: AsyncSession) -> Optional[User]:
        """Get user by ID."""
        try:
            user_uuid = uuid.UUID(user_id)
            result = await db.execute(
                select(UserModel).where(UserModel.id == user_uuid)
            )
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                return None
            
            return User(
                user_id=str(user_model.id),
                email=user_model.email,
                full_name=user_model.full_name,
                role=user_model.role,
                department=user_model.department,
                register_number=user_model.register_number,
                created_at=user_model.created_at,
                is_active=user_model.is_active
            )
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None


# Singleton instance
_auth_service = None

def get_auth_service() -> AuthService:
    """Get singleton instance of auth service."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
