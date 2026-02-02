"""
SkillLens PostgreSQL Migration - Comprehensive Test Suite
Tests all working endpoints: Auth, Resume, Scoring
"""

import requests
import json
from pathlib import Path
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test@skilllens.com",
    "password": "TestPassword123!",
    "full_name": "Test User",
    "role": "student",
    "department": "Computer Science",
    "register_number": "CS2024001"
}

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_section(title):
    print(f"\n{Colors.BLUE}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{Colors.END}\n")


# Test 1: Health Checks
def test_health_checks():
    print_section("TEST 1: Health Checks")
    
    try:
        # Root endpoint
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        print_success(f"Root endpoint: {data['message']}")
        
        # Health check
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        print_success(f"Health check: {data['status']}")
        
        # Auth health
        response = requests.get(f"{BASE_URL}/api/auth/health")
        assert response.status_code == 200
        data = response.json()
        print_success(f"Auth service: {data['status']} - Database: {data['database']}")
        
        # Scoring health
        response = requests.get(f"{BASE_URL}/api/scoring/health")
        assert response.status_code == 200
        data = response.json()
        print_success(f"Scoring service: {data['status']} - Database: {data['database']}")
        
        return True
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False


# Test 2: User Registration
def test_user_registration():
    print_section("TEST 2: User Registration")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=TEST_USER
        )
        
        if response.status_code == 400 and "already registered" in response.text:
            print_warning("User already exists (expected if running tests multiple times)")
            return None  # Not a failure, just already exists
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_USER["email"]
        assert data["user"]["full_name"] == TEST_USER["full_name"]
        
        print_success(f"User registered: {data['user']['email']}")
        print_info(f"User ID: {data['user']['user_id']}")
        print_info(f"Token: {data['access_token'][:30]}...")
        
        return data["access_token"]
    except Exception as e:
        print_error(f"Registration failed: {e}")
        return None


# Test 3: User Login
def test_user_login():
    print_section("TEST 3: User Login")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        print_success(f"Login successful: {data['user']['email']}")
        print_info(f"Token: {data['access_token'][:30]}...")
        
        return data["access_token"]
    except Exception as e:
        print_error(f"Login failed: {e}")
        return None


# Test 4: Get Current User
def test_get_current_user(token):
    print_section("TEST 4: Get Current User Profile")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == TEST_USER["email"]
        assert data["full_name"] == TEST_USER["full_name"]
        
        print_success(f"Profile retrieved: {data['full_name']}")
        print_info(f"Email: {data['email']}")
        print_info(f"Role: {data['role']}")
        print_info(f"Department: {data.get('department', 'N/A')}")
        
        return data["user_id"]
    except Exception as e:
        print_error(f"Get profile failed: {e}")
        return None


# Test 5: Resume Upload
def test_resume_upload():
    print_section("TEST 5: Resume Upload")
    
    try:
        # Create a sample resume file
        sample_resume = """
JOHN DOE
Software Engineer | Python Developer

CONTACT:
Email: john.doe@example.com
Phone: +1234567890

SKILLS:
Python, JavaScript, SQL, Docker, AWS, React, Node.js, MongoDB, Git, FastAPI

EXPERIENCE:
Senior Software Engineer at Tech Corp (2021-2023)
- Developed microservices using Python and FastAPI
- Implemented RESTful APIs and database integrations
- Managed AWS infrastructure and Docker containers
- Led team of 3 junior developers

Software Developer at StartupXYZ (2019-2021)
- Built web applications using React and Node.js
- Worked on MongoDB database design
- Implemented CI/CD pipelines

PROJECTS:
1. E-commerce Platform
   Technologies: React, Node.js, MongoDB, Stripe API
   Description: Full-stack e-commerce solution with payment integration

2. Data Analytics Dashboard
   Technologies: Python, Pandas, Plotly, FastAPI
   Description: Real-time analytics dashboard for business metrics

3. Task Management System
   Technologies: React, FastAPI, PostgreSQL
   Description: Collaborative task management with real-time updates

EDUCATION:
B.Tech in Computer Science
XYZ University (2015-2019)
GPA: 3.8/4.0
"""
        
        # Save to temporary file
        resume_path = Path("temp_test_resume.txt")
        resume_path.write_text(sample_resume)
        
        # Upload resume
        with open(resume_path, "rb") as f:
            files = {"file": ("resume.txt", f, "text/plain")}
            response = requests.post(
                f"{BASE_URL}/api/resume/upload",
                files=files
            )
        
        # Clean up
        resume_path.unlink()
        
        assert response.status_code == 201
        data = response.json()
        
        assert "resume_id" in data
        assert "parsed_data" in data
        
        parsed = data["parsed_data"]
        print_success(f"Resume uploaded: {data['filename']}")
        print_info(f"Resume ID: {data['resume_id']}")
        print_info(f"Name extracted: {parsed.get('name', 'N/A')}")
        print_info(f"Skills found: {len(parsed.get('skills', []))} skills")
        print_info(f"  - {', '.join(parsed.get('skills', [])[:5])}...")
        print_info(f"Experience: {len(parsed.get('experience', []))} positions")
        print_info(f"Projects: {len(parsed.get('projects', []))} projects")
        
        return data["resume_id"], data["user_id"]
    except Exception as e:
        print_error(f"Resume upload failed: {e}")
        return None, None


