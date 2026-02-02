# Local Setup Guide (Without Docker) - Windows

## 🚀 Quick Setup for Testing

Follow these steps to run SkillLens locally on Windows without Docker.

---

## Step 1: Install PostgreSQL

### Option A: Using Chocolatey (Recommended)
```powershell
# Install Chocolatey if not installed
# Run PowerShell as Administrator
choco install postgresql16

# Start PostgreSQL service
net start postgresql-x64-16
```

### Option B: Manual Installation
1. Download PostgreSQL 16 from: https://www.postgresql.org/download/windows/
2. Run the installer
3. Remember the password you set for the `postgres` user
4. Make sure to install pgAdmin (optional but helpful)

---

## Step 2: Create Database

```powershell
# Open PowerShell and run:
cd f:\SkilLens

# Connect to PostgreSQL (it will ask for password)
psql -U postgres

# In psql, run these commands:
CREATE DATABASE skilllens;
CREATE USER skilllens WITH PASSWORD 'skilllens';
GRANT ALL PRIVILEGES ON DATABASE skilllens TO skilllens;
\q
```

**Alternative using pgAdmin:**
1. Open pgAdmin
2. Right-click "Databases" → Create → Database
3. Name: `skilllens`
4. Owner: Create new user `skilllens` with password `skilllens`

---

## Step 3: Setup Python Environment

```powershell
# Navigate to backend directory
cd f:\SkilLens\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt
```

---

## Step 4: Configure Environment

```powershell
# Copy environment file
cd f:\SkilLens
copy .env.example .env

# Edit .env file with your settings
notepad .env
```

**Update these values in .env:**
```bash
# PostgreSQL Database
DATABASE_URL=postgresql+asyncpg://skilllens:skilllens@localhost:5432/skilllens

# Neo4j (Optional - can skip for now)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=skilllens123

# JWT Secret (change this!)
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# API Keys (Optional - has fallbacks)
OPENAI_API_KEY=your_key_here_or_leave_blank
HUGGINGFACE_API_KEY=your_key_here_or_leave_blank
SERPAPI_KEY=your_key_here_or_leave_blank

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

---

## Step 5: Initialize Database

```powershell
# Make sure you're in backend directory with venv activated
cd f:\SkilLens\backend
.\venv\Scripts\Activate.ps1

# Initialize database with schema
python scripts\init_db.py

