"""
Institutional Analytics Service
Provides analytics for placement cells and departments.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class InstitutionalAnalytics:
    """
    Analytics service for educational institutions.
    Tracks student progress, placement statistics, and department performance.
    """
    
    def __init__(self):
        """Initialize analytics service."""
        pass
    
    async def get_placement_statistics(self, department: Optional[str] = None) -> Dict:
        """
        Get placement statistics for institution or department.
        
        Args:
            department: Optional department filter
            
        Returns:
            Placement statistics
        """
        try:
            # Mock data
            stats = {
                "total_students": 500,
                "placed_students": 380,
                "placement_rate": 76.0,
                "average_package": "$95k",
                "highest_package": "$180k",
                "companies_visited": 85,
                "offers_made": 450,
                "department_breakdown": [
                    {
                        "department": "Computer Science",
                        "students": 200,
                        "placed": 165,
                        "placement_rate": 82.5,
                        "avg_package": "$105k"
                    },
                    {
                        "department": "Information Technology",
                        "students": 150,
                        "placed": 118,
                        "placement_rate": 78.7,
                        "avg_package": "$98k"
                    },
                    {
                        "department": "Electronics",
                        "students": 100,
                        "placed": 68,
                        "placement_rate": 68.0,
                        "avg_package": "$85k"
                    },
                    {
                        "department": "Mechanical",
                        "students": 50,
                        "placed": 29,
                        "placement_rate": 58.0,
                        "avg_package": "$75k"
                    }
                ],
                "top_recruiters": [
                    {"company": "Google", "offers": 15},
                    {"company": "Microsoft", "offers": 12},
                    {"company": "Amazon", "offers": 18},
                    {"company": "Meta", "offers": 8},
                    {"company": "Apple", "offers": 6}
                ],
                "skill_demand": [
                    {"skill": "Python", "percentage": 85},
                    {"skill": "JavaScript", "percentage": 78},
                    {"skill": "React", "percentage": 72},
                    {"skill": "SQL", "percentage": 80},
                    {"skill": "AWS", "percentage": 65}
                ]
            }
            
            if department:
                # Filter by department
                dept_data = next(
                    (d for d in stats["department_breakdown"] if d["department"] == department),
                    None
                )
                if dept_data:
                    stats["total_students"] = dept_data["students"]
                    stats["placed_students"] = dept_data["placed"]
                    stats["placement_rate"] = dept_data["placement_rate"]
                    stats["average_package"] = dept_data["avg_package"]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting placement statistics: {e}")
            return {}
    
    async def get_student_readiness_distribution(self) -> Dict:
        """Get distribution of student readiness scores."""
        try:
            return {
                "distribution": [
                    {"range": "0-20", "count": 25, "percentage": 5},
                    {"range": "21-40", "count": 75, "percentage": 15},
                    {"range": "41-60", "count": 150, "percentage": 30},
                    {"range": "61-80", "count": 175, "percentage": 35},
                    {"range": "81-100", "count": 75, "percentage": 15}
                ],
                "average_score": 62.5,
                "median_score": 65.0,
                "total_students": 500
            }
        except Exception as e:
            logger.error(f"Error getting readiness distribution: {e}")
            return {}
    
    async def get_skill_gap_analysis(self) -> Dict:
        """Get institution-wide skill gap analysis."""
        try:
            return {
                "most_common_gaps": [
                    {"skill": "Docker", "students_missing": 320, "percentage": 64},
                    {"skill": "Kubernetes", "students_missing": 380, "percentage": 76},
                    {"skill": "AWS", "students_missing": 280, "percentage": 56},
                    {"skill": "TypeScript", "students_missing": 250, "percentage": 50},
                    {"skill": "MongoDB", "students_missing": 200, "percentage": 40}
                ],
                "most_common_skills": [
                    {"skill": "Python", "students_have": 425, "percentage": 85},
                    {"skill": "Java", "students_have": 400, "percentage": 80},
                    {"skill": "SQL", "students_have": 380, "percentage": 76},
                    {"skill": "HTML/CSS", "students_have": 450, "percentage": 90},
                    {"skill": "Git", "students_have": 375, "percentage": 75}
                ],
                "recommendations": [
                    "Organize Docker workshops",
                    "Add cloud computing to curriculum",
                    "Partner with AWS for training",
                    "Increase focus on modern frameworks"
                ]
            }
        except Exception as e:
            logger.error(f"Error getting skill gap analysis: {e}")
            return {}
    
    async def get_timeline_analytics(self, days: int = 30) -> Dict:
        """Get time-series analytics for the past N days."""
        try:
            # Generate mock timeline data
            timeline = []
            base_date = datetime.utcnow() - timedelta(days=days)
            
            for i in range(days):
                date = base_date + timedelta(days=i)
                timeline.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "active_users": random.randint(50, 150),
                    "resumes_uploaded": random.randint(5, 25),
                    "assessments_taken": random.randint(10, 40),
                    "ai_interactions": random.randint(30, 100)
                })
            
            return {
                "timeline": timeline,
                "period_days": days,
                "totals": {
                    "active_users": sum(d["active_users"] for d in timeline),
                    "resumes_uploaded": sum(d["resumes_uploaded"] for d in timeline),
                    "assessments_taken": sum(d["assessments_taken"] for d in timeline),
                    "ai_interactions": sum(d["ai_interactions"] for d in timeline)
                }
            }
        except Exception as e:
            logger.error(f"Error getting timeline analytics: {e}")
            return {}


# Singleton instance
_analytics_service = None

def get_analytics_service() -> InstitutionalAnalytics:
    """Get singleton instance of analytics service."""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = InstitutionalAnalytics()
    return _analytics_service
