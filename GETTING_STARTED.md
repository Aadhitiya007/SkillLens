# 🚀 Getting Started with SkillLens

This guide will help you set up and run SkillLens locally.

## Prerequisites

- **Docker & Docker Compose** (recommended)
- **Python 3.11+** (for local development)
- **Node.js 18+** (for frontend)
- **Git**

## Quick Start with Docker (Recommended)

### 1. Clone and Setup

```bash
cd F:\SkilLens
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required API Keys
OPENAI_API_KEY=your_openai_key_here
HUGGINGFACE_API_KEY=your_hf_key_here
SERPAPI_KEY=your_serpapi_key_here

# Database (use defaults for Docker)
MONGODB_URI=mongodb://mongodb:27017/skilllens
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=skilllens_neo4j_password

# JWT Secret (generate a random string)
JWT_SECRET=your-super-secret-jwt-key-change-this
```

### 3. Get Free API Keys

#### OpenAI (GPT-3.5)
1. Visit https://platform.openai.com/
2. Sign up for an account
3. Go to API Keys section
4. Create a new API key
5. **Note**: New accounts get free credits

#### Hugging Face
1. Visit https://huggingface.co/
2. Sign up for an account
3. Go to Settings → Access Tokens
4. Create a new token
5. **Note**: Free tier available

#### SerpAPI (Optional for Job Intelligence)
1. Visit https://serpapi.com/
2. Sign up for an account
3. Get your API key from dashboard
4. **Note**: 100 free searches/month

### 4. Start All Services

```bash
docker-compose up --build
```

This will start:
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **MongoDB**: localhost:27017
- **Neo4j Browser**: http://localhost:7474

### 5. Initialize Skill Knowledge Graph

Once the services are running, initialize the Neo4j skill graph:

```bash
# In a new terminal
docker exec -it skilllens-backend python scripts/init_skill_graph.py
```

Or use the API endpoint:
```bash
curl -X POST http://localhost:8000/api/skills/initialize
```

### 6. Access the Application

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474 (username: `neo4j`, password: `skilllens_neo4j_password`)

## Local Development (Without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Make sure MongoDB and Neo4j are running locally
# Update .env with local connection strings

# Run backend
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## Testing the Application

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. Upload a Resume

```bash
curl -X POST http://localhost:8000/api/resume/upload \
  -F "file=@path/to/your/resume.pdf" \
  -F "user_id=demo_user"
```

### 3. Get Skill Hierarchy

```bash
curl http://localhost:8000/api/skills/hierarchy
```

### 4. Analyze Skill Gap

```bash
curl -X POST http://localhost:8000/api/skills/gap-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "user_skills": ["Python", "SQL"],
    "target_role": "Data Engineer"
  }'
```

### 5. Calculate Readiness Score

```bash
curl -X POST http://localhost:8000/api/scoring/readiness \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "target_role": "Data Engineer",
    "include_explanation": true
  }'
```

## Using the Web Interface

1. Open http://localhost:3000
2. Click "Get Started" or "Start Your Assessment"
3. Upload your resume (PDF or DOCX)
4. View your skill analysis
5. Check your career readiness score
6. Get personalized recommendations

## Viewing the Knowledge Graph

1. Open http://localhost:7474
2. Login with:
   - Username: `neo4j`
   - Password: `skilllens_neo4j_password`
3. Run Cypher queries:

```cypher
// View all skills
MATCH (s:Skill) RETURN s

// View skill hierarchy
MATCH (s:Skill)-[r:REQUIRES]->(dep:Skill)
RETURN s, r, dep

// View role requirements
MATCH (r:Role)-[:NEEDS]->(s:Skill)
WHERE r.title = "Data Engineer"
RETURN r, s
```

## Troubleshooting

### Docker Issues

**Services won't start:**
```bash
# Clean up and rebuild
docker-compose down -v
docker-compose up --build
```

**Port conflicts:**
- Check if ports 3000, 8000, 7474, 7687, 27017 are available
- Modify ports in `docker-compose.yml` if needed

### API Key Issues

**OpenAI errors:**
- Verify your API key is correct
- Check you have available credits
- Ensure no extra spaces in `.env` file

**Hugging Face model loading:**
- First run may take time to download models
- Check internet connection
- Models are cached after first download

### Database Connection Issues

**MongoDB:**
```bash
# Check if MongoDB is running
docker ps | grep mongodb

# View logs
docker logs skilllens-mongodb
```

**Neo4j:**
```bash
# Check if Neo4j is running
docker ps | grep neo4j

# View logs
docker logs skilllens-neo4j
```

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Upload your resume**: Test the resume parsing
3. **Try different roles**: Analyze gaps for various roles
4. **View the knowledge graph**: Explore skill relationships
5. **Check the code**: Review the implementation

## Development Workflow

### Adding New Skills

Edit `backend/app/services/skill_graph.py` and add skills to the `_create_skill_nodes` method.

### Adding New Roles

Edit `backend/app/services/skill_graph.py` and add roles to the `_create_role_nodes` method.

### Customizing Scoring

Edit `backend/app/services/scoring_engine.py` to adjust scoring weights and factors.

## Production Deployment

See the main README.md for deployment instructions to:
- AWS
- Render
- Azure
- Google Cloud Platform

## Support

For issues or questions:
1. Check the logs: `docker-compose logs`
2. Review the API documentation: http://localhost:8000/docs
3. Check Neo4j browser for graph data: http://localhost:7474

---

**Happy coding! 🚀**
