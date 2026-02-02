"""
Career readiness scoring engine with Explainable AI.
Calculates readiness scores and generates plain-English explanations using GPT-3.5.
"""

import logging
from typing import List, Dict, Optional
from openai import AsyncOpenAI

from app.config import settings
from app.models.scoring import ReadinessScore, FactorContribution
from app.models.resume import ResumeData

logger = logging.getLogger(__name__)


class ScoringEngine:
    """Service for calculating career readiness scores with XAI."""
    
    def __init__(self):
        """Initialize scoring engine with OpenAI client."""
        self.client = None
        if settings.openai_api_key:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    def calculate_technical_skills_score(
        self,
        user_skills: List[str],
        required_skills: List[str]
    ) -> tuple[float, str]:
        """
        Calculate technical skills match score.
        
        Returns:
            Tuple of (score, details)
        """
        if not required_skills:
            return 100.0, "No specific skills required"
        
        matched_skills = set(user_skills) & set(required_skills)
        match_percentage = (len(matched_skills) / len(required_skills)) * 100
        
        details = f"Matched {len(matched_skills)}/{len(required_skills)} required skills"
        
        return match_percentage, details
    
    def calculate_experience_score(
        self,
        experience_list: List,
        target_years: int = 2
    ) -> tuple[float, str]:
        """
        Calculate experience relevance score.
        
        Returns:
            Tuple of (score, details)
        """
        if not experience_list:
            return 0.0, "No work experience found"
        
        # Simple heuristic: score based on number of experiences
        # In production, this should parse years of experience
        experience_count = len(experience_list)
        
        if experience_count >= target_years:
            score = 100.0
            details = f"{experience_count} relevant experiences found"
        else:
            score = (experience_count / target_years) * 100
            details = f"{experience_count} experiences (target: {target_years})"
        
        return score, details
    
    def calculate_project_score(
        self,
        projects: List,
        min_projects: int = 3
    ) -> tuple[float, str]:
        """
        Calculate project portfolio score.
        
        Returns:
            Tuple of (score, details)
        """
        if not projects:
            return 0.0, "No projects found"
        
        project_count = len(projects)
        
        if project_count >= min_projects:
            score = 100.0
            details = f"{project_count} projects in portfolio"
        else:
            score = (project_count / min_projects) * 100
            details = f"{project_count} projects (recommended: {min_projects})"
        
        return score, details
    
    def calculate_tool_proficiency_score(
        self,
        user_tools: List[str],
        required_tools: List[str]
    ) -> tuple[float, str]:
        """
        Calculate tool proficiency score.
        
        Returns:
            Tuple of (score, details)
        """
        if not required_tools:
            return 100.0, "No specific tools required"
        
        matched_tools = set(user_tools) & set(required_tools)
        match_percentage = (len(matched_tools) / len(required_tools)) * 100
        
        details = f"Proficient in {len(matched_tools)}/{len(required_tools)} required tools"
        
        return match_percentage, details
    
    async def calculate_readiness_score(
        self,
        resume_data: ResumeData,
        target_role: str,
        required_skills: List[str],
        required_tools: Optional[List[str]] = None
    ) -> ReadinessScore:
        """
        Calculate overall career readiness score with factor breakdown.
        
        Args:
            resume_data: Parsed resume data
            target_role: Target role title
            required_skills: List of required skills for the role
            required_tools: Optional list of required tools
            
        Returns:
            ReadinessScore with detailed breakdown
        """
        required_tools = required_tools or []
        
        # Define scoring weights
        weights = {
            "technical_skills": 0.40,
            "experience": 0.25,
            "projects": 0.20,
            "tools": 0.15
        }
        
        # Calculate individual factor scores
        tech_score, tech_details = self.calculate_technical_skills_score(
            resume_data.skills,
            required_skills
        )
        
        exp_score, exp_details = self.calculate_experience_score(
            resume_data.experience
        )
        
        proj_score, proj_details = self.calculate_project_score(
            resume_data.projects
        )
        
        tool_score, tool_details = self.calculate_tool_proficiency_score(
            resume_data.tools,
            required_tools
        )
        
        # Create factor contributions
        factors = [
            FactorContribution(
                factor_name="Technical Skills",
                weight=weights["technical_skills"],
                score=tech_score,
                contribution=tech_score * weights["technical_skills"],
                details=tech_details
            ),
            FactorContribution(
                factor_name="Experience",
                weight=weights["experience"],
                score=exp_score,
                contribution=exp_score * weights["experience"],
                details=exp_details
            ),
            FactorContribution(
                factor_name="Project Portfolio",
                weight=weights["projects"],
                score=proj_score,
                contribution=proj_score * weights["projects"],
                details=proj_details
            ),
            FactorContribution(
                factor_name="Tool Proficiency",
                weight=weights["tools"],
                score=tool_score,
                contribution=tool_score * weights["tools"],
                details=tool_details
            )
        ]
        
        # Calculate overall score
        overall_score = sum(f.contribution for f in factors)
        
        # Identify strengths and weaknesses
        strengths = [f.factor_name for f in factors if f.score >= 70]
        weaknesses = [f.factor_name for f in factors if f.score < 50]
        
        # Generate explanation using GPT-3.5
        explanation = await self.generate_explanation(
            overall_score,
            factors,
            target_role,
            resume_data
        )
        
        # Generate recommendations
        recommendations = self.generate_recommendations(factors, required_skills, resume_data.skills)
        
        return ReadinessScore(
            overall_score=round(overall_score, 2),
            target_role=target_role,
            factors=factors,
            explanation=explanation,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations
        )
    
    async def generate_explanation(
        self,
        score: float,
        factors: List[FactorContribution],
        target_role: str,
        resume_data: ResumeData
    ) -> str:
        """
        Generate plain-English explanation using GPT-3.5.
        
        Args:
            score: Overall readiness score
            factors: List of factor contributions
            target_role: Target role title
            resume_data: Resume data
            
        Returns:
            Plain-English explanation
        """
        if not self.client:
            # Fallback explanation without GPT
            return self._generate_fallback_explanation(score, factors, target_role)
        
        try:
            # Prepare context for GPT
            factor_summary = "\n".join([
                f"- {f.factor_name}: {f.score:.1f}% (weight: {f.weight*100}%, contribution: {f.contribution:.1f})"
                for f in factors
            ])
            
            prompt = f"""You are a career advisor explaining a career readiness assessment.

Target Role: {target_role}
Overall Readiness Score: {score:.1f}%

Factor Breakdown:
{factor_summary}

User's Skills: {', '.join(resume_data.skills[:10])}
Experience Count: {len(resume_data.experience)}
Project Count: {len(resume_data.projects)}

Generate a concise, encouraging 2-3 sentence explanation of this readiness score. 
Focus on what's strong and what needs improvement. Be specific and actionable.
"""
            
            response = await self.client.chat.completions.create(
                model=settings.gpt_model,
                messages=[
                    {"role": "system", "content": "You are a helpful career advisor providing clear, actionable feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.gpt_temperature,
                max_tokens=200
            )
            
            explanation = response.choices[0].message.content.strip()
            logger.info("Generated explanation using GPT-3.5")
            return explanation
        
        except Exception as e:
            logger.error(f"Error generating explanation with GPT: {e}")
            return self._generate_fallback_explanation(score, factors, target_role)
    
    def _generate_fallback_explanation(
        self,
        score: float,
        factors: List[FactorContribution],
        target_role: str
    ) -> str:
        """Generate explanation without GPT (fallback)."""
        if score >= 80:
            level = "excellent"
        elif score >= 60:
            level = "good"
        elif score >= 40:
            level = "moderate"
        else:
            level = "developing"
        
        strong_factors = [f.factor_name for f in factors if f.score >= 70]
        weak_factors = [f.factor_name for f in factors if f.score < 50]
        
        explanation = f"Your readiness for {target_role} is {level} at {score:.1f}%. "
        
        if strong_factors:
            explanation += f"Strong areas: {', '.join(strong_factors)}. "
        
        if weak_factors:
            explanation += f"Areas for improvement: {', '.join(weak_factors)}."
        
        return explanation
    
    def generate_recommendations(
        self,
        factors: List[FactorContribution],
        required_skills: List[str],
        user_skills: List[str]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Check each factor
        for factor in factors:
            if factor.score < 50:
                if factor.factor_name == "Technical Skills":
                    missing = set(required_skills) - set(user_skills)
                    if missing:
                        recommendations.append(
                            f"Learn key skills: {', '.join(list(missing)[:3])}"
                        )
                elif factor.factor_name == "Experience":
                    recommendations.append(
                        "Gain practical experience through internships or freelance projects"
                    )
                elif factor.factor_name == "Project Portfolio":
                    recommendations.append(
                        "Build 2-3 projects showcasing your skills"
                    )
                elif factor.factor_name == "Tool Proficiency":
                    recommendations.append(
                        "Practice with industry-standard tools and frameworks"
                    )
        
        if not recommendations:
            recommendations.append("Continue building on your strong foundation")
        
        return recommendations


# Global instance
scoring_engine = ScoringEngine()
