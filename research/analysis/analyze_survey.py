"""
Statistical Analysis Script for SkillLens Research Survey
Analyzes survey data to identify patterns and correlations
"""

import pandas as pd
import numpy as np
from scipy import stats
import json
from pathlib import Path

# Load survey data
data_path = Path(__file__).parent.parent / 'data' / 'survey_data.csv'
df = pd.read_csv(data_path)

print("=" * 80)
print("SKILLLENS RESEARCH SURVEY - STATISTICAL ANALYSIS")
print("=" * 80)
print(f"\nDataset: {len(df)} student responses")
print(f"Data loaded from: {data_path}\n")

# ============================================================================
# 1. DESCRIPTIVE STATISTICS
# ============================================================================
print("\n" + "=" * 80)
print("1. DESCRIPTIVE STATISTICS")
print("=" * 80)

# Numeric columns
numeric_stats = df[['Resume_Difficulty', 'Applications', 'Shortlists']].describe()
print("\nNumeric Variables:")
print(numeric_stats)

# Calculate success rate
df['Success_Rate'] = (df['Shortlists'] / df['Applications'] * 100).round(2)
print(f"\nAverage Success Rate: {df['Success_Rate'].mean():.2f}%")
print(f"Median Success Rate: {df['Success_Rate'].median():.2f}%")

# Binary variables - percentage saying "Yes"
binary_cols = ['Knows_Rejection_Reason', 'Applied_No_Response', 'Resume_Matches_JD', 
               'Knows_Required_Skills', 'ATS_Aware', 'Guidance_Generic', 'AI_Tool_Helps']

print("\nBinary Variables (% responding 'Yes'):")
for col in binary_cols:
    yes_pct = (df[col] == 'Yes').sum() / len(df) * 100
    print(f"  {col}: {yes_pct:.1f}%")

# ============================================================================
# 2. CORRELATION ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("2. CORRELATION ANALYSIS")
print("=" * 80)

# Convert binary to numeric for correlation
df_numeric = df.copy()
for col in binary_cols:
    df_numeric[col + '_Numeric'] = (df_numeric[col] == 'Yes').astype(int)

# Key correlations
correlations = {}

# ATS Awareness vs Shortlists
ats_aware_shortlists = df_numeric.groupby('ATS_Aware')['Shortlists'].mean()
print(f"\nATS Awareness vs Shortlists:")
print(f"  ATS Aware (Yes): {ats_aware_shortlists.get('Yes', 0):.2f} avg shortlists")
print(f"  ATS Aware (No): {ats_aware_shortlists.get('No', 0):.2f} avg shortlists")
correlations['ATS_Aware_vs_Shortlists'] = {
    'ATS_Yes': float(ats_aware_shortlists.get('Yes', 0)),
    'ATS_No': float(ats_aware_shortlists.get('No', 0))
}

# Resume Difficulty vs Shortlists
difficulty_corr = df['Resume_Difficulty'].corr(df['Shortlists'])
print(f"\nResume Difficulty vs Shortlists Correlation: {difficulty_corr:.3f}")
correlations['Difficulty_vs_Shortlists'] = float(difficulty_corr)

# Knows Required Skills vs Shortlists
skills_shortlists = df_numeric.groupby('Knows_Required_Skills')['Shortlists'].mean()
print(f"\nKnows Required Skills vs Shortlists:")
print(f"  Knows Skills (Yes): {skills_shortlists.get('Yes', 0):.2f} avg shortlists")
print(f"  Knows Skills (No): {skills_shortlists.get('No', 0):.2f} avg shortlists")
correlations['Skills_vs_Shortlists'] = {
    'Skills_Yes': float(skills_shortlists.get('Yes', 0)),
    'Skills_No': float(skills_shortlists.get('No', 0))
}

# Applications vs Shortlists
apps_corr = df['Applications'].corr(df['Shortlists'])
print(f"\nApplications vs Shortlists Correlation: {apps_corr:.3f}")
correlations['Applications_vs_Shortlists'] = float(apps_corr)

# ============================================================================
# 3. CHI-SQUARE TESTS (Categorical Relationships)
# ============================================================================
print("\n" + "=" * 80)
print("3. CHI-SQUARE TESTS FOR CATEGORICAL RELATIONSHIPS")
print("=" * 80)

# Create binary success indicator (at least 1 shortlist)
df['Has_Shortlist'] = (df['Shortlists'] > 0).astype(int)

chi_square_results = {}

# ATS Awareness vs Success
contingency_ats = pd.crosstab(df['ATS_Aware'], df['Has_Shortlist'])
chi2_ats, p_ats, dof_ats, expected_ats = stats.chi2_contingency(contingency_ats)
print(f"\nATS Awareness vs Success:")
print(f"  Chi-square statistic: {chi2_ats:.3f}")
print(f"  P-value: {p_ats:.4f}")
print(f"  Significant: {'Yes' if p_ats < 0.05 else 'No'}")
chi_square_results['ATS_vs_Success'] = {
    'chi2': float(chi2_ats),
    'p_value': float(p_ats),
    'significant': bool(p_ats < 0.05)
}

# Knows Required Skills vs Success
contingency_skills = pd.crosstab(df['Knows_Required_Skills'], df['Has_Shortlist'])
chi2_skills, p_skills, dof_skills, expected_skills = stats.chi2_contingency(contingency_skills)
print(f"\nKnows Required Skills vs Success:")
print(f"  Chi-square statistic: {chi2_skills:.3f}")
print(f"  P-value: {p_skills:.4f}")
print(f"  Significant: {'Yes' if p_skills < 0.05 else 'No'}")
chi_square_results['Skills_vs_Success'] = {
    'chi2': float(chi2_skills),
    'p_value': float(p_skills),
    'significant': bool(p_skills < 0.05)
}

