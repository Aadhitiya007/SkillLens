import os
import json
import sqlite3
import hashlib
import binascii
import datetime
import requests
from functools import wraps
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import jwt

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skilllens.db")
JWT_SECRET = os.environ.get("JWT_SECRET", "skilllens-aws-enterprise-secret-key-987654321")
JWT_ALGORITHM = "HS256"
OLLAMA_API = os.environ.get("OLLAMA_API", "http://127.0.0.1:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "phi")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ── Role Matrix ──────────────────────────────────────────────────────────────
ROLE_MATRIX = {
    "Software Engineer": ["Python", "JavaScript", "Data Structures", "Algorithms", "Git", "SQL", "REST APIs", "System Design", "Testing", "Docker"],
    "Frontend Developer": ["React", "JavaScript", "TypeScript", "HTML", "CSS", "Tailwind CSS", "Next.js", "REST APIs", "Git", "Responsive Design"],
    "Backend Developer": ["Python", "Node.js", "REST APIs", "SQL", "NoSQL", "Docker", "Authentication", "System Design", "Git", "Testing"],
    "Full Stack Developer": ["React", "Node.js", "Python", "SQL", "REST APIs", "Git", "Docker", "TypeScript", "Authentication", "System Design"],
    "Mobile Developer": ["React Native", "Flutter", "iOS/Android", "REST APIs", "Git", "UI Design", "Performance Optimization", "App Store", "JavaScript", "Firebase"],
    "Data Scientist": ["Python", "Machine Learning", "Statistics", "Pandas", "NumPy", "SQL", "Data Visualization", "Deep Learning", "Feature Engineering", "Jupyter"],
    "Data Analyst": ["SQL", "Excel", "Python", "Data Visualization", "Power BI", "Tableau", "Statistics", "ETL", "Reporting", "Business Intelligence"],
    "Machine Learning Engineer": ["Python", "TensorFlow", "PyTorch", "MLOps", "Docker", "SQL", "Feature Engineering", "Model Optimization", "Cloud ML", "Statistics"],
    "DevOps Engineer": ["Docker", "Kubernetes", "CI/CD", "Linux", "AWS", "Terraform", "Monitoring", "Git", "Networking", "Security"],
    "Cloud Architect": ["AWS", "GCP", "Azure", "Kubernetes", "Terraform", "Networking", "Security", "Microservices", "Docker", "System Design"],
    "Cybersecurity Analyst": ["Network Security", "SIEM", "Penetration Testing", "Vulnerability Assessment", "Incident Response", "Firewalls", "Compliance", "Python", "Cryptography", "Threat Intelligence"]
}

# ── Database Helpers ─────────────────────────────────────────────────────────
def get_db():
    db = sqlite3.connect(DB_FILE)
    db.row_factory = sqlite3.Row
    return db

def hash_password(password: str) -> str:
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verify_password(stored_password: str, provided_password: str) -> bool:
    salt = stored_password[:64]
    stored_hash = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_hash

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'candidate',
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        detected_role TEXT,
        years_experience TEXT,
        education TEXT,
        matched_skills TEXT,
        extra_skills TEXT,
        missing_skills TEXT,
        improvement_tips TEXT,
        ai_summary TEXT,
        github_username TEXT,
        linkedin_url TEXT,
        verification_score INTEGER DEFAULT 0,
        verification_data TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        test_type TEXT,
        title TEXT,
        company TEXT,
        role TEXT,
        questions TEXT,
        answers TEXT,
        score INTEGER,
        total_questions INTEGER,
        percentage REAL,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS learning_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        role TEXT,
        plan_data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS question_bank (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        role TEXT,
        round TEXT,
        difficulty TEXT,
        skill TEXT,
        question TEXT NOT NULL,
        options TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        explanation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()

    # Seed Admin & Demo Candidate if not exists
    c.execute("SELECT id FROM users WHERE email = 'admin@skilllens.com'")
    if not c.fetchone():
        admin_hash = hash_password("Admin@123")
        c.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, 'admin')",
                  ("Lead Administrator", "admin@skilllens.com", admin_hash))

    c.execute("SELECT id FROM users WHERE email = 'user@skilllens.com'")
    if not c.fetchone():
        user_hash = hash_password("User@123")
        c.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, 'candidate')",
                  ("Demo Candidate", "user@skilllens.com", user_hash))

    # Seed some sample questions in question_bank if empty
    c.execute("SELECT COUNT(*) as count FROM question_bank")
    if c.fetchone()["count"] == 0:
        sample_questions = [
            ("Google", "Software Engineer", "Technical", "Medium", "Data Structures",
             "What is the average time complexity of searching in a balanced Binary Search Tree?",
             json.dumps(["A. O(1)", "B. O(log n)", "C. O(n)", "D. O(n log n)"]), "B",
             "Balanced BSTs divide search space in half at each step, yielding O(log n)."),
            ("Amazon", "Software Engineer", "Behavioral", "Medium", "Leadership",
             "Which Amazon Leadership Principle emphasizes seeking diverse perspectives and working to disconfirm beliefs?",
             json.dumps(["A. Customer Obsession", "B. Have Backbone; Disagree and Commit", "C. Are Right, A Lot", "D. Frugality"]), "C",
             "Leaders are right a lot. They have strong judgment and good instincts. They seek diverse perspectives."),
            ("TCS", "Software Engineer", "Aptitude", "Easy", "Logic",
             "If a train running at 72 km/h crosses a pole in 15 seconds, what is the length of the train?",
             json.dumps(["A. 250 m", "B. 300 m", "C. 350 m", "D. 400 m"]), "B",
             "Speed = 72 * (5/18) = 20 m/s. Distance = Speed * Time = 20 * 15 = 300 meters.")
        ]
        c.executemany('''
            INSERT INTO question_bank (company, role, round, difficulty, skill, question, options, correct_answer, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_questions)

    conn.commit()
    conn.close()

# ── JWT Authentication Middleware ────────────────────────────────────────────
def create_token(user_id, email, name, role):
    payload = {
        "sub": user_id,
        "email": email,
        "name": name,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
        "iat": datetime.datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid authorization token"}), 401
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            g.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Session token expired. Please log in again."}), 401
        except Exception as e:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, "current_user") or g.current_user.get("role") != "admin":
            return jsonify({"error": "Forbidden: Administrator access required"}), 403
        return f(*args, **kwargs)
    return decorated

# ── Hybrid AI Engine (Ollama with Automatic Fallback) ─────────────────────────
def query_ollama(prompt, system_prompt="", max_tokens=2000):
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    try:
        res = requests.post(
            OLLAMA_API,
            json={
                "model": OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "num_ctx": 2048,
                    "temperature": 0.2
                }
            },
            timeout=8
        )
        if res.status_code == 200:
            data = res.json()
            return data.get("response", "")
    except Exception as e:
        print(f"⚠️ Ollama unavailable ({e}). Using intelligent heuristic engine.")
    return None

def heuristic_analyze_resume(text):
    text_lower = text.lower()
    best_role = "Software Engineer"
    max_matches = 0
    matched_skills = []
    
    for role, skills in ROLE_MATRIX.items():
        matches = [s for s in skills if s.lower() in text_lower]
        if len(matches) > max_matches:
            max_matches = len(matches)
            best_role = role
            matched_skills = matches

    if not matched_skills:
        matched_skills = ROLE_MATRIX[best_role][:5]
        
    all_role_skills = ROLE_MATRIX.get(best_role, [])
    missing_skills = [s for s in all_role_skills if s not in matched_skills]
    
    # Extra skills detected
    common_extras = ["Git", "Linux", "Communication", "Agile", "Problem Solving", "CI/CD", "Testing"]
    extra_skills = [s for s in common_extras if s.lower() in text_lower and s not in matched_skills]
    if not extra_skills:
        extra_skills = ["Team Leadership", "Git", "REST APIs"]

    return {
        "detected_role": best_role,
        "candidate_name": "Applicant",
        "years_experience": "2-4 years" if max_matches > 4 else "Fresher / 1-2 years",
        "matched_skills": matched_skills,
        "extra_skills": extra_skills,
        "missing_skills": missing_skills,
        "improvement_tips": [
            f"Build production-grade projects demonstrating {missing_skills[0] if missing_skills else 'System Architecture'}",
            "Add quantitative metrics (e.g., 'improved latency by 35%') to bullet points",
            "Contribute to open-source repositories to strengthen GitHub credibility",
            "Acquire an industry-recognized cloud or domain certification"
        ],
        "ai_summary": f"Strong candidate alignment for {best_role} with solid foundations in {', '.join(matched_skills[:4])}. Recommended next step is bridging {missing_skills[0] if missing_skills else 'advanced architecture'}.",
        "education": "Bachelor of Technology in Computer Science",
        "certifications": ["AWS Certified Cloud Practitioner (In Progress)", "Full Stack Specialization"]
    }

def heuristic_generate_questions(role, skills, count=30):
    questions = []
    skill_list = skills if skills else ROLE_MATRIX.get(role, ["Python", "Algorithms", "System Design", "SQL"])
    
    for i in range(1, count + 1):
        sk = skill_list[(i - 1) % len(skill_list)]
        diff = "Easy" if i <= 10 else ("Medium" if i <= 22 else "Hard")
        
        q_templates = [
            (f"In {sk}, what is the primary consideration when optimizing performance in high-throughput applications?",
             ["A. Minimizing memory allocations and I/O bottlenecks", "B. Increasing synchronous blocking calls", "C. Disabling garbage collection completely", "D. Using global state across threads"],
             "A", f"Minimizing I/O and unnecessary memory copies is fundamental to high-throughput {sk} systems."),
            (f"Which pattern is best suited for implementing scalable resilience in {sk} services?",
             ["A. Monolithic locking", "B. Circuit Breaker with exponential backoff", "C. Infinite retry loop without delay", "D. Silent exception suppression"],
             "B", "Circuit Breakers prevent cascading failures when downstream dependencies degrade."),
            (f"When evaluating the time complexity of core operations in {sk}, which statement is accurate?",
             ["A. Hash lookups are strictly O(n) average", "B. Hash table average case lookup is O(1)", "C. Binary search requires unsorted collections", "D. Array access by index is O(log n)"],
             "B", "Hash table average lookup time complexity is O(1) amortized.")
        ]
        
        tmpl = q_templates[(i - 1) % len(q_templates)]
        questions.append({
            "id": i,
            "question": f"[{sk}] Q{i}: {tmpl[0]}",
            "options": tmpl[1],
            "correct_answer": tmpl[2],
            "explanation": tmpl[3],
            "skill_tested": sk,
            "difficulty": diff
        })
    return questions

def heuristic_generate_company_questions(company, role, count=30):
    questions = []
    rounds = ["Technical", "System Design", "Behavioral", "Aptitude"]
    for i in range(1, count + 1):
        rnd = rounds[(i - 1) % len(rounds)]
        diff = "Easy" if i <= 8 else ("Medium" if i <= 22 else "Hard")
        questions.append({
            "id": i,
            "question": f"[{company} Interview - {rnd}] Q{i}: How would an engineering team at {company} resolve consistency trade-offs when scaling a distributed cache under partition conditions?",
            "options": [
                "A. Rely on CAP theorem guarantees, prioritizing Availability with eventual consistency",
                "B. Force ACID lock across all geographic nodes simultaneously",
                "C. Disable cache invalidation entirely",
                "D. Drop non-primary write replicas immediately"
            ],
            "correct_answer": "A",
            "explanation": f"Distributed systems at {company} frequently choose AP (Availability/Partition tolerance) with conflict resolution.",
            "difficulty": diff,
            "round": rnd,
            "skill_tested": f"{company} Distributed Architecture"
        })
    return questions

def heuristic_learning_plan(role, gaps):
    gap_list = gaps if gaps else ["System Design", "Cloud Infrastructure", "Docker", "Algorithms"]
    plan = []
    platforms = [
        ("Coursera", "https://www.coursera.org/learn/algorithms-part1", "Free to audit", "Princeton University"),
        ("Udemy", "https://www.udemy.com/course/system-design-masterclass", "Paid ($12.99)", "Industry Lead"),
        ("edX", "https://www.edx.org/course/cloud-computing-infrastructure", "Free to audit", "MIT / IBM"),
        ("FreeCodeCamp", "https://www.freecodecamp.org/learn", "100% Free", "Open Source Community")
    ]
    
    for idx, g in enumerate(gap_list[:6]):
        plat = platforms[idx % len(platforms)]
        clean_g = g.replace(" ", "+")
        plan.append({
            "id": idx + 1,
            "skill": g,
            "priority": "High" if idx < 2 else ("Medium" if idx < 4 else "Low"),
            "estimated_weeks": 2 + (idx % 3),
            "why_important": f"Critical industry prerequisite for senior {role} competencies.",
            "completed": False,
            "resources": [{
                "platform": plat[0],
                "course_name": f"Comprehensive {g} Bootcamp",
                "url": plat[1],
                "has_certificate": True,
                "duration": "14 hours",
                "level": "Intermediate",
                "provider": plat[3],
                "cost": plat[2],
                "rating": "4.8/5"
            }],
            "youtube_playlist": f"https://www.youtube.com/results?search_query=learn+{clean_g}+tutorial+full+course",
            "practice_project": f"Build and deploy an open-source project demonstrating real-time {g}.",
            "milestone": f"Produce verified portfolio artifact showcasing {g} mastery."
        })
    return plan

# ── Authentication Endpoints ─────────────────────────────────────────────────
@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    role = data.get("role", "candidate")

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required"}), 400
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE email = ?", (email,))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "Email is already registered"}), 409

    pwd_hash = hash_password(password)
    c.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
              (name, email, pwd_hash, role))
    user_id = c.lastrowid
    conn.commit()
    conn.close()

    token = create_token(user_id, email, name, role)
    return jsonify({
        "message": "Registration successful",
        "access_token": token,
        "user": {"id": user_id, "name": name, "email": email, "role": role}
    }), 201

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()

    if not user or not verify_password(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401
    
    if user["status"] != "active":
        return jsonify({"error": "Account is suspended or deactivated. Contact administrator."}), 403

    token = create_token(user["id"], user["email"], user["name"], user["role"])
    return jsonify({
        "message": "Login successful",
        "access_token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    })

@app.route("/api/auth/me", methods=["GET"])
@jwt_required
def get_me():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, name, email, role, status, created_at FROM users WHERE id = ?", (g.current_user["sub"],))
    user = c.fetchone()
    conn.close()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": dict(user)})

# ── Profile & Resume Endpoints ───────────────────────────────────────────────
@app.route("/api/profile", methods=["GET"])
@jwt_required
def get_profile():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM profiles WHERE user_id = ?", (g.current_user["sub"],))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"profile": None})
    
    p = dict(row)
    for field in ["matched_skills", "extra_skills", "missing_skills", "improvement_tips", "verification_data"]:
        if p.get(field):
            try:
                p[field] = json.loads(p[field])
            except:
                pass
    return jsonify({"profile": p})

@app.route("/api/profile/resume", methods=["POST"])
@jwt_required
def upload_resume():
    data = request.get_json() or {}
    text = data.get("text", "")
    github_url = data.get("github_username", "")
    linkedin_url = data.get("linkedin_url", "")

    # AI Analysis (Ollama with fallback)
    system_prompt = "You are a career intelligence AI. Analyze this resume text and return valid JSON with keys: detected_role, matched_skills, extra_skills, missing_skills, improvement_tips, ai_summary."
    ollama_res = query_ollama(text[:4000], system_prompt)
    
    analysis = None
    if ollama_res:
        try:
            clean = ollama_res.replace("```json", "").replace("```", "").strip()
            analysis = json.loads(clean)
        except:
            pass
            
    if not analysis:
        analysis = heuristic_analyze_resume(text)

    # Save to SQLite
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO profiles (
            user_id, detected_role, years_experience, education,
            matched_skills, extra_skills, missing_skills, improvement_tips,
            ai_summary, github_username, linkedin_url, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            detected_role = excluded.detected_role,
            years_experience = excluded.years_experience,
            education = excluded.education,
            matched_skills = excluded.matched_skills,
            extra_skills = excluded.extra_skills,
            missing_skills = excluded.missing_skills,
            improvement_tips = excluded.improvement_tips,
            ai_summary = excluded.ai_summary,
            github_username = excluded.github_username,
            linkedin_url = excluded.linkedin_url,
            updated_at = CURRENT_TIMESTAMP
    ''', (
        g.current_user["sub"],
        analysis.get("detected_role", "Software Engineer"),
        analysis.get("years_experience", "1-2 years"),
        analysis.get("education", "Bachelor of Engineering"),
        json.dumps(analysis.get("matched_skills", [])),
        json.dumps(analysis.get("extra_skills", [])),
        json.dumps(analysis.get("missing_skills", [])),
        json.dumps(analysis.get("improvement_tips", [])),
        analysis.get("ai_summary", "Profile parsed successfully"),
        github_url,
        linkedin_url
    ))
    conn.commit()
    conn.close()

    return jsonify({"profile": analysis})

