from pathlib import Path

import streamlit as st

from analyse_job_market import (
    clean_data,
    extract_skills_per_job,
    keyword_categories,
    keyword_groups,
)
from lib.data import build_ai_jobs_df, load_job_data, process_jobs
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


@st.cache_data
def cached_extract_skills(descriptions, groups):
    return extract_skills_per_job(descriptions, groups)


st.set_page_config(page_title="AI in the Data Science Job Market", layout="wide")
st.title("AI in the Data Science Job Market")

# Load data
file_path = Path("data") / "jobs_merged.json"
if not file_path.exists():
    st.error("Merged job data file not found: data/jobs_merged.json")
    st.stop()

data = load_job_data(file_path, file_path.stat().st_mtime)
metadata = data.get("search_metadata", {})
jobs = data.get("jobs", [])
if not jobs:
    st.error("No jobs found in the selected file.")
    st.stop()

all_df = process_jobs(jobs)
all_df = clean_data(all_df)

# Sidebar renders + returns date-filtered df
df = sidebar.render(all_df, metadata)

# Skill extraction (uses filtered df so date filter cascades through)
skill_counts, per_job_skills = cached_extract_skills(df['description'].tolist(), keyword_groups)

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
