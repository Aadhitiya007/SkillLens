"""
Pydantic models for prediction endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class PredictionRequest(BaseModel):
    """Request for shortlisting probability prediction."""
    resume_id: Optional[str] = None
    resume_text: Optional[str] = None
    job_description: str
    user_skills: List[str] = []
    experience_years: float = 0.0
    
    class Config:
        json_schema_extra = {
            "example": {
                "resume_text": "Software Engineer with 3 years experience in Python, React...",
                "job_description": "Looking for Full Stack Developer with React, Node.js, MongoDB...",
                "user_skills": ["Python", "React", "JavaScript"],
                "experience_years": 3.0
            }
        }


class PredictionResponse(BaseModel):
    """Response with shortlisting probability."""
    shortlist_probability: float = Field(..., ge=0, le=100, description="Probability of being shortlisted (0-100%)")
    confidence: str  # "High", "Medium", "Low"
    factors: Dict[str, float]  # Contributing factors
    recommendations: List[str]  # What to improve
    predicted_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "shortlist_probability": 75.5,
                "confidence": "High",
                "factors": {
                    "skill_match": 0.85,
                    "ats_compatibility": 0.90,
                    "experience_match": 0.70,
                    "resume_quality": 0.80
                },
                "recommendations": [
                    "Add MongoDB to your skills",
                    "Improve ATS compatibility by 10%"
                ]
            }
        }


class BatchPredictionRequest(BaseModel):
    """Request for batch predictions."""
    resume_id: Optional[str] = None
    resume_text: Optional[str] = None
    job_descriptions: List[str]
    user_skills: List[str] = []
    experience_years: float = 0.0


class JobPrediction(BaseModel):
    """Single job prediction."""
    job_description: str
    shortlist_probability: float
    confidence: str
    rank: int  # Ranking among all jobs


class BatchPredictionResponse(BaseModel):
    """Response with multiple predictions."""
    predictions: List[JobPrediction]
    best_match: JobPrediction
    total_jobs: int
    predicted_at: datetime = Field(default_factory=datetime.utcnow)
