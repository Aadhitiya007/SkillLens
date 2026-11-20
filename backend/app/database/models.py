"""
SQLAlchemy ORM models for PostgreSQL database.
Defines all database tables using SQLAlchemy 2.0 declarative syntax.
"""

from sqlalchemy import (
    String, Integer, Boolean, Numeric, Text, DateTime, Date,
    ForeignKey, Index, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, List
import uuid


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="student")
    department: Mapped[Optional[str]] = mapped_column(String(100))
    register_number: Mapped[Optional[str]] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    resumes: Mapped[List["Resume"]] = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    readiness_scores: Mapped[List["ReadinessScore"]] = relationship("ReadinessScore", back_populates="user", cascade="all, delete-orphan")
    assessments: Mapped[List["Assessment"]] = relationship("Assessment", back_populates="user", cascade="all, delete-orphan")
    assessment_results: Mapped[List["AssessmentResult"]] = relationship("AssessmentResult", back_populates="user", cascade="all, delete-orphan")
    learning_plans: Mapped[List["LearningPlan"]] = relationship("LearningPlan", back_populates="user", cascade="all, delete-orphan")
    learning_progress: Mapped[List["LearningProgress"]] = relationship("LearningProgress", back_populates="user", cascade="all, delete-orphan")
    predictions: Mapped[List["Prediction"]] = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class Resume(Base):
    """Resume file and parsed data model."""
    __tablename__ = "resumes"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    parsed_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="resumes")
    readiness_scores: Mapped[List["ReadinessScore"]] = relationship("ReadinessScore", back_populates="resume")
    predictions: Mapped[List["Prediction"]] = relationship("Prediction", back_populates="resume")
    
    __table_args__ = (
        Index("idx_resumes_user_id", "user_id"),
        Index("idx_resumes_uploaded_at", "uploaded_at"),
    )


class ReadinessScore(Base):
    """Career readiness score model."""
    __tablename__ = "readiness_scores"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="SET NULL"))
    target_role: Mapped[str] = mapped_column(String(255), nullable=False)
    overall_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    technical_skills_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    experience_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    project_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    tool_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    explanation: Mapped[Optional[str]] = mapped_column(Text)
    strengths: Mapped[Optional[dict]] = mapped_column(JSONB)
    weaknesses: Mapped[Optional[dict]] = mapped_column(JSONB)
    recommendations: Mapped[Optional[dict]] = mapped_column(JSONB)
    factors: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="readiness_scores")
    resume: Mapped[Optional["Resume"]] = relationship("Resume", back_populates="readiness_scores")
    
    __table_args__ = (
        Index("idx_readiness_scores_user_id", "user_id"),
        Index("idx_readiness_scores_created_at", "created_at"),
    )


class Assessment(Base):
    """Skill assessment model."""
    __tablename__ = "assessments"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill: Mapped[str] = mapped_column(String(100), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False)
    questions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    total_points: Mapped[int] = mapped_column(Integer, nullable=False)
    time_limit_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="assessments")
    results: Mapped[List["AssessmentResult"]] = relationship("AssessmentResult", back_populates="assessment", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_assessments_user_id", "user_id"),
        Index("idx_assessments_skill", "skill"),
    )


class AssessmentResult(Base):
    """Assessment result model."""
    __tablename__ = "assessment_results"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    answers: Mapped[dict] = mapped_column(JSONB, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, nullable=False)
    percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    confidence_level: Mapped[str] = mapped_column(String(50), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    feedback: Mapped[Optional[dict]] = mapped_column(JSONB)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="results")
    user: Mapped["User"] = relationship("User", back_populates="assessment_results")
    
    __table_args__ = (
        Index("idx_assessment_results_user_id", "user_id"),
        Index("idx_assessment_results_assessment_id", "assessment_id"),
    )


