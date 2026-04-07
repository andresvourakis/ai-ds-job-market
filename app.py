import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from collections import Counter
import re
from analyse_job_market import keyword_groups, keyword_categories, extract_skills_per_job, clean_data

def highlight_skills_in_text(text, found_skills):
    """
    Highlight skills in text using word boundaries to avoid partial matches.
    """
    skill_variations = {}
    for group in keyword_groups:
        canonical_name = group[0]
        if canonical_name in found_skills:
            skill_variations[canonical_name] = list(group)

    all_variations = []
    for variations in skill_variations.values():
        all_variations.extend(variations)

    all_variations.sort(key=len, reverse=True)

    highlighted_text = text
    for variation in all_variations:
        pattern = r'\b' + re.escape(variation) + r'\b'
        highlighted_text = re.sub(
            pattern,
            lambda m: f"**:blue[{m.group(0)}]**",
            highlighted_text,
            flags=re.IGNORECASE
        )

    return highlighted_text

def normalize_job_title(title):
    """
    Normalize job titles to group similar Data Scientist positions together
    Returns: (seniority, ai_focused)
    """
    title_lower = title.lower()

    seniority = 'Mid'
    if any(x in title_lower for x in ['senior', 'sr.', 'sr ', 'iii', 'iv']):
        seniority = 'Senior'
    elif any(x in title_lower for x in ['staff', 'principal', 'distinguished']):
        seniority = 'Staff+'
    elif any(x in title_lower for x in ['lead', 'manager', 'head']):
        seniority = 'Lead/Manager'
    elif any(x in title_lower for x in ['director', 'vp', 'chief']):
        seniority = 'Director+'
    elif any(x in title_lower for x in ['junior', 'jr.', 'jr ', 'entry', 'associate', ' i ', ' ii ']):
        seniority = 'Junior'
    elif any(x in title_lower for x in ['intern']):
        seniority = 'Intern'

    ai_focused = any(x in title_lower for x in ['ai', 'artificial intelligence', 'genai', 'generative', 'llm', 'nlp', 'agentic'])

    return seniority, ai_focused

def extract_ai_specialization(title):
    """
    Extract specific AI specialization keywords mentioned in the title
    """
    title_lower = title.lower()
    specializations = []

    if 'genai' in title_lower or 'generative ai' in title_lower or 'gen ai' in title_lower:
        specializations.append('GenAI')
    if 'llm' in title_lower or 'large language model' in title_lower:
        specializations.append('LLM')
    if 'nlp' in title_lower or 'natural language processing' in title_lower:
        specializations.append('NLP')
    if 'agentic' in title_lower or 'ai agent' in title_lower:
        specializations.append('Agentic AI')
    if 'machine learning' in title_lower or 'ml' in title_lower:
        specializations.append('Machine Learning')

    if 'ai' in title_lower or 'artificial intelligence' in title_lower:
        specializations.append('AI')

    if not specializations:
        specializations.append('General')

    return specializations

def categorize_title_type(title):
    """
    Categorize job title as either 'General' or 'AI-Specialized'
    """
    specializations = extract_ai_specialization(title)
    if specializations == ['General']:
        return 'General'
    return 'AI-Specialized'

def format_normalized_title(seniority, ai_focused):
    """Format the normalized title for display"""
    title = f"{seniority} Data Scientist"
    if ai_focused:
        title += " (AI-focused)"
    return title

def parse_salary(salary_str):
    """
    Parse salary string to extract min and max values in annual terms.
    Returns (min_salary, max_salary) or (None, None) if unparseable.
    """
    if not salary_str:
        return None, None

    salary_str = salary_str.lower().replace(',', '').replace('$', '')
    is_hourly = 'hour' in salary_str

    k_pattern = r'(\d+\.?\d*)\s*k'
    k_matches = re.findall(k_pattern, salary_str)

    plain_pattern = r'(\d{4,})'
    plain_matches = re.findall(plain_pattern, salary_str.replace('k', ''))

    values = []

    if k_matches:
        for num in k_matches:
            values.append(float(num) * 1000)
    elif plain_matches:
        for num in plain_matches:
            values.append(float(num))
    elif is_hourly:
        hourly_matches = re.findall(r'(\d+\.?\d*)', salary_str)
        for num in hourly_matches:
            val = float(num)
            if val < 500:
                values.append(val * 2080)

    if len(values) == 0:
        return None, None
    elif len(values) == 1:
        return values[0], values[0]
    else:
        return min(values[:2]), max(values[:2])

