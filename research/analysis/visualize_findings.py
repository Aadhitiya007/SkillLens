"""
Visualization Script for SkillLens Research Survey
Generates publication-quality charts and graphs
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style for professional-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

# Load data
data_path = Path(__file__).parent.parent / 'data' / 'survey_data.csv'
df = pd.read_csv(data_path)

# Create output directory
viz_dir = Path(__file__).parent.parent / 'visualizations'
viz_dir.mkdir(exist_ok=True)

print("=" * 80)
print("GENERATING VISUALIZATIONS FOR SKILLLENS RESEARCH")
print("=" * 80)
print(f"\nOutput directory: {viz_dir}\n")

# ============================================================================
# 1. AWARENESS METRICS BAR CHART
# ============================================================================
print("1. Creating Awareness Metrics Bar Chart...")

binary_cols = ['Knows_Rejection_Reason', 'ATS_Aware', 'Knows_Required_Skills', 
               'Resume_Matches_JD']
labels = ['Knows Why\nRejected', 'ATS\nAware', 'Knows Required\nSkills', 
          'Resume Matches\nJob Description']

percentages = [(df[col] == 'Yes').sum() / len(df) * 100 for col in binary_cols]

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.bar(labels, percentages, color=['#e74c3c', '#e74c3c', '#3498db', '#3498db'], 
              edgecolor='black', linewidth=1.5, alpha=0.8)

# Add percentage labels on bars
for bar, pct in zip(bars, percentages):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{pct:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=12)

ax.set_ylabel('Percentage of Students (%)', fontweight='bold')
ax.set_title('Student Awareness of Key Career Readiness Factors\n(n=100)', 
             fontweight='bold', pad=20)
ax.set_ylim(0, 100)
ax.axhline(y=50, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='50% Threshold')
ax.legend()

plt.tight_layout()
output_file = viz_dir / 'awareness_metrics.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: {output_file}")
plt.close()

# ============================================================================
# 2. PROBLEM INDICATORS BAR CHART
# ============================================================================
print("2. Creating Problem Indicators Bar Chart...")

problem_cols = ['Applied_No_Response', 'Guidance_Generic', 'AI_Tool_Helps']
problem_labels = ['Applied but\nNo Response', 'Guidance is\nGeneric', 'AI Tool\nWould Help']
problem_pcts = [(df[col] == 'Yes').sum() / len(df) * 100 for col in problem_cols]

fig, ax = plt.subplots(figsize=(10, 7))
bars = ax.bar(problem_labels, problem_pcts, 
              color=['#e67e22', '#e67e22', '#27ae60'], 
              edgecolor='black', linewidth=1.5, alpha=0.8)

for bar, pct in zip(bars, problem_pcts):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{pct:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=12)

ax.set_ylabel('Percentage of Students (%)', fontweight='bold')
ax.set_title('Problem Indicators and Solution Demand\n(n=100)', 
             fontweight='bold', pad=20)
ax.set_ylim(0, 110)

plt.tight_layout()
output_file = viz_dir / 'problem_indicators.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: {output_file}")
plt.close()

# ============================================================================
# 3. ATS AWARENESS IMPACT
# ============================================================================
print("3. Creating ATS Awareness Impact Chart...")

ats_groups = df.groupby('ATS_Aware').agg({
    'Shortlists': 'mean',
    'Applications': 'mean'
}).reset_index()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Shortlists comparison
x = np.arange(len(ats_groups))
width = 0.6
bars1 = ax1.bar(x, ats_groups['Shortlists'], width, 
                color=['#e74c3c', '#27ae60'], 
                edgecolor='black', linewidth=1.5, alpha=0.8)

ax1.set_ylabel('Average Shortlists', fontweight='bold')
ax1.set_title('Impact of ATS Awareness on Shortlisting Success', fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(['Not ATS Aware', 'ATS Aware'])
ax1.set_ylim(0, max(ats_groups['Shortlists']) * 1.3)

for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
            f'{height:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=11)

# Applications comparison
bars2 = ax2.bar(x, ats_groups['Applications'], width, 
                color=['#e74c3c', '#27ae60'], 
                edgecolor='black', linewidth=1.5, alpha=0.8)

ax2.set_ylabel('Average Applications', fontweight='bold')
ax2.set_title('Application Volume by ATS Awareness', fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(['Not ATS Aware', 'ATS Aware'])

for bar in bars2:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
            f'{height:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=11)

plt.tight_layout()
output_file = viz_dir / 'ats_awareness_impact.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: {output_file}")
plt.close()

# ============================================================================
# 4. APPLICATIONS VS SHORTLISTS SCATTER
# ============================================================================
print("4. Creating Applications vs Shortlists Scatter Plot...")

fig, ax = plt.subplots(figsize=(12, 8))

# Color by ATS awareness
colors = df['ATS_Aware'].map({'Yes': '#27ae60', 'No': '#e74c3c'})
scatter = ax.scatter(df['Applications'], df['Shortlists'], 
                     c=colors, s=100, alpha=0.6, edgecolors='black', linewidth=1)

# Add trend line
z = np.polyfit(df['Applications'], df['Shortlists'], 1)
p = np.poly1d(z)
ax.plot(df['Applications'].sort_values(), p(df['Applications'].sort_values()), 
        "k--", alpha=0.5, linewidth=2, label=f'Trend: y={z[0]:.3f}x+{z[1]:.2f}')

ax.set_xlabel('Number of Applications', fontweight='bold')
ax.set_ylabel('Number of Shortlists', fontweight='bold')
ax.set_title('Application Volume vs Shortlisting Success\n(Green = ATS Aware, Red = Not ATS Aware)', 
             fontweight='bold', pad=20)
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
output_file = viz_dir / 'applications_vs_shortlists.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: {output_file}")
plt.close()

# ============================================================================
# 5. RESUME DIFFICULTY DISTRIBUTION
# ============================================================================
print("5. Creating Resume Difficulty Distribution...")

fig, ax = plt.subplots(figsize=(10, 7))

difficulty_counts = df['Resume_Difficulty'].value_counts().sort_index()
bars = ax.bar(difficulty_counts.index, difficulty_counts.values, 
              color='#9b59b6', edgecolor='black', linewidth=1.5, alpha=0.8)

for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
            f'{int(height)}', ha='center', va='bottom', fontweight='bold', fontsize=11)

ax.set_xlabel('Resume Difficulty Rating (1=Easy, 5=Very Difficult)', fontweight='bold')
ax.set_ylabel('Number of Students', fontweight='bold')
ax.set_title('Distribution of Self-Reported Resume Preparation Difficulty\n(n=100)', 
             fontweight='bold', pad=20)
ax.set_xticks([1, 2, 3, 4, 5])

plt.tight_layout()
output_file = viz_dir / 'resume_difficulty_distribution.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: {output_file}")
plt.close()

# ============================================================================
# 6. CORRELATION HEATMAP
# ============================================================================
print("6. Creating Correlation Heatmap...")

# Prepare numeric data
df_numeric = df.copy()
binary_cols_all = ['Knows_Rejection_Reason', 'Applied_No_Response', 'Resume_Matches_JD', 
                   'Knows_Required_Skills', 'ATS_Aware', 'Guidance_Generic', 'AI_Tool_Helps']
for col in binary_cols_all:
    df_numeric[col] = (df_numeric[col] == 'Yes').astype(int)

# Select columns for correlation
corr_cols = ['Resume_Difficulty', 'Applications', 'Shortlists', 
             'ATS_Aware', 'Knows_Required_Skills', 'Resume_Matches_JD']
corr_labels = ['Resume\nDifficulty', 'Applications', 'Shortlists', 
               'ATS\nAware', 'Knows\nSkills', 'Resume\nMatches JD']

corr_matrix = df_numeric[corr_cols].corr()

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdYlGn', center=0,
            square=True, linewidths=1, cbar_kws={"shrink": 0.8},
            xticklabels=corr_labels, yticklabels=corr_labels, ax=ax)

ax.set_title('Correlation Matrix: Key Variables\n(n=100)', fontweight='bold', pad=20)

plt.tight_layout()
output_file = viz_dir / 'correlation_heatmap.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: {output_file}")
plt.close()

# ============================================================================
# 7. SUCCESS RATE BY KNOWLEDGE FACTORS
# ============================================================================
print("7. Creating Success Rate Comparison...")

df['Success_Rate'] = (df['Shortlists'] / df['Applications'] * 100)

fig, ax = plt.subplots(figsize=(12, 7))

factors = ['ATS_Aware', 'Knows_Required_Skills', 'Resume_Matches_JD']
factor_labels = ['ATS\nAware', 'Knows\nRequired Skills', 'Resume\nMatches JD']

yes_rates = [df[df[factor] == 'Yes']['Success_Rate'].mean() for factor in factors]
no_rates = [df[df[factor] == 'No']['Success_Rate'].mean() for factor in factors]

x = np.arange(len(factors))
width = 0.35

bars1 = ax.bar(x - width/2, no_rates, width, label='No', 
               color='#e74c3c', edgecolor='black', linewidth=1.5, alpha=0.8)
bars2 = ax.bar(x + width/2, yes_rates, width, label='Yes', 
               color='#27ae60', edgecolor='black', linewidth=1.5, alpha=0.8)

ax.set_ylabel('Average Success Rate (%)', fontweight='bold')
ax.set_title('Success Rate (Shortlists/Applications) by Knowledge Factors\n(n=100)', 
             fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(factor_labels)
ax.legend()

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                f'{height:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=10)

plt.tight_layout()
output_file = viz_dir / 'success_rate_comparison.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: {output_file}")
plt.close()

print("\n" + "=" * 80)
print("ALL VISUALIZATIONS GENERATED SUCCESSFULLY")
print("=" * 80)
print(f"\nTotal charts created: 7")
print(f"Location: {viz_dir}")
