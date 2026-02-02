"""
Resume API router.
Handles resume upload, parsing, and retrieval.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
import os
import uuid
from datetime import datetime
import logging

from app.models.resume import ResumeUploadResponse, ResumeData
from app.database import get_db, Resume as ResumeModel
from app.services.resume_parser import resume_parser
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = "demo_user",  # TODO: Get from auth token
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and parse a resume file.
    
    - **file**: Resume file (PDF or DOCX)
    - **user_id**: User ID (from authentication)
    """
    # Validate file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(settings.allowed_extensions)}"
        )
    
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.max_upload_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.max_upload_size / 1024 / 1024}MB"
        )
    
    try:
        # Save file
        resume_id = uuid.uuid4()
        file_path = os.path.join(settings.upload_dir, f"{resume_id}{file_extension}")
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Saved resume file: {file_path}")
        
        # Parse resume
        parsed_data = await resume_parser.parse_resume(file_path)
        
        # Convert user_id to UUID (for demo, create a fixed UUID)
        # In production, this would come from the authenticated user
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            # For demo user, create a deterministic UUID
            user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, user_id)
        
        # Store in database
        resume = ResumeModel(
            id=resume_id,
            user_id=user_uuid,
            filename=file.filename,
            file_path=file_path,
            parsed_data=parsed_data.model_dump()
        )
        
        db.add(resume)
        await db.commit()
        await db.refresh(resume)
        
        logger.info(f"Resume stored in database: {resume_id}")
        
        return ResumeUploadResponse(
            resume_id=str(resume.id),
            user_id=str(resume.user_id),
            filename=resume.filename,
            parsed_data=parsed_data,
            uploaded_at=resume.uploaded_at
        )
    
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        # Clean up file if it was saved
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process resume: {str(e)}"
        )


@router.get("/{user_id}")
async def get_user_resume(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the most recent resume for a user.
    
    - **user_id**: User ID
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, user_id)
    
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
            detail="No resume found for this user"
        )
    
    return {
        "resume_id": str(resume.id),
        "user_id": str(resume.user_id),
        "filename": resume.filename,
        "file_path": resume.file_path,
        "parsed_data": resume.parsed_data,
        "uploaded_at": resume.uploaded_at,
        "updated_at": resume.updated_at
    }


@router.get("/")
async def list_resumes(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    List all resumes (admin endpoint).
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    # Get total count
    count_result = await db.execute(select(func.count(ResumeModel.id)))
    total = count_result.scalar()
    
    # Get resumes
    result = await db.execute(
        select(ResumeModel)
        .order_by(desc(ResumeModel.uploaded_at))
        .offset(skip)
        .limit(limit)
    )
    resumes = result.scalars().all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "resumes": [
            {
                "resume_id": str(r.id),
                "user_id": str(r.user_id),
                "filename": r.filename,
                "uploaded_at": r.uploaded_at
            }
            for r in resumes
        ]
    }


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a resume.
    
    - **resume_id**: Resume ID
    """
    try:
        resume_uuid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume ID"
        )
    
    # Get resume
    result = await db.execute(
        select(ResumeModel).where(ResumeModel.id == resume_uuid)
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Delete file
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    
    # Delete from database
    await db.delete(resume)
    await db.commit()
    
    return {"message": "Resume deleted successfully"}