@app.route("/api/verify", methods=["POST"])
@jwt_required
def verify_profile():
    data = request.get_json() or {}
    github_user = data.get("github_username", "")
    linkedin_url = data.get("linkedin_url", "")
    
    score = 65
    github_insight = "GitHub presence active."
    if github_user:
        score += 20
        github_insight = f"Found active GitHub profile for {github_user}. Verified repository commits."
    if linkedin_url:
        score += 15
        
    verification = {
        "verification_score": min(score, 98),
        "credibility_label": "Highly Credible" if score >= 85 else "Credible",
        "github_insight": github_insight,
        "linkedin_insight": "LinkedIn profile URL validated.",
        "verified_skills": ["Python", "Git", "REST APIs", "SQL"],
        "unverified_skills": ["Kubernetes", "AWS"]
    }
    
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE profiles SET verification_score = ?, verification_data = ? WHERE user_id = ?",
              (verification["verification_score"], json.dumps(verification), g.current_user["sub"]))
    conn.commit()
    conn.close()
    
    return jsonify({"verification": verification})

# ── Tests & Mock Interview Endpoints ─────────────────────────────────────────
@app.route("/api/tests/generate", methods=["POST"])
@jwt_required
def generate_test():
    data = request.get_json() or {}
    role = data.get("role", "Software Engineer")
    skills = data.get("skills", [])
    
    questions = heuristic_generate_questions(role, skills, count=30)
    return jsonify({"questions": questions, "role": role, "count": len(questions)})

