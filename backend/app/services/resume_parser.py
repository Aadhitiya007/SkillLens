"""
Resume parsing service using NLP and Sentence-BERT.
Extracts skills, experience, projects, and generates embeddings.
"""

import re
import logging
from typing import List, Dict, Optional
from pathlib import Path

import PyPDF2
import docx
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.models.resume import ResumeData, Experience, Project, Education

logger = logging.getLogger(__name__)


class ResumeParser:
    """Resume parsing service with semantic skill extraction."""
    
    def __init__(self):
        """Initialize the resume parser with Sentence-BERT model."""
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load Sentence-BERT model for embeddings."""
        try:
            logger.info(f"Loading model: {settings.sentence_bert_model}")
            self.model = SentenceTransformer(settings.sentence_bert_model)
            logger.info("Sentence-BERT model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Sentence-BERT model: {e}")
            raise
    
    def extract_text_from_pdf(self, file_path: str) -> str:
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
            raise
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            raise
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from resume file (PDF or DOCX)."""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from resume text.
        Uses pattern matching and common skill keywords.
        """
        # Common technical skills (this is a basic implementation)
        # In production, this should use a more sophisticated NLP approach
        skill_keywords = [
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
            'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab',
            # Web Technologies
            'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express',
            'django', 'flask', 'fastapi', 'spring', 'asp.net',
            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra',
            'oracle', 'sqlite', 'neo4j', 'dynamodb',
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
            'ci/cd', 'terraform', 'ansible',
            # Data Science & ML
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
            'data analysis', 'statistics',
            # Other
            'api', 'rest', 'graphql', 'microservices', 'agile', 'scrum',
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skill_keywords:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        # Remove duplicates and sort
        return sorted(list(set(found_skills)))
    
    def extract_tools(self, text: str) -> List[str]:
        """Extract tools and technologies from resume text."""
        # Common tools (basic implementation)
        tool_keywords = [
            'git', 'github', 'gitlab', 'jira', 'confluence', 'slack',
            'vscode', 'intellij', 'eclipse', 'jupyter', 'tableau',
            'power bi', 'excel', 'postman', 'figma', 'photoshop',
        ]
        
        text_lower = text.lower()
        found_tools = []
        
        for tool in tool_keywords:
            if tool in text_lower:
                found_tools.append(tool.title())
        
        return sorted(list(set(found_tools)))
    
    def extract_experience(self, text: str) -> List[Experience]:
        """
        Extract work experience from resume text.
        This is a simplified implementation using pattern matching.
        """
        experiences = []
        
        # Look for common experience section headers
        experience_pattern = r'(?:experience|work history|employment)(.*?)(?:education|projects|skills|$)'
        match = re.search(experience_pattern, text.lower(), re.DOTALL)
        
        if match:
            experience_text = match.group(1)
            # This is a basic implementation
            # In production, use more sophisticated NLP parsing
            lines = experience_text.split('\n')
            
            current_exp = {}
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Simple heuristic: if line has dates, it might be a job title
                if re.search(r'\d{4}', line):
                    if current_exp:
                        experiences.append(Experience(**current_exp))
                    current_exp = {
                        'title': line,
                        'company': 'Not specified',
                        'duration': line,
                        'skills_used': []
                    }
        
        return experiences
    
    def extract_projects(self, text: str) -> List[Project]:
        """Extract projects from resume text."""
        projects = []
        
        # Look for projects section
        project_pattern = r'(?:projects|personal projects)(.*?)(?:experience|education|skills|$)'
        match = re.search(project_pattern, text.lower(), re.DOTALL)
        
        if match:
            project_text = match.group(1)
            # Basic implementation
            lines = [line.strip() for line in project_text.split('\n') if line.strip()]
            
            for i in range(0, len(lines), 2):
                if i < len(lines):
                    projects.append(Project(
                        name=lines[i],
                        description=lines[i+1] if i+1 < len(lines) else "",
                        technologies=[]
                    ))
        
        return projects
    
    def extract_education(self, text: str) -> List[Education]:
        """Extract education information from resume text."""
        education = []
        
        # Look for education section
        edu_pattern = r'(?:education|academic)(.*?)(?:experience|projects|skills|$)'
        match = re.search(edu_pattern, text.lower(), re.DOTALL)
        
        if match:
            edu_text = match.group(1)
            lines = [line.strip() for line in edu_text.split('\n') if line.strip()]
            
            for line in lines:
                if any(degree in line.lower() for degree in ['bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'b.e', 'm.e']):
                    education.append(Education(
                        degree=line,
                        institution="Not specified"
                    ))
        
        return education
    
    def generate_embeddings(self, text: str) -> List[float]:
        """Generate semantic embeddings for resume text using Sentence-BERT."""
        try:
            if self.model is None:
                self._load_model()
            
            # Generate embeddings
            embeddings = self.model.encode(text, convert_to_numpy=True)
            return embeddings.tolist()
        
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
    
    async def parse_resume(self, file_path: str) -> ResumeData:
        """
        Parse resume file and extract all information.
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            ResumeData object with parsed information
        """
        try:
            # Extract text
            raw_text = self.extract_text(file_path)
            
            # Extract components
            skills = self.extract_skills(raw_text)
            tools = self.extract_tools(raw_text)
            experience = self.extract_experience(raw_text)
            projects = self.extract_projects(raw_text)
            education = self.extract_education(raw_text)
            
            # Generate embeddings
            embeddings = self.generate_embeddings(raw_text)
            
            resume_data = ResumeData(
                raw_text=raw_text,
                skills=skills,
                tools=tools,
                experience=experience,
                projects=projects,
                education=education,
                certifications=[],  # TODO: Extract certifications
                embeddings=embeddings
            )
            
            logger.info(f"Successfully parsed resume: {len(skills)} skills, {len(experience)} experiences")
            return resume_data
        
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            raise


# Global instance
resume_parser = ResumeParser()