# Page config
st.set_page_config(page_title="DS/AI Job Market Analysis", layout="wide")

st.title("DS/AI Job Market Analysis")
st.markdown("Analyzing how AI is disrupting the Data Science job market")

# Load data
data_dir = Path("data")
file_path = data_dir / "jobs_merged.json"
if not file_path.exists():
    st.error("Merged job data file not found: data/jobs_merged.json")
    st.stop()

@st.cache_data
def load_job_data(filepath, _mtime):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

data = load_job_data(file_path, file_path.stat().st_mtime)

metadata = data.get("search_metadata", {})
jobs = data.get("jobs", [])
if not jobs:
    st.error("No jobs found in the selected file.")
    st.stop()

@st.cache_data
def process_jobs(jobs_list):
    processed = []
    for job in jobs_list:
        ext = job.get('detected_extensions', {})
        posted_at_str = ext.get('posted_at', 'N/A') if isinstance(ext, dict) else 'N/A'
        salary_raw = ext.get('salary') if isinstance(ext, dict) else None
        salary_min, salary_max = parse_salary(salary_raw)
        salary_mid = (salary_min + salary_max) / 2 if salary_min and salary_max else None

        processed.append({
            'title': job.get('title', 'N/A'),
            'company_name': job.get('company_name', 'N/A'),
            'location': job.get('location', 'N/A'),
            'description': job.get('description', ''),
            'posted_at': posted_at_str,
            'schedule_type': ext.get('schedule_type', 'N/A') if isinstance(ext, dict) else 'N/A',
            'salary': salary_raw or 'N/A',
            'salary_min': salary_min,
            'salary_max': salary_max,
            'salary_mid': salary_mid,
            'job_id': job.get('job_id', ''),
            'share_link': job.get('share_link', ''),
            'apply_options': job.get('apply_options', []),
        })
    df = pd.DataFrame(processed)
    df['posted_at_date'] = pd.to_datetime(df['posted_at'], errors='coerce')
    return df

all_df = process_jobs(jobs)
all_df = clean_data(all_df)