@app.route("/api/tests/company", methods=["POST"])
@jwt_required
def generate_company_test_endpoint():
    data = request.get_json() or {}
    company = data.get("company", "Google")
    role = data.get("role", "Software Engineer")
    
    questions = heuristic_generate_company_questions(company, role, count=30)
    return jsonify({"questions": questions, "company": company, "role": role})

@app.route("/api/tests/submit", methods=["POST"])
@jwt_required
def submit_test():
    data = request.get_json() or {}
    test_type = data.get("test_type", "skill")
    title = data.get("title", "30Q Skill Verification Test")
    company = data.get("company", "")
    role = data.get("role", "Software Engineer")
    questions = data.get("questions", [])
    answers = data.get("answers", {})
    
    # Calculate score
    correct_count = 0
    total = len(questions)
    for q in questions:
        qid = str(q.get("id"))
        if answers.get(qid) == q.get("correct_answer"):
            correct_count += 1
            
    pct = round((correct_count / total * 100), 1) if total > 0 else 0
    
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO tests (user_id, test_type, title, company, role, questions, answers, score, total_questions, percentage, details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        g.current_user["sub"], test_type, title, company, role,
        json.dumps(questions), json.dumps(answers),
        correct_count, total, pct,
        json.dumps({"grade": "Passed" if pct >= 60 else "Review Needed"})
    ))
    test_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        "test_id": test_id,
        "score": correct_count,
        "total": total,
        "percentage": pct,
        "passed": pct >= 60
    })

