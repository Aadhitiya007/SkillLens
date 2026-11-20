"""
Pydantic models for user management and authentication.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""
    STUDENT = "student"
    ADMIN = "admin"
    PLACEMENT_CELL = "placement_cell"
    FACULTY = "faculty"


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.STUDENT


class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=8)
    department: Optional[str] = None
    register_number: Optional[str] = None


class UserUpdate(BaseModel):
    """User update model."""
    full_name: Optional[str] = None
    department: Optional[str] = None
    register_number: Optional[str] = None


class UserInDB(UserBase):
    """User model as stored in database."""
    id: str = Field(alias="_id")
    hashed_password: str
    department: Optional[str] = None
    register_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    class Config:
        populate_by_name = True


class UserResponse(UserBase):
    """User response model (without password)."""
    id: str
    department: Optional[str] = None
    register_number: Optional[str] = None
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    user_id: Optional[str] = None
    email: Optional[str] = None