# Date range filter
df_with_valid_dates = all_df[all_df['posted_at_date'].notna()]
if len(df_with_valid_dates) > 0:
    min_date = df_with_valid_dates['posted_at_date'].min().date()
    max_date = df_with_valid_dates['posted_at_date'].max().date()

    filter_col1, filter_col2 = st.columns([1, 3])
    with filter_col1:
        date_range = st.date_input(
            "Filter by posting date",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        is_full_range = (start_date == min_date and end_date == max_date)
        if is_full_range:
            df = all_df
        else:
            dated_mask = (
                (all_df['posted_at_date'].notna()) &
                (all_df['posted_at_date'].dt.date >= start_date) &
                (all_df['posted_at_date'].dt.date <= end_date)
            )
            df = all_df[dated_mask]
    else:
        df = all_df
else:
    df = all_df

if not (len(df) == len(all_df)):
    st.caption(f"Showing {len(df)} of {len(all_df)} jobs. Jobs without posting dates are excluded when filtering by date.")

# Extract skills once for the entire app
@st.cache_data
def cached_extract_skills(descriptions, groups):
    return extract_skills_per_job(descriptions, groups)

skill_counts, per_job_skills = cached_extract_skills(df['description'].tolist(), keyword_groups)

# Build AI job data
ai_skills = keyword_categories.get("Artificial Intelligence", [])
ai_skills_set = set(ai_skills)

ai_job_indices = []
ai_job_skills = {}
for i, idx in enumerate(df.index):
    job_skills = per_job_skills[i]
    ai_skills_found = [s for s in job_skills if s in ai_skills_set]
    if ai_skills_found:
        ai_job_indices.append(idx)
        ai_job_skills[idx] = ai_skills_found

ai_jobs_df = df.loc[ai_job_indices].copy()
ai_jobs_df['ai_skills'] = ai_jobs_df.index.map(lambda idx: ai_job_skills.get(idx, []))
ai_jobs_df['ai_skill_count'] = ai_jobs_df['ai_skills'].apply(len)

st.header("Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Jobs", len(df))
with col2:
    pct_ai = (len(ai_jobs_df) / len(df) * 100) if len(df) > 0 else 0
    st.metric("Jobs with AI Keywords", len(ai_jobs_df), f"{pct_ai:.0f}% of total jobs", delta_color="off", delta_arrow="off")
with col3:
    ai_jobs_specific_df = ai_jobs_df[ai_jobs_df['ai_skills'].apply(lambda skills: any(s != 'AI' for s in skills))]
    pct_ai_specific = (len(ai_jobs_specific_df) / len(df) * 100) if len(df) > 0 else 0
    st.metric("Jobs with AI Skills", len(ai_jobs_specific_df), f"{pct_ai_specific:.0f}% of total jobs", delta_color="off", delta_arrow="off")
with col4:
    ai_skill_counts = {skill: skill_counts.get(skill, 0) for skill in ai_skills if skill != 'AI'}
    top_ai_skill = max(ai_skill_counts.items(), key=lambda x: x[1]) if ai_skill_counts else ("N/A", 0)
    top_ai_pct = (top_ai_skill[1] / len(df) * 100) if len(df) > 0 else 0
    st.metric("Top AI Skill", top_ai_skill[0], f"in {top_ai_pct:.0f}% of jobs", delta_color="off", delta_arrow="off")
with col5:
    avg_ai_skills = ai_jobs_df['ai_skill_count'].mean() if len(ai_jobs_df) > 0 else 0
    st.metric("Avg AI Skills per Job", f"{avg_ai_skills:.1f}")

st.header("Top Skills in Demand")

ai_skill_counts_sorted = sorted(
    [(skill, skill_counts.get(skill, 0)) for skill in ai_skills if skill != 'AI'],
    key=lambda x: x[1],
    reverse=True
)[:10]

if ai_skill_counts_sorted:
    ai_skills_df = pd.DataFrame(ai_skill_counts_sorted, columns=['Skill', 'Frequency'])
    ai_skills_df['Percentage'] = (ai_skills_df['Frequency'] / len(df) * 100).round(1)
    ai_skills_df['Label'] = ai_skills_df.apply(
        lambda row: f"{row['Skill']} ({row['Percentage']}%)", axis=1
    )

    all_skills_df = pd.DataFrame(
        skill_counts.most_common(20),
        columns=['Skill', 'Frequency']
    )
    all_skills_df['Percentage'] = (all_skills_df['Frequency'] / len(df) * 100).round(1)

    chart_col1, chart_col2 = st.columns(2, gap="medium")

    with chart_col1:
        fig = px.bar(
            all_skills_df,
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
            height=500,
            title_font_size=20,
            font=dict(color='#1F2937', size=12),
            xaxis=dict(tickfont=dict(color='#1F2937', size=12), title_font=dict(color='#1F2937', size=13)),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        fig = px.bar(
            ai_skills_df,
            x='Frequency',
            y='Skill',
            orientation='h',
            title='Top 10 AI Skills in Data Science Jobs (% of all jobs)',
            labels={'Frequency': 'Number of Job Postings'},
            color='Frequency',
            color_continuous_scale=[[0, '#D9E5F1'], [0.5, '#6B88A8'], [1, '#2E4A6B']],
            text='Percentage'
        )
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending', 'tickfont': dict(color='#1F2937', size=12), 'title_font': dict(color='#1F2937', size=13)},
            height=500,
            title_font_size=20,
            font=dict(color='#1F2937', size=12),
            xaxis=dict(tickfont=dict(color='#1F2937', size=12), title_font=dict(color='#1F2937', size=13)),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

st.header("Job Titles Requiring AI Skills")

if len(ai_jobs_df) > 0:
    ai_jobs_df['seniority'], ai_jobs_df['ai_in_title'] = zip(*ai_jobs_df['title'].apply(normalize_job_title))

    st.subheader("By Seniority Level")
    seniority_counts = ai_jobs_df['seniority'].value_counts()
    seniority_df = pd.DataFrame({
        'Seniority': seniority_counts.index,
        'Frequency': seniority_counts.values
    })
    seniority_df['Percentage'] = (seniority_df['Frequency'] / len(ai_jobs_df) * 100).round(1)

    fig1 = px.bar(
        seniority_df,
        x='Frequency',
        y='Seniority',
        orientation='h',
        title='AI Jobs by Seniority Level',
        labels={'Frequency': 'Number of Postings'},
        color='Frequency',
        color_continuous_scale=[[0, '#D9E5F1'], [0.5, '#6B88A8'], [1, '#2E4A6B']],
        text='Percentage',
        hover_data={'Percentage': ':.1f', 'Frequency': True}
    )
    fig1.update_traces(texttemplate='%{text}%', textposition='outside')
    fig1.update_layout(
        yaxis={'categoryorder': 'total ascending', 'tickfont': dict(color='#1F2937', size=12), 'title_font': dict(color='#1F2937', size=13)},
        height=400,
        title_font_size=20,
        font=dict(color='#1F2937', size=12),
        xaxis=dict(tickfont=dict(color='#1F2937', size=12), title_font=dict(color='#1F2937', size=13)),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig1, use_container_width=True)

    with st.expander("Seniority Keywords Used"):
        st.markdown("""
        - **Intern**: intern
        - **Junior**: junior, jr., jr, entry, associate, I, II
        - **Mid**: (default if no other seniority keyword found)
        - **Senior**: senior, sr., sr, III, IV
        - **Staff+**: staff, principal, distinguished
        - **Lead/Manager**: lead, manager, head
        - **Director+**: director, vp, chief
        """)

    st.subheader("General vs AI-Specialized Titles")
    ai_jobs_df['title_category'] = ai_jobs_df['title'].apply(categorize_title_type)
    title_type_counts = ai_jobs_df['title_category'].value_counts()
    title_type_df = pd.DataFrame({
        'Title Type': title_type_counts.index,
        'Frequency': title_type_counts.values
    })
    title_type_df['Percentage'] = (title_type_df['Frequency'] / len(ai_jobs_df) * 100).round(1)

    fig2 = px.bar(
        title_type_df,
        x='Frequency',
        y='Title Type',
        orientation='h',
        title='General vs AI-Specialized Job Titles',
        labels={'Frequency': 'Number of Postings'},
        color='Frequency',
        color_continuous_scale=[[0, '#D9E5F1'], [0.5, '#6B88A8'], [1, '#2E4A6B']],
        text='Percentage',
        hover_data={'Percentage': ':.1f', 'Frequency': True}
    )
    fig2.update_traces(texttemplate='%{text}%', textposition='outside')
    fig2.update_layout(
        yaxis={'categoryorder': 'total ascending', 'tickfont': dict(color='#1F2937', size=12), 'title_font': dict(color='#1F2937', size=13)},
        height=300,
        title_font_size=20,
        font=dict(color='#1F2937', size=12),
        xaxis=dict(tickfont=dict(color='#1F2937', size=12), title_font=dict(color='#1F2937', size=13)),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("Categorization Logic"):
        st.markdown("""
        - **AI-Specialized**: Titles mentioning specific AI keywords (GenAI, LLM, NLP, Machine Learning, Agentic AI, or AI/Artificial Intelligence)
        - **General**: Titles without AI specialization keywords (e.g., "Data Scientist", "Senior Data Scientist")
        """)

    st.subheader("Specific AI Specialization Types")

    all_specializations = []
    for title in ai_jobs_df['title']:
        specs = extract_ai_specialization(title)
        specific_specs = [s for s in specs if s != 'General']
        all_specializations.extend(specific_specs)

    if all_specializations:
        spec_counts = pd.Series(all_specializations).value_counts()
        spec_df = pd.DataFrame({
            'Specialization': spec_counts.index,
            'Frequency': spec_counts.values
        })
        ai_specialized_count = len(ai_jobs_df[ai_jobs_df['title_category'] == 'AI-Specialized'])
        spec_df['Percentage'] = (spec_df['Frequency'] / ai_specialized_count * 100).round(1)

        fig3 = px.bar(
            spec_df,
            x='Frequency',
            y='Specialization',
            orientation='h',
            title='Breakdown of AI Specialization Types',
            labels={'Frequency': 'Number of Job Titles'},
            color='Frequency',
            color_continuous_scale=[[0, '#D9E5F1'], [0.5, '#6B88A8'], [1, '#2E4A6B']],
            text='Percentage',
            hover_data={'Percentage': ':.1f', 'Frequency': True}
        )
        fig3.update_traces(texttemplate='%{text}%', textposition='outside')
        fig3.update_layout(
            yaxis={'categoryorder': 'total ascending', 'tickfont': dict(color='#1F2937', size=12), 'title_font': dict(color='#1F2937', size=13)},
            height=350,
            title_font_size=20,
            font=dict(color='#1F2937', size=12),
            xaxis=dict(tickfont=dict(color='#1F2937', size=12), title_font=dict(color='#1F2937', size=13)),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig3, use_container_width=True)

        with st.expander("Specialization Keywords Used"):
            st.markdown("""
            - **AI**: ai, artificial intelligence
            - **GenAI**: genai, generative ai, gen ai
            - **LLM**: llm, large language model
            - **NLP**: nlp, natural language processing
            - **Agentic AI**: agentic, ai agent
            - **Machine Learning**: machine learning, ml

            *Note: This chart only shows AI-specialized jobs (excludes General titles). A single job can be counted in multiple categories if it mentions multiple specializations.*
            """)
    else:
        st.info("No specific AI specialization keywords found in titles")
else:
    st.info("No AI-specialized jobs found")

st.header("Most Common AI Skill Combinations")

if len(ai_jobs_df) > 0:
    skill_pairs = Counter()

    for skills_list in ai_jobs_df['ai_skills']:
        if len(skills_list) >= 2:
            sorted_skills = sorted(skills_list)
            for i in range(len(sorted_skills)):
                for j in range(i + 1, len(sorted_skills)):
                    skill_pairs[(sorted_skills[i], sorted_skills[j])] += 1

    if skill_pairs:
        top_pairs = skill_pairs.most_common(10)
        pairs_df = pd.DataFrame(
            [(f"{pair[0]} + {pair[1]}", count) for pair, count in top_pairs],
            columns=['Skill Combination', 'Frequency']
        )
        pairs_df['Percentage'] = (pairs_df['Frequency'] / len(ai_jobs_df) * 100).round(1)

        fig = px.bar(
            pairs_df,
            x='Frequency',
            y='Skill Combination',
            orientation='h',
            title='Top 10 AI Skill Pairs',
            labels={'Frequency': 'Number of Jobs'},
            color='Frequency',
            color_continuous_scale=[[0, '#E3EBF3'], [0.5, '#7A95B0'], [1, '#3B5F7F']],
            text='Percentage'
        )
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending', 'tickfont': dict(color='#1F2937', size=12), 'title_font': dict(color='#1F2937', size=13)},
            height=400,
            title_font_size=20,
            font=dict(color='#1F2937', size=12),
            xaxis=dict(tickfont=dict(color='#1F2937', size=12), title_font=dict(color='#1F2937', size=13)),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No skill combinations found (jobs have only single AI skills)")

st.header("AI Skill Depth Analysis")

if len(ai_jobs_df) > 0:
    skill_depth_bins = pd.cut(
        ai_jobs_df['ai_skill_count'],
        bins=[1, 3, 6, 11, float('inf')],
        labels=['1-2 skills', '3-5 skills', '6-10 skills', '11+ skills'],
        right=False
    )
    depth_counts = skill_depth_bins.value_counts().sort_index()

    depth_df = pd.DataFrame({
        'Skill Range': depth_counts.index,
        'Number of Jobs': depth_counts.values
    })
    depth_df['Percentage'] = (depth_df['Number of Jobs'] / len(ai_jobs_df) * 100).round(1)

    fig = px.bar(
        depth_df,
        x='Number of Jobs',
        y='Skill Range',
        orientation='h',
        title='Distribution of AI Skill Requirements',
        labels={'Number of Jobs': 'Number of Postings'},
        color='Number of Jobs',
        color_continuous_scale=[[0, '#D9E5F1'], [0.5, '#6B88A8'], [1, '#2E4A6B']],
        text='Percentage'
    )
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending', 'tickfont': dict(color='#1F2937', size=12), 'title_font': dict(color='#1F2937', size=13)},
        height=300,
        title_font_size=20,
        font=dict(color='#1F2937', size=12),
        xaxis=dict(tickfont=dict(color='#1F2937', size=12), title_font=dict(color='#1F2937', size=13)),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)

st.header("Salary Analysis: AI Skills Premium")

jobs_with_salary = ai_jobs_df[ai_jobs_df['salary_mid'].notna()].copy()

if len(jobs_with_salary) >= 20:
    jobs_with_salary['seniority'] = jobs_with_salary['title'].apply(lambda t: normalize_job_title(t)[0])

    non_ai_jobs = df[~df.index.isin(ai_jobs_df.index)]
    non_ai_with_salary = non_ai_jobs[non_ai_jobs['salary_mid'].notna()].copy()

    if len(non_ai_with_salary) >= 10:
        non_ai_with_salary['seniority'] = non_ai_with_salary['title'].apply(lambda t: normalize_job_title(t)[0])

        comparison_data = []
        seniority_order = ['Junior', 'Mid', 'Senior', 'Staff+', 'Lead/Manager', 'Director+']

        for seniority in seniority_order:
            ai_sen = jobs_with_salary[jobs_with_salary['seniority'] == seniority]
            non_ai_sen = non_ai_with_salary[non_ai_with_salary['seniority'] == seniority]

            if len(ai_sen) >= 3 and len(non_ai_sen) >= 3:
                ai_median = ai_sen['salary_mid'].median()
                non_ai_median = non_ai_sen['salary_mid'].median()
                diff = ai_median - non_ai_median
                pct_diff = (diff / non_ai_median) * 100

                comparison_data.append({
                    'Seniority': seniority,
                    'AI Jobs Median': ai_median,
                    'Non-AI Jobs Median': non_ai_median,
                    'Difference': diff,
                    'Pct Difference': pct_diff,
                    'AI Sample': len(ai_sen),
                    'Non-AI Sample': len(non_ai_sen)
                })

        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)

            col1, col2, col3 = st.columns(3)

            with col1:
                avg_premium = comparison_df['Pct Difference'].mean()
                st.metric(
                    "Avg AI Salary Premium",
                    f"{avg_premium:+.1f}%",
                    help="Average salary difference for AI-skilled jobs vs non-AI jobs, controlling for seniority"
                )

            with col2:
                total_ai_salary_jobs = len(jobs_with_salary)
                pct_ai_salary = (total_ai_salary_jobs / len(ai_jobs_df) * 100) if len(ai_jobs_df) > 0 else 0
                st.metric(
                    "AI Jobs with Salary Data",
                    total_ai_salary_jobs,
                    f"{pct_ai_salary:.0f}% of AI jobs", delta_color="off", delta_arrow="off"
                )

            with col3:
                total_non_ai_salary_jobs = len(non_ai_with_salary)
                pct_non_ai_salary = (total_non_ai_salary_jobs / len(non_ai_jobs) * 100) if len(non_ai_jobs) > 0 else 0
                st.metric(
                    "Non-AI Jobs with Salary Data",
                    total_non_ai_salary_jobs,
                    f"{pct_non_ai_salary:.0f}% of non-AI jobs", delta_color="off", delta_arrow="off"
                )

            chart_data = []
            for _, row in comparison_df.iterrows():
                chart_data.append({
                    'Seniority': row['Seniority'],
                    'Category': 'AI Jobs',
                    'Median Salary': row['AI Jobs Median'],
                    'Sample Size': row['AI Sample']
                })
                chart_data.append({
                    'Seniority': row['Seniority'],
                    'Category': 'Non-AI Jobs',
                    'Median Salary': row['Non-AI Jobs Median'],
                    'Sample Size': row['Non-AI Sample']
                })

            chart_df = pd.DataFrame(chart_data)

            fig = px.bar(
                chart_df,
                x='Seniority',
                y='Median Salary',
                color='Category',
                barmode='group',
                title='Median Salary by Seniority: AI vs Non-AI Jobs',
                color_discrete_map={'AI Jobs': '#2E4A6B', 'Non-AI Jobs': '#8BA5C0'},
                hover_data={'Sample Size': True}
            )

            for _, row in comparison_df.iterrows():
                sen = row['Seniority']
                pct = row['Pct Difference']
                ai_median = row['AI Jobs Median']
                non_ai_median = row['Non-AI Jobs Median']
                max_salary = max(ai_median, non_ai_median)

                fig.add_annotation(
                    x=sen,
                    y=max_salary,
                    text=f"{pct:+.1f}%",
                    showarrow=False,
                    yshift=15,
                    font=dict(size=11, color='#1F2937', family='Arial Black')
                )

            fig.update_layout(
                title_font_size=20,
                font=dict(color='#1F2937', size=12),
                xaxis=dict(
                    categoryorder='array',
                    categoryarray=seniority_order,
                    tickfont=dict(color='#1F2937', size=12),
                    title_font=dict(color='#1F2937', size=13)
                ),
                yaxis=dict(
                    tickformat='$,.0f',
                    tickfont=dict(color='#1F2937', size=12),
                    title_font=dict(color='#1F2937', size=13)
                ),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                ),
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

            with st.expander("Detailed Salary Comparison by Seniority"):
                display_df = comparison_df.copy()
                display_df['AI Jobs Median'] = display_df['AI Jobs Median'].apply(lambda x: f"${x:,.0f}")
                display_df['Non-AI Jobs Median'] = display_df['Non-AI Jobs Median'].apply(lambda x: f"${x:,.0f}")
                display_df['Difference'] = display_df['Difference'].apply(lambda x: f"${x:+,.0f}")
                display_df['Pct Difference'] = display_df['Pct Difference'].apply(lambda x: f"{x:+.1f}%")
                display_df = display_df.rename(columns={
                    'AI Sample': 'AI Jobs (n)',
                    'Non-AI Sample': 'Non-AI Jobs (n)',
                    'Pct Difference': '% Difference'
                })
                st.dataframe(display_df, use_container_width=True, hide_index=True)

                st.markdown("""
                **Note:** Salary data is only available for ~35% of job postings.
                Comparisons are made within the same seniority level to control for experience differences.
                """)
        else:
            st.info("Not enough data to compare salaries by seniority level (need at least 3 jobs in each category).")
    else:
        st.info(f"Not enough non-AI jobs with salary data for comparison ({len(non_ai_with_salary)} found, need at least 10).")
else:
    st.info(f"Not enough AI jobs with salary data ({len(jobs_with_salary)} found, need at least 20).")

st.header("AI Job Explorer")

col1, col2, col3 = st.columns(3)

with col1:
    selected_skill = st.selectbox(
        "Filter by AI Skill",
        ["All"] + sorted(ai_skills)
    )

with col2:
    ai_specialization_options = ["All", "GenAI", "LLM", "NLP", "Agentic AI", "Machine Learning", "AI", "General"]
    selected_specialization = st.selectbox(
        "Filter by AI Specialization in Title",
        ai_specialization_options
    )

with col3:
    min_skills = st.slider(
        "Minimum AI Skills Required",
        min_value=1,
        max_value=int(ai_jobs_df['ai_skill_count'].max()) if len(ai_jobs_df) > 0 else 10,
        value=1
    )

filtered_jobs = ai_jobs_df.copy()

if selected_specialization != "All":
    filtered_jobs = filtered_jobs[
        filtered_jobs['title'].apply(lambda title: selected_specialization in extract_ai_specialization(title))
    ]

if selected_skill != "All":
    filtered_jobs = filtered_jobs[filtered_jobs['ai_skills'].apply(lambda x: selected_skill in x)]

if selected_specialization == "All":
    filtered_jobs = filtered_jobs[filtered_jobs['ai_skill_count'] >= min_skills]

st.subheader(f"Matching Jobs ({len(filtered_jobs)} found)")

if len(filtered_jobs) > 0:
    display_df = filtered_jobs[['title', 'company_name', 'location', 'ai_skill_count', 'ai_skills']].copy()
    display_df['ai_skills'] = display_df['ai_skills'].apply(lambda x: ', '.join(x))
    display_df.columns = ['Job Title', 'Company', 'Location', 'AI Skills Count', 'AI Skills']

    event = st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    if event.selection and len(event.selection.rows) > 0:
        selected_row_idx = event.selection.rows[0]
        selected_row = filtered_jobs.iloc[selected_row_idx]

        st.markdown("---")
        st.subheader("Job Details")

        with st.container(border=True):
            st.markdown(f"### {selected_row['title']}")

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown(f"**Company**  \n{selected_row['company_name']}")
            with col_b:
                st.markdown(f"**Location**  \n{selected_row['location']}")
            with col_c:
                salary = selected_row.get('salary', 'N/A')
                if salary and salary != 'N/A':
                    st.markdown(f"**Salary**  \n{salary}")
                else:
                    st.markdown(f"**AI Skills**  \n{selected_row['ai_skill_count']} detected")

            if selected_row['apply_options'] and len(selected_row['apply_options']) > 0:
                links = [f"[{opt['title']}]({opt['link']})" for opt in selected_row['apply_options'] if 'link' in opt and 'title' in opt]
                if links:
                    st.markdown("**Apply via:** " + " | ".join(links))
            elif selected_row['share_link']:
                st.markdown(f"**[View Job Posting]({selected_row['share_link']})**")

        col1, col2 = st.columns([1, 3])

        with col1:
            with st.container(border=True):
                st.markdown("**AI Skills Found**")
                for skill in selected_row['ai_skills']:
                    st.markdown(f"- {skill}")

        with col2:
            with st.container(border=True):
                st.markdown("**Job Description**")

                description = selected_row['description']
                highlighted_desc = highlight_skills_in_text(description, selected_row['ai_skills'])
                highlighted_desc = highlighted_desc.replace('\n', '  \n')

                st.markdown(highlighted_desc)
    else:
        st.info("Click on any row in the table above to view full job details with highlighted AI skills")
else:
    st.info("No jobs match the selected filters.")

st.header("Job Postings Distribution by Date")

all_df_with_dates = all_df[all_df['posted_at_date'].notna()].copy()
all_jobs_without_date = len(all_df) - len(all_df_with_dates)

if len(all_df_with_dates) > 0:
    date_counts = all_df_with_dates['posted_at_date'].dt.date.value_counts().sort_index()

    fig = px.bar(
        x=date_counts.index,
        y=date_counts.values,
        labels={'x': 'Posted Date', 'y': 'Number of Jobs'},
        title=f'Job Postings Distribution by Date ({len(all_df_with_dates)} jobs)',
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

    st.caption(f"Based on {len(all_df_with_dates)} jobs with posting dates ({len(all_df_with_dates)/len(all_df)*100:.0f}% of total). "
               f"{all_jobs_without_date} jobs ({all_jobs_without_date/len(all_df)*100:.0f}%) do not have date information from the source.")
else:
    st.warning("No jobs with valid posted dates found.")