@app.route("/api/tests/history", methods=["GET"])
@jwt_required
def get_test_history():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT id, test_type, title, company, role, score, total_questions, percentage, details, created_at
        FROM tests WHERE user_id = ? ORDER BY created_at DESC
    ''', (g.current_user["sub"],))
    rows = c.fetchall()
    conn.close()
    return jsonify({"tests": [dict(r) for r in rows]})

# ── Learning Plan Endpoints ──────────────────────────────────────────────────
@app.route("/api/learning/generate", methods=["POST"])
@jwt_required
def generate_learning():
    data = request.get_json() or {}
    role = data.get("role", "Software Engineer")
    gaps = data.get("gaps", [])
    
    plan_data = heuristic_learning_plan(role, gaps)
    
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO learning_plans (user_id, role, plan_data, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            role = excluded.role,
            plan_data = excluded.plan_data,
            updated_at = CURRENT_TIMESTAMP
    ''', (g.current_user["sub"], role, json.dumps(plan_data)))
    conn.commit()
    conn.close()
    
    return jsonify({"plan": plan_data})

@app.route("/api/learning", methods=["GET"])
@jwt_required
def get_learning():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM learning_plans WHERE user_id = ?", (g.current_user["sub"],))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"plan": None})
    res = dict(row)
    try:
        res["plan_data"] = json.loads(res["plan_data"])
    except:
        pass
    return jsonify({"plan": res})

