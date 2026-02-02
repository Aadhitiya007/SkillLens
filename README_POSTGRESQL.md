# 🔷 SkillLens - PostgreSQL Migration Complete

**AI-Powered Career Intelligence & Workforce Readiness Platform**

> **Latest Update**: Successfully migrated from MongoDB to PostgreSQL for better data integrity, simpler deployment, and more powerful analytics.

---

## 🎯 What's New - PostgreSQL Migration

### ✅ Completed Features
- **Authentication System**: User registration, login, JWT tokens, bcrypt password hashing
- **Resume Management**: Upload, parse, store resumes with JSONB for flexible data
- **Career Readiness Scoring**: Multi-factor scoring with explainable AI
- **PostgreSQL Database**: 13 tables with proper relationships and constraints
- **Docker Support**: One-command deployment with Docker Compose

### 🚀 Quick Start (Updated)

#### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd SkilLens

# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# Access the application
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - PostgreSQL: localhost:5432
# - Neo4j: http://localhost:7474
```

#### Option 2: Local Development

```bash
# 1. Install PostgreSQL 16
# Download from: https://www.postgresql.org/download/

# 2. Create database
psql -U postgres
CREATE DATABASE skilllens;
CREATE USER skilllens WITH PASSWORD 'skilllens';
GRANT ALL PRIVILEGES ON DATABASE skilllens TO skilllens;
\q

# 3. Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Configure environment
cp ../.env.example ../.env
# Edit .env with your settings:
# DATABASE_URL=postgresql+asyncpg://skilllens:skilllens@localhost:5432/skilllens

# 5. Initialize database
python scripts/init_db.py --seed

# 6. Run backend
uvicorn app.main:app --reload

# 7. Access API docs
open http://localhost:8000/docs
```

---

## 📚 API Endpoints (Working)

### Authentication (`/api/auth`)

**Register User**
```bash
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "securepass123",
  "full_name": "John Doe",
  "role": "student"
}
```

**Login**
```bash
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Get Current User**
```bash
GET /api/auth/me
Headers: Authorization: Bearer <token>
```

### Resume Management (`/api/resume`)

**Upload Resume**
```bash
POST /api/resume/upload
Content-Type: multipart/form-data
file: <resume.pdf>
```

**Get User Resume**
```bash
GET /api/resume/{user_id}
```

**List All Resumes**
```bash
GET /api/resume/?skip=0&limit=10
```

**Delete Resume**
```bash
DELETE /api/resume/{resume_id}
```

### Career Readiness Scoring (`/api/scoring`)

**Calculate Readiness Score**
```bash
POST /api/scoring/readiness
{
  "user_id": "uuid-or-demo_user",
  "target_role": "Data Engineer"
}
```

**Get Score History**
```bash
GET /api/scoring/history/{user_id}?target_role=Data%20Engineer&limit=10
```

**Get Latest Explanation**
```bash
GET /api/scoring/explanation/{user_id}
```

---

## 🗄️ Database Schema

### PostgreSQL Tables

| Table | Purpose | Key Features |
|-------|---------|--------------|
| `users` | User accounts | JWT auth, roles, profiles |
| `resumes` | Resume files | JSONB for parsed data |
| `readiness_scores` | Career assessments | Multi-factor scoring |
| `assessments` | Skill tests | JSONB for questions |
| `assessment_results` | Test scores | Performance tracking |
| `learning_plans` | Learning paths | Personalized roadmaps |
| `learning_progress` | Progress tracking | Skill completion |
| `job_listings` | Cached jobs | External API data |
| `predictions` | ML predictions | Shortlisting probability |
| `conversations` | AI agent chat | Session history |
| `skills` | Skill catalog | Optional (Neo4j alternative) |
| `skill_prerequisites` | Dependencies | Optional graph fallback |

### Key Features
- **UUID Primary Keys**: Better security
- **JSONB Columns**: Flexible data storage
- **Foreign Keys**: Data integrity
- **Automatic Timestamps**: Audit trail
- **Indexes**: Optimized queries
- **Cascading Deletes**: Clean data management

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 16 + Neo4j (optional)
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **NLP**: Hugging Face Sentence-BERT
- **LLM**: OpenAI GPT-3.5 (with fallbacks)
- **Agent**: LangChain
- **ML**: Scikit-learn, TensorFlow/PyTorch

### Frontend
- **Framework**: Next.js 14 (React 18)
- **Styling**: TailwindCSS
- **Charts**: Recharts
- **Graph Viz**: D3.js

### Infrastructure
- **Containerization**: Docker
- **Database**: PostgreSQL 16, Neo4j 5.16
- **Deployment**: Render / AWS / DigitalOcean

