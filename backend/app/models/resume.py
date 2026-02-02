"""
Pydantic models for resume data.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class Experience(BaseModel):
    """Work experience model."""
    title: str
    company: str
    duration: str
    description: Optional[str] = None
    skills_used: List[str] = []


class Project(BaseModel):
    """Project model."""
    name: str
    description: str
    technologies: List[str] = []
    duration: Optional[str] = None
    url: Optional[str] = None


class Education(BaseModel):
    """Education model."""
    degree: str
    institution: str
    year: Optional[str] = None
    gpa: Optional[float] = None


class ResumeData(BaseModel):
    """Parsed resume data."""
    raw_text: str
    skills: List[str] = []
    tools: List[str] = []
    experience: List[Experience] = []
    projects: List[Project] = []
    education: List[Education] = []
    certifications: List[str] = []
    embeddings: Optional[List[float]] = None


class ResumeUploadResponse(BaseModel):
    """Resume upload response."""
    resume_id: str
    user_id: str
    filename: str
    parsed_data: ResumeData
    uploaded_at: datetime


class ResumeInDB(BaseModel):
    """Resume model as stored in database."""
    id: str = Field(alias="_id")
    user_id: str
    filename: str
    file_path: str
    parsed_data: ResumeData
    uploaded_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
