# Testing Guide for PostgreSQL Migration

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 16 (or Docker)
- Backend dependencies installed

### Option 1: Test with Docker (Recommended)

```bash
# 1. Start services
docker-compose up -d

# Wait for services to be ready (about 10-15 seconds)
docker-compose logs -f backend

# 2. Run tests
cd backend
python test_migration.py
```

### Option 2: Test Locally

```bash
# 1. Ensure PostgreSQL is running
# Check with: psql -U skilllens -d skilllens -c "SELECT 1"

# 2. Initialize database (if not done)
cd backend
python scripts/init_db.py --seed

# 3. Start backend
uvicorn app.main:app --reload

# 4. In another terminal, run tests
python test_migration.py
```

---

## 🧪 What Gets Tested

### 1. Health Checks ✅
- Root endpoint (`/`)
- Health check endpoint (`/health`)
- Auth service health (`/api/auth/health`)
- Scoring service health (`/api/scoring/health`)

### 2. Authentication ✅
- User registration with validation
- User login with JWT
- Get current user profile
- Token validation

### 3. Resume Management ✅
- Upload resume file
- Parse resume data
- Extract skills, experience, projects
- Retrieve user resume
- JSONB storage verification

### 4. Career Readiness Scoring ✅
- Calculate multi-factor score
- Generate AI explanation
- Get score history
- View recommendations
- Track strengths/weaknesses

---

## 📊 Expected Output

```
╔════════════════════════════════════════════════════════════════════╗
║               SkillLens PostgreSQL Migration Test Suite           ║
║                    Testing Working Features                        ║
╚════════════════════════════════════════════════════════════════════╝

ℹ️  Testing against: http://localhost:8000
ℹ️  Make sure the backend is running!

======================================================================
  TEST 1: Health Checks
======================================================================

✅ Root endpoint: Welcome to SkillLens API
✅ Health check: healthy
✅ Auth service: healthy - Database: PostgreSQL
✅ Scoring service: healthy - Database: PostgreSQL

======================================================================
  TEST 2: User Registration
======================================================================

✅ User registered: test@skilllens.com
ℹ️  User ID: uuid-here
ℹ️  Token: eyJ0eXAiOiJKV1QiLCJhbGc...

======================================================================
  TEST 3: User Login
======================================================================

✅ Login successful: test@skilllens.com
ℹ️  Token: eyJ0eXAiOiJKV1QiLCJhbGc...

======================================================================
  TEST 4: Get Current User Profile
======================================================================

✅ Profile retrieved: Test User
ℹ️  Email: test@skilllens.com
ℹ️  Role: student
ℹ️  Department: Computer Science

======================================================================
  TEST 5: Resume Upload
======================================================================

✅ Resume uploaded: resume.txt
ℹ️  Resume ID: uuid-here
ℹ️  Name extracted: JOHN DOE
ℹ️  Skills found: 10 skills
ℹ️    - Python, JavaScript, SQL, Docker, AWS...
ℹ️  Experience: 2 positions
ℹ️  Projects: 3 projects

======================================================================
  TEST 6: Get User Resume
======================================================================

✅ Resume retrieved: resume.txt
ℹ️  Uploaded: 2026-01-04T11:00:00Z

======================================================================
  TEST 7: Calculate Career Readiness Score
======================================================================

✅ Readiness score calculated: 67.4/100
ℹ️  Target role: Data Engineer

ℹ️  
Factor Breakdown:
  Technical Skills     [████████░░░░░░░░░░░░] 44.4%
  Experience           [████████████████████] 100.0%
  Project Portfolio    [█████████████░░░░░░░] 66.7%
  Tool Proficiency     [███████████████░░░░░] 75.0%

ℹ️  Strengths: Experience, Tool Proficiency
ℹ️  Weaknesses: Technical Skills

ℹ️  
Recommendations:
  1. Learn Apache Spark, Kafka to meet core requirements
  2. Build 1-2 more projects showcasing data engineering skills

ℹ️  
Explanation:
  Your readiness for Data Engineer is good at 67.4%...

======================================================================
  TEST 8: Get Score History
======================================================================

✅ Score history retrieved: 1 records

ℹ️  
Recent Scores:
  2026-01-04T11:00:00Z: 67.4 (Data Engineer)

======================================================================
  TEST 9: Get Latest Score Explanation
======================================================================

✅ Explanation retrieved
ℹ️  Score: 67.4/100
ℹ️  Target Role: Data Engineer
ℹ️  Calculated: 2026-01-04T11:00:00Z

======================================================================
  TEST SUMMARY
======================================================================

Total Tests: 9
Passed: 9
Failed: 0
Success Rate: 100.0%

  health               ✅ PASS
  login                ✅ PASS
  profile              ✅ PASS
  resume_upload        ✅ PASS
  get_resume           ✅ PASS
  calculate_score      ✅ PASS
  score_history        ✅ PASS
  explanation          ✅ PASS

✅ All tests passed! 🎉
ℹ️  Your PostgreSQL migration is working correctly!
```

