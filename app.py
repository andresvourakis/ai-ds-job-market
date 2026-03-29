import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
from analyse_job_market import keyword_groups, keyword_categories, extract_skills_per_job, clean_data

st.set_page_config(page_title="DS/AI Job Market Analysis", layout="wide")

st.title("DS/AI Job Market Analysis")

# File selection
data_dir = Path("data")
file_path = data_dir / "jobs_merged.json"
if not file_path.exists():
    st.error("Merged job data file not found: data/jobs_merged.json")
    st.stop()

# Load data
@st.cache_data
def load_job_data(filepath, _mtime):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

data = load_job_data(file_path, file_path.stat().st_mtime)

# Display metadata
st.sidebar.header("Collection Info")
metadata = data.get("search_metadata", {})
st.sidebar.metric("Total Jobs", metadata.get("total_jobs_collected", 0))
st.sidebar.metric("Query", metadata.get("query", "N/A"))
st.sidebar.metric("Location", metadata.get("location", "N/A"))
if "collection_timestamp" in metadata:
    st.sidebar.text(f"Collected: {metadata['collection_timestamp'][:10]}")

# Extract jobs
jobs = data.get("jobs", [])
if not jobs:
    st.error("No jobs found in the selected file.")
    st.stop()

# Convert to DataFrame
@st.cache_data
def process_jobs(jobs_list):
    processed = []
    for job in jobs_list:
        posted_at_str = job.get('detected_extensions', {}).get('posted_at', 'N/A')
        processed.append({
            'title': job.get('title', 'N/A'),
            'company_name': job.get('company_name', 'N/A'),
            'location': job.get('location', 'N/A'),
            'description': job.get('description', ''),
            'posted_at': posted_at_str,
            'schedule_type': job.get('detected_extensions', {}).get('schedule_type', 'N/A'),
            'salary': job.get('detected_extensions', {}).get('salary', 'N/A'),
            'job_id': job.get('job_id', ''),
        })
    df = pd.DataFrame(processed)
    df['posted_at_date'] = pd.to_datetime(df['posted_at'], errors='coerce')
    return df

df = process_jobs(jobs)

# Apply deduplication using semantic matching (title + company + description prefix)
df = clean_data(df)

# Tab layout
tab1, tab2 = st.tabs(["Jobs by Post Date", "Skill Analysis"])