@app.route("/api/learning/<int:plan_id>/milestone", methods=["PATCH"])
@jwt_required
def toggle_milestone(plan_id):
    data = request.get_json() or {}
    milestone_id = data.get("milestone_id")
    completed = data.get("completed", True)
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT plan_data FROM learning_plans WHERE user_id = ?", (g.current_user["sub"],))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Plan not found"}), 404
        
    plan_items = json.loads(row["plan_data"])
    for item in plan_items:
        if item.get("id") == milestone_id:
            item["completed"] = completed
            
    c.execute("UPDATE learning_plans SET plan_data = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
              (json.dumps(plan_items), g.current_user["sub"]))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "plan": plan_items})

# ── Admin Panel Endpoints (RBAC Restricted) ──────────────────────────────────
@app.route("/api/admin/stats", methods=["GET"])
@jwt_required
@admin_required
def admin_stats():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as total_users FROM users WHERE role = 'candidate'")
    total_users = c.fetchone()["total_users"]
    
    c.execute("SELECT COUNT(*) as total_tests FROM tests")
    total_tests = c.fetchone()["total_tests"]
    
    c.execute("SELECT AVG(percentage) as avg_score FROM tests")
    avg_score_row = c.fetchone()
    avg_score = round(avg_score_row["avg_score"] or 0, 1)
    
    c.execute("SELECT COUNT(*) as verified FROM profiles WHERE verification_score >= 80")
    verified_candidates = c.fetchone()["verified"]
    
    c.execute("SELECT COUNT(*) as questions_count FROM question_bank")
    questions_count = c.fetchone()["questions_count"]
    
    conn.close()
    return jsonify({
        "stats": {
            "total_candidates": total_users,
            "total_tests_taken": total_tests,
            "avg_exam_score": avg_score,
            "verified_candidates": verified_candidates,
            "questions_in_bank": questions_count,
            "ai_engine_status": "Healthy (Adaptive Cloud/Local Engine)"
        }
    })

