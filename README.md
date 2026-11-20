<<<<<<< HEAD
# SkillLens — AI Career Intelligence Platform

Upload resume → GitHub + LinkedIn verification → 30Q skill test → certified learning plan → company mock interviews

## ✅ Quick Start (VS Code)

### 1. Get your Anthropic API key
Go to [console.anthropic.com](https://console.anthropic.com) → API Keys → Create Key

### 2. Add your API key
Open `.env.local` and replace the placeholder with your real key:
```
VITE_ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxx
```

### 3. Install and run
```bash
=======
# 🔷 SkillLens

**AI-Powered Career Intelligence & Workforce Readiness Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)

![SkillLens Banner](.github/images/banner.png)

SkillLens is an AI-powered career intelligence platform that predicts, explains, and optimizes employability using semantic NLP, knowledge graphs, and adaptive AI agents.

## 📸 Platform Overview

### Dashboard Preview
![Dashboard Mockup](.github/images/dashboard.png)

### How It Works
![Workflow Diagram](.github/images/workflow.png)

## 🎯 Features

![Features Showcase](.github/images/features.png)

### Core Modules

1. **Resume & Profile Intelligence** - Semantic skill extraction using Sentence-BERT
2. **Skill Ontology & Knowledge Graph** - Neo4j-based skill hierarchy and dependency detection
3. **Explainable Career Readiness Scoring** - XAI-powered readiness assessment with plain-English explanations
4. **Career Readiness Prediction Engine** - Time-series ML for 30/60/90 day forecasts
5. **Adaptive Learning Agent** - LangChain-based agent for dynamic learning path generation
6. **Skill Verification Engine** - AI-generated assessments and confidence scoring
7. **Job Market Intelligence** - Real-time job market data and trend analysis
8. **Institutional Analytics** - Placement cell dashboards and department-wise analytics

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **NLP**: Hugging Face Sentence-BERT
- **LLM**: OpenAI GPT-3.5
- **Agent**: LangChain
- **ML**: Scikit-learn, TensorFlow/PyTorch
- **Databases**: MongoDB, Neo4j

### Frontend
- **Framework**: Next.js 14 (React 18)
- **Styling**: TailwindCSS
- **Charts**: Recharts
- **Graph Viz**: D3.js

### Infrastructure
- **Containerization**: Docker
- **Deployment**: Render / AWS

### System Architecture
![Architecture Diagram](.github/images/architecture.png)

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### API Keys Required

Create a `.env` file in the root directory (see `.env.example`):

```env
# OpenAI
OPENAI_API_KEY=your_openai_key

# Hugging Face
HUGGINGFACE_API_KEY=your_hf_key

# SerpAPI
SERPAPI_KEY=your_serpapi_key

# MongoDB
MONGODB_URI=mongodb://mongodb:27017/skilllens

# Neo4j
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# JWT
JWT_SECRET=your_jwt_secret
```

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/xmanojpx/SkillLens.git
   cd SkillLens
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start services with Docker**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Neo4j Browser: http://localhost:7474

### Local Development (without Docker)

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
>>>>>>> ef5fe4969dc5015a2f1823b2a57d7a57265e143c
npm install
npm run dev
```

<<<<<<< HEAD
Open [http://localhost:5173](http://localhost:5173)

## How it works (no backend needed)
The Vite dev server proxies `/api/v1/messages` → `https://api.anthropic.com/v1/messages`.
Your API key stays in `.env.local` and is injected at the proxy level — it never goes to the browser.

## Features
- **Resume Upload** — PDF, PNG, JPG, WEBP or paste text
- **GitHub Verification** — Live API checks repos, languages, activity
- **LinkedIn AI Check** — NLP analysis of profile credibility
- **30Q Skill Test** — Auto-generated from YOUR resume skills
- **Company Mock Test** — Styled like Google/Amazon/TCS real interviews (year-specific)
- **Certified Learning Path** — Coursera, Udemy, edX + YouTube tutorials

## ⚠️ Security
- Never commit `.env.local` to GitHub — it's already in `.gitignore`
- The API key is injected by the Vite proxy (server-side), NOT exposed to the browser
- Auth and user data are stored in `localStorage` (local only, no external database)

## Bugs fixed in this version
- Timer expiry now correctly captures all answered questions (stale closure fix)
- Submit button passes current answer state correctly
- YouTube playlist URL generation in learning plan fixed
- Double-submission of quiz results prevented with `finishedRef`
=======
## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🏗️ Project Structure

```
SkilLens/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # Application entry point
│   │   ├── config.py       # Configuration management
│   │   ├── models/         # Pydantic models
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── database/       # Database clients
│   │   └── utils/          # Utilities
│   ├── tests/              # Backend tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities
│   │   └── styles/        # Global styles
│   ├── package.json
│   └── Dockerfile
├── research/               # Research component
│   ├── data/              # Survey data (100 students)
│   ├── analysis/          # Statistical analysis scripts
│   ├── visualizations/    # Generated charts (7 PNG files)
│   ├── docs/              # Research documentation
│   └── requirements.txt   # Analysis dependencies
├── docker-compose.yml      # Multi-container setup
├── .env.example           # Environment template
└── README.md
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📊 Database Setup

### Neo4j Initial Setup

The skill knowledge graph is initialized on first run. To manually populate:

```bash
# Access Neo4j browser at http://localhost:7474
# Run initialization script
python backend/scripts/init_skill_graph.py
```

## 🎓 Use Cases

### For Students
- Upload resume and get instant career readiness score
- Discover skill gaps with explanations
- Get personalized learning roadmaps
- Track progress with adaptive AI agent
- Verify skills with AI-generated assessments

### For Institutions
- Department-wise employability analytics
- Skill gap heatmaps
- Placement readiness tracking
- Role-wise trend analysis

## 🔬 Research Foundation

> [!IMPORTANT]
> **SkillLens is built on empirical research, not assumptions.**

![Research Statistics](.github/images/research-stats.png)

### Research Study

**Title**: "A Study on Resume Preparation Challenges and Skill–Shortlisting Mismatch Among Engineering Students Using AI-Based Career Readiness Analysis"

**Methodology**: Structured survey of 100 engineering students with statistical validation

### Key Research Findings

| Finding | Impact | SkillLens Solution |
|---------|--------|-------------------|
| **76% don't know rejection reasons** | Students cannot improve without feedback | Explainable readiness scores |
| **Only 26% ATS aware** | ATS-aware students get **5.9x more shortlists** (p=0.002) | ATS-aligned resume analysis |
| **52% don't know required skills** | Skills-aware students get **7.4x more shortlists** (p<0.001) | Skill gap identification |
| **76% feel guidance is generic** | One-size-fits-all advice fails | Adaptive AI learning agent |
| **9.5% average success rate** | 2.34 shortlists from 40.5 applications | Predictive readiness modeling |
| **100% want AI-based tool** | Universal demand for intelligent solutions | Complete SkillLens platform |

### Statistical Validation

- **Chi-square tests**: ATS awareness (χ² = 9.39, p = 0.002), Skills knowledge (χ² = 26.67, p < 0.001)
- **Correlation analysis**: Resume difficulty vs shortlists (r = -0.907)
- **7 publication-quality visualizations** generated from survey data

### Research-to-Feature Traceability

Every major SkillLens feature maps directly to a statistically validated finding:

1. **Explainable Readiness Score** ← 76% rejection blindness
2. **Adaptive AI Agent** ← 76% generic guidance problem
3. **ATS-Aligned Analysis** ← 26% awareness, 5.9x impact
4. **Skill Gap Identification** ← 52% unaware, 7.4x impact
5. **Semantic Resume-JD Matching** ← 76% lack confidence
6. **Predictive Modeling** ← 9.5% success rate
7. **AI Resume Builder** ← 3.5/5 difficulty, r = -0.907

### Research Documentation

Comprehensive research materials available in [`/research`](file:///f:/SkilLens/research):

- **[Methodology](file:///f:/SkilLens/research/docs/methodology.md)**: Research design, sampling, survey instrument
- **[Findings](file:///f:/SkilLens/research/docs/findings.md)**: Statistical analysis and key insights
- **[Research-to-Features](file:///f:/SkilLens/research/docs/research_to_features.md)**: Explicit feature justifications
- **[Viva Defense Guide](file:///f:/SkilLens/research/docs/viva_defense_guide.md)**: Academic defense preparation
- **[Survey Data](file:///f:/SkilLens/research/data/survey_data.csv)**: Complete dataset (100 students)
- **[Visualizations](file:///f:/SkilLens/research/visualizations)**: 7 publication-ready charts

### Technical Innovation

SkillLens incorporates:
- **Semantic NLP** for resume understanding beyond keywords
- **Knowledge Graphs** for skill relationship modeling
- **Explainable AI (XAI)** for transparent scoring
- **Predictive Modeling** for career trajectory forecasting
- **Agentic AI** for adaptive learning path generation


## 📝 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct, development process, and how to submit pull requests.

## 📧 Contact

For questions, support, or bug reports, please [open an issue](https://github.com/xmanojpx/SkillLens/issues) on GitHub.

---

**Built with ❤️ for career intelligence and workforce readiness**
>>>>>>> ef5fe4969dc5015a2f1823b2a57d7a57265e143c
