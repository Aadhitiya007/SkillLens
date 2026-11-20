"""
Job Market Intelligence Service
Provides job recommendations and market trend analysis.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class JobMarketService:
    """
    Job market intelligence and recommendations.
    Integrates with job search APIs and provides matching algorithms.
    """
    
    def __init__(self):
        """Initialize job market service."""
        # Mock job database
        self.jobs_database = self._load_mock_jobs()
    
    def _load_mock_jobs(self) -> List[Dict]:
        """Load mock job postings."""
        return [
            {
                "job_id": "job001",
                "title": "Full Stack Developer",
                "company": "Tech Corp",
                "location": "Remote",
                "required_skills": ["JavaScript", "React", "Node.js", "MongoDB"],
                "preferred_skills": ["TypeScript", "Docker", "AWS"],
                "experience_years": 2,
                "salary_range": "$80k-$120k",
                "posted_date": "2024-12-20"
            },
            {
                "job_id": "job002",
                "title": "Backend Developer",
                "company": "StartupXYZ",
                "location": "San Francisco, CA",
                "required_skills": ["Python", "Django", "PostgreSQL", "REST APIs"],
                "preferred_skills": ["Redis", "Docker", "Kubernetes"],
                "experience_years": 3,
                "salary_range": "$100k-$140k",
                "posted_date": "2024-12-22"
            },
            {
                "job_id": "job003",
                "title": "Data Scientist",
                "company": "DataCo",
                "location": "New York, NY",
                "required_skills": ["Python", "Machine Learning", "Pandas", "SQL"],
                "preferred_skills": ["TensorFlow", "PyTorch", "AWS"],
                "experience_years": 2,
                "salary_range": "$90k-$130k",
                "posted_date": "2024-12-25"
            },
            {
                "job_id": "job004",
                "title": "Frontend Developer",
                "company": "WebAgency",
                "location": "Remote",
                "required_skills": ["React", "JavaScript", "HTML", "CSS"],
                "preferred_skills": ["TypeScript", "Next.js", "Tailwind"],
                "experience_years": 1,
                "salary_range": "$70k-$100k",
                "posted_date": "2024-12-28"
            },
            {
                "job_id": "job005",
                "title": "DevOps Engineer",
                "company": "CloudTech",
                "location": "Austin, TX",
                "required_skills": ["Docker", "Kubernetes", "AWS", "Linux"],
                "preferred_skills": ["Terraform", "Ansible", "Python"],
                "experience_years": 3,
                "salary_range": "$110k-$150k",
                "posted_date": "2024-12-30"
            }
        ]
    
    def calculate_match_score(self, user_skills: List[str], job: Dict) -> float:
        """Calculate match score between user skills and job requirements."""
        required_skills = set(job["required_skills"])
        preferred_skills = set(job.get("preferred_skills", []))
        user_skills_set = set(user_skills)
        
        # Required skills match (70% weight)
        required_match = len(user_skills_set & required_skills) / len(required_skills) if required_skills else 0
        
        # Preferred skills match (30% weight)
        preferred_match = len(user_skills_set & preferred_skills) / len(preferred_skills) if preferred_skills else 0
        
        # Combined score
        score = (required_match * 0.7 + preferred_match * 0.3) * 100
        
        return round(score, 1)
    
    async def get_job_recommendations(self, user_skills: List[str], 
                                     experience_years: float = 0,
                                     limit: int = 10) -> List[Dict]:
        """
        Get personalized job recommendations.
        
        Args:
            user_skills: User's current skills
            experience_years: Years of experience
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended jobs with match scores
        """
        try:
            recommendations = []
            
            for job in self.jobs_database:
                # Calculate match score
                match_score = self.calculate_match_score(user_skills, job)
                
                # Filter by experience (allow ±1 year flexibility)
                exp_match = abs(job["experience_years"] - experience_years) <= 1
                
                # Add to recommendations if decent match
                if match_score >= 30:  # At least 30% match
                    recommendations.append({
                        **job,
                        "match_score": match_score,
                        "experience_match": exp_match,
                        "missing_skills": list(set(job["required_skills"]) - set(user_skills))
                    })
            
            # Sort by match score
            recommendations.sort(key=lambda x: x["match_score"], reverse=True)
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error getting job recommendations: {e}")
            return []
    
    async def get_market_trends(self, skill: Optional[str] = None) -> Dict:
        """
        Get job market trends and insights.
        
        Args:
            skill: Optional skill to analyze
            
        Returns:
            Market trend data
        """
        try:
            # Mock trend data
            trends = {
                "total_jobs": len(self.jobs_database),
                "top_skills": [
                    {"skill": "Python", "demand": 95, "growth": "+12%"},
                    {"skill": "JavaScript", "demand": 90, "growth": "+8%"},
                    {"skill": "React", "demand": 88, "growth": "+15%"},
                    {"skill": "Docker", "demand": 85, "growth": "+20%"},
                    {"skill": "AWS", "demand": 82, "growth": "+18%"}
                ],
                "top_roles": [
                    {"role": "Full Stack Developer", "openings": 1250, "avg_salary": "$100k"},
                    {"role": "Backend Developer", "openings": 980, "avg_salary": "$110k"},
                    {"role": "DevOps Engineer", "openings": 750, "avg_salary": "$120k"},
                    {"role": "Data Scientist", "openings": 650, "avg_salary": "$115k"},
                    {"role": "Frontend Developer", "openings": 580, "avg_salary": "$90k"}
                ],
                "salary_trends": {
                    "average": "$105k",
                    "median": "$100k",
                    "range": "$70k-$150k"
                },
                "remote_percentage": 65,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting market trends: {e}")
            return {}


# Singleton instance
_job_market_service = None

def get_job_market_service() -> JobMarketService:
    """Get singleton instance of job market service."""
    global _job_market_service
    if _job_market_service is None:
        _job_market_service = JobMarketService()
    return _job_market_service