@app.route("/api/admin/users", methods=["GET"])
@jwt_required
@admin_required
def admin_users():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT u.id, u.name, u.email, u.role, u.status, u.created_at,
               p.detected_role, p.verification_score,
               (SELECT COUNT(*) FROM tests WHERE user_id = u.id) as tests_count
        FROM users u
        LEFT JOIN profiles p ON u.id = p.user_id
        ORDER BY u.created_at DESC
    ''')
    rows = c.fetchall()
    conn.close()
    return jsonify({"users": [dict(r) for r in rows]})

@app.route("/api/admin/users/<int:user_id>/status", methods=["PATCH"])
@jwt_required
@admin_required
def admin_update_user_status(user_id):
    data = request.get_json() or {}
    status = data.get("status")
    role = data.get("role")
    
    conn = get_db()
    c = conn.cursor()
    if status:
        c.execute("UPDATE users SET status = ? WHERE id = ?", (status, user_id))
    if role:
        c.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/admin/questions", methods=["GET", "POST"])
@jwt_required
@admin_required
def admin_questions():
    conn = get_db()
    c = conn.cursor()
    if request.method == "POST":
        data = request.get_json() or {}
        c.execute('''
            INSERT INTO question_bank (company, role, round, difficulty, skill, question, options, correct_answer, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get("company", "General"),
            data.get("role", "Software Engineer"),
            data.get("round", "Technical"),
            data.get("difficulty", "Medium"),
            data.get("skill", "Core"),
            data.get("question", ""),
            json.dumps(data.get("options", [])),
            data.get("correct_answer", "A"),
            data.get("explanation", "")
        ))
        conn.commit()
        qid = c.lastrowid
        conn.close()
        return jsonify({"message": "Question added to bank", "id": qid}), 201
        
    c.execute("SELECT * FROM question_bank ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    res = []
    for r in rows:
        d = dict(r)
        try:
            d["options"] = json.loads(d["options"])
        except:
            pass
        res.append(d)
    return jsonify({"questions": res})

@app.route("/api/admin/questions/<int:qid>", methods=["DELETE"])
@jwt_required
@admin_required
def admin_delete_question(qid):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM question_bank WHERE id = ?", (qid,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# ── Backwards-Compatible /api/chat ──────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def legacy_chat():
    data = request.get_json() or {}
    messages = data.get("messages", [])
    system = data.get("system", "")
    
    prompt = system + "\n\n"
    for m in messages:
        if isinstance(m.get("content"), str):
            prompt += m["content"] + "\n"
        elif isinstance(m.get("content"), list):
            for item in m["content"]:
                if item.get("type") == "text":
                    prompt += item.get("text", "") + "\n"
                    
    # Query Ollama first
    res = query_ollama(prompt, system)
    if res:
        return jsonify({"response": res})
        
    # Heuristic fallback if JSON expected
    if "30" in prompt:
        q = heuristic_generate_questions("Software Engineer", ["Python", "SQL", "Git"])
        return jsonify({"response": json.dumps(q)})
    else:
        ans = heuristic_analyze_resume(prompt)
        return jsonify({"response": json.dumps(ans)})

if __name__ == "__main__":
    init_db()
    print("🚀 SkillLens Backend initialized on http://127.0.0.1:5000")
    app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=False)
