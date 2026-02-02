"""
Jobs API Router
Endpoints for job recommendations and market intelligence.
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from pydantic import BaseModel

from app.services.job_market import get_job_market_service

router = APIRouter()


class JobRecommendationRequest(BaseModel):
    """Request for job recommendations."""
    user_skills: List[str]
    experience_years: float = 0
    limit: int = 10


@router.post("/recommendations")
async def get_job_recommendations(request: JobRecommendationRequest):
    """
    Get personalized job recommendations based on skills and experience.
    
    Returns jobs ranked by match score with missing skills identified.
    """
    try:
        service = get_job_market_service()
        recommendations = await service.get_job_recommendations(
            request.user_skills,
            request.experience_years,
            request.limit
        )
        return {
            "recommendations": recommendations,
            "total": len(recommendations)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting recommendations: {str(e)}"
        )


@router.get("/market-trends")
async def get_market_trends(skill: Optional[str] = Query(None)):
    """
    Get job market trends and insights.
    
    Returns top skills, roles, salary trends, and market statistics.
    """
    try:
        service = get_job_market_service()
        trends = await service.get_market_trends(skill)
        return trends
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting market trends: {str(e)}"
        )


@router.get("/health")
async def jobs_health_check():
    """Health check for jobs service."""
    return {
        "status": "healthy",
        "service": "Job Market Intelligence",
        "features": [
            "Job Recommendations",
            "Market Trends",
            "Skill Demand Analysis",
            "Salary Insights"
        ]
    }
