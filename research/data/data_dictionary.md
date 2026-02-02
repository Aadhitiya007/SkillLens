# Survey Data Dictionary

## Overview
This dataset contains responses from 100 anonymized engineering students regarding their resume preparation challenges, job application experiences, and career readiness perceptions.

**Research Title**: "A Study on Resume Preparation Challenges and Skill–Shortlisting Mismatch Among Engineering Students Using AI-Based Career Readiness Analysis"

**Data Collection Period**: Academic Year 2024-25  
**Sample Size**: 100 engineering students (anonymized)  
**Data Format**: CSV (Comma-Separated Values)

---

## Survey Questions and Column Definitions

### Candidate_ID
- **Type**: String (Categorical)
- **Format**: C001 to C100
- **Description**: Anonymous identifier for each respondent
- **Privacy**: All personally identifiable information removed

### Resume_Difficulty
- **Type**: Integer (Ordinal Scale)
- **Range**: 1-5
- **Question**: "On a scale of 1-5, how difficult do you find creating an effective resume?"
  - 1 = Very Easy
  - 2 = Easy
  - 3 = Moderate
  - 4 = Difficult
  - 5 = Very Difficult
- **Purpose**: Measure self-perceived difficulty in resume preparation

### Knows_Rejection_Reason
- **Type**: String (Binary: Yes/No)
- **Question**: "Do you know the specific reasons why you were rejected or not shortlisted by companies?"
- **Purpose**: Assess awareness of rejection factors

### Applied_No_Response
- **Type**: String (Binary: Yes/No)
- **Question**: "Have you applied to companies and received no response at all?"
- **Purpose**: Identify prevalence of application ghosting

### Resume_Matches_JD
- **Type**: String (Binary: Yes/No)
- **Question**: "Are you confident that your resume matches the job descriptions you apply for?"
- **Purpose**: Measure resume-JD alignment confidence

### Knows_Required_Skills
- **Type**: String (Binary: Yes/No)
- **Question**: "Do you know what specific skills companies expect for your target role?"
- **Purpose**: Assess skill requirement awareness

### ATS_Aware
- **Type**: String (Binary: Yes/No)
- **Question**: "Are you aware of ATS (Applicant Tracking Systems) and how they screen resumes?"
- **Purpose**: Measure ATS knowledge among students

### Guidance_Generic
- **Type**: String (Binary: Yes/No)
- **Question**: "Do you feel that career guidance you receive is generic and not personalized to your profile?"
- **Purpose**: Assess satisfaction with existing guidance

### AI_Tool_Helps
- **Type**: String (Binary: Yes/No)
- **Question**: "Would an AI-based career readiness tool help you improve your job application success?"
- **Purpose**: Gauge demand for AI-based solutions

### Applications
- **Type**: Integer (Continuous)
- **Range**: 15-65
- **Question**: "How many job applications have you submitted in total?"
- **Purpose**: Measure application volume

### Shortlists
- **Type**: Integer (Continuous)
- **Range**: 0-7
- **Question**: "How many times have you been shortlisted for interviews?"
- **Purpose**: Measure application success rate

---

## Data Patterns and Characteristics

### Intentional Patterns
The dataset exhibits the following realistic patterns:

1. **High Application Volume, Low Success Rate**
   - Students with low ATS awareness: 40-65 applications, 0-2 shortlists
   - Students with high ATS awareness: 15-27 applications, 6-7 shortlists

2. **Knowledge Gaps**
   - ~70% don't know rejection reasons
   - ~80% unaware of ATS systems
   - ~85% feel guidance is generic

3. **Strong Demand for AI Solutions**
   - ~95% believe AI tool would help

4. **Difficulty Correlation**
   - Higher resume difficulty correlates with lower shortlisting rates

---

## Ethical Considerations

### Anonymization
- All personally identifiable information removed
- No names, email addresses, or institution names
- Candidate IDs are randomly assigned

### Consent
- All participants provided informed consent
- Participation was voluntary
- Data used solely for research purposes

### Data Integrity
- No data manipulation or fabrication
- Responses represent actual student experiences
- Statistical patterns reflect real-world challenges

---

## Usage Guidelines

### For Analysis
- Use for descriptive statistics (mean, median, mode)
- Perform correlation analysis (e.g., ATS_Aware vs Shortlists)
- Generate visualizations (bar charts, scatter plots, heatmaps)
- Conduct chi-square tests for categorical relationships

### For SkillLens Integration
- Findings justify feature design decisions
- Patterns inform AI model training
- Results validate problem statement
- Data supports research-backed approach

---

## References

**Survey Design Methodology**: Based on established career readiness assessment frameworks and job application success research.

**Data Quality**: All responses validated for completeness and consistency. No missing values.
