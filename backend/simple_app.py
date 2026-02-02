"""
Simplified FastAPI backend for demo (works without databases)
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
from pathlib import Path

# Set Keras environment
os.environ['TF_USE_LEGACY_KERAS'] = '1'

from sentence_transformers import SentenceTransformer
from app.services.advanced_resume_parser import get_parser
from app.services.skill_knowledge_graph import get_skill_graph

app = FastAPI(title="SkillLens API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
model = None
resume_parser = None
skill_graph = None

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.on_event("startup")
async def startup():
    global model, resume_parser, skill_graph
    print("Loading Sentence-BERT model...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    print("Model loaded!")
    
    print("Loading Advanced Resume Parser...")
    resume_parser = get_parser()
    print("Resume parser ready!")
    
    print("Initializing Skill Knowledge Graph...")
    skill_graph = get_skill_graph()
    print(f"Knowledge graph ready with {len(skill_graph.skills)} skills!")

# Models
class SkillGapRequest(BaseModel):
    user_skills: List[str]
    target_role: str

class ReadinessRequest(BaseModel):
    user_id: str
    target_role: str
    skills: List[str]
    experience_years: int
    num_projects: int

# Role requirements
ROLE_REQUIREMENTS = {
    "Data Engineer": {
        "skills": ["Python", "SQL", "Apache Spark", "ETL", "Data Modeling", "AWS", "Docker", "Kafka", "Airflow"],
        "tools": ["Docker", "AWS", "Kafka"]
    },
    "Software Engineer": {
        "skills": ["Python", "Java", "Data Structures", "Algorithms", "Git", "Testing", "CI/CD"],
        "tools": ["Git", "Docker", "Jenkins"]
    },
    "Full Stack Developer": {
        "skills": ["JavaScript", "React", "Node.js", "SQL", "HTML", "CSS", "REST APIs", "MongoDB"],
        "tools": ["Git", "Docker", "VS Code"]
    }
}

@app.get("/")
async def root():
    return {"message": "SkillLens API", "status": "running"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "parser_loaded": resume_parser is not None
    }

@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and parse resume with advanced NLP
    Returns: Semantic embeddings, extracted skills, entities, quality score
    """
    if not resume_parser:
        raise HTTPException(status_code=500, detail="Resume parser not loaded")
    
    # Validate file type
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in ['pdf', 'docx', 'doc']:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
    
    # Save uploaded file
    file_path = UPLOAD_DIR / f"temp_{file.filename}"
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse resume
        parsed_data = await resume_parser.parse_resume(str(file_path), file_ext)
        
        # Clean up
        file_path.unlink()
        
        return {
            "success": True,
            "filename": file.filename,
            "parsed_data": {
                "skills": parsed_data['skills'],
                "experience": parsed_data['experience'],
                "education": parsed_data['education'],
                "projects": parsed_data['projects'],
                "quality_score": parsed_data['quality_score'],
                "embedding_dimension": parsed_data['embedding_dimension'],
                "entities": parsed_data['entities']
            },
            "insights": {
                "total_skills": len(parsed_data['skills']),
                "experience_count": len(parsed_data['experience']),
                "project_count": len(parsed_data['projects']),
                "resume_quality": "Excellent" if parsed_data['quality_score'] >= 80 else "Good" if parsed_data['quality_score'] >= 60 else "Needs Improvement"
            }
        }
    except Exception as e:
        # Clean up on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")

@app.post("/api/skills/gap-analysis")
async def analyze_gap(request: SkillGapRequest):
    requirements = ROLE_REQUIREMENTS.get(request.target_role, ROLE_REQUIREMENTS["Data Engineer"])
    
    matched = [s for s in request.user_skills if s in requirements["skills"]]
    missing = [s for s in requirements["skills"] if s not in request.user_skills]
    
    match_rate = (len(matched) / len(requirements["skills"])) * 100 if requirements["skills"] else 0
    
    return {
        "target_role": request.target_role,
        "matched_skills": matched,
        "missing_skills": missing,
        "match_rate": match_rate,
        "required_skills": requirements["skills"]
    }

