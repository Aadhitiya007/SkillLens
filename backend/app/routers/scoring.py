"""
Scoring API router.
Handles career readiness scoring and explanations.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
import logging
import uuid

from app.models.scoring import ReadinessScoreRequest, ReadinessScore
from app.database import get_db, Resume as ResumeModel, ReadinessScore as ScoreModel
from app.services.scoring_engine import scoring_engine

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/readiness", response_model=ReadinessScore)
async def calculate_readiness(
    request: ReadinessScoreRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate career readiness score for a user.
    
    - **user_id**: User ID
    - **target_role**: Target role title (e.g., "Data Engineer")
    - **include_explanation**: Whether to include GPT-generated explanation
    """
    try:
        # Convert user_id to UUID
        try:
            user_uuid = uuid.UUID(request.user_id)
        except ValueError:
            user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, request.user_id)
        
        # Get user's most recent resume
        result = await db.execute(
            select(ResumeModel)
            .where(ResumeModel.user_id == user_uuid)
            .order_by(desc(ResumeModel.uploaded_at))
            .limit(1)
        )
        resume = result.scalar_one_or_none()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resume found for this user. Please upload a resume first."
            )
        
        # Get required skills for target role
        # In production, this would come from Neo4j knowledge graph
        role_requirements = {
            "Data Engineer": {
                "skills": ["Python", "SQL", "Apache Spark", "ETL", "Data Modeling", "AWS", "Docker"],
                "tools": ["Git", "Jupyter", "Airflow"]
            },
            "Software Engineer": {
                "skills": ["Python", "Java", "JavaScript", "SQL", "Docker", "CI/CD"],
                "tools": ["Git", "Jira", "Jenkins"]
            },
            "Data Scientist": {
                "skills": ["Python", "R", "SQL", "Machine Learning", "Statistics", "Deep Learning"],
                "tools": ["Jupyter", "Git", "TensorFlow"]
            },
            "Full Stack Developer": {
                "skills": ["JavaScript", "React", "Node.js", "SQL", "MongoDB", "Docker"],
                "tools": ["Git", "VS Code", "Postman"]
            }
        }
        
        requirements = role_requirements.get(
            request.target_role,
            {"skills": [], "tools": []}
        )
        
        # Parse resume data
        from app.models.resume import ResumeData
        resume_data = ResumeData(**resume.parsed_data)
        
        # Calculate readiness score
        score_result = await scoring_engine.calculate_readiness_score(
            resume_data=resume_data,
            target_role=request.target_role,
            required_skills=requirements["skills"],
            required_tools=requirements.get("tools", [])
        )
        
        # Store score in database
        score_record = ScoreModel(
            user_id=user_uuid,
            resume_id=resume.id,
            target_role=request.target_role,
            overall_score=score_result.overall_score,
            technical_skills_score=score_result.factors[0].score if len(score_result.factors) > 0 else None,
            experience_score=score_result.factors[1].score if len(score_result.factors) > 1 else None,
            project_score=score_result.factors[2].score if len(score_result.factors) > 2 else None,
            tool_score=score_result.factors[3].score if len(score_result.factors) > 3 else None,
            explanation=score_result.explanation,
            strengths=score_result.strengths,
            weaknesses=score_result.weaknesses,
            recommendations=score_result.recommendations,
            factors=[f.model_dump() for f in score_result.factors]
        )
        
        db.add(score_record)
        await db.commit()
        await db.refresh(score_record)
        
        logger.info(f"Calculated readiness score for user {request.user_id}: {score_result.overall_score}")
        
        return score_result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating readiness score: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate readiness score: {str(e)}"
        )


@router.get("/history/{user_id}")
async def get_score_history(
    user_id: str,
    target_role: str = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get historical readiness scores for a user.
    
    - **user_id**: User ID
    - **target_role**: Optional filter by target role
    - **limit**: Maximum number of records to return
    """
    try:
        # Convert user_id to UUID
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, user_id)
        
        # Build query
        query = select(ScoreModel).where(ScoreModel.user_id == user_uuid)
        
        if target_role:
            query = query.where(ScoreModel.target_role == target_role)
        
        query = query.order_by(desc(ScoreModel.created_at)).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        scores = result.scalars().all()
        
        # Format response
        history = [
            {
                "date": score.created_at,
                "score": float(score.overall_score),
                "target_role": score.target_role
            }
            for score in scores
        ]
        
        return {
            "user_id": user_id,
            "target_role": target_role,
            "history": history,
            "count": len(history)
        }
    
    except Exception as e:
        logger.error(f"Error getting score history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get score history: {str(e)}"
        )


@router.get("/explanation/{user_id}")
async def get_latest_explanation(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the latest readiness score explanation for a user.
    
    - **user_id**: User ID
    """
    try:
        # Convert user_id to UUID
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, user_id)
        
        # Get latest score
        result = await db.execute(
            select(ScoreModel)
            .where(ScoreModel.user_id == user_uuid)
            .order_by(desc(ScoreModel.created_at))
            .limit(1)
        )
        score = result.scalar_one_or_none()
        
        if not score:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No readiness score found for this user"
            )
        
        return {
            "user_id": user_id,
            "calculated_at": score.created_at,
            "overall_score": float(score.overall_score),
            "target_role": score.target_role,
            "explanation": score.explanation,
            "strengths": score.strengths,
            "weaknesses": score.weaknesses,
            "recommendations": score.recommendations,
            "factors": score.factors
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting explanation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get explanation: {str(e)}"
        )


@router.get("/health")
async def scoring_health_check():
    """Health check for scoring service."""
    return {
        "status": "healthy",
        "service": "Career Readiness Scoring",
        "database": "PostgreSQL",
        "features": [
            "Multi-factor Scoring",
            "Explainable AI",
            "Score History Tracking",
            "Personalized Recommendations"
        ]
    }