# ============================================================================
# 4. KEY FINDINGS SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("4. KEY FINDINGS SUMMARY")
print("=" * 80)

findings = []

# Finding 1: Rejection Awareness
rejection_aware_pct = (df['Knows_Rejection_Reason'] == 'Yes').sum() / len(df) * 100
finding1 = f"Only {rejection_aware_pct:.1f}% of students know why they were rejected"
print(f"\n✓ {finding1}")
findings.append(finding1)

# Finding 2: Generic Guidance
generic_pct = (df['Guidance_Generic'] == 'Yes').sum() / len(df) * 100
finding2 = f"{generic_pct:.1f}% feel current guidance is generic and not personalized"
print(f"✓ {finding2}")
findings.append(finding2)

# Finding 3: ATS Awareness
ats_aware_pct = (df['ATS_Aware'] == 'Yes').sum() / len(df) * 100
finding3 = f"Only {ats_aware_pct:.1f}% are aware of ATS systems"
print(f"✓ {finding3}")
findings.append(finding3)

# Finding 4: ATS Impact
ats_impact = ats_aware_shortlists.get('Yes', 0) / ats_aware_shortlists.get('No', 1)
finding4 = f"Students with ATS awareness have {ats_impact:.1f}x higher shortlisting rates"
print(f"✓ {finding4}")
findings.append(finding4)

# Finding 5: AI Tool Demand
ai_demand_pct = (df['AI_Tool_Helps'] == 'Yes').sum() / len(df) * 100
finding5 = f"{ai_demand_pct:.1f}% believe an AI-based tool would help them"
print(f"✓ {finding5}")
findings.append(finding5)

# Finding 6: Success Rate
avg_success = df['Success_Rate'].mean()
finding6 = f"Average success rate is only {avg_success:.2f}% (shortlists/applications)"
print(f"✓ {finding6}")
findings.append(finding6)

# ============================================================================
# 5. EXPORT RESULTS
# ============================================================================
print("\n" + "=" * 80)
print("5. EXPORTING RESULTS")
print("=" * 80)

# Prepare results dictionary
results = {
    'dataset_info': {
        'total_responses': len(df),
        'data_file': str(data_path)
    },
    'descriptive_stats': {
        'resume_difficulty': {
            'mean': float(df['Resume_Difficulty'].mean()),
            'median': float(df['Resume_Difficulty'].median()),
            'std': float(df['Resume_Difficulty'].std())
        },
        'applications': {
            'mean': float(df['Applications'].mean()),
            'median': float(df['Applications'].median()),
            'std': float(df['Applications'].std())
        },
        'shortlists': {
            'mean': float(df['Shortlists'].mean()),
            'median': float(df['Shortlists'].median()),
            'std': float(df['Shortlists'].std())
        },
        'success_rate': {
            'mean': float(df['Success_Rate'].mean()),
            'median': float(df['Success_Rate'].median())
        }
    },
    'binary_percentages': {
        col: float((df[col] == 'Yes').sum() / len(df) * 100)
        for col in binary_cols
    },
    'correlations': correlations,
    'chi_square_tests': chi_square_results,
    'key_findings': findings
}

# Save to JSON
output_json = Path(__file__).parent / 'analysis_results.json'
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)
print(f"\n✓ Results exported to: {output_json}")

# Save to Markdown
output_md = Path(__file__).parent / 'statistical_summary.md'
with open(output_md, 'w', encoding='utf-8') as f:
    f.write("# Statistical Analysis Summary\n\n")
    f.write(f"**Dataset**: {len(df)} student responses\n\n")
    
    f.write("## Key Findings\n\n")
    for i, finding in enumerate(findings, 1):
        f.write(f"{i}. {finding}\n")
    
    f.write("\n## Descriptive Statistics\n\n")
    f.write("| Metric | Mean | Median | Std Dev |\n")
    f.write("|--------|------|--------|----------|\n")
    f.write(f"| Resume Difficulty (1-5) | {df['Resume_Difficulty'].mean():.2f} | {df['Resume_Difficulty'].median():.1f} | {df['Resume_Difficulty'].std():.2f} |\n")
    f.write(f"| Applications | {df['Applications'].mean():.1f} | {df['Applications'].median():.1f} | {df['Applications'].std():.2f} |\n")
    f.write(f"| Shortlists | {df['Shortlists'].mean():.2f} | {df['Shortlists'].median():.1f} | {df['Shortlists'].std():.2f} |\n")
    f.write(f"| Success Rate (%) | {df['Success_Rate'].mean():.2f} | {df['Success_Rate'].median():.2f} | {df['Success_Rate'].std():.2f} |\n")
    
    f.write("\n## Binary Variables (% Yes)\n\n")
    for col in binary_cols:
        yes_pct = (df[col] == 'Yes').sum() / len(df) * 100
        f.write(f"- **{col}**: {yes_pct:.1f}%\n")
    
    f.write("\n## Correlations\n\n")
    f.write(f"- **ATS Awareness → Shortlists**: ATS-aware students get {ats_aware_shortlists.get('Yes', 0):.2f} vs {ats_aware_shortlists.get('No', 0):.2f} shortlists\n")
    f.write(f"- **Resume Difficulty ↔ Shortlists**: r = {difficulty_corr:.3f} (negative correlation)\n")
    f.write(f"- **Applications ↔ Shortlists**: r = {apps_corr:.3f}\n")

print(f"✓ Summary exported to: {output_md}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