class LearningPlan(Base):
    """Learning plan model."""
    __tablename__ = "learning_plans"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_role: Mapped[str] = mapped_column(String(255), nullable=False)
    current_skills: Mapped[dict] = mapped_column(JSONB, nullable=False)
    target_skills: Mapped[dict] = mapped_column(JSONB, nullable=False)
    learning_path: Mapped[dict] = mapped_column(JSONB, nullable=False)
    estimated_weeks: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="learning_plans")
    progress: Mapped[List["LearningProgress"]] = relationship("LearningProgress", back_populates="learning_plan", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_learning_plans_user_id", "user_id"),
        Index("idx_learning_plans_status", "status"),
    )


class LearningProgress(Base):
    """Learning progress tracking model."""
    __tablename__ = "learning_progress"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    learning_plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("learning_plans.id", ondelete="CASCADE"))
    skill: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="learning_progress")
    learning_plan: Mapped[Optional["LearningPlan"]] = relationship("LearningPlan", back_populates="progress")
    
    __table_args__ = (
        Index("idx_learning_progress_user_id", "user_id"),
        Index("idx_learning_progress_plan_id", "learning_plan_id"),
    )


class JobListing(Base):
    """Job listing model (cached from external APIs)."""
    __tablename__ = "job_listings"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    required_skills: Mapped[Optional[dict]] = mapped_column(JSONB)
    salary_range: Mapped[Optional[str]] = mapped_column(String(100))
    job_type: Mapped[Optional[str]] = mapped_column(String(50))
    experience_level: Mapped[Optional[str]] = mapped_column(String(50))
    source: Mapped[Optional[str]] = mapped_column(String(100))
    external_url: Mapped[Optional[str]] = mapped_column(Text)
    posted_date: Mapped[Optional[datetime]] = mapped_column(Date)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index("idx_job_listings_posted_date", "posted_date"),
        Index("idx_job_listings_location", "location"),
    )


class Prediction(Base):
    """Shortlisting probability prediction model."""
    __tablename__ = "predictions"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="SET NULL"))
    job_description: Mapped[str] = mapped_column(Text, nullable=False)
    shortlist_probability: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    confidence: Mapped[str] = mapped_column(String(50), nullable=False)
    factors: Mapped[dict] = mapped_column(JSONB, nullable=False)
    recommendations: Mapped[Optional[dict]] = mapped_column(JSONB)
    predicted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="predictions")
    resume: Mapped[Optional["Resume"]] = relationship("Resume", back_populates="predictions")
    
    __table_args__ = (
        Index("idx_predictions_user_id", "user_id"),
        Index("idx_predictions_predicted_at", "predicted_at"),
    )


class Conversation(Base):
    """AI agent conversation history model."""
    __tablename__ = "conversations"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    conversation_metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversations")
    
    __table_args__ = (
        Index("idx_conversations_user_id", "user_id"),
        Index("idx_conversations_session_id", "session_id"),
    )


class Skill(Base):
    """Skill catalog model (optional if not using Neo4j)."""
    __tablename__ = "skills"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    difficulty_level: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    prerequisites: Mapped[List["SkillPrerequisite"]] = relationship(
        "SkillPrerequisite",
        foreign_keys="SkillPrerequisite.skill_id",
        back_populates="skill",
        cascade="all, delete-orphan"
    )
    required_by: Mapped[List["SkillPrerequisite"]] = relationship(
        "SkillPrerequisite",
        foreign_keys="SkillPrerequisite.prerequisite_id",
        back_populates="prerequisite",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index("idx_skills_category", "category"),
        Index("idx_skills_name", "name"),
    )


class SkillPrerequisite(Base):
    """Skill prerequisite relationship model (optional if not using Neo4j)."""
    __tablename__ = "skill_prerequisites"
    
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    prerequisite_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    importance: Mapped[str] = mapped_column(String(50), default="recommended")
    
    # Relationships
    skill: Mapped["Skill"] = relationship("Skill", foreign_keys=[skill_id], back_populates="prerequisites")
    prerequisite: Mapped["Skill"] = relationship("Skill", foreign_keys=[prerequisite_id], back_populates="required_by")
