"""
Learning Path Generator Service
Generates personalized learning paths based on skill gaps and target roles.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

from app.models.agent_models import LearningPath, LearningStep, LearningPathRequest
from app.services.skill_knowledge_graph import SkillKnowledgeGraph

logger = logging.getLogger(__name__)


class LearningPathGenerator:
    """
    Generates personalized learning paths for students.
    Uses skill knowledge graph to determine dependencies and optimal learning order.
    """
    
    def __init__(self):
        """Initialize the learning path generator."""
        self.skill_graph = SkillKnowledgeGraph()
        
        # Resource recommendations by skill category
        self.resource_database = {
            "Python": [
                {"type": "course", "title": "Python for Everybody", "url": "https://www.coursera.org/specializations/python"},
                {"type": "documentation", "title": "Official Python Tutorial", "url": "https://docs.python.org/3/tutorial/"},
                {"type": "practice", "title": "LeetCode Python", "url": "https://leetcode.com/problemset/all/?difficulty=EASY&page=1&topicSlugs=python"}
            ],
            "JavaScript": [
                {"type": "course", "title": "JavaScript Basics", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/"},
                {"type": "documentation", "title": "MDN Web Docs", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript"},
                {"type": "practice", "title": "JavaScript30", "url": "https://javascript30.com/"}
            ],
            "React": [
                {"type": "course", "title": "React Official Tutorial", "url": "https://react.dev/learn"},
                {"type": "course", "title": "Full Stack Open", "url": "https://fullstackopen.com/en/"},
                {"type": "practice", "title": "React Projects", "url": "https://github.com/topics/react-projects"}
            ],
            "Node.js": [
                {"type": "course", "title": "Node.js Tutorial", "url": "https://nodejs.dev/learn"},
                {"type": "documentation", "title": "Node.js Docs", "url": "https://nodejs.org/en/docs/"},
                {"type": "practice", "title": "Build Node.js Projects", "url": "https://www.freecodecamp.org/news/tag/node-js/"}
            ],
            "SQL": [
                {"type": "course", "title": "SQL for Data Science", "url": "https://www.coursera.org/learn/sql-for-data-science"},
                {"type": "practice", "title": "SQLBolt", "url": "https://sqlbolt.com/"},
                {"type": "practice", "title": "HackerRank SQL", "url": "https://www.hackerrank.com/domains/sql"}
            ],
            "MongoDB": [
                {"type": "course", "title": "MongoDB University", "url": "https://university.mongodb.com/"},
                {"type": "documentation", "title": "MongoDB Manual", "url": "https://www.mongodb.com/docs/manual/"},
                {"type": "practice", "title": "MongoDB Tutorials", "url": "https://www.mongodb.com/developer/"}
            ],
            "Docker": [
                {"type": "course", "title": "Docker for Beginners", "url": "https://docker-curriculum.com/"},
                {"type": "documentation", "title": "Docker Docs", "url": "https://docs.docker.com/"},
                {"type": "practice", "title": "Docker Labs", "url": "https://training.play-with-docker.com/"}
            ],
            "Git": [
                {"type": "course", "title": "Git Basics", "url": "https://git-scm.com/book/en/v2"},
                {"type": "practice", "title": "Learn Git Branching", "url": "https://learngitbranching.js.org/"},
                {"type": "practice", "title": "GitHub Skills", "url": "https://skills.github.com/"}
            ]
        }
        
        # Time estimates by difficulty and skill type
        self.time_estimates = {
            "Beginner": {
                "programming_language": "4-6 weeks",
                "framework": "3-4 weeks",
                "tool": "1-2 weeks",
                "concept": "2-3 weeks"
            },
            "Intermediate": {
                "programming_language": "2-3 weeks",
                "framework": "2-3 weeks",
                "tool": "1 week",
                "concept": "1-2 weeks"
            },
            "Advanced": {
                "programming_language": "1-2 weeks",
                "framework": "1-2 weeks",
                "tool": "3-5 days",
                "concept": "1 week"
            }
        }
    
    def _get_skill_category(self, skill: str) -> str:
        """Determine skill category for time estimation."""
        skill_lower = skill.lower()
        
        if any(lang in skill_lower for lang in ["python", "javascript", "java", "c++", "go", "rust"]):
            return "programming_language"
        elif any(fw in skill_lower for fw in ["react", "angular", "vue", "django", "flask", "spring"]):
            return "framework"
        elif any(tool in skill_lower for tool in ["git", "docker", "kubernetes", "jenkins"]):
            return "tool"
        else:
            return "concept"
    
    def _estimate_time(self, skill: str, experience_level: str) -> str:
        """Estimate time required to learn a skill."""
        category = self._get_skill_category(skill)
        return self.time_estimates.get(experience_level, self.time_estimates["Beginner"]).get(category, "2-3 weeks")
    
    def _get_resources(self, skill: str) -> List[Dict[str, str]]:
        """Get learning resources for a skill."""
        # Check if we have specific resources for this skill
        if skill in self.resource_database:
            return self.resource_database[skill]
        
        # Return generic resources
        return [
            {"type": "search", "title": f"{skill} Tutorial", "url": f"https://www.google.com/search?q={skill.replace(' ', '+')}+tutorial"},
            {"type": "search", "title": f"{skill} Documentation", "url": f"https://www.google.com/search?q={skill.replace(' ', '+')}+documentation"},
            {"type": "practice", "title": f"{skill} Projects", "url": f"https://github.com/topics/{skill.lower().replace(' ', '-')}"}
        ]
    
    def _determine_difficulty(self, skill: str, prerequisites: List[str], current_skills: List[str]) -> str:
        """Determine difficulty level based on prerequisites and current skills."""
        # If all prerequisites are met, it's easier
        prereqs_met = all(prereq in current_skills for prereq in prerequisites)
        
        if prereqs_met:
            return "Intermediate"
        elif len(prerequisites) == 0:
            return "Beginner"
        else:
            return "Advanced"
    
    async def generate_learning_path(self, request: LearningPathRequest) -> LearningPath:
        """
        Generate a personalized learning path.
        
        Args:
            request: Learning path request with user info and target role
            
        Returns:
            Complete learning path with steps and resources
        """
        try:
            # Get required skills for target role
            required_skills = await self._get_required_skills_for_role(request.target_role)
            
            # Identify skill gaps
            skill_gaps = [skill for skill in required_skills if skill not in request.current_skills]
            
            if not skill_gaps:
                # User already has all required skills
                return LearningPath(
                    user_id=request.user_id,
                    target_role=request.target_role,
                    steps=[],
                    total_estimated_time="0 weeks - You already have the required skills!",
                    skill_dependencies={},
                    generated_at=datetime.utcnow()
                )
            
            # Get optimal learning order using skill graph
            ordered_skills = await self._order_skills_by_dependencies(skill_gaps, request.current_skills)
            
            # Generate learning steps
            steps = []
            total_weeks = 0
            skill_dependencies = {}
            
            for idx, skill in enumerate(ordered_skills, 1):
                # Get prerequisites
                prerequisites = await self.skill_graph.get_prerequisites(skill)
                skill_dependencies[skill] = prerequisites
                
                # Determine difficulty
                difficulty = self._determine_difficulty(skill, prerequisites, request.current_skills + ordered_skills[:idx-1])
                
                # Estimate time
                estimated_time = self._estimate_time(skill, request.experience_level)
                
                # Extract weeks for total calculation
                try:
                    weeks = int(estimated_time.split('-')[0].split()[0])
                    total_weeks += weeks
                except:
                    total_weeks += 2  # Default 2 weeks
                
                # Get resources
                resources = self._get_resources(skill)
                
                # Create learning step
                step = LearningStep(
                    step_number=idx,
                    skill=skill,
                    description=f"Learn {skill} to enhance your {request.target_role} capabilities",
                    estimated_time=estimated_time,
                    resources=resources,
                    prerequisites=prerequisites,
                    difficulty=difficulty
                )
                steps.append(step)
            
            # Calculate total time
            total_months = total_weeks // 4
            remaining_weeks = total_weeks % 4
            
            if total_months > 0:
                total_time = f"{total_months} month{'s' if total_months > 1 else ''}"
                if remaining_weeks > 0:
                    total_time += f" {remaining_weeks} week{'s' if remaining_weeks > 1 else ''}"
            else:
                total_time = f"{total_weeks} week{'s' if total_weeks > 1 else ''}"
            
            return LearningPath(
                user_id=request.user_id,
                target_role=request.target_role,
                steps=steps,
                total_estimated_time=total_time,
                skill_dependencies=skill_dependencies,
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error generating learning path: {e}")
            # Return empty path on error
            return LearningPath(
                user_id=request.user_id,
                target_role=request.target_role,
                steps=[],
                total_estimated_time="Unable to calculate",
                skill_dependencies={},
                generated_at=datetime.utcnow()
            )
    
    async def _get_required_skills_for_role(self, role: str) -> List[str]:
        """Get required skills for a target role."""
        # Role-to-skills mapping (can be enhanced with database/API)
        role_skills = {
            "Full Stack Developer": ["HTML/CSS", "JavaScript", "React", "Node.js", "SQL", "MongoDB", "Git", "REST APIs"],
            "Backend Developer": ["Python", "Node.js", "SQL", "MongoDB", "REST APIs", "Docker", "Git"],
            "Frontend Developer": ["HTML/CSS", "JavaScript", "React", "TypeScript", "Git", "Responsive Design"],
            "Data Scientist": ["Python", "SQL", "Machine Learning", "Statistics", "Pandas", "NumPy", "Data Visualization"],
            "DevOps Engineer": ["Linux", "Docker", "Kubernetes", "CI/CD", "Git", "Python", "Cloud Platforms"],
            "Mobile Developer": ["React Native", "JavaScript", "Mobile UI/UX", "REST APIs", "Git"],
            "Machine Learning Engineer": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "SQL", "Git"]
        }
        
        return role_skills.get(role, ["Programming", "Problem Solving", "Git", "Communication"])
    
    async def _order_skills_by_dependencies(self, skills: List[str], current_skills: List[str]) -> List[str]:
        """Order skills based on dependencies (topological sort)."""
        try:
            # Use skill graph to get optimal order
            ordered = await self.skill_graph.get_learning_order(skills, current_skills)
            return ordered if ordered else skills
        except Exception as e:
            logger.error(f"Error ordering skills: {e}")
            # Fallback to original order
            return skills


# Singleton instance
_generator_instance = None

def get_learning_path_generator() -> LearningPathGenerator:
    """Get singleton instance of the learning path generator."""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = LearningPathGenerator()
    return _generator_instance
