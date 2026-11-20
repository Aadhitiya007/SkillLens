-- SkillLens PostgreSQL Database Schema
-- Complete schema for all application data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'student',
    department VARCHAR(100),
    register_number VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Resumes table
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    parsed_data JSONB,  -- Stores parsed resume data as JSON
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Readiness scores table
CREATE TABLE readiness_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    resume_id UUID REFERENCES resumes(id) ON DELETE SET NULL,
    target_role VARCHAR(255) NOT NULL,
    overall_score NUMERIC(5,2) NOT NULL,
    technical_skills_score NUMERIC(5,2),
    experience_score NUMERIC(5,2),
    project_score NUMERIC(5,2),
    tool_score NUMERIC(5,2),
    explanation TEXT,
    strengths JSONB,  -- Array of strings
    weaknesses JSONB,  -- Array of strings
    recommendations JSONB,  -- Array of strings
    factors JSONB,  -- Detailed factor breakdown
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Assessments table
CREATE TABLE assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill VARCHAR(100) NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    questions JSONB NOT NULL,  -- Array of question objects
    total_points INTEGER NOT NULL,
    time_limit_minutes INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Assessment results table
CREATE TABLE assessment_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    answers JSONB NOT NULL,  -- Array of answer objects
    score INTEGER NOT NULL,
    max_score INTEGER NOT NULL,
    percentage NUMERIC(5,2) NOT NULL,
    confidence_level VARCHAR(50) NOT NULL,
    passed BOOLEAN NOT NULL,
    feedback JSONB,  -- Array of feedback strings
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Learning plans table
CREATE TABLE learning_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_role VARCHAR(255) NOT NULL,
    current_skills JSONB NOT NULL,  -- Array of skills
    target_skills JSONB NOT NULL,  -- Array of skills
    learning_path JSONB NOT NULL,  -- Array of learning step objects
    estimated_weeks INTEGER,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Learning progress table
CREATE TABLE learning_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    learning_plan_id UUID REFERENCES learning_plans(id) ON DELETE CASCADE,
    skill VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,  -- 'not_started', 'in_progress', 'completed'
    progress_percentage INTEGER DEFAULT 0,
    notes TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Job listings table (cached from external APIs)
CREATE TABLE job_listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    description TEXT,
    required_skills JSONB,  -- Array of skills
    salary_range VARCHAR(100),
    job_type VARCHAR(50),
    experience_level VARCHAR(50),
    source VARCHAR(100),  -- 'serpapi', 'linkedin', etc.
    external_url TEXT,
    posted_date DATE,
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Predictions table (shortlisting probability)
CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    resume_id UUID REFERENCES resumes(id) ON DELETE SET NULL,
    job_description TEXT NOT NULL,
    shortlist_probability NUMERIC(5,2) NOT NULL,
    confidence VARCHAR(50) NOT NULL,
    factors JSONB NOT NULL,  -- Contributing factors
    recommendations JSONB,  -- Improvement suggestions
    predicted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Conversation history table (for AI agent)
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID NOT NULL,
    role VARCHAR(50) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    metadata JSONB,  -- Additional context
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Skills table (optional, if not using Neo4j)
CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(100),
    description TEXT,
    difficulty_level VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Skill prerequisites table (optional, if not using Neo4j)
CREATE TABLE skill_prerequisites (
    skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    prerequisite_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    importance VARCHAR(50) DEFAULT 'recommended',  -- 'required' or 'recommended'
    PRIMARY KEY (skill_id, prerequisite_id)
);

-- Indexes for performance
CREATE INDEX idx_resumes_user_id ON resumes(user_id);
CREATE INDEX idx_resumes_uploaded_at ON resumes(uploaded_at DESC);

CREATE INDEX idx_readiness_scores_user_id ON readiness_scores(user_id);
CREATE INDEX idx_readiness_scores_created_at ON readiness_scores(created_at DESC);

CREATE INDEX idx_assessments_user_id ON assessments(user_id);
CREATE INDEX idx_assessments_skill ON assessments(skill);

CREATE INDEX idx_assessment_results_user_id ON assessment_results(user_id);
CREATE INDEX idx_assessment_results_assessment_id ON assessment_results(assessment_id);

CREATE INDEX idx_learning_plans_user_id ON learning_plans(user_id);
CREATE INDEX idx_learning_plans_status ON learning_plans(status);

CREATE INDEX idx_learning_progress_user_id ON learning_progress(user_id);
CREATE INDEX idx_learning_progress_plan_id ON learning_progress(learning_plan_id);

CREATE INDEX idx_job_listings_posted_date ON job_listings(posted_date DESC);
CREATE INDEX idx_job_listings_location ON job_listings(location);

CREATE INDEX idx_predictions_user_id ON predictions(user_id);
CREATE INDEX idx_predictions_predicted_at ON predictions(predicted_at DESC);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_session_id ON conversations(session_id);

CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_skills_name ON skills(name);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resumes_updated_at BEFORE UPDATE ON resumes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_plans_updated_at BEFORE UPDATE ON learning_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_progress_updated_at BEFORE UPDATE ON learning_progress
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE users IS 'User accounts with authentication and profile information';
COMMENT ON TABLE resumes IS 'Uploaded resumes with parsed data stored as JSONB';
COMMENT ON TABLE readiness_scores IS 'Career readiness assessment scores with detailed breakdown';
COMMENT ON TABLE assessments IS 'Skill verification assessments with questions';
COMMENT ON TABLE assessment_results IS 'User responses and scores for assessments';
COMMENT ON TABLE learning_plans IS 'Personalized learning paths for skill development';
COMMENT ON TABLE learning_progress IS 'User progress tracking for learning plans';
COMMENT ON TABLE job_listings IS 'Cached job listings from external APIs';
COMMENT ON TABLE predictions IS 'Shortlisting probability predictions';
COMMENT ON TABLE conversations IS 'AI agent conversation history';
COMMENT ON TABLE skills IS 'Skill catalog (optional if not using Neo4j)';
COMMENT ON TABLE skill_prerequisites IS 'Skill dependency graph (optional if not using Neo4j)';