---

## 🔍 Manual Testing via API Docs

### 1. Open Swagger UI
```bash
open http://localhost:8000/docs
```

### 2. Test Authentication
1. Go to `/api/auth/register`
2. Click "Try it out"
3. Enter test data:
   ```json
   {
     "email": "manual@test.com",
     "password": "TestPass123",
     "full_name": "Manual Test",
     "role": "student"
   }
   ```
4. Click "Execute"
5. Copy the `access_token` from response

### 3. Test Authenticated Endpoints
1. Click "Authorize" button at top
2. Enter: `Bearer YOUR_TOKEN_HERE`
3. Click "Authorize"
4. Now you can test protected endpoints

### 4. Test Resume Upload
1. Go to `/api/resume/upload`
2. Click "Try it out"
3. Choose a PDF or TXT file
4. Click "Execute"
5. Check parsed data in response

### 5. Test Scoring
1. Go to `/api/scoring/readiness`
2. Enter:
   ```json
   {
     "user_id": "demo_user",
     "target_role": "Data Engineer"
   }
   ```
3. Click "Execute"
4. Review score breakdown

---

## 🗄️ Database Verification

### Check Data in PostgreSQL

```bash
# Connect to database
docker exec -it skilllens-postgres psql -U skilllens

# Or locally
psql -U skilllens -d skilllens
```

### Useful Queries

```sql
-- Check all tables
\dt

-- Count records
SELECT 
    (SELECT COUNT(*) FROM users) as users,
    (SELECT COUNT(*) FROM resumes) as resumes,
    (SELECT COUNT(*) FROM readiness_scores) as scores;

-- View users
SELECT id, email, full_name, role, created_at 
FROM users 
ORDER BY created_at DESC;

-- View resumes with skills
SELECT 
    filename,
    parsed_data->>'name' as candidate_name,
    parsed_data->'skills' as skills,
    uploaded_at
FROM resumes
ORDER BY uploaded_at DESC;

-- View readiness scores
SELECT 
    target_role,
    overall_score,
    technical_skills_score,
    experience_score,
    created_at
FROM readiness_scores
ORDER BY created_at DESC;

-- Get detailed score with explanation
SELECT 
    target_role,
    overall_score,
    explanation,
    strengths,
    weaknesses,
    recommendations
FROM readiness_scores
ORDER BY created_at DESC
LIMIT 1;
```

---

## 🐛 Troubleshooting

### Backend Not Starting

```bash
# Check Docker logs
docker-compose logs backend

# Check PostgreSQL
docker-compose logs postgres

# Restart services
docker-compose restart
```

### Database Connection Error

```bash
# Verify PostgreSQL is running
docker ps | grep postgres

# Check connection
docker exec -it skilllens-postgres psql -U skilllens -c "SELECT 1"

# Reinitialize database
docker exec -it skilllens-backend python scripts/init_db.py
```

### Tests Failing

```bash
# Check backend is running
curl http://localhost:8000/health

# Check logs
docker-compose logs -f backend

# Restart and retry
docker-compose restart backend
sleep 5
python test_migration.py
```

### Import Errors

```bash
# Reinstall dependencies
cd backend
pip install -r requirements.txt

# Or with Docker
docker-compose build backend
docker-compose up -d
```

---

## ✅ Success Criteria

Your migration is working correctly if:

- ✅ All 9 tests pass
- ✅ Users can register and login
- ✅ Resumes can be uploaded and parsed
- ✅ Readiness scores are calculated
- ✅ Data persists in PostgreSQL
- ✅ API documentation loads at `/docs`

---

## 📈 What's Working

### ✅ Fully Functional
- User authentication (JWT, bcrypt)
- Resume upload and parsing
- Career readiness scoring
- Score history tracking
- PostgreSQL database with proper schema
- JSONB for flexible data
- Health check endpoints

### ⏳ Not Yet Implemented
- Skill verification assessments
- ML predictions
- Job market integration
- AI agent chat
- Learning path generation

---

## 🎯 Next Steps After Testing

1. **If all tests pass**: Migration is successful! You can:
   - Continue with remaining routers
   - Deploy to staging
   - Integrate with frontend

2. **If tests fail**: Check:
   - Backend logs
   - Database connection
   - Environment variables
   - Dependencies installed

---

**Ready to test!** Run `python backend/test_migration.py` and see your PostgreSQL migration in action! 🚀
