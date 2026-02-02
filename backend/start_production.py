#!/usr/bin/env python
"""
SkillLens Production Startup Script
Starts the production backend with all features enabled.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from app_production import app

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting SkillLens Production Backend")
    print("=" * 70)
    print()
    print("📋 Configuration:")
    print("  • Port: 8000")
    print("  • Host: 0.0.0.0")
    print("  • Environment: Production")
    print()
    print("✨ Features Enabled:")
    print("  ✅ JWT Authentication")
    print("  ✅ MongoDB Persistence")
    print("  ✅ Neo4j Knowledge Graph")
    print("  ✅ Sentence-BERT Resume Parser")
    print("  ✅ LangChain AI Agent")
    print("  ✅ ML Predictive Models")
    print("  ✅ Real-time Analytics")
    print()
    print("📚 Documentation:")
    print("  • API Docs: http://localhost:8000/docs")
    print("  • Health Check: http://localhost:8000/health")
    print()
    print("=" * 70)
    print()
    
    uvicorn.run(
        "app_production:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload in production
        log_level="info",
        access_log=True
    )
