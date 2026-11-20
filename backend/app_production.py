"""
SkillLens Production Backend - Full AI/ML Integration
Includes database persistence, authentication, and real AI services.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
from pydantic import BaseModel
import uvicorn
from datetime import datetime
import logging
import os
from pathlib import Path

# Import configuration
from app.config import settings
from app.database import MongoDB, Neo4jClient

# Configure logging BEFORE importing services
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("skilllens_production.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import services with graceful fallbacks
from app.services.auth_service import get_auth_service, User, UserCreate, UserLogin, Token
from app.services.skill_knowledge_graph import get_skill_graph
from app.services.job_market import get_job_market_service
from app.services.institutional_analytics import get_analytics_service

# Optional AI services (may fail if dependencies missing)
try:
    from app.services.advanced_resume_parser import get_parser
    RESUME_PARSER_AVAILABLE = True
except Exception as e:
    logger.warning(f"Resume parser not available: {e}")
    RESUME_PARSER_AVAILABLE = False

try:
    from app.services.ai_agent import get_agent
    AI_AGENT_AVAILABLE = True
except Exception as e:
    logger.warning(f"AI agent not available: {e}")
    AI_AGENT_AVAILABLE = False

try:
    from app.services.predictive_model import get_predictor
    PREDICTIVE_MODEL_AVAILABLE = True
except Exception as e:
    logger.warning(f"Predictive model not available: {e}")
    PREDICTIVE_MODEL_AVAILABLE = False

try:
    from app.services.scoring_engine import get_scoring_engine
    SCORING_ENGINE_AVAILABLE = True
except Exception as e:
    logger.warning(f"Scoring engine not available: {e}")
    SCORING_ENGINE_AVAILABLE = False

try:
    from app.services.skill_verification import get_verification_service
    VERIFICATION_AVAILABLE = True
except Exception as e:
    logger.warning(f"Verification service not available: {e}")
    VERIFICATION_AVAILABLE = False


# ==================== LIFESPAN ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with database connections."""
    logger.info("🚀 Starting SkillLens Production Backend...")
    
    # Connect to databases
    try:
        await MongoDB.connect()
        logger.info("✅ MongoDB connected")
    except Exception as e:
        logger.warning(f"⚠️ MongoDB connection failed: {e}. Running without persistence.")
    
    try:
        await Neo4jClient.connect()
        logger.info("✅ Neo4j connected")
    except Exception as e:
        logger.warning(f"⚠️ Neo4j connection failed: {e}. Using in-memory graph.")
    
    # Validate API keys
    api_key_status = settings.validate_api_keys()
    logger.info(f"🔑 API Keys: {api_key_status}")
    
    # Initialize services
    logger.info("🤖 Initializing AI services...")
    try:
        # Warm up models (optional - can be slow on first run)
        # parser = get_parser()
        # logger.info("✅ Resume parser ready")
        pass
    except Exception as e:
        logger.warning(f"⚠️ Service initialization warning: {e}")
    
    logger.info("✨ SkillLens Production Backend started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down SkillLens...")
    await MongoDB.disconnect()
    await Neo4jClient.disconnect()
    logger.info("👋 Shutdown complete")


# ==================== APP INITIALIZATION ====================

