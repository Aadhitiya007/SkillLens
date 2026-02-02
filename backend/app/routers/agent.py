"""
AI Agent API Router
Endpoints for conversational AI agent and learning path generation.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional

from app.models.agent_models import (
    ChatRequest, AgentResponse, ConversationHistory,
    LearningPathRequest, LearningPath
)
from app.services.ai_agent import get_agent
from app.services.learning_path_generator import get_learning_path_generator

router = APIRouter()


@router.post("/chat", response_model=AgentResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Send a message to the AI agent and get a response.
    
    The agent provides personalized career guidance based on:
    - User's current skills and experience
    - Target role and career goals
    - Conversation history and context
    
    **Research Justification**: Addresses the finding that 76% of students
    feel current guidance is generic and not personalized.
    """
    try:
        agent = get_agent()
        response = await agent.chat(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.get("/conversation/{user_id}", response_model=Optional[ConversationHistory])
async def get_conversation_history(user_id: str):
    """
    Retrieve conversation history for a user.
    
    Returns the full conversation history including:
    - All messages exchanged
    - Conversation context (skills, goals, etc.)
    - Timestamps
    """
    try:
        agent = get_agent()
        history = await agent.get_conversation_history(user_id)
        
        if history is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No conversation history found for user {user_id}"
            )
        
        return history
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation history: {str(e)}"
        )


@router.delete("/conversation/{user_id}")
async def clear_conversation_history(user_id: str):
    """
    Clear conversation history for a user.
    
    This allows users to start fresh conversations or reset context.
    """
    try:
        agent = get_agent()
        success = await agent.clear_conversation(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No conversation history found for user {user_id}"
            )
        
        return {"message": f"Conversation history cleared for user {user_id}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing conversation history: {str(e)}"
        )


@router.post("/learning-path", response_model=LearningPath)
async def generate_learning_path(request: LearningPathRequest):
    """
    Generate a personalized learning path for a target role.
    
    The learning path includes:
    - Ordered list of skills to learn (based on dependencies)
    - Time estimates for each skill
    - Learning resources (courses, documentation, practice)
    - Prerequisites and difficulty levels
    
    **Research Justification**: Addresses multiple findings:
    - 52% don't know required skills (7.4x impact on success)
    - 76% feel guidance is generic
    - Need for structured, personalized learning roadmaps
    """
    try:
        generator = get_learning_path_generator()
        learning_path = await generator.generate_learning_path(request)
        return learning_path
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating learning path: {str(e)}"
        )


@router.get("/health")
async def agent_health_check():
    """Health check for AI agent service."""
    try:
        agent = get_agent()
        return {
            "status": "healthy",
            "service": "AI Agent",
            "features": [
                "Conversational AI",
                "Learning Path Generation",
                "Skill Gap Analysis",
                "Personalized Recommendations"
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI Agent service unavailable: {str(e)}"
        )
