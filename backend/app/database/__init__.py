"""Database package initialization."""

from app.database.postgresql import PostgreSQL, get_db, create_session
# Neo4j is optional - uncomment if you want to use it
# from app.database.neo4j_client import Neo4jClient, get_neo4j
from app.database.models import (
    Base,
    User,
    Resume,
    ReadinessScore,
    Assessment,
    AssessmentResult,
    LearningPlan,
    LearningProgress,
    JobListing,
    Prediction,
    Conversation,
    Skill,
    SkillPrerequisite,
)

__all__ = [
    # PostgreSQL
    "PostgreSQL",
    "get_db",
    "create_session",
    # Neo4j (optional)
    # "Neo4jClient",
    # "get_neo4j",
    # ORM Models
    "Base",
    "User",
    "Resume",
    "ReadinessScore",
    "Assessment",
    "AssessmentResult",
    "LearningPlan",
    "LearningProgress",
    "JobListing",
    "Prediction",
    "Conversation",
    "Skill",
    "SkillPrerequisite",
]
