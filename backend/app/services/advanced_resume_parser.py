"""
Advanced Resume Parser with Sentence-BERT and NER
Implements semantic understanding and entity extraction
"""

import os
os.environ['TF_USE_LEGACY_KERAS'] = '1'

from typing import List, Dict, Optional
import re
from datetime import datetime
import PyPDF2
import docx
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import numpy as np

class AdvancedResumeParser:
    """
    Advanced resume parser using:
    - Sentence-BERT for semantic embeddings
    - BERT-NER for entity extraction
    - Pattern matching for structured data
    """
    
    def __init__(self):
        print("Loading AI models...")
        # Load Sentence-BERT for embeddings
        self.sentence_bert = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Load NER model for entity extraction
        try:
            self.ner_pipeline = pipeline(
                "ner",
                model="dslim/bert-base-NER",
                aggregation_strategy="simple"
            )
        except:
            print("Warning: NER model not available, using fallback")
            self.ner_pipeline = None
        
        print("Models loaded successfully!")
        
        # Skill patterns (expanded list)
        self.common_skills = [
            # Programming Languages
            "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
            "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB",
            
            # Web Technologies
            "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Express",
            "Django", "Flask", "FastAPI", "Spring Boot", "ASP.NET",
            
            # Databases
            "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Cassandra",
            "DynamoDB", "Neo4j", "Elasticsearch",
            
            # Cloud & DevOps
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "GitLab CI",
            "Terraform", "Ansible", "Linux", "Nginx",
            
            # Data Science & ML
            "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-learn",
            "Pandas", "NumPy", "Matplotlib", "Jupyter", "Apache Spark", "Hadoop",
            "NLP", "Computer Vision", "Data Analysis", "Statistics",
            
            # Big Data
            "Kafka", "Airflow", "ETL", "Data Modeling", "Data Warehousing",
            "Apache Spark", "Hive", "Presto",
            
            # Tools
            "Git", "GitHub", "Jira", "Confluence", "Postman", "VS Code",
            "IntelliJ", "Figma", "Adobe XD"
        ]
    
    async def parse_resume(self, file_path: str, file_type: str) -> Dict:
        """
        Main parsing function
        
        Args:
            file_path: Path to resume file
            file_type: 'pdf' or 'docx'
            
        Returns:
            Parsed resume data with embeddings and entities
        """
        # Extract text
        text = self._extract_text(file_path, file_type)
        
        if not text:
            raise ValueError("Could not extract text from resume")
        
        # Generate semantic embeddings
        embeddings = self._generate_embeddings(text)
        
        # Extract entities using NER
        entities = self._extract_entities(text)
        
        # Extract structured data
        skills = self._extract_skills(text)
        experience = self._extract_experience(text)
        education = self._extract_education(text)
        projects = self._extract_projects(text)
        
        # Calculate resume quality score
        quality_score = self._calculate_quality_score({
            'text': text,
            'skills': skills,
            'experience': experience,
            'education': education,
            'projects': projects
        })
        
        return {
            'text': text,
            'embeddings': embeddings.tolist(),
            'embedding_dimension': len(embeddings),
            'entities': entities,
            'skills': skills,
            'experience': experience,
            'education': education,
            'projects': projects,
            'quality_score': quality_score,
            'parsed_at': datetime.utcnow().isoformat()
        }
    
    def _extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text from PDF or DOCX"""
        try:
            if file_type.lower() == 'pdf':
                return self._extract_from_pdf(file_path)
            elif file_type.lower() in ['docx', 'doc']:
                return self._extract_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"PDF extraction error: {e}")
        return text.strip()
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        text = ""
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"DOCX extraction error: {e}")
        return text.strip()
    
    def _generate_embeddings(self, text: str) -> np.ndarray:
        """Generate 384-dimensional semantic embeddings using Sentence-BERT"""
        # Truncate if too long (BERT has max length)
        max_length = 512
        words = text.split()
        if len(words) > max_length:
            text = ' '.join(words[:max_length])
        
        embeddings = self.sentence_bert.encode(text)
        return embeddings
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities using BERT-NER"""
        entities = {
            'organizations': [],
            'persons': [],
            'locations': [],
            'misc': []
        }
        
        if not self.ner_pipeline:
            return entities
        
        try:
            # Run NER
            ner_results = self.ner_pipeline(text[:512])  # Limit length
            
            for entity in ner_results:
                entity_type = entity['entity_group']
                entity_text = entity['word']
                
                if entity_type == 'ORG':
                    entities['organizations'].append(entity_text)
                elif entity_type == 'PER':
                    entities['persons'].append(entity_text)
                elif entity_type == 'LOC':
                    entities['locations'].append(entity_text)
                else:
                    entities['misc'].append(entity_text)
        except Exception as e:
            print(f"NER extraction error: {e}")
        
        return entities
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills using pattern matching and common skill list"""
        found_skills = []
        text_lower = text.lower()
        
        for skill in self.common_skills:
            # Case-insensitive search with word boundaries
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        
        return list(set(found_skills))  # Remove duplicates
    
    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience"""
        experience = []
        
        # Pattern for years (e.g., "2020-2023", "2020 - Present")
        year_pattern = r'(\d{4})\s*[-–]\s*(\d{4}|Present|Current)'
        
        # Split by common section headers
        sections = re.split(r'\n(?:EXPERIENCE|WORK EXPERIENCE|EMPLOYMENT)\n', text, flags=re.IGNORECASE)
        
        if len(sections) > 1:
            exp_section = sections[1]
            
            # Find all year ranges
            matches = re.finditer(year_pattern, exp_section)
            for match in matches:
                start_year = match.group(1)
                end_year = match.group(2)
                
                # Get surrounding context (company, role)
                context_start = max(0, match.start() - 100)
                context_end = min(len(exp_section), match.end() + 200)
                context = exp_section[context_start:context_end]
                
                experience.append({
                    'period': f"{start_year} - {end_year}",
                    'context': context.strip()
                })
        
        return experience
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education details"""
        education = []
        
        # Common degree patterns
        degree_patterns = [
            r'B\.?Tech', r'B\.?E\.?', r'Bachelor',
            r'M\.?Tech', r'M\.?E\.?', r'Master',
            r'Ph\.?D', r'Doctorate'
        ]
        
        for pattern in degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get surrounding context
                context_start = max(0, match.start() - 50)
                context_end = min(len(text), match.end() + 150)
                context = text[context_start:context_end]
                
                education.append({
                    'degree': match.group(),
                    'context': context.strip()
                })
        
        return education
    
    def _extract_projects(self, text: str) -> List[Dict]:
        """Extract project details"""
        projects = []
        
        # Split by common section headers
        sections = re.split(r'\n(?:PROJECTS|PROJECT WORK)\n', text, flags=re.IGNORECASE)
        
        if len(sections) > 1:
            project_section = sections[1]
            
            # Split by bullet points or numbers
            project_items = re.split(r'\n\s*[•\-\*\d+\.]\s*', project_section)
            
            for item in project_items[:5]:  # Limit to 5 projects
                if len(item.strip()) > 20:  # Ignore very short items
                    projects.append({
                        'description': item.strip()[:300]  # Limit length
                    })
        
        return projects
    
    def _calculate_quality_score(self, resume_data: Dict) -> float:
        """
        Calculate resume quality score (0-100)
        Based on multiple factors
        """
        score = 0.0
        
        # Text length (max 20 points)
        text_length = len(resume_data['text'])
        if text_length > 2000:
            score += 20
        elif text_length > 1000:
            score += 15
        elif text_length > 500:
            score += 10
        else:
            score += 5
        
        # Skills (max 30 points)
        num_skills = len(resume_data['skills'])
        score += min(num_skills * 3, 30)
        
        # Experience (max 25 points)
        num_experience = len(resume_data['experience'])
        score += min(num_experience * 12.5, 25)
        
        # Education (max 15 points)
        num_education = len(resume_data['education'])
        score += min(num_education * 7.5, 15)
        
        # Projects (max 10 points)
        num_projects = len(resume_data['projects'])
        score += min(num_projects * 5, 10)
        
        return min(score, 100.0)

# Singleton instance
_parser_instance = None

def get_parser() -> AdvancedResumeParser:
    """Get or create parser instance"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = AdvancedResumeParser()
    return _parser_instance