# Optional: Add seed data
python scripts\init_db.py --seed
```

**Expected output:**
```
INFO:root:Connecting to PostgreSQL...
INFO:root:Creating database tables...
INFO:root:✅ Database initialized successfully!
INFO:root:Database URL: postgresql+asyncpg://skilllens:skilllens@localhost:5432/skilllens
```

---

## Step 6: Start Backend Server

```powershell
# Make sure venv is activated
cd f:\SkilLens\backend
.\venv\Scripts\Activate.ps1

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Will watch for changes in these directories: ['f:\\SkilLens\\backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## Step 7: Verify Installation

### A. Check API Documentation
Open browser: http://localhost:8000/docs

You should see the Swagger UI with all endpoints.

### B. Check Health Endpoint
```powershell
# In a new PowerShell window
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "SkillLens API is running",
  "version": "1.0.0",
  "database": "PostgreSQL"
}
```

### C. Check Database Connection
```powershell
# Connect to database
psql -U skilllens -d skilllens

# Check tables
\dt

# Should show:
#  public | assessment_results
#  public | assessments
#  public | conversations
#  public | job_listings
#  public | learning_plans
#  public | learning_progress
#  public | predictions
#  public | readiness_scores
#  public | resumes
#  public | skill_prerequisites
#  public | skills
#  public | users

# Exit
\q
```

---

## Step 8: Run Tests

```powershell
# In a new PowerShell window (keep server running)
cd f:\SkilLens\backend
.\venv\Scripts\Activate.ps1

# Run test suite
python test_migration.py
```

**Expected output:**
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

... (more tests)

======================================================================
  TEST SUMMARY
======================================================================

Total Tests: 9
Passed: 9
Failed: 0
Success Rate: 100.0%

✅ All tests passed! 🎉
```

---

## 🔧 Troubleshooting

### Issue 1: PostgreSQL Not Running

```powershell
# Check if PostgreSQL is running
Get-Service -Name postgresql*

# Start PostgreSQL service
net start postgresql-x64-16

# Or using services.msc
services.msc
# Find "postgresql-x64-16" and start it
```

### Issue 2: Connection Refused

```powershell
# Check PostgreSQL is listening on port 5432
netstat -an | findstr 5432

# If not, check PostgreSQL config
# File: C:\Program Files\PostgreSQL\16\data\postgresql.conf
# Ensure: listen_addresses = '*' or 'localhost'
```

### Issue 3: Authentication Failed

```powershell
# Reset password for skilllens user
psql -U postgres
ALTER USER skilllens WITH PASSWORD 'skilllens';
\q

# Update .env file with correct password
```

### Issue 4: Module Not Found

```powershell
# Reinstall dependencies
cd f:\SkilLens\backend
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue 5: Port Already in Use

```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

### Issue 6: Database Tables Not Created

```powershell
# Drop and recreate database
psql -U postgres
DROP DATABASE skilllens;
CREATE DATABASE skilllens;
GRANT ALL PRIVILEGES ON DATABASE skilllens TO skilllens;
\q

# Reinitialize
cd f:\SkilLens\backend
python scripts\init_db.py --seed
```

---

## 📊 Verify Everything is Working

### 1. Check API Endpoints

Visit http://localhost:8000/docs and test:

- **POST /api/auth/register** - Create a user
- **POST /api/auth/login** - Get JWT token
- **GET /api/auth/me** - Get profile (use token)
- **POST /api/resume/upload** - Upload a resume
- **POST /api/scoring/readiness** - Calculate score

### 2. Check Database

```sql
-- Connect
psql -U skilllens -d skilllens

-- Check data
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM resumes;
SELECT COUNT(*) FROM readiness_scores;

-- View recent data
SELECT email, full_name, role, created_at FROM users ORDER BY created_at DESC LIMIT 5;
SELECT filename, uploaded_at FROM resumes ORDER BY uploaded_at DESC LIMIT 5;
SELECT target_role, overall_score, created_at FROM readiness_scores ORDER BY created_at DESC LIMIT 5;
```

### 3. Check Logs

The server will show logs in the terminal where you ran `uvicorn`. Look for:
- ✅ "Application startup complete"
- ✅ "Connected to PostgreSQL database"
- ✅ "Database tables created/verified"

---

## 🎯 Quick Commands Reference

```powershell
# Start PostgreSQL
net start postgresql-x64-16

# Activate Python environment
cd f:\SkilLens\backend
.\venv\Scripts\Activate.ps1

# Initialize database
python scripts\init_db.py --seed

# Start backend
uvicorn app.main:app --reload

# Run tests
python test_migration.py

# Connect to database
psql -U skilllens -d skilllens

# Stop server
# Press CTRL+C in the terminal running uvicorn
```

---

## ✅ Success Checklist

- [ ] PostgreSQL installed and running
- [ ] Database `skilllens` created
- [ ] User `skilllens` created with password
- [ ] Python virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] Database initialized (13 tables created)
- [ ] Backend server starts without errors
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Health check returns "healthy"
- [ ] Test suite passes all tests

---

## 🚀 You're Ready!

Once all checks pass, you have a fully functional SkillLens backend with:
- ✅ PostgreSQL database
- ✅ User authentication
- ✅ Resume management
- ✅ Career readiness scoring
- ✅ API documentation

**Next steps:**
- Test the API endpoints
- Upload sample resumes
- Calculate readiness scores
- View the data in PostgreSQL

Need help? Check the troubleshooting section above! 🎉
