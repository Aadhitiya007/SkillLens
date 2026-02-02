# SkillLens Production Deployment Guide

## Overview

The production backend (`app_production.py`) is now ready with:

✅ **Database Integration** - MongoDB for persistence, Neo4j for knowledge graph  
✅ **JWT Authentication** - Secure user authentication and authorization  
✅ **Real AI Services** - Sentence-BERT, LangChain, ML models  
✅ **Graceful Fallbacks** - Works even if some AI dependencies are missing  
✅ **Production Features** - Error handling, logging, validation  

---

## Quick Start

### Option 1: Run Production App (Recommended)

```bash
cd backend
python start_production.py
```

### Option 2: Run with Uvicorn

```bash
cd backend
uvicorn app_production:app --host 0.0.0.0 --port 8000
```

### Option 3: Run Enhanced Demo (No Database)

```bash
cd backend
python app_enhanced.py
```

---

## Features Comparison

| Feature | app_enhanced.py | app_production.py |
|---------|-----------------|-------------------|
| **Authentication** | ❌ None | ✅ JWT |
| **Database** | ❌ In-memory | ✅ MongoDB + Neo4j |
| **Resume Parser** | ❌ Mock | ✅ Sentence-BERT |
| **AI Agent** | ❌ Keywords | ✅ LangChain |
| **Predictions** | ❌ Simple formula | ✅ ML Model |
| **Persistence** | ❌ Lost on restart | ✅ Saved to DB |
| **Fallbacks** | N/A | ✅ Graceful degradation |

---

## API Endpoints

### Authentication

```bash
# Register
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "role": "student"
}

# Login
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

# Get current user
GET /api/auth/me
Headers: Authorization: Bearer <token>
```

### Resume Analysis

```bash
# Upload resume (requires auth)
POST /api/resume/upload
Headers: Authorization: Bearer <token>
Body: multipart/form-data with file

# List resumes
GET /api/resume/list
Headers: Authorization: Bearer <token>
```

### AI Agent

```bash
# Chat with AI
POST /api/agent/chat
Headers: Authorization: Bearer <token>
{
  "message": "How do I become a full stack developer?",
  "context": {}
}
```

### Skills & Knowledge Graph

```bash
# Get skill hierarchy
GET /api/skills/hierarchy

# Analyze skill gap
POST /api/skills/gap-analysis
Headers: Authorization: Bearer <token>
{
  "user_skills": ["Python", "SQL"],
  "target_role": "Data Engineer"
}

# Get learning path
POST /api/skills/learning-path
Headers: Authorization: Bearer <token>
{
  "current_skills": ["Python"],
  "target_role": "ML Engineer"
}
```

### Predictions

```bash
# Predict shortlist probability
POST /api/predictions/shortlist
Headers: Authorization: Bearer <token>
{
  "resume_text": "...",
  "job_description": "...",
  "user_skills": ["Python", "ML"],
  "experience_years": 2
}
```

### Job Market

```bash
# Get job recommendations
POST /api/jobs/recommendations
Headers: Authorization: Bearer <token>
{
  "user_skills": ["Python", "React"],
  "experience_years": 2,
  "limit": 10
}

# Get market trends
GET /api/jobs/market-trends
```

### Verification

```bash
# Generate assessment
POST /api/verification/generate-assessment
Headers: Authorization: Bearer <token>
{
  "skill": "Python",
  "difficulty": "intermediate",
  "num_questions": 5
}
```

### Analytics

```bash
# Get placement statistics
GET /api/analytics/placement-statistics?department=CS
Headers: Authorization: Bearer <token>

# Get readiness distribution
GET /api/analytics/readiness-distribution
Headers: Authorization: Bearer <token>

# Get skill gaps
GET /api/analytics/skill-gap-analysis
Headers: Authorization: Bearer <token>
```

### Scoring

```bash
# Calculate readiness score
POST /api/scoring/readiness
Headers: Authorization: Bearer <token>
{
  "user_skills": ["Python", "SQL", "Docker"],
  "target_role": "DevOps Engineer",
  "experience_years": 3
}
```

---

## Database Setup

