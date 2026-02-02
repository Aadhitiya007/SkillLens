"""
Comprehensive test suite for SkillLens backend.
Tests all major services and API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints for all services."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["message"] == "Welcome to SkillLens API"
    
    def test_health_check(self):
        """Test main health check."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_agent_health(self):
        """Test AI agent health."""
        response = client.get("/api/agent/health")
        assert response.status_code == 200
        assert "AI Agent" in response.json()["service"]
    
    def test_predictions_health(self):
        """Test predictions health."""
        response = client.get("/api/predictions/health")
        assert response.status_code in [200, 503]  # May be degraded if model not loaded
    
    def test_verification_health(self):
        """Test verification health."""
        response = client.get("/api/verification/health")
        assert response.status_code == 200
    
    def test_jobs_health(self):
        """Test jobs health."""
        response = client.get("/api/jobs/health")
        assert response.status_code == 200
    
    def test_analytics_health(self):
        """Test analytics health."""
        response = client.get("/api/analytics/health")
        assert response.status_code == 200


class TestAIAgent:
    """Test AI agent functionality."""
    
    def test_chat_endpoint(self):
        """Test chat with AI agent."""
        payload = {
            "user_id": "test_user",
            "message": "What skills do I need for a Full Stack role?",
            "context": {"target_role": "Full Stack Developer"}
        }
        response = client.post("/api/agent/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "suggestions" in data


class TestPredictions:
    """Test prediction service."""
    
    def test_shortlist_probability(self):
        """Test shortlisting probability prediction."""
        payload = {
            "resume_text": "Software Engineer with 3 years experience in Python and React",
            "job_description": "Looking for Full Stack Developer with React and Node.js",
            "user_skills": ["Python", "React", "JavaScript"],
            "experience_years": 3.0
        }
        response = client.post("/api/predictions/shortlist-probability", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "shortlist_probability" in data
        assert 0 <= data["shortlist_probability"] <= 100


class TestVerification:
    """Test skill verification."""
    
    def test_generate_assessment(self):
        """Test assessment generation."""
        payload = {
            "user_id": "test_user",
            "skill": "Python",
            "difficulty": "intermediate",
            "num_questions": 5
        }
        response = client.post("/api/verification/generate-assessment", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "assessment_id" in data
        assert len(data["questions"]) == 5


class TestJobs:
    """Test job market intelligence."""
    
    def test_job_recommendations(self):
        """Test job recommendations."""
        payload = {
            "user_skills": ["Python", "React", "JavaScript"],
            "experience_years": 2.0,
            "limit": 5
        }
        response = client.post("/api/jobs/recommendations", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert len(data["recommendations"]) <= 5
    
    def test_market_trends(self):
        """Test market trends."""
        response = client.get("/api/jobs/market-trends")
        assert response.status_code == 200
        data = response.json()
        assert "top_skills" in data
        assert "top_roles" in data


class TestAnalytics:
    """Test institutional analytics."""
    
    def test_placement_statistics(self):
        """Test placement statistics."""
        response = client.get("/api/analytics/placement-statistics")
        assert response.status_code == 200
        data = response.json()
        assert "total_students" in data
        assert "placement_rate" in data
    
    def test_readiness_distribution(self):
        """Test readiness distribution."""
        response = client.get("/api/analytics/readiness-distribution")
        assert response.status_code == 200
        data = response.json()
        assert "distribution" in data
    
    def test_skill_gap_analysis(self):
        """Test skill gap analysis."""
        response = client.get("/api/analytics/skill-gap-analysis")
        assert response.status_code == 200
        data = response.json()
        assert "most_common_gaps" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
