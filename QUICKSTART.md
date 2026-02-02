# SkillLens - Quick Start (No Docker Required!)

## 🚀 Super Simple Setup

### Step 1: Install PostgreSQL

**Download and Install:**
1. Go to: https://www.postgresql.org/download/windows/
2. Download PostgreSQL 16 installer
3. Run installer
4. **Remember the password you set for `postgres` user!**
5. Keep default port (5432)
6. Install all components

**Or use Chocolatey (if you have it):**
```powershell
choco install postgresql16
```

### Step 2: Run Setup Script

```powershell
# Navigate to project
cd f:\SkilLens

# Run setup (double-click or run in PowerShell)
.\setup_local.bat
```

The script will:
- ✅ Check Python installation
- ✅ Check PostgreSQL installation  
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Create .env file
- ✅ Create database
- ✅ Initialize schema

### Step 3: Start Backend

```powershell
# Double-click or run:
.\start_backend.bat
```

### Step 4: Test It

```powershell
# In a new terminal, double-click or run:
.\run_tests.bat
```

---

## 📝 Manual Setup (If Scripts Don't Work)

### 1. Install Dependencies

```powershell
cd f:\SkilLens\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Create Database

```powershell
# Open PowerShell and run:
psql -U postgres

# In psql prompt, type:
CREATE DATABASE skilllens;
CREATE USER skilllens WITH PASSWORD 'skilllens';
GRANT ALL PRIVILEGES ON DATABASE skilllens TO skilllens;
\q
```

### 3. Configure Environment

```powershell
cd f:\SkilLens
copy .env.example .env
notepad .env
```

Update this line:
```
DATABASE_URL=postgresql+asyncpg://skilllens:skilllens@localhost:5432/skilllens
```

### 4. Initialize Database

```powershell
cd f:\SkilLens\backend
.\venv\Scripts\Activate.ps1
python scripts\init_db.py --seed
```

### 5. Start Server

```powershell
uvicorn app.main:app --reload
```

### 6. Test

Open browser: http://localhost:8000/docs

Or run tests:
```powershell
python test_migration.py
```

---

## ✅ Verify It's Working

### Check 1: API Docs
Open: http://localhost:8000/docs

You should see Swagger UI with all endpoints.

### Check 2: Health Check
Open: http://localhost:8000/health

Should return:
```json
{
  "status": "healthy",
  "message": "SkillLens API is running"
}
```

### Check 3: Database
```powershell
psql -U skilllens -d skilllens
\dt
# Should show 13 tables
\q
```

### Check 4: Run Tests
```powershell
cd f:\SkilLens\backend
.\venv\Scripts\Activate.ps1
python test_migration.py
```

All 9 tests should pass! ✅

---

## 🐛 Common Issues

### Issue: PostgreSQL not found
**Solution:** Add PostgreSQL to PATH
```powershell
# Add to PATH (replace with your PostgreSQL path):
$env:Path += ";C:\Program Files\PostgreSQL\16\bin"
```

### Issue: Python not found
**Solution:** Install Python 3.11+ from python.org

### Issue: Permission denied
**Solution:** Run PowerShell as Administrator

### Issue: Database connection failed
**Solution:** Check PostgreSQL is running:
```powershell
Get-Service -Name postgresql*
# If not running:
net start postgresql-x64-16
```

### Issue: Module not found
**Solution:** Reinstall dependencies:
```powershell
cd f:\SkilLens\backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🎯 What You Get

After setup, you'll have:

✅ **PostgreSQL Database** with 13 tables
✅ **User Authentication** (JWT, bcrypt)
✅ **Resume Upload & Parsing**
✅ **Career Readiness Scoring**
✅ **API Documentation** at /docs
✅ **Test Suite** to verify everything

---

## 📚 Quick Commands

```powershell
# Start backend
.\start_backend.bat

# Run tests
.\run_tests.bat

# Connect to database
psql -U skilllens -d skilllens

# Reinitialize database
cd backend
.\venv\Scripts\Activate.ps1
python scripts\init_db.py --drop --seed
```

---

## 🚀 Next Steps

1. **Test the API**: Visit http://localhost:8000/docs
2. **Upload a resume**: Use POST /api/resume/upload
3. **Calculate score**: Use POST /api/scoring/readiness
4. **Check database**: Use psql to view data

---

**Need help?** Check `LOCAL_SETUP_WINDOWS.md` for detailed instructions!
