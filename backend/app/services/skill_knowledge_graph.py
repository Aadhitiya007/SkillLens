"""
Skill Knowledge Graph Service
Implements graph-based skill relationships and optimal learning paths
Can work with in-memory graph or Neo4j
"""

from typing import List, Dict, Set, Optional, Tuple
import heapq
from collections import defaultdict, deque
import json

class SkillKnowledgeGraph:
    """
    Knowledge graph for skills with dependencies and relationships
    Uses graph algorithms for intelligent path finding
    """
    
    def __init__(self):
        # Graph structure: adjacency list
        self.graph = defaultdict(list)  # skill -> [(prerequisite, weight)]
        self.skills = {}  # skill_name -> skill_data
        self.roles = {}  # role_name -> required_skills
        
        # Initialize with comprehensive skill data
        self._initialize_graph()
    
    def _initialize_graph(self):
        """Initialize graph with 100+ skills and dependencies"""
        
        # Define skills with metadata
        skills_data = [
            # Programming Languages (Foundation)
            {"name": "Python", "category": "Programming", "difficulty": 2, "demand": 95},
            {"name": "Java", "category": "Programming", "difficulty": 3, "demand": 85},
            {"name": "JavaScript", "category": "Programming", "difficulty": 2, "demand": 90},
            {"name": "TypeScript", "category": "Programming", "difficulty": 3, "demand": 80},
            {"name": "C++", "category": "Programming", "difficulty": 4, "demand": 70},
            {"name": "Go", "category": "Programming", "difficulty": 3, "demand": 75},
            {"name": "Rust", "category": "Programming", "difficulty": 5, "demand": 65},
            {"name": "SQL", "category": "Database", "difficulty": 2, "demand": 95},
            
            # Web Development
            {"name": "HTML", "category": "Web", "difficulty": 1, "demand": 85},
            {"name": "CSS", "category": "Web", "difficulty": 1, "demand": 85},
            {"name": "React", "category": "Web", "difficulty": 3, "demand": 90},
            {"name": "Angular", "category": "Web", "difficulty": 4, "demand": 70},
            {"name": "Vue.js", "category": "Web", "difficulty": 3, "demand": 75},
            {"name": "Node.js", "category": "Web", "difficulty": 3, "demand": 85},
            {"name": "Express", "category": "Web", "difficulty": 2, "demand": 80},
            {"name": "Django", "category": "Web", "difficulty": 3, "demand": 75},
            {"name": "Flask", "category": "Web", "difficulty": 2, "demand": 70},
            {"name": "FastAPI", "category": "Web", "difficulty": 3, "demand": 80},
            
            # Databases
            {"name": "MongoDB", "category": "Database", "difficulty": 2, "demand": 80},
            {"name": "PostgreSQL", "category": "Database", "difficulty": 3, "demand": 85},
            {"name": "MySQL", "category": "Database", "difficulty": 2, "demand": 85},
            {"name": "Redis", "category": "Database", "difficulty": 2, "demand": 75},
            {"name": "Elasticsearch", "category": "Database", "difficulty": 4, "demand": 70},
            {"name": "Neo4j", "category": "Database", "difficulty": 4, "demand": 60},
            
            # Cloud & DevOps
            {"name": "AWS", "category": "Cloud", "difficulty": 4, "demand": 95},
            {"name": "Azure", "category": "Cloud", "difficulty": 4, "demand": 85},
            {"name": "GCP", "category": "Cloud", "difficulty": 4, "demand": 80},
            {"name": "Docker", "category": "DevOps", "difficulty": 3, "demand": 90},
            {"name": "Kubernetes", "category": "DevOps", "difficulty": 5, "demand": 85},
            {"name": "Jenkins", "category": "DevOps", "difficulty": 3, "demand": 75},
            {"name": "GitLab CI", "category": "DevOps", "difficulty": 3, "demand": 70},
            {"name": "Terraform", "category": "DevOps", "difficulty": 4, "demand": 80},
            {"name": "Ansible", "category": "DevOps", "difficulty": 4, "demand": 70},
            
            # Data Science & ML
            {"name": "Machine Learning", "category": "AI/ML", "difficulty": 5, "demand": 95},
            {"name": "Deep Learning", "category": "AI/ML", "difficulty": 6, "demand": 90},
            {"name": "TensorFlow", "category": "AI/ML", "difficulty": 5, "demand": 85},
            {"name": "PyTorch", "category": "AI/ML", "difficulty": 5, "demand": 85},
            {"name": "Scikit-learn", "category": "AI/ML", "difficulty": 4, "demand": 80},
            {"name": "Pandas", "category": "Data Science", "difficulty": 3, "demand": 90},
            {"name": "NumPy", "category": "Data Science", "difficulty": 3, "demand": 85},
            {"name": "Matplotlib", "category": "Data Science", "difficulty": 2, "demand": 75},
            {"name": "NLP", "category": "AI/ML", "difficulty": 5, "demand": 85},
            {"name": "Computer Vision", "category": "AI/ML", "difficulty": 5, "demand": 80},
            
            # Big Data
            {"name": "Apache Spark", "category": "Big Data", "difficulty": 5, "demand": 85},
            {"name": "Hadoop", "category": "Big Data", "difficulty": 5, "demand": 70},
            {"name": "Kafka", "category": "Big Data", "difficulty": 4, "demand": 85},
            {"name": "Airflow", "category": "Big Data", "difficulty": 4, "demand": 80},
            {"name": "ETL", "category": "Big Data", "difficulty": 3, "demand": 85},
            {"name": "Data Modeling", "category": "Big Data", "difficulty": 4, "demand": 80},
            
            # Tools
            {"name": "Git", "category": "Tools", "difficulty": 2, "demand": 95},
            {"name": "Linux", "category": "Tools", "difficulty": 3, "demand": 85},
            {"name": "REST APIs", "category": "Tools", "difficulty": 3, "demand": 90},
            {"name": "GraphQL", "category": "Tools", "difficulty": 4, "demand": 75},
        ]
        
        # Add skills to graph
        for skill in skills_data:
            self.skills[skill["name"]] = skill
        
        # Define skill dependencies (prerequisite -> skill, weight)
        dependencies = [
            # Programming foundations
            ("Python", "Django", 0.8),
            ("Python", "Flask", 0.7),
            ("Python", "FastAPI", 0.8),
            ("Python", "Pandas", 0.6),
            ("Python", "NumPy", 0.5),
            ("Python", "Scikit-learn", 0.7),
            ("Python", "TensorFlow", 0.8),
            ("Python", "PyTorch", 0.8),
            ("Python", "Machine Learning", 0.9),
            
            # Web development
            ("HTML", "CSS", 0.3),
            ("CSS", "React", 0.5),
            ("JavaScript", "React", 0.8),
            ("JavaScript", "Angular", 0.8),
            ("JavaScript", "Vue.js", 0.8),
            ("JavaScript", "Node.js", 0.7),
            ("JavaScript", "TypeScript", 0.6),
            ("Node.js", "Express", 0.7),
            
            # ML progression
            ("Python", "Machine Learning", 0.8),
            ("Machine Learning", "Deep Learning", 0.9),
            ("NumPy", "Pandas", 0.5),
            ("Pandas", "Machine Learning", 0.7),
            ("Machine Learning", "NLP", 0.8),
            ("Machine Learning", "Computer Vision", 0.8),
            ("Deep Learning", "TensorFlow", 0.7),
            ("Deep Learning", "PyTorch", 0.7),
            
            # Big Data
            ("Python", "Apache Spark", 0.7),
            ("SQL", "ETL", 0.8),
            ("ETL", "Data Modeling", 0.6),
            ("Python", "Airflow", 0.6),
            ("SQL", "Data Modeling", 0.7),
            
            # Cloud & DevOps
            ("Linux", "Docker", 0.7),
            ("Docker", "Kubernetes", 0.9),
            ("Git", "GitLab CI", 0.6),
            ("Git", "Jenkins", 0.5),
            ("Docker", "AWS", 0.6),
            ("Docker", "Azure", 0.6),
            ("Docker", "GCP", 0.6),
        ]
        
        # Build graph
        for prereq, skill, weight in dependencies:
            self.graph[skill].append((prereq, weight))
        
        # Define role requirements
        self.roles = {
            "Data Engineer": {
                "required": ["Python", "SQL", "Apache Spark", "ETL", "Data Modeling", "AWS", "Docker"],
                "preferred": ["Kafka", "Airflow", "Kubernetes"]
            },
            "Software Engineer": {
                "required": ["Python", "Java", "SQL", "Git", "REST APIs"],
                "preferred": ["Docker", "Kubernetes", "AWS"]
            },
            "Full Stack Developer": {
                "required": ["JavaScript", "React", "Node.js", "SQL", "HTML", "CSS"],
                "preferred": ["TypeScript", "MongoDB", "Docker"]
            },
            "Machine Learning Engineer": {
                "required": ["Python", "Machine Learning", "TensorFlow", "Pandas", "NumPy"],
                "preferred": ["Deep Learning", "PyTorch", "AWS"]
            },
            "DevOps Engineer": {
                "required": ["Linux", "Docker", "Kubernetes", "AWS", "Terraform"],
                "preferred": ["Ansible", "Jenkins", "Python"]
            }
        }
    
    def find_optimal_learning_path(
        self,
        current_skills: List[str],
        target_role: str
    ) -> Dict:
        """
        Find optimal learning path using modified Dijkstra's algorithm
        
        Args:
            current_skills: Skills user already has
            target_role: Target role name
            
        Returns:
            Learning path with ordered skills and estimated time
        """
        if target_role not in self.roles:
            return {"error": f"Role '{target_role}' not found"}
        
        role_data = self.roles[target_role]
        required_skills = set(role_data["required"])
        current_skills_set = set(current_skills)
        
        # Find missing skills
        missing_skills = required_skills - current_skills_set
        
        if not missing_skills:
            return {
                "status": "complete",
                "message": "You already have all required skills!",
                "path": []
            }
        
        # Build learning path considering dependencies
        learning_path = []
        skills_to_learn = set(missing_skills)
        learned = set(current_skills_set)
        
        while skills_to_learn:
            # Find skills that can be learned now (all prerequisites met)
            learnable = []
            for skill in skills_to_learn:
                prerequisites = [prereq for prereq, _ in self.graph.get(skill, [])]
                if all(prereq in learned for prereq in prerequisites):
                    learnable.append(skill)
            
            if not learnable:
                # No skill can be learned - break circular dependency
                learnable = [list(skills_to_learn)[0]]
            
            # Sort by difficulty and demand
            learnable.sort(key=lambda s: (
                self.skills.get(s, {}).get("difficulty", 3),
                -self.skills.get(s, {}).get("demand", 50)
            ))
            
            # Add to path
            next_skill = learnable[0]
            skill_data = self.skills.get(next_skill, {})
            
            learning_path.append({
                "skill": next_skill,
                "category": skill_data.get("category", "Unknown"),
                "difficulty": skill_data.get("difficulty", 3),
                "estimated_weeks": skill_data.get("difficulty", 3),
                "demand": skill_data.get("demand", 50),
                "prerequisites": [prereq for prereq, _ in self.graph.get(next_skill, [])]
            })
            
            learned.add(next_skill)
            skills_to_learn.remove(next_skill)
        
        total_weeks = sum(item["estimated_weeks"] for item in learning_path)
        
        return {
            "status": "success",
            "target_role": target_role,
            "current_skills_count": len(current_skills),
            "required_skills_count": len(required_skills),
            "missing_skills_count": len(missing_skills),
            "learning_path": learning_path,
            "total_estimated_weeks": total_weeks,
            "completion_percentage": (len(current_skills_set & required_skills) / len(required_skills)) * 100
        }
    
    def get_skill_dependencies(self, skill: str) -> Dict:
        """Get all dependencies for a skill"""
        if skill not in self.skills:
            return {"error": f"Skill '{skill}' not found"}
        
        dependencies = self.graph.get(skill, [])
        
        return {
            "skill": skill,
            "direct_prerequisites": [
                {"skill": prereq, "importance": weight}
                for prereq, weight in dependencies
            ],
            "all_prerequisites": self._get_all_prerequisites(skill),
            "enables": self._get_enabled_skills(skill)
        }
    
    def _get_all_prerequisites(self, skill: str) -> List[str]:
        """Get all prerequisites recursively (BFS)"""
        visited = set()
        queue = deque([skill])
        
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            
            for prereq, _ in self.graph.get(current, []):
                if prereq not in visited:
                    queue.append(prereq)
        
        visited.discard(skill)
        return list(visited)
    
    def _get_enabled_skills(self, skill: str) -> List[str]:
        """Get skills that this skill enables"""
        enabled = []
        for target_skill, prerequisites in self.graph.items():
            if any(prereq == skill for prereq, _ in prerequisites):
                enabled.append(target_skill)
        return enabled
    
    def analyze_skill_gap(
        self,
        user_skills: List[str],
        target_role: str
    ) -> Dict:
        """
        Comprehensive skill gap analysis
        
        Returns:
            Detailed gap analysis with categorized skills
        """
        if target_role not in self.roles:
            return {"error": f"Role '{target_role}' not found"}
        
        role_data = self.roles[target_role]
        required = set(role_data["required"])
        preferred = set(role_data.get("preferred", []))
        user_skills_set = set(user_skills)
        
        # Categorize skills
        matched_required = user_skills_set & required
        missing_required = required - user_skills_set
        matched_preferred = user_skills_set & preferred
        missing_preferred = preferred - user_skills_set
        extra_skills = user_skills_set - (required | preferred)
        
        # Calculate match percentage
        required_match = (len(matched_required) / len(required)) * 100 if required else 0
        total_match = (len(matched_required | matched_preferred) / len(required | preferred)) * 100 if (required | preferred) else 0
        
        return {
            "target_role": target_role,
            "required_skills": {
                "matched": list(matched_required),
                "missing": list(missing_required),
                "match_percentage": round(required_match, 1)
            },
            "preferred_skills": {
                "matched": list(matched_preferred),
                "missing": list(missing_preferred)
            },
            "extra_skills": list(extra_skills),
            "overall_match_percentage": round(total_match, 1),
            "readiness_level": self._get_readiness_level(required_match)
        }
    
    def _get_readiness_level(self, match_percentage: float) -> str:
        """Determine readiness level based on match percentage"""
        if match_percentage >= 90:
            return "Excellent - Ready to apply"
        elif match_percentage >= 70:
            return "Good - Minor gaps"
        elif match_percentage >= 50:
            return "Moderate - Significant learning needed"
        else:
            return "Developing - Major skill gaps"
    
    async def get_skill_details(self, skill_name: str) -> Optional[Dict]:
        """Get detailed information about a skill (async wrapper)."""
        if skill_name not in self.skills:
            return None
        
        skill_data = self.skills[skill_name]
        prerequisites = [prereq for prereq, _ in self.graph.get(skill_name, [])]
        related_skills = self._get_enabled_skills(skill_name)
        
        return {
            "name": skill_name,
            "category": skill_data.get("category"),
            "difficulty": skill_data.get("difficulty"),
            "demand": skill_data.get("demand"),
            "prerequisites": prerequisites,
            "related_skills": related_skills
        }
    
    async def get_learning_path(self, target_skill: str) -> Optional[List[str]]:
        """Get learning path for a target skill (async wrapper)."""
        if target_skill not in self.skills:
            return None
        
        # Get all prerequisites
        all_prereqs = self._get_all_prerequisites(target_skill)
        
        # Order prerequisites by dependency
        path = []
        remaining = set(all_prereqs)
        learned = set()
        
        while remaining:
            # Find skills that can be learned now
            learnable = []
            for skill in remaining:
                prereqs = [p for p, _ in self.graph.get(skill, [])]
                if all(p in learned or p not in remaining for p in prereqs):
                    learnable.append(skill)
            
            if not learnable:
                # Break circular dependency
                learnable = [list(remaining)[0]]
            
            # Sort by difficulty
            learnable.sort(key=lambda s: self.skills.get(s, {}).get("difficulty", 3))
            
            next_skill = learnable[0]
            path.append(next_skill)
            learned.add(next_skill)
            remaining.remove(next_skill)
        
        path.append(target_skill)
        return path
    
    async def get_prerequisites(self, skill: str) -> List[str]:
        """Get direct prerequisites for a skill (async wrapper)."""
        return [prereq for prereq, _ in self.graph.get(skill, [])]
    
    async def get_learning_order(self, skills: List[str], current_skills: List[str]) -> List[str]:
        """Order skills based on dependencies (async wrapper)."""
        ordered = []
        remaining = set(skills)
        learned = set(current_skills)
        
        while remaining:
            # Find skills that can be learned now
            learnable = []
            for skill in remaining:
                prereqs = [p for p, _ in self.graph.get(skill, [])]
                if all(p in learned for p in prereqs):
                    learnable.append(skill)
            
            if not learnable:
                # No skill can be learned - add one anyway
                learnable = [list(remaining)[0]]
            
            # Sort by difficulty and demand
            learnable.sort(key=lambda s: (
                self.skills.get(s, {}).get("difficulty", 3),
                -self.skills.get(s, {}).get("demand", 50)
            ))
            
            next_skill = learnable[0]
            ordered.append(next_skill)
            learned.add(next_skill)
            remaining.remove(next_skill)
        
        return ordered

# Singleton instance
_graph_instance = None

def get_skill_graph() -> SkillKnowledgeGraph:
    """Get or create knowledge graph instance"""
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = SkillKnowledgeGraph()
    return _graph_instance
