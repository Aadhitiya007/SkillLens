# SkillLens Research Component

## Overview

This directory contains the complete research foundation for SkillLens, including empirical survey data, statistical analysis, and academic documentation.

**Research Title**: "A Study on Resume Preparation Challenges and Skill–Shortlisting Mismatch Among Engineering Students Using AI-Based Career Readiness Analysis"

---

## Directory Structure

```
research/
├── data/                      # Survey data
│   ├── survey_data.csv       # 100 student responses
│   └── data_dictionary.md    # Data documentation
├── analysis/                  # Statistical analysis
│   ├── analyze_survey.py     # Analysis script
│   ├── visualize_findings.py # Visualization script
│   ├── analysis_results.json # Generated results
│   └── statistical_summary.md # Summary report
├── visualizations/            # Generated charts (7 PNG files)
│   ├── awareness_metrics.png
│   ├── problem_indicators.png
│   ├── ats_awareness_impact.png
│   ├── applications_vs_shortlists.png
│   ├── success_rate_comparison.png
│   ├── correlation_heatmap.png
│   └── resume_difficulty_distribution.png
├── docs/                      # Research documentation
│   ├── methodology.md        # Research design
│   ├── findings.md           # Detailed findings
│   ├── research_to_features.md # Feature justifications
│   └── viva_defense_guide.md # Viva preparation
└── requirements.txt           # Python dependencies
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Statistical Analysis

```bash
cd analysis
python analyze_survey.py
```

**Output**:
- `analysis_results.json` - Complete statistical results
- `statistical_summary.md` - Human-readable summary

### 3. Generate Visualizations

```bash
cd analysis
python visualize_findings.py
```

**Output**: 7 publication-quality PNG charts in `visualizations/`

---

## Key Research Findings

### Statistical Highlights

| Metric | Value | Significance |
|--------|-------|--------------|
| **Sample Size** | 100 students | n=100 |
| **Rejection Awareness** | 24% | Only 1 in 4 know why rejected |
| **ATS Awareness** | 26% | Critical knowledge gap |
| **ATS Impact** | **5.9x** | Shortlisting multiplier (p=0.002) |
| **Skills Impact** | **7.4x** | Shortlisting multiplier (p<0.001) |
| **Generic Guidance** | 76% | Dissatisfaction with current support |
| **AI Tool Demand** | 100% | Universal demand |
| **Success Rate** | 9.5% | Average shortlists/applications |

### Chi-Square Validation

- **ATS Awareness vs Success**: χ² = 9.39, p = 0.002 (highly significant)
- **Skills Knowledge vs Success**: χ² = 26.67, p < 0.001 (extremely significant)

---

## Research-to-Feature Mapping

| Survey Finding | SkillLens Feature |
|----------------|-------------------|
| 76% rejection blindness | Explainable Readiness Score |
| 76% generic guidance | Adaptive AI Learning Agent |
| 26% ATS aware, 5.9x impact | ATS-Aligned Resume Analysis |
| 52% unaware of skills, 7.4x impact | Skill Gap Identification |
| 76% lack resume-JD confidence | Semantic Resume-JD Matching |
| 9.5% success rate | Predictive Readiness Modeling |
| 3.5/5 difficulty, r=-0.907 | AI-Powered Resume Builder |

---

## Documentation

### For Academic Review

1. **[Methodology](docs/methodology.md)** - Research design, sampling, survey instrument, ethics
2. **[Findings](docs/findings.md)** - Comprehensive statistical analysis with visualizations
3. **[Research-to-Features](docs/research_to_features.md)** - Explicit feature justifications

### For Viva Defense

4. **[Viva Defense Guide](docs/viva_defense_guide.md)** - Prepared answers for 12+ common questions

### For Data Analysis

5. **[Data Dictionary](data/data_dictionary.md)** - Survey design and variable definitions
6. **[Statistical Summary](analysis/statistical_summary.md)** - Quick reference results

---

## Visualizations

All visualizations are publication-ready (300 DPI, professional styling):

1. **Awareness Metrics** - Student awareness of key factors
2. **Problem Indicators** - Validation of problems SkillLens solves
3. **ATS Awareness Impact** - Dramatic effect of ATS knowledge
4. **Applications vs Shortlists** - Scatter plot with trend line
5. **Success Rate Comparison** - Impact of knowledge factors
6. **Correlation Heatmap** - Relationships between variables
7. **Resume Difficulty Distribution** - Self-reported difficulty levels

---

## Using This Research

### For Project Report

1. Include methodology in "Research Design" section
2. Present key findings with visualizations
3. Use research-to-features mapping to justify design decisions
4. Cite statistical validation (chi-square, correlations)

### For Viva Preparation

1. Read [Viva Defense Guide](docs/viva_defense_guide.md)
2. Memorize key numbers (see Quick Reference table)
3. Practice answers to common questions
4. Review visualizations to explain visually

### For Feature Development

1. Consult [Research-to-Features](docs/research_to_features.md) for justifications
2. Use findings to prioritize features
3. Measure success against baseline metrics
4. Validate with users that features address validated problems

---

## Reproducing Analysis

### Re-run Analysis

```bash
cd analysis
python analyze_survey.py
python visualize_findings.py
```

### Modify Survey Data

1. Edit `data/survey_data.csv`
2. Maintain same column structure
3. Re-run analysis scripts
4. New results and visualizations generated automatically

---

## Academic Rigor

### Validity

- ✓ Structured survey instrument
- ✓ Clear operational definitions
- ✓ Standardized data collection
- ✓ Statistical validation (chi-square, correlation)

### Reliability

- ✓ Based on established frameworks
- ✓ Consistent response patterns
- ✓ Reproducible analysis

### Ethics

- ✓ Informed consent
- ✓ Anonymization (no PII)
- ✓ Voluntary participation
- ✓ Secure data storage

---

## Citation

If using this research, please cite:

```
SkillLens Research Team (2024). "A Study on Resume Preparation Challenges 
and Skill–Shortlisting Mismatch Among Engineering Students Using AI-Based 
Career Readiness Analysis." SkillLens Project Documentation.
```

---

## Contact

For questions about the research methodology or findings, please refer to the documentation or open an issue in the main repository.

---

**Research Version**: 1.0  
**Last Updated**: December 31, 2024  
**Dataset**: 100 engineering students  
**Analysis Tools**: Python (pandas, scipy, matplotlib, seaborn)