with tab1:
    st.header("Jobs by Post Date")

    df_with_dates = df[df['posted_at_date'].notna()].copy()
    jobs_without_date = len(df) - len(df_with_dates)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Jobs", len(df))
    with col2:
        st.metric("With Posted Date", len(df_with_dates))
    with col3:
        st.metric("Without Posted Date", jobs_without_date)

    if len(df_with_dates) > 0:
        date_counts = df_with_dates['posted_at_date'].dt.date.value_counts().sort_index()

        fig = px.bar(
            x=date_counts.index,
            y=date_counts.values,
            labels={'x': 'Posted Date', 'y': 'Number of Jobs'},
            title=f'Job Postings Distribution by Date ({len(df_with_dates)} jobs with dates)',
            color=date_counts.values,
            color_continuous_scale=[[0, '#D9E5F1'], [0.5, '#6B88A8'], [1, '#2E4A6B']]
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            height=500,
            title_font_size=20,
            font=dict(color='#1F2937', size=12),
            xaxis=dict(tickfont=dict(color='#1F2937', size=12), title_font=dict(color='#1F2937', size=13)),
            yaxis=dict(tickfont=dict(color='#1F2937', size=12), title_font=dict(color='#1F2937', size=13)),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Summary by Date")
        summary_df = pd.DataFrame({
            'Posted Date': date_counts.index,
            'Job Count': date_counts.values
        })
        summary_df['Percentage'] = (summary_df['Job Count'] / len(df_with_dates) * 100).round(1)
        st.dataframe(summary_df, use_container_width=True)

        if jobs_without_date > 0:
            with st.expander(f"About the {jobs_without_date} jobs without dates"):
                st.write(f"""
                **{jobs_without_date} jobs ({jobs_without_date/len(df)*100:.1f}%)** don't have posted date information.

                This happens when Google's Jobs API doesn't provide a `posted_at` field for certain listings.
                These jobs are still included in the dataset and appear in other analysis tabs.
                """)
    else:
        st.warning("No jobs with valid posted dates found.")

with tab2:
    st.header("Skill Requirements Analysis")

    # Extract skills from descriptions using keyword groups
    @st.cache_data
    def cached_extract_skills(descriptions, groups):
        return extract_skills_per_job(descriptions, groups)

    skill_counts, per_job_skills = cached_extract_skills(df['description'].tolist(), keyword_groups)
    jobs_with_skills = sum(1 for skills in per_job_skills if skills)

    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Jobs", len(df))
    with col2:
        st.metric("Jobs with Skills Detected", jobs_with_skills)
    with col3:
        jobs_without_skills = len(df) - jobs_with_skills
        st.metric("Jobs without Skills", jobs_without_skills, f"{jobs_without_skills/len(df)*100:.1f}%")

    st.markdown("---")

    if skill_counts:
        # Convert to DataFrame
        skills_df = pd.DataFrame(
            skill_counts.most_common(20),
            columns=['Skill', 'Frequency']
        )
        skills_df['Percentage'] = (skills_df['Frequency'] / len(df) * 100).round(1)

        # Create horizontal bar chart
        fig = px.bar(
            skills_df,
            x='Frequency',
            y='Skill',
            orientation='h',
            title='Top 20 Most Mentioned Skills (% of all jobs)',
            labels={'Frequency': 'Number of Job Postings'},
            color='Frequency',
            color_continuous_scale=[[0, '#D9E5F1'], [0.5, '#6B88A8'], [1, '#2E4A6B']],
            text='Percentage'
        )
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending', 'tickfont': dict(color='#1F2937', size=12), 'title_font': dict(color='#1F2937', size=13)},
            height=600,
            title_font_size=20,
            font=dict(color='#1F2937', size=12),
            xaxis=dict(tickfont=dict(color='#1F2937', size=12), title_font=dict(color='#1F2937', size=13)),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

        # Show skills by category
        st.subheader("Skills by Category")

        for category, skills in keyword_categories.items():
            with st.expander(f"{category} ({len(skills)} skills)"):
                category_counts = {skill: skill_counts.get(skill, 0) for skill in skills if skill_counts.get(skill, 0) > 0}
                if category_counts:
                    category_df = pd.DataFrame(
                        sorted(category_counts.items(), key=lambda x: x[1], reverse=True),
                        columns=['Skill', 'Frequency']
                    )
                    category_df['Percentage'] = (category_df['Frequency'] / len(df) * 100).round(1)
                    st.dataframe(category_df, use_container_width=True)
                else:
                    st.info("No skills from this category detected.")

        # Show full table
        st.subheader("All Skills Detected")
        all_skills_df = pd.DataFrame(
            skill_counts.most_common(),
            columns=['Skill', 'Frequency']
        )
        all_skills_df['Percentage'] = (all_skills_df['Frequency'] / len(df) * 100).round(1)
        st.dataframe(all_skills_df, use_container_width=True)
    else:
        st.warning("No skills detected in job descriptions.")

    # Additional insights
    st.subheader("Additional Insights")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Unique Companies", df['company_name'].nunique())
        st.metric("Total Unique Locations", df['location'].nunique())

    with col2:
        schedule_counts = df['schedule_type'].value_counts()
        if len(schedule_counts) > 0:
            st.metric("Most Common Schedule", schedule_counts.index[0])

        # Count jobs with salary info
        jobs_with_salary = df[df['salary'] != 'N/A'].shape[0]
        st.metric("Jobs with Salary Info", f"{jobs_with_salary} ({jobs_with_salary/len(df)*100:.1f}%)")
