import streamlit as st

from analyse_job_market import keyword_groups
from lib import production
from lib.data import extract_skills_cached, load_dashboard_data
from sections import (
    production_clouds,
    production_explorer,
    production_gap,
    production_metrics,
    production_salary,
    production_seniority,
    production_skills,
    production_trend,
    sidebar,
)

st.title("ML in Production in the Data Science Job Market")
st.markdown(
    "How often Data Scientist postings ask for the skills that take a model from a notebook to a "
    "running, monitored service. LLM-specific skills are covered on the AI in Data Science page."
)

all_df, metadata = load_dashboard_data()

# Sidebar renders + returns date-filtered df
df = sidebar.render(all_df, metadata)

# Same skill extraction as the AI page, then the production lens on top of it
_, per_job_skills = extract_skills_cached(df['description'].tolist(), keyword_groups)
prod_df = production.build_production_jobs_df(df, per_job_skills)

production_metrics.render(prod_df)
production_gap.render(prod_df)
production_skills.render(prod_df)
production_clouds.render(prod_df)
production_seniority.render(prod_df)
production_salary.render(prod_df)
production_trend.render(prod_df)
production_explorer.render(prod_df)
