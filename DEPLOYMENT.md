"""
Deployment guide for SkillLens
Complete instructions for deploying to production.
"""

# SkillLens Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- Domain name (optional, for production)
- SSL certificate (optional, for HTTPS)

## Environment Setup

1. **Create .env file in root directory**:

```env
# OpenAI API Key (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Database Credentials
MONGODB_USER=admin
MONGODB_PASSWORD=your_secure_password
NEO4J_PASSWORD=your_secure_password

# Application Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# CORS Origins
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## Local Deployment

### Using Docker Compose

1. **Build and start all services**:
```bash
docker-compose up -d --build
```

2. **Check service status**:
```bash
docker-compose ps
```

3. **View logs**:
```bash
docker-compose logs -f
```

4. **Access services**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MongoDB: localhost:27017
- Neo4j Browser: http://localhost:7474

### Without Docker

1. **Start MongoDB and Neo4j** (using Docker or local installation)

2. **Backend**:
```bash
cd backend
pip install -r requirements.txt
python -m app.services.model_trainer  # Train ML model
uvicorn app.main:app --reload
```

3. **Frontend**:
```bash
cd frontend
npm install
npm run dev
```

## Production Deployment

### Option 1: Render (Recommended for Quick Deploy)

#### Backend Deployment

1. Create new Web Service on Render
2. Connect GitHub repository
3. Configure:
   - **Build Command**: `pip install -r requirements.txt && python -m app.services.model_trainer`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: Add all from .env

#### Frontend Deployment

1. Create new Static Site on Render
2. Configure:
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `.next`

### Option 2: AWS Deployment

#### Using AWS ECS (Elastic Container Service)

1. **Push Docker images to ECR**:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t skillens-backend ./backend
docker tag skillens-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/skillens-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/skillens-backend:latest
```

2. **Create ECS Task Definition**
3. **Create ECS Service**
4. **Configure Load Balancer**

#### Database Setup

- **MongoDB**: Use MongoDB Atlas (managed service)
- **Neo4j**: Use Neo4j Aura (managed service)

### Option 3: DigitalOcean App Platform

1. **Create new app**
2. **Connect repository**
3. **Configure components**:
   - Backend: Python app
   - Frontend: Static site
   - Databases: Managed MongoDB and PostgreSQL (or use external Neo4j)

## Post-Deployment

### 1. Train ML Model

```bash
# SSH into backend container/server
python -m app.services.model_trainer
```

### 2. Initialize Databases

```bash
# MongoDB: Create indexes
# Neo4j: Load skill graph data
```

### 3. Verify Deployment

```bash
# Test health endpoints
curl https://your-api-domain.com/health
curl https://your-api-domain.com/api/agent/health
curl https://your-api-domain.com/api/predictions/health
```

### 4. Monitor Services

- Set up logging (CloudWatch, Datadog, etc.)
- Configure alerts
- Monitor API response times
- Track error rates

## Scaling

### Horizontal Scaling

- Use load balancer
- Deploy multiple backend instances
- Use Redis for session management

### Database Scaling

- MongoDB: Enable sharding
- Neo4j: Use clustering
- Add read replicas

## Security Checklist

- [ ] HTTPS enabled
- [ ] API keys in environment variables (not code)
- [ ] Database credentials secured
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention
- [ ] XSS protection

## Backup Strategy

### Automated Backups

```bash
# MongoDB backup
mongodump --uri="mongodb://..." --out=/backups/$(date +%Y%m%d)

# Neo4j backup
neo4j-admin backup --backup-dir=/backups/$(date +%Y%m%d)
```

### Backup Schedule

- Daily: Full database backup
- Hourly: Incremental backups
- Weekly: ML model snapshots

## Troubleshooting

### Backend won't start

- Check MongoDB connection
- Verify Neo4j connection
- Check OpenAI API key
- Review logs: `docker-compose logs backend`

### Frontend build fails

- Clear node_modules: `rm -rf node_modules && npm install`
- Check environment variables
- Verify API URL configuration

### ML predictions not working

- Ensure model is trained: `python -m app.services.model_trainer`
- Check model file exists: `backend/models/shortlist_predictor.pkl`
- Verify scikit-learn version matches

## Maintenance

### Regular Updates

```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker-compose down
docker-compose up -d --build

# Retrain model if needed
docker-compose exec backend python -m app.services.model_trainer
```

### Database Maintenance

- Weekly: Optimize indexes
- Monthly: Analyze query performance
- Quarterly: Review and archive old data

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review API docs: `/docs`
- Check health endpoints: `/health`

---

**Deployment Checklist**:
- [ ] Environment variables configured
- [ ] Databases running
- [ ] ML model trained
- [ ] HTTPS enabled
- [ ] Monitoring set up
- [ ] Backups configured
- [ ] Security hardened
- [ ] Load testing completed
