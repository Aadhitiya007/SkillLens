"""
Pydantic models for career readiness scoring.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class FactorContribution(BaseModel):
    """Individual factor contribution to readiness score."""
    factor_name: str
    weight: float
    score: float
    contribution: float
    details: Optional[str] = None


class ReadinessScore(BaseModel):
    """Career readiness score model."""
    overall_score: float = Field(..., ge=0, le=100)
    target_role: str
    factors: List[FactorContribution]
    explanation: str
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]


class ReadinessScoreRequest(BaseModel):
    """Request model for readiness scoring."""
    user_id: str
    target_role: str
    include_explanation: bool = True


class ReadinessScoreInDB(BaseModel):
    """Readiness score as stored in database."""
    id: str = Field(alias="_id")
    user_id: str
    score_data: ReadinessScore
    calculated_at: datetime
    
    class Config:
        populate_by_name = True


class ReadinessHistory(BaseModel):
    """Historical readiness scores for a user."""
    user_id: str
    target_role: str
    scores: List[Dict[str, Any]]  # List of {date, score} pairs
