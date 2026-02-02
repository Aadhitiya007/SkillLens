"""
Pydantic models for skill verification.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class QuestionType(str, Enum):
    """Question type enumeration."""
    MULTIPLE_CHOICE = "multiple_choice"
    CODE = "code"
    THEORETICAL = "theoretical"


class DifficultyLevel(str, Enum):
    """Difficulty level enumeration."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Question(BaseModel):
    """Single assessment question."""
    question_id: str
    skill: str
    question_text: str
    question_type: QuestionType
    difficulty: DifficultyLevel
    options: Optional[List[str]] = None  # For multiple choice
    correct_answer: str
    explanation: str
    points: int = 10


class AssessmentRequest(BaseModel):
    """Request to generate skill assessment."""
    user_id: str
    skill: str
    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    num_questions: int = Field(default=5, ge=1, le=20)


class AssessmentResponse(BaseModel):
    """Generated assessment."""
    assessment_id: str
    skill: str
    questions: List[Question]
    total_points: int
    time_limit_minutes: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AnswerSubmission(BaseModel):
    """User's answer to a question."""
    question_id: str
    user_answer: str


class AssessmentSubmission(BaseModel):
    """Complete assessment submission."""
    assessment_id: str
    user_id: str
    answers: List[AnswerSubmission]


class AssessmentResult(BaseModel):
    """Assessment results."""
    assessment_id: str
    user_id: str
    skill: str
    score: int
    max_score: int
    percentage: float
    confidence_level: str  # "Verified", "Partial", "Not Verified"
    passed: bool
    feedback: List[str]
    completed_at: datetime = Field(default_factory=datetime.utcnow)
