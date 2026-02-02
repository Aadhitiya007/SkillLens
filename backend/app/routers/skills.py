"""
Skills API router.
Handles skill graph operations, gap analysis, and learning paths.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from pydantic import BaseModel
import logging

from app.services.skill_graph import skill_graph_service
from app.database import get_db, Collections

logger = logging.getLogger(__name__)

router = APIRouter()


class SkillGapRequest(BaseModel):
    """Request model for skill gap analysis."""
    user_skills: List[str]
    target_role: str


class LearningPathRequest(BaseModel):
    """Request model for learning path generation."""
    user_skills: List[str]
    target_role: str


@router.post("/initialize")
async def initialize_skill_graph():
    """
    Initialize the skill knowledge graph.
    This should be called once during setup.
    """
    try:
        await skill_graph_service.initialize_skill_graph()
        return {"message": "Skill graph initialized successfully"}
    except Exception as e:
        logger.error(f"Error initializing skill graph: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize skill graph: {str(e)}"
        )


@router.get("/hierarchy")
async def get_skill_hierarchy():
    """
    Get the complete skill hierarchy organized by category.
    """
    try:
        hierarchy = await skill_graph_service.get_skill_hierarchy()
        return hierarchy
    except Exception as e:
        logger.error(f"Error getting skill hierarchy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get skill hierarchy: {str(e)}"
        )


@router.post("/gap-analysis")
async def analyze_skill_gap(request: SkillGapRequest):
    """
    Analyze skill gaps for a target role.
    
    - **user_skills**: List of skills the user currently has
    - **target_role**: Target role title (e.g., "Data Engineer")
    """
    try:
        missing_skills = await skill_graph_service.find_missing_skills(
            request.user_skills,
            request.target_role
        )
        
        explanation = await skill_graph_service.explain_skill_gap(
            request.user_skills,
            request.target_role
        )
        
        return {
            "target_role": request.target_role,
            "user_skills_count": len(request.user_skills),
            "missing_skills": missing_skills,
            "explanation": explanation
        }
    
    except Exception as e:
        logger.error(f"Error analyzing skill gap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze skill gap: {str(e)}"
        )


@router.get("/dependencies/{skill}")
async def get_skill_dependencies(skill: str):
    """
    Get all dependencies for a specific skill.
    
    - **skill**: Skill name
    """
    try:
        dependencies = await skill_graph_service.get_skill_dependencies(skill)
        return {
            "skill": skill,
            "dependencies": dependencies,
            "count": len(dependencies)
        }
    except Exception as e:
        logger.error(f"Error getting skill dependencies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get skill dependencies: {str(e)}"
        )


@router.post("/learning-path")
async def generate_learning_path(request: LearningPathRequest):
    """
    Generate an ordered learning path for a target role.
    
    - **user_skills**: List of skills the user currently has
    - **target_role**: Target role title
    """
    try:
        learning_path = await skill_graph_service.get_learning_path(
            request.user_skills,
            request.target_role
        )
        
        return {
            "target_role": request.target_role,
            "total_skills_to_learn": len(learning_path),
            "learning_path": learning_path
        }
    
    except Exception as e:
        logger.error(f"Error generating learning path: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate learning path: {str(e)}"
        )
