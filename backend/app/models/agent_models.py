"""
Pydantic models for AI Agent module.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Individual chat message."""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Request to send message to AI agent."""
    user_id: str
    message: str
    context: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "message": "I want to become a full-stack developer. What skills do I need?",
                "context": {
                    "resume_id": "resume456",
                    "target_role": "Full Stack Developer"
                }
            }
        }


class AgentResponse(BaseModel):
    """Response from AI agent."""
    message: str
    conversation_id: str
    suggestions: Optional[List[str]] = None
    learning_path_available: bool = False
    metadata: Optional[Dict[str, Any]] = None


class ConversationContext(BaseModel):
    """Context for conversation."""
    user_id: str
    resume_id: Optional[str] = None
    target_role: Optional[str] = None
    skill_gaps: List[str] = []
    current_skills: List[str] = []
    experience_level: Optional[str] = None


class ConversationHistory(BaseModel):
    """Full conversation history."""
    user_id: str
    conversation_id: str
    messages: List[ChatMessage]
    context: ConversationContext
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LearningStep(BaseModel):
    """Individual step in learning path."""
    step_number: int
    skill: str
    description: str
    estimated_time: str  # e.g., "2 weeks", "1 month"
    resources: List[Dict[str, str]]  # [{"type": "course", "title": "...", "url": "..."}]
    prerequisites: List[str] = []
    difficulty: str  # "Beginner", "Intermediate", "Advanced"


class LearningPath(BaseModel):
    """Generated learning path."""
    user_id: str
    target_role: str
    steps: List[LearningStep]
    total_estimated_time: str
    skill_dependencies: Dict[str, List[str]] = {}
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "target_role": "Full Stack Developer",
                "steps": [
                    {
                        "step_number": 1,
                        "skill": "HTML/CSS",
                        "description": "Learn fundamental web technologies",
                        "estimated_time": "2 weeks",
                        "resources": [
                            {"type": "course", "title": "HTML & CSS Basics", "url": "https://example.com"}
                        ],
                        "prerequisites": [],
                        "difficulty": "Beginner"
                    }
                ],
                "total_estimated_time": "6 months",
                "skill_dependencies": {
                    "React": ["JavaScript", "HTML/CSS"]
                }
            }
        }


class LearningPathRequest(BaseModel):
    """Request to generate learning path."""
    user_id: str
    resume_id: Optional[str] = None
    target_role: str
    current_skills: List[str] = []
    experience_level: str = "Beginner"  # Beginner, Intermediate, Advanced
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "resume_id": "resume456",
                "target_role": "Full Stack Developer",
                "current_skills": ["Python", "HTML"],
                "experience_level": "Beginner"
            }
        }