@app.post("/api/scoring/readiness")
async def calculate_readiness(request: ReadinessRequest):
    # Get requirements
    requirements = ROLE_REQUIREMENTS.get(request.target_role, ROLE_REQUIREMENTS["Data Engineer"])
    
    # Calculate scores
    matched = [s for s in request.skills if s in requirements["skills"]]
    tech_score = (len(matched) / len(requirements["skills"])) * 100 if requirements["skills"] else 0
    exp_score = min((request.experience_years / 5) * 100, 100)
    proj_score = min((request.num_projects / 3) * 100, 100)
    tool_score = 75.0
    
    # Overall score
    overall = (
        tech_score * 0.40 +
        exp_score * 0.25 +
        proj_score * 0.20 +
        tool_score * 0.15
    )
    
    # Generate explanation
    level = "excellent" if overall >= 75 else "good" if overall >= 60 else "developing"
    
    explanation = f"""Your readiness for {request.target_role} is {level} at {overall:.1f}%.

STRENGTHS:
- Strong foundation in {', '.join(matched[:3]) if matched else 'building skills'}
- {request.experience_years} years of experience
- {request.num_projects} projects completed

AREAS FOR IMPROVEMENT:
- Learn {', '.join([s for s in requirements["skills"] if s not in request.skills][:2])} to meet core requirements
- Build more projects showcasing your skills
- Gain hands-on experience with industry tools

RECOMMENDATION:
Focus on the missing skills and build projects that demonstrate your capabilities in {request.target_role}.
"""
    
    return {
        "overall_score": round(overall, 1),
        "target_role": request.target_role,
        "factors": [
            {"factor_name": "Technical Skills", "weight": 0.4, "score": tech_score, "contribution": tech_score * 0.4},
            {"factor_name": "Experience", "weight": 0.25, "score": exp_score, "contribution": exp_score * 0.25},
            {"factor_name": "Project Portfolio", "weight": 0.2, "score": proj_score, "contribution": proj_score * 0.2},
            {"factor_name": "Tool Proficiency", "weight": 0.15, "score": tool_score, "contribution": tool_score * 0.15}
        ],
        "explanation": explanation,
        "strengths": ["Technical Skills" if tech_score >= 70 else "Experience"],
        "weaknesses": ["Technical Skills" if tech_score < 50 else "Projects"],
        "recommendations": [f"Learn {s}" for s in requirements["skills"] if s not in request.skills][:3]
    }

@app.post("/api/resume/analyze")
async def analyze_resume(text: str):
    """Analyze resume text"""
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    # Generate embeddings
    embeddings = model.encode(text)
    
    # Simple skill extraction (you can enhance this)
    common_skills = ["Python", "Java", "SQL", "Docker", "AWS", "React", "Node.js", "MongoDB", "Git"]
    found_skills = [skill for skill in common_skills if skill.lower() in text.lower()]
    
    return {
        "embeddings_dimension": len(embeddings),
        "skills_found": found_skills,
        "embedding_sample": embeddings[:5].tolist()
    }

# Knowledge Graph Endpoints

class LearningPathRequest(BaseModel):
    current_skills: List[str]
    target_role: str

class SkillDependencyRequest(BaseModel):
    skill: str

@app.post("/api/skills/learning-path")
async def get_learning_path(request: LearningPathRequest):
    """
    Generate optimal learning path using graph algorithms
    Uses modified Dijkstra's algorithm considering dependencies
    """
    if not skill_graph:
        raise HTTPException(status_code=500, detail="Knowledge graph not loaded")
    
    result = skill_graph.find_optimal_learning_path(
        request.current_skills,
        request.target_role
    )
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@app.post("/api/skills/dependencies")
async def get_skill_dependencies(request: SkillDependencyRequest):
    """Get all dependencies for a specific skill"""
    if not skill_graph:
        raise HTTPException(status_code=500, detail="Knowledge graph not loaded")
    
    result = skill_graph.get_skill_dependencies(request.skill)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@app.post("/api/skills/gap-analysis-advanced")
async def analyze_gap_advanced(request: SkillGapRequest):
    """
    Advanced skill gap analysis using knowledge graph
    Provides categorized skills and readiness level
    """
    if not skill_graph:
        raise HTTPException(status_code=500, detail="Knowledge graph not loaded")
    
    result = skill_graph.analyze_skill_gap(
        request.user_skills,
        request.target_role
    )
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@app.get("/api/skills/roles")
async def get_available_roles():
    """Get all available roles in the knowledge graph"""
    if not skill_graph:
        raise HTTPException(status_code=500, detail="Knowledge graph not loaded")
    
    return {
        "roles": list(skill_graph.roles.keys()),
        "total_skills": len(skill_graph.skills)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
