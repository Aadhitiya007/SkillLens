"""Models package initialization."""

from app.models.user import (
    UserRole,
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDB,
    UserResponse,
    Token,
    TokenData,
)
from app.models.resume import (
    Experience,
    Project,
    Education,
    ResumeData,
    ResumeUploadResponse,
    ResumeInDB,
)
from app.models.scoring import (
    FactorContribution,
    ReadinessScore,
    ReadinessScoreRequest,
    ReadinessScoreInDB,
    ReadinessHistory,
)

__all__ = [
    # User models
    "UserRole",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    "Token",
    "TokenData",
    # Resume models
    "Experience",
    "Project",
    "Education",
    "ResumeData",
    "ResumeUploadResponse",
    "ResumeInDB",
    # Scoring models
    "FactorContribution",
    "ReadinessScore",
    "ReadinessScoreRequest",
    "ReadinessScoreInDB",
    "ReadinessHistory",
]
