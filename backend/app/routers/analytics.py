"""
Analytics API Router
Endpoints for institutional analytics and reporting.
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional

from app.services.institutional_analytics import get_analytics_service

router = APIRouter()


@router.get("/placement-statistics")
async def get_placement_statistics(department: Optional[str] = Query(None)):
    """
    Get placement statistics for institution or specific department.
    
    Returns placement rates, average packages, top recruiters, and more.
    """
    try:
        service = get_analytics_service()
        stats = await service.get_placement_statistics(department)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting placement statistics: {str(e)}"
        )


@router.get("/readiness-distribution")
async def get_readiness_distribution():
    """
    Get distribution of student readiness scores.
    
    Returns score ranges with student counts and percentages.
    """
    try:
        service = get_analytics_service()
        distribution = await service.get_student_readiness_distribution()
        return distribution
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting readiness distribution: {str(e)}"
        )


@router.get("/skill-gap-analysis")
async def get_skill_gap_analysis():
    """
    Get institution-wide skill gap analysis.
    
    Returns most common skill gaps and recommendations.
    """
    try:
        service = get_analytics_service()
        analysis = await service.get_skill_gap_analysis()
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting skill gap analysis: {str(e)}"
        )


@router.get("/timeline")
async def get_timeline_analytics(days: int = Query(30, ge=1, le=365)):
    """
    Get time-series analytics for the past N days.
    
    Returns daily metrics for active users, uploads, assessments, etc.
    """
    try:
        service = get_analytics_service()
        timeline = await service.get_timeline_analytics(days)
        return timeline
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting timeline analytics: {str(e)}"
        )


@router.get("/health")
async def analytics_health_check():
    """Health check for analytics service."""
    return {
        "status": "healthy",
        "service": "Institutional Analytics",
        "features": [
            "Placement Statistics",
            "Readiness Distribution",
            "Skill Gap Analysis",
            "Timeline Analytics"
        ]
    }