---

## 🔧 Configuration

### Environment Variables

```bash
# PostgreSQL Database
DATABASE_URL=postgresql+asyncpg://skilllens:skilllens@localhost:5432/skilllens

# Neo4j Graph Database (Optional)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=skilllens123

# JWT Authentication
JWT_SECRET=your-super-secret-jwt-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# OpenAI (Optional - has fallbacks)
OPENAI_API_KEY=your_openai_key

# Hugging Face
HUGGINGFACE_API_KEY=your_hf_key

# SerpAPI (Optional)
SERPAPI_KEY=your_serpapi_key

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

---

## 📊 Features

### Core Modules

1. **Resume & Profile Intelligence** ✅
   - Semantic skill extraction using Sentence-BERT
   - PDF/DOCX parsing
   - JSONB storage for flexible data

2. **Authentication & Authorization** ✅
   - JWT-based authentication
   - Role-based access control (student, admin, faculty, placement_cell)
   - Bcrypt password hashing

3. **Explainable Career Readiness Scoring** ✅
   - Multi-factor scoring (skills, experience, projects, tools)
   - GPT-powered explanations (with fallbacks)
   - Score history tracking
   - Personalized recommendations

4. **Skill Ontology & Knowledge Graph** 🔄
   - Neo4j-based skill hierarchy (optional)
   - PostgreSQL fallback with skill prerequisites
   - Dependency detection

5. **Adaptive Learning Agent** ⏳
   - LangChain-based agent
   - Dynamic learning path generation
   - Progress tracking

6. **Skill Verification Engine** ⏳
   - AI-generated assessments
   - Confidence scoring
   - Performance analytics

7. **Job Market Intelligence** ⏳
   - Real-time job data (SerpAPI)
   - Trend analysis
   - Shortlisting probability

8. **Institutional Analytics** ✅
   - Department-wise analytics
   - Placement tracking
   - Skill gap heatmaps

---

## 🧪 Testing

### Manual Testing

```bash
# Visit API documentation
open http://localhost:8000/docs

# Test authentication
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","full_name":"Test User","role":"student"}'

# Test resume upload
curl -X POST http://localhost:8000/api/resume/upload \
  -F "file=@sample_resume.pdf"

# Test scoring
curl -X POST http://localhost:8000/api/scoring/readiness \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo_user","target_role":"Data Engineer"}'
```

### Database Verification

```bash
# Connect to PostgreSQL
docker exec -it skilllens-postgres psql -U skilllens

# Or locally
psql -U skilllens -d skilllens

# Check data
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM resumes;
SELECT COUNT(*) FROM readiness_scores;

# View parsed resume data
SELECT filename, parsed_data->'skills' as skills FROM resumes;
```

---

## 🔬 Research Foundation

> [!IMPORTANT]
> **SkillLens is built on empirical research, not assumptions.**

### Research Study

**Title**: "A Study on Resume Preparation Challenges and Skill–Shortlisting Mismatch Among Engineering Students Using AI-Based Career Readiness Analysis"

**Methodology**: Structured survey of 100 engineering students with statistical validation

### Key Findings

| Finding | Impact | SkillLens Solution |
|---------|--------|----------------------|
| **76% don't know rejection reasons** | Cannot improve without feedback | Explainable readiness scores |
| **Only 26% ATS aware** | 5.9x more shortlists (p=0.002) | ATS-aligned analysis |
| **52% don't know required skills** | 7.4x more shortlists (p<0.001) | Skill gap identification |
| **76% feel guidance is generic** | One-size-fits-all fails | Adaptive AI agent |
| **100% want AI-based tool** | Universal demand | Complete platform |

---

## 📈 Migration Status

**Overall Progress: 50% Complete**

### ✅ Completed
- Database schema and ORM models
- Authentication system
- Resume management
- Career readiness scoring
- Docker Compose setup
- API documentation

### 🔄 In Progress
- Skill verification endpoints
- Prediction endpoints
- Job market integration
- AI agent endpoints

### ⏳ Remaining
- Comprehensive testing
- Frontend integration
- Performance optimization
- Production deployment

---

## 🚀 Deployment

### Docker Deployment

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Reset database (CAUTION)
docker-compose down -v
docker-compose up -d
```

### Production Deployment

See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) for detailed instructions on deploying to:
- Render
- AWS
- DigitalOcean
- Heroku

---

## 📝 License

MIT License

---

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines.

---

## 📧 Contact

For questions or support, please open an issue.

---

**Built with ❤️ for career intelligence and workforce readiness**

**Database**: PostgreSQL 16 | **AI**: Sentence-BERT + GPT-3.5 | **Framework**: FastAPI + Next.js