# Test 6: Get Resume
def test_get_resume(user_id):
    print_section("TEST 6: Get User Resume")
    
    try:
        response = requests.get(f"{BASE_URL}/api/resume/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "resume_id" in data
        assert "parsed_data" in data
        
        print_success(f"Resume retrieved: {data['filename']}")
        print_info(f"Uploaded: {data['uploaded_at']}")
        
        return True
    except Exception as e:
        print_error(f"Get resume failed: {e}")
        return False


# Test 7: Calculate Readiness Score
def test_calculate_readiness_score(user_id):
    print_section("TEST 7: Calculate Career Readiness Score")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/scoring/readiness",
            json={
                "user_id": user_id,
                "target_role": "Data Engineer"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "overall_score" in data
        assert "factors" in data
        assert "explanation" in data
        
        print_success(f"Readiness score calculated: {data['overall_score']}/100")
        print_info(f"Target role: {data['target_role']}")
        
        print_info("\nFactor Breakdown:")
        for factor in data["factors"]:
            bar_length = int(factor["score"] / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"  {factor['factor_name']:20} [{bar}] {factor['score']:.1f}%")
        
        print_info(f"\nStrengths: {', '.join(data.get('strengths', []))}")
        print_info(f"Weaknesses: {', '.join(data.get('weaknesses', []))}")
        
        print_info("\nRecommendations:")
        for i, rec in enumerate(data.get("recommendations", []), 1):
            print(f"  {i}. {rec}")
        
        print_info(f"\nExplanation:")
        print(f"  {data['explanation']}")
        
        return True
    except Exception as e:
        print_error(f"Calculate score failed: {e}")
        return False


# Test 8: Get Score History
def test_get_score_history(user_id):
    print_section("TEST 8: Get Score History")
    
    try:
        response = requests.get(f"{BASE_URL}/api/scoring/history/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "history" in data
        assert "count" in data
        
        print_success(f"Score history retrieved: {data['count']} records")
        
        if data["history"]:
            print_info("\nRecent Scores:")
            for score in data["history"][:5]:
                print(f"  {score['date']}: {score['score']:.1f} ({score['target_role']})")
        
        return True
    except Exception as e:
        print_error(f"Get score history failed: {e}")
        return False


# Test 9: Get Latest Explanation
def test_get_explanation(user_id):
    print_section("TEST 9: Get Latest Score Explanation")
    
    try:
        response = requests.get(f"{BASE_URL}/api/scoring/explanation/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "overall_score" in data
        assert "explanation" in data
        
        print_success(f"Explanation retrieved")
        print_info(f"Score: {data['overall_score']}/100")
        print_info(f"Target Role: {data['target_role']}")
        print_info(f"Calculated: {data['calculated_at']}")
        
        return True
    except Exception as e:
        print_error(f"Get explanation failed: {e}")
        return False


# Main test runner
def run_all_tests():
    print(f"\n{Colors.BLUE}")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "SkillLens PostgreSQL Migration Test Suite" + " " * 11 + "║")
    print("║" + " " * 20 + "Testing Working Features" + " " * 24 + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"{Colors.END}\n")
    
    print_info(f"Testing against: {BASE_URL}")
    print_info("Make sure the backend is running!")
    print()
    
    time.sleep(1)
    
    results = {}
    
    # Run tests
    results["health"] = test_health_checks()
    if not results["health"]:
        print_error("Backend is not running or not responding!")
        return
    
    token = test_user_registration()
    if token is None:
        # Try login instead
        token = test_user_login()
    
    if not token:
        print_error("Authentication failed! Cannot continue tests.")
        return
    
    results["login"] = True
    
    user_id = test_get_current_user(token)
    if not user_id:
        print_error("Cannot get user profile! Cannot continue tests.")
        return
    
    results["profile"] = True
    
    resume_id, resume_user_id = test_resume_upload()
    results["resume_upload"] = resume_id is not None
    
    if resume_user_id:
        results["get_resume"] = test_get_resume(resume_user_id)
        results["calculate_score"] = test_calculate_readiness_score(resume_user_id)
        results["score_history"] = test_get_score_history(resume_user_id)
        results["explanation"] = test_get_explanation(resume_user_id)
    
    # Summary
    print_section("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {Colors.GREEN}{passed}{Colors.END}")
    print(f"Failed: {Colors.RED}{total - passed}{Colors.END}")
    print(f"Success Rate: {(passed/total*100):.1f}%\n")
    
    for test, result in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if result else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"  {test:20} {status}")
    
    print()
    
    if passed == total:
        print_success("All tests passed! 🎉")
        print_info("Your PostgreSQL migration is working correctly!")
    else:
        print_warning(f"{total - passed} test(s) failed. Check the errors above.")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.END}")
    except Exception as e:
        print_error(f"Test suite error: {e}")
