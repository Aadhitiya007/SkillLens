"""
File Upload Service
Handles resume file uploads with validation and storage.
"""

import logging
import os
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import UploadFile
import PyPDF2
from docx import Document

from app.database import MongoDB

logger = logging.getLogger(__name__)


class FileUploadService:
    """Service for handling file uploads."""
    
    def __init__(self):
        """Initialize file upload service."""
        self.upload_dir = Path("uploads/resumes")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.db = MongoDB.get_database()
        
        # Allowed file types
        self.allowed_extensions = {".pdf", ".docx", ".doc", ".txt"}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    def _validate_file(self, file: UploadFile) -> tuple[bool, str]:
        """
        Validate uploaded file.
        
        Returns:
            (is_valid, error_message)
        """
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.allowed_extensions:
            return False, f"File type {file_ext} not allowed. Allowed: {', '.join(self.allowed_extensions)}"
        
        # File size will be checked during read
        return True, ""
    
    def _extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise Exception("Failed to extract text from PDF")
    
    def _extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            raise Exception("Failed to extract text from DOCX")
    
    def _extract_text_from_txt(self, file_path: Path) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Error reading TXT file: {e}")
            raise Exception("Failed to read TXT file")
    
    async def upload_resume(self, file: UploadFile, user_id: str) -> dict:
        """
        Upload and process resume file.
        
        Args:
            file: Uploaded file
            user_id: User ID
            
        Returns:
            Resume metadata and extracted text
        """
        try:
            # Validate file
            is_valid, error_msg = self._validate_file(file)
            if not is_valid:
                raise ValueError(error_msg)
            
            # Generate unique filename
            file_ext = Path(file.filename).suffix.lower()
            resume_id = f"resume_{uuid.uuid4().hex}"
            filename = f"{resume_id}{file_ext}"
            file_path = self.upload_dir / filename
            
            # Read and save file
            content = await file.read()
            
            # Check file size
            if len(content) > self.max_file_size:
                raise ValueError(f"File size exceeds {self.max_file_size / 1024 / 1024}MB limit")
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Extract text based on file type
            if file_ext == '.pdf':
                text = self._extract_text_from_pdf(file_path)
            elif file_ext in ['.docx', '.doc']:
                text = self._extract_text_from_docx(file_path)
            elif file_ext == '.txt':
                text = self._extract_text_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            # Store metadata in database
            resume_doc = {
                "resume_id": resume_id,
                "user_id": user_id,
                "filename": file.filename,
                "file_path": str(file_path),
                "file_size": len(content),
                "file_type": file_ext,
                "text_content": text,
                "uploaded_at": datetime.utcnow(),
                "processed": False
            }
            
            await self.db.resumes.insert_one(resume_doc)
            
            return {
                "resume_id": resume_id,
                "filename": file.filename,
                "file_size": len(content),
                "text_length": len(text),
                "uploaded_at": resume_doc["uploaded_at"],
                "text_preview": text[:500] + "..." if len(text) > 500 else text
            }
            
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error uploading resume: {e}")
            raise Exception("Failed to upload resume")
    
    async def get_resume(self, resume_id: str, user_id: str) -> Optional[dict]:
        """Get resume by ID."""
        try:
            resume = await self.db.resumes.find_one({
                "resume_id": resume_id,
                "user_id": user_id
            })
            return resume
        except Exception as e:
            logger.error(f"Error getting resume: {e}")
            return None
    
    async def list_user_resumes(self, user_id: str) -> list:
        """List all resumes for a user."""
        try:
            cursor = self.db.resumes.find({"user_id": user_id})
            resumes = await cursor.to_list(length=100)
            return resumes
        except Exception as e:
            logger.error(f"Error listing resumes: {e}")
            return []
    
    async def delete_resume(self, resume_id: str, user_id: str) -> bool:
        """Delete resume."""
        try:
            # Get resume
            resume = await self.get_resume(resume_id, user_id)
            if not resume:
                return False
            
            # Delete file
            file_path = Path(resume["file_path"])
            if file_path.exists():
                file_path.unlink()
            
            # Delete from database
            result = await self.db.resumes.delete_one({
                "resume_id": resume_id,
                "user_id": user_id
            })
            
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting resume: {e}")
            return False


# Singleton instance
_upload_service = None

def get_upload_service() -> FileUploadService:
    """Get singleton instance of upload service."""
    global _upload_service
    if _upload_service is None:
        _upload_service = FileUploadService()
    return _upload_service