### MongoDB (Required for Persistence)

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or install locally
# Windows: Download from mongodb.com
# Mac: brew install mongodb-community
# Linux: sudo apt install mongodb
```

### Neo4j (Optional - Knowledge Graph)

```bash
# Using Docker
docker run -d -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  --name neo4j neo4j:latest

# Access browser: http://localhost:7474
```

### Environment Variables

Create `.env` file:

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017/skilllens
MONGODB_DB_NAME=skilllens

# Neo4j (optional)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# JWT
JWT_SECRET=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# OpenAI (optional - for AI agent)
OPENAI_API_KEY=sk-...

# Hugging Face (optional - for resume parser)
HUGGINGFACE_API_KEY=hf_...

# SerpAPI (optional - for job intelligence)
SERPAPI_KEY=...
```

---

## Service Availability

The production app works in **degraded mode** if some services are unavailable:

### Full Mode (All Dependencies)
- ✅ Sentence-BERT resume parsing
- ✅ LangChain AI agent
- ✅ ML predictive models
- ✅ Advanced scoring engine
- ✅ AI-generated assessments

### Fallback Mode (Missing Dependencies)
- ⚠️ Basic resume parsing (regex-based)
- ⚠️ Simple AI responses (keyword-based)
- ⚠️ Formula-based predictions
- ⚠️ Basic scoring
- ⚠️ Template assessments

**Check service status:**
```bash
curl http://localhost:8000/health
```

---

## Testing

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. Register User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### 3. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

Save the `access_token` from the response.

### 4. Upload Resume

```bash
curl -X POST http://localhost:8000/api/resume/upload \
  -H "Authorization: Bearer <your-token>" \
  -F "file=@/path/to/resume.pdf"
```

### 5. Chat with AI

```bash
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I become a data scientist?"
  }'
```

---

## Production Deployment

### Using Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "start_production.py"]
```

```bash
# Build
docker build -t skilllens-backend .

# Run
docker run -d -p 8000:8000 \
  -e MONGODB_URI=mongodb://host.docker.internal:27017/skilllens \
  -e OPENAI_API_KEY=sk-... \
  skilllens-backend
```

### Using Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URI=mongodb://mongodb:27017/skilllens
      - NEO4J_URI=bolt://neo4j:7687
    depends_on:
      - mongodb
      - neo4j

  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

  neo4j:
    image: neo4j:latest
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
    volumes:
      - neo4j_data:/data

volumes:
  mongodb_data:
  neo4j_data:
```

---

## Troubleshooting

### Import Errors

If you see import errors for AI services, the app will run in fallback mode. To enable full features:

```bash
pip install sentence-transformers transformers langchain langchain-openai
```

### Database Connection Failed

The app works without databases but data won't persist. To enable persistence:

1. Start MongoDB: `docker run -d -p 27017:27017 mongo`
2. Update `.env` with connection string
3. Restart app

### API Key Issues

AI features require API keys. Without them, basic fallbacks are used:

- **OpenAI**: For AI agent chat
- **Hugging Face**: For resume parsing (can work offline too)
- **SerpAPI**: For job market data (optional)

---

## Monitoring

### Logs

Logs are written to:
- Console (stdout)
- File: `skilllens_production.log`

### Health Endpoint

```bash
# Check service health
curl http://localhost:8000/health

# Response shows:
# - Database connection status
# - AI service availability
# - Feature status
```

---

## Security

### Production Checklist

- [ ] Change `JWT_SECRET` to a strong random value
- [ ] Use HTTPS in production
- [ ] Enable rate limiting (add middleware)
- [ ] Set up proper CORS origins
- [ ] Use environment variables for secrets
- [ ] Enable database authentication
- [ ] Set up monitoring and alerting
- [ ] Regular security updates

---

## Next Steps

1. **Start the app**: `python start_production.py`
2. **Test endpoints**: Use the API documentation at `http://localhost:8000/docs`
3. **Register a user**: Create your first account
4. **Upload a resume**: Test the AI parsing
5. **Chat with AI**: Try the career coach
6. **Check analytics**: View the dashboards

---

## Support

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Logs**: Check `skilllens_production.log`

**Congratulations! Your production-ready SkillLens backend is now running! 🚀**
