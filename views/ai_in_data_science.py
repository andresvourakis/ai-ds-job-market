import streamlit as st

from analyse_job_market import keyword_categories, keyword_groups
from lib.data import build_ai_jobs_df, extract_skills_cached, load_dashboard_data
from sections import (
    ai_titles,
    job_explorer,
    metrics,
    salary,
    sidebar,
    skill_analysis,
    time_distribution,
    top_skills,
)

st.title("AI in the Data Science Job Market")

all_df, metadata = load_dashboard_data()

# Sidebar renders + returns date-filtered df
df = sidebar.render(all_df, metadata)

# Skill extraction (uses filtered df so date filter cascades through)
skill_counts, per_job_skills = extract_skills_cached(df['description'].tolist(), keyword_groups)

ai_skills = keyword_categories.get("Artificial Intelligence", [])
ai_skills_set = set(ai_skills)
ai_jobs_df = build_ai_jobs_df(df, per_job_skills, ai_skills_set)

# Render sections in original order
metrics.render(df, ai_jobs_df, ai_skills, skill_counts)
top_skills.render(df, ai_skills, skill_counts)
ai_titles.render(ai_jobs_df)
skill_analysis.render(ai_jobs_df)
salary.render(df, ai_jobs_df)
job_explorer.render(ai_jobs_df, ai_skills)
time_distribution.render(all_df)