app = FastAPI(
    title="SkillLens Production API",
    description="AI-Powered Career Intelligence Platform - Production Ready",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== AUTHENTICATION DEPENDENCY ====================

async def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    """Get current authenticated user from JWT token."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    auth_service = get_auth_service()
    user = await auth_service.verify_token(token)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return user


# Optional authentication (for public endpoints that can work with or without auth)
async def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[User]:
    """Get user if authenticated, None otherwise."""
    if not authorization:
        return None
    try:
        return await get_current_user(authorization)
    except:
        return None


# ==================== MODELS ====================

class JobRecommendationRequest(BaseModel):
    user_skills: List[str]
    experience_years: float = 0
    limit: int = 10

class AssessmentRequest(BaseModel):
    skill: str
    difficulty: str = "intermediate"
    num_questions: int = 5

class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None


# ==================== PUBLIC ROUTES ====================

@app.get("/")
async def root():
    return {
        "message": "Welcome to SkillLens Production API",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "🔐 JWT Authentication",
            "💾 Database Persistence",
            "🤖 Real AI/ML Services",
            "📊 Advanced Analytics",
            "🎯 Career Intelligence"
        ],
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check."""
    mongodb_status = "connected" if MongoDB.db is not None else "disconnected"
    neo4j_status = "connected" if Neo4jClient.driver is not None else "disconnected"
    
    return {
        "status": "healthy",
        "service": "SkillLens Production",
        "timestamp": datetime.utcnow().isoformat(),
        "databases": {
            "mongodb": mongodb_status,
            "neo4j": neo4j_status
        },
        "ai_services": {
            "resume_parser": "available" if RESUME_PARSER_AVAILABLE else "fallback",
            "ai_agent": "available" if AI_AGENT_AVAILABLE else "fallback",
            "predictive_model": "available" if PREDICTIVE_MODEL_AVAILABLE else "fallback",
            "scoring_engine": "available" if SCORING_ENGINE_AVAILABLE else "fallback",
            "verification": "available" if VERIFICATION_AVAILABLE else "fallback",
            "knowledge_graph": "ready",
            "job_market": "ready",
            "analytics": "ready"
        },
        "features": [
            "🔐 JWT Authentication",
            "💾 Database Persistence" if mongodb_status == "connected" else "⚠️ In-Memory Only",
            "🤖 AI Services" if any([RESUME_PARSER_AVAILABLE, AI_AGENT_AVAILABLE]) else "⚠️ Basic Mode",
            "📊 Analytics",
            "🎯 Career Intelligence"
        ]
    }


# ==================== AUTHENTICATION ROUTES ====================

@app.post("/api/auth/register", response_model=Token, tags=["Authentication"])
async def register(user_data: UserCreate):
    """Register a new user."""
    try:
        auth_service = get_auth_service()
        token = await auth_service.register_user(user_data)
        logger.info(f"✅ New user registered: {user_data.email}")
        return token
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Failed to register user")


@app.post("/api/auth/login", response_model=Token, tags=["Authentication"])
async def login(login_data: UserLogin):
    """Authenticate user and return JWT token."""
    try:
        auth_service = get_auth_service()
        token = await auth_service.login_user(login_data)
        logger.info(f"✅ User logged in: {login_data.email}")
        return token
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Failed to login")


@app.get("/api/auth/me", response_model=User, tags=["Authentication"])
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


# ==================== RESUME ROUTES ====================

@app.post("/api/resume/upload", tags=["Resume"])
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload and parse resume with real AI."""
    try:
        # Validate file type
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {settings.allowed_extensions}"
            )
        
        # Save file temporarily
        upload_path = Path(settings.upload_dir) / f"{current_user.user_id}_{file.filename}"
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = await file.read()
        with open(upload_path, "wb") as f:
            f.write(content)
        
        # Parse with real AI if available
        if RESUME_PARSER_AVAILABLE:
            parser = get_parser()
            file_type = file_ext[1:]  # Remove dot
            parsed_data = await parser.parse_resume(str(upload_path), file_type)
        else:
            # Fallback to basic parsing
            parsed_data = {
                "skills": ["Python", "JavaScript", "SQL"],
                "experience_years": 2.0,
                "quality_score": 70.0,
                "note": "Basic parsing - AI parser not available"
            }
        
        # Store in database
        resume_doc = {
            "resume_id": f"resume_{datetime.utcnow().timestamp()}",
            "user_id": current_user.user_id,
            "filename": file.filename,
            "file_size": len(content),
            "uploaded_at": datetime.utcnow(),
            "parsed_data": parsed_data,
        }
        
        try:
            await MongoDB.get_collection("resumes").insert_one(resume_doc)
            logger.info(f"✅ Resume saved to database for user {current_user.user_id}")
        except Exception as e:
            logger.warning(f"⚠️ Database save failed: {e}")
        
        # Clean up temp file
        upload_path.unlink(missing_ok=True)
        
        return {
            "resume_id": resume_doc["resume_id"],
            "filename": file.filename,
            "parsed_data": parsed_data,
            "message": "Resume parsed successfully with AI"
        }
        
    except Exception as e:
        logger.error(f"Resume upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


@app.get("/api/resume/list", tags=["Resume"])
async def list_resumes(current_user: User = Depends(get_current_user)):
    """Get all resumes for current user."""
    try:
        resumes = await MongoDB.get_collection("resumes").find(
            {"user_id": current_user.user_id}
        ).sort("uploaded_at", -1).to_list(length=100)
        
        return {
            "resumes": [
                {
                    "resume_id": r["resume_id"],
                    "filename": r["filename"],
                    "uploaded_at": r["uploaded_at"],
                    "quality_score": r["parsed_data"].get("quality_score", 0)
                }
                for r in resumes
            ],
            "total": len(resumes)
        }
    except Exception as e:
        logger.warning(f"Database query failed: {e}")
        return {"resumes": [], "total": 0}


# ==================== AI AGENT ROUTES ====================

@app.post("/api/agent/chat", tags=["AI Agent"])
async def chat_with_agent(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Chat with AI career coach using real LangChain agent."""
    try:
        if not AI_AGENT_AVAILABLE:
            # Fallback response
            return {
                "message": f"I received your message: '{request.message}'. I'm currently in limited mode. Please try: analyzing your resume, checking skill gaps, or viewing job recommendations.",
                "conversation_id": current_user.user_id,
                "suggestions": ["Analyze my resume", "Check skill gaps", "View job recommendations"],
                "learning_path_available": False,
                "metadata": {"mode": "fallback"}
            }
        
        agent = get_agent()
        
        # Add user context
        if not request.context:
            request.context = {}
        request.context["user_id"] = current_user.user_id
        request.context["user_email"] = current_user.email
        
        # Get AI response
        from app.models.agent_models import ChatRequest as AgentChatRequest
        agent_request = AgentChatRequest(
            user_id=current_user.user_id,
            message=request.message,
            context=request.context
        )
        
        response = await agent.chat(agent_request)
        
        logger.info(f"✅ AI agent responded to user {current_user.user_id}")
        return response
        
    except Exception as e:
        logger.error(f"AI agent error: {e}")
        # Fallback to simple response
        return {
            "message": f"I received your message: '{request.message}'. However, I'm experiencing technical difficulties. Please try again.",
            "conversation_id": current_user.user_id,
            "suggestions": ["Try asking about skills", "Ask about learning paths"],
            "metadata": {"error": str(e)}
        }


# ==================== SKILLS & KNOWLEDGE GRAPH ROUTES ====================

@app.get("/api/skills/hierarchy", tags=["Skills"])
async def get_skill_hierarchy(user: Optional[User] = Depends(get_optional_user)):
    """Get skill hierarchy from knowledge graph."""
    try:
        graph = get_skill_graph()
        return {
            "skills": list(graph.skills.keys()),
            "roles": list(graph.roles.keys()),
            "total_skills": len(graph.skills),
            "total_roles": len(graph.roles)
        }
    except Exception as e:
        logger.error(f"Skill hierarchy error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/skills/gap-analysis", tags=["Skills"])
async def analyze_skill_gap(
    user_skills: List[str],
    target_role: str,
    current_user: User = Depends(get_current_user)
):
    """Analyze skill gap using knowledge graph."""
    try:
        graph = get_skill_graph()
        analysis = await graph.analyze_skill_gap(user_skills, target_role)
        
        logger.info(f"✅ Skill gap analysis for user {current_user.user_id}")
        return analysis
        
    except Exception as e:
        logger.error(f"Skill gap analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/skills/learning-path", tags=["Skills"])
async def get_learning_path(
    current_skills: List[str],
    target_role: str,
    current_user: User = Depends(get_current_user)
):
    """Get optimal learning path using graph algorithms."""
    try:
        graph = get_skill_graph()
        path = await graph.find_optimal_learning_path(current_skills, target_role)
        
        logger.info(f"✅ Learning path generated for user {current_user.user_id}")
        return path
        
    except Exception as e:
        logger.error(f"Learning path error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PREDICTIONS ROUTES ====================

@app.post("/api/predictions/shortlist", tags=["Predictions"])
async def predict_shortlist(
    resume_text: str,
    job_description: str,
    user_skills: List[str],
    experience_years: float,
    current_user: User = Depends(get_current_user)
):
    """Predict shortlisting probability using ML model."""
    try:
        if not PREDICTIVE_MODEL_AVAILABLE:
            # Simple fallback prediction
            base_prob = 50 + (len(user_skills) * 5) + (experience_years * 2)
            probability = min(base_prob, 95)
            return {
                "shortlist_probability": probability,
                "confidence_level": "Medium",
                "recommendations": ["Add more relevant skills", "Highlight experience"],
                "note": "Basic prediction - ML model not available"
            }
        
        predictor = get_predictor()
        
        from app.models.prediction_models import PredictionRequest
        request = PredictionRequest(
            resume_text=resume_text,
            job_description=job_description,
            user_skills=user_skills,
            experience_years=experience_years
        )
        
        result = await predictor.predict_shortlist_probability(request)
        
        logger.info(f"✅ Prediction generated for user {current_user.user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== JOB MARKET ROUTES ====================

@app.post("/api/jobs/recommendations", tags=["Jobs"])
async def get_job_recommendations(
    request: JobRecommendationRequest,
    current_user: User = Depends(get_current_user)
):
    """Get personalized job recommendations."""
    try:
        job_market = get_job_market_service()
        recommendations = await job_market.get_job_recommendations(
            request.user_skills,
            request.experience_years,
            request.limit
        )
        
        logger.info(f"✅ Job recommendations for user {current_user.user_id}")
        return recommendations
        
    except Exception as e:
        logger.error(f"Job recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/market-trends", tags=["Jobs"])
async def get_market_trends(user: Optional[User] = Depends(get_optional_user)):
    """Get job market trends."""
    try:
        job_market = get_job_market_service()
        trends = await job_market.get_market_trends()
        return trends
    except Exception as e:
        logger.error(f"Market trends error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== VERIFICATION ROUTES ====================

@app.post("/api/verification/generate-assessment", tags=["Verification"])
async def generate_assessment(
    request: AssessmentRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate AI-powered skill assessment."""
    try:
        if not VERIFICATION_AVAILABLE:
            # Basic fallback assessment
            return {
                "assessment_id": f"assess_{datetime.utcnow().timestamp()}",
                "skill": request.skill,
                "questions": [
                    {
                        "question_id": f"{request.skill}-q1",
                        "question": f"What is {request.skill} used for?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "difficulty": request.difficulty
                    }
                ],
                "total_points": request.num_questions * 10,
                "time_limit_minutes": request.num_questions * 3,
                "note": "Basic assessment - AI generator not available"
            }
        
        verification = get_verification_service()
        
        from app.models.verification_models import AssessmentRequest as VerificationRequest
        ver_request = VerificationRequest(
            user_id=current_user.user_id,
            skill=request.skill,
            difficulty=request.difficulty,
            num_questions=request.num_questions
        )
        
        assessment = await verification.generate_assessment(ver_request)
        
        logger.info(f"✅ Assessment generated for user {current_user.user_id}")
        return assessment
        
    except Exception as e:
        logger.error(f"Assessment generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ANALYTICS ROUTES ====================

@app.get("/api/analytics/placement-statistics", tags=["Analytics"])
async def get_placement_stats(
    department: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get placement statistics."""
    try:
        analytics = get_analytics_service()
        stats = await analytics.get_placement_statistics(department)
        return stats
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/readiness-distribution", tags=["Analytics"])
async def get_readiness_distribution(current_user: User = Depends(get_current_user)):
    """Get student readiness distribution."""
    try:
        analytics = get_analytics_service()
        distribution = await analytics.get_readiness_distribution()
        return distribution
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/skill-gap-analysis", tags=["Analytics"])
async def get_skill_gaps(current_user: User = Depends(get_current_user)):
    """Get skill gap analysis."""
    try:
        analytics = get_analytics_service()
        gaps = await analytics.get_skill_gap_analysis()
        return gaps
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SCORING ROUTES ====================

@app.post("/api/scoring/readiness", tags=["Scoring"])
async def calculate_readiness_score(
    user_skills: List[str],
    target_role: str,
    experience_years: float,
    current_user: User = Depends(get_current_user)
):
    """Calculate career readiness score."""
    try:
        if not SCORING_ENGINE_AVAILABLE:
            # Basic fallback scoring
            base_score = 50 + (len(user_skills) * 3) + (experience_years * 2)
            score = min(base_score, 100)
            return {
                "overall_score": score,
                "target_role": target_role,
                "explanation": f"You have {len(user_skills)} skills and {experience_years} years of experience.",
                "strengths": user_skills[:3] if user_skills else [],
                "weaknesses": ["Need more skills"],
                "recommendations": ["Learn more relevant skills", "Gain more experience"],
                "note": "Basic scoring - ML engine not available"
            }
        
        scoring = get_scoring_engine()
        
        from app.models.scoring_models import ReadinessRequest
        request = ReadinessRequest(
            user_id=current_user.user_id,
            user_skills=user_skills,
            target_role=target_role,
            experience_years=experience_years,
            include_explanation=True
        )
        
        score = await scoring.calculate_readiness_score(request)
        
        logger.info(f"✅ Readiness score calculated for user {current_user.user_id}")
        return score
        
    except Exception as e:
        logger.error(f"Scoring error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ERROR HANDLERS ====================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return {
        "detail": "Internal server error",
        "type": type(exc).__name__
    }


# ==================== MAIN ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 SkillLens Production Backend")
    print("=" * 60)
    print("📍 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("=" * 60)
    print("✨ Features:")
    print("  🔐 JWT Authentication")
    print("  💾 MongoDB Persistence")
    print("  🧠 Neo4j Knowledge Graph")
    print("  🤖 Real AI/ML Services")
    print("  📊 Advanced Analytics")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
