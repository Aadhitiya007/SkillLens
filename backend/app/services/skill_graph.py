"""
Skill ontology and knowledge graph service using Neo4j.
Models skill relationships, dependencies, and role requirements.
"""

import logging
from typing import List, Dict, Optional, Set
from app.database import Neo4jClient
from app.config import settings

logger = logging.getLogger(__name__)


class SkillGraphService:
    """Service for managing skill knowledge graph in Neo4j."""
    
    async def initialize_skill_graph(self):
        """
        Initialize the skill knowledge graph with predefined skill hierarchy.
        This creates the foundational skill ontology.
        """
        try:
            # Create constraints
            await self._create_constraints()
            
            # Create skill hierarchy
            await self._create_skill_nodes()
            await self._create_role_nodes()
            await self._create_relationships()
            
            logger.info("Skill graph initialized successfully")
        
        except Exception as e:
            logger.error(f"Error initializing skill graph: {e}")
            raise
    
    async def _create_constraints(self):
        """Create uniqueness constraints on nodes."""
        constraints = [
            "CREATE CONSTRAINT skill_name IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE",
            "CREATE CONSTRAINT tool_name IF NOT EXISTS FOR (t:Tool) REQUIRE t.name IS UNIQUE",
            "CREATE CONSTRAINT role_title IF NOT EXISTS FOR (r:Role) REQUIRE r.title IS UNIQUE",
        ]
        
        for constraint in constraints:
            try:
                await Neo4jClient.execute_write(constraint)
            except Exception as e:
                logger.warning(f"Constraint may already exist: {e}")
    
    async def _create_skill_nodes(self):
        """Create skill nodes with hierarchy."""
        # Sample skill hierarchy for Data Engineer role
        skills_data = [
            # Programming Languages
            {"name": "Python", "category": "Programming", "level": "Core"},
            {"name": "SQL", "category": "Programming", "level": "Core"},
            {"name": "Java", "category": "Programming", "level": "Advanced"},
            {"name": "Scala", "category": "Programming", "level": "Advanced"},
            
            # Data Engineering
            {"name": "Data Modeling", "category": "Data Engineering", "level": "Core"},
            {"name": "ETL", "category": "Data Engineering", "level": "Core"},
            {"name": "Data Warehousing", "category": "Data Engineering", "level": "Core"},
            {"name": "Data Pipeline", "category": "Data Engineering", "level": "Core"},
            
            # Big Data
            {"name": "Apache Spark", "category": "Big Data", "level": "Core"},
            {"name": "Hadoop", "category": "Big Data", "level": "Advanced"},
            {"name": "Kafka", "category": "Big Data", "level": "Core"},
            
            # Cloud
            {"name": "AWS", "category": "Cloud", "level": "Core"},
            {"name": "Azure", "category": "Cloud", "level": "Advanced"},
            {"name": "GCP", "category": "Cloud", "level": "Advanced"},
            
            # Databases
            {"name": "PostgreSQL", "category": "Database", "level": "Core"},
            {"name": "MongoDB", "category": "Database", "level": "Advanced"},
            {"name": "Redis", "category": "Database", "level": "Advanced"},
            
            # DevOps
            {"name": "Docker", "category": "DevOps", "level": "Core"},
            {"name": "Kubernetes", "category": "DevOps", "level": "Advanced"},
            {"name": "CI/CD", "category": "DevOps", "level": "Core"},
            
            # Soft Skills
            {"name": "Problem Solving", "category": "Soft Skills", "level": "Core"},
            {"name": "Communication", "category": "Soft Skills", "level": "Core"},
            {"name": "Teamwork", "category": "Soft Skills", "level": "Core"},
        ]
        
        query = """
        UNWIND $skills AS skill
        MERGE (s:Skill {name: skill.name})
        SET s.category = skill.category,
            s.level = skill.level
        """
        
        await Neo4jClient.execute_write(query, {"skills": skills_data})
        logger.info(f"Created {len(skills_data)} skill nodes")
    
    async def _create_role_nodes(self):
        """Create role nodes."""
        roles_data = [
            {"title": "Data Engineer", "industry": "Technology", "seniority": "Mid"},
            {"title": "Software Engineer", "industry": "Technology", "seniority": "Mid"},
            {"title": "Data Scientist", "industry": "Technology", "seniority": "Mid"},
            {"title": "DevOps Engineer", "industry": "Technology", "seniority": "Mid"},
            {"title": "Full Stack Developer", "industry": "Technology", "seniority": "Mid"},
        ]
        
        query = """
        UNWIND $roles AS role
        MERGE (r:Role {title: role.title})
        SET r.industry = role.industry,
            r.seniority = role.seniority
        """
        
        await Neo4jClient.execute_write(query, {"roles": roles_data})
        logger.info(f"Created {len(roles_data)} role nodes")
    
    async def _create_relationships(self):
        """Create relationships between skills and roles."""
        # Skill dependencies (REQUIRES)
        dependencies = [
            ("Apache Spark", "Python"),
            ("Apache Spark", "Scala"),
            ("Data Pipeline", "ETL"),
            ("Data Pipeline", "Apache Spark"),
            ("Kubernetes", "Docker"),
            ("Data Warehousing", "SQL"),
        ]
        
        for skill1, skill2 in dependencies:
            query = """
            MATCH (s1:Skill {name: $skill1})
            MATCH (s2:Skill {name: $skill2})
            MERGE (s1)-[:REQUIRES]->(s2)
            """
            await Neo4jClient.execute_write(query, {"skill1": skill1, "skill2": skill2})
        
        # Role requirements (NEEDS)
        role_requirements = {
            "Data Engineer": ["Python", "SQL", "Apache Spark", "ETL", "Data Modeling", 
                            "AWS", "Docker", "PostgreSQL", "Kafka"],
            "Software Engineer": ["Python", "Java", "SQL", "Docker", "CI/CD", 
                                "Problem Solving", "Communication"],
            "Data Scientist": ["Python", "SQL", "Problem Solving", "Communication"],
        }
        
        for role, skills in role_requirements.items():
            for skill in skills:
                query = """
                MATCH (r:Role {title: $role})
                MATCH (s:Skill {name: $skill})
                MERGE (r)-[:NEEDS]->(s)
                """
                await Neo4jClient.execute_write(query, {"role": role, "skill": skill})
        
        logger.info("Created skill relationships")
    
    async def find_missing_skills(self, user_skills: List[str], target_role: str) -> Dict:
        """
        Find missing skills for a target role.
        
        Args:
            user_skills: List of skills the user has
            target_role: Target role title
            
        Returns:
            Dictionary with missing skills and their categories
        """
        query = """
        MATCH (r:Role {title: $role})-[:NEEDS]->(s:Skill)
        WHERE NOT s.name IN $user_skills
        RETURN s.name AS skill, s.category AS category, s.level AS level
        ORDER BY s.level, s.category
        """
        
        result = await Neo4jClient.execute_query(
            query,
            {"role": target_role, "user_skills": user_skills}
        )
        
        missing_skills = {
            "core": [],
            "advanced": [],
            "total_count": len(result)
        }
        
        for record in result:
            skill_info = {
                "name": record["skill"],
                "category": record["category"]
            }
            
            if record["level"] == "Core":
                missing_skills["core"].append(skill_info)
            else:
                missing_skills["advanced"].append(skill_info)
        
        return missing_skills
    
    async def get_skill_dependencies(self, skill: str) -> List[str]:
        """
        Get all dependencies for a skill.
        
        Args:
            skill: Skill name
            
        Returns:
            List of prerequisite skills
        """
        query = """
        MATCH (s:Skill {name: $skill})-[:REQUIRES]->(dep:Skill)
        RETURN dep.name AS dependency
        """
        
        result = await Neo4jClient.execute_query(query, {"skill": skill})
        return [record["dependency"] for record in result]
    
    async def get_skill_hierarchy(self) -> Dict:
        """
        Get the complete skill hierarchy.
        
        Returns:
            Dictionary with skills organized by category
        """
        query = """
        MATCH (s:Skill)
        RETURN s.name AS skill, s.category AS category, s.level AS level
        ORDER BY s.category, s.level
        """
        
        result = await Neo4jClient.execute_query(query)
        
        hierarchy = {}
        for record in result:
            category = record["category"]
            if category not in hierarchy:
                hierarchy[category] = []
            
            hierarchy[category].append({
                "name": record["skill"],
                "level": record["level"]
            })
        
        return hierarchy
    
    async def explain_skill_gap(self, user_skills: List[str], target_role: str) -> str:
        """
        Generate a detailed explanation of skill gaps.
        
        Args:
            user_skills: List of user's current skills
            target_role: Target role title
            
        Returns:
            Plain-English explanation of skill gaps
        """
        missing = await self.find_missing_skills(user_skills, target_role)
        
        if missing["total_count"] == 0:
            return f"You have all the required skills for {target_role}!"
        
        explanation = f"For the {target_role} role, you are missing {missing['total_count']} skills:\n\n"
        
        if missing["core"]:
            explanation += "**Core Skills (High Priority):**\n"
            for skill in missing["core"]:
                deps = await self.get_skill_dependencies(skill["name"])
                explanation += f"- {skill['name']} ({skill['category']})"
                if deps:
                    explanation += f" - Requires: {', '.join(deps)}"
                explanation += "\n"
        
        if missing["advanced"]:
            explanation += "\n**Advanced Skills (Nice to Have):**\n"
            for skill in missing["advanced"]:
                explanation += f"- {skill['name']} ({skill['category']})\n"
        
        return explanation
    
    async def get_learning_path(self, user_skills: List[str], target_role: str) -> List[Dict]:
        """
        Generate an ordered learning path based on skill dependencies.
        
        Args:
            user_skills: List of user's current skills
            target_role: Target role title
            
        Returns:
            Ordered list of skills to learn
        """
        missing = await self.find_missing_skills(user_skills, target_role)
        
        # Start with core skills that have no dependencies or whose dependencies are met
        learning_path = []
        
        # Add core skills first
        for skill in missing["core"]:
            deps = await self.get_skill_dependencies(skill["name"])
            unmet_deps = [d for d in deps if d not in user_skills]
            
            learning_path.append({
                "skill": skill["name"],
                "category": skill["category"],
                "priority": "High",
                "prerequisites": deps,
                "unmet_prerequisites": unmet_deps
            })
        
        # Add advanced skills
        for skill in missing["advanced"]:
            deps = await self.get_skill_dependencies(skill["name"])
            unmet_deps = [d for d in deps if d not in user_skills]
            
            learning_path.append({
                "skill": skill["name"],
                "category": skill["category"],
                "priority": "Medium",
                "prerequisites": deps,
                "unmet_prerequisites": unmet_deps
            })
        
        # Sort by number of unmet prerequisites (learn foundational skills first)
        learning_path.sort(key=lambda x: len(x["unmet_prerequisites"]))
        
        return learning_path


# Global instance
skill_graph_service = SkillGraphService()
