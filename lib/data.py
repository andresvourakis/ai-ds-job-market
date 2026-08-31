import gzip
import json
import os
import re
import urllib.request
from pathlib import Path

import pandas as pd
import streamlit as st

from analyse_job_market import clean_data, extract_skills_per_job

# The dataset is published weekly by the scraper repo (ds-google-job-search) to a
# Hugging Face dataset repo. A local data/jobs_merged.json, if present, takes
# precedence so you can develop against a specific file.
DATA_FILE = Path("data") / "jobs_merged.json"
DATA_URL = os.getenv(
    "JOB_DATA_URL",
    "https://huggingface.co/datasets/futureproofds/ai-ds-job-market/resolve/main/jobs_merged.json.gz",
)
DATA_TTL_SECONDS = 6 * 60 * 60  # re-download at most every 6 hours


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


def fetch_job_data():
    """Uncached loader: local file if present, otherwise download from DATA_URL."""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    with urllib.request.urlopen(DATA_URL, timeout=300) as resp:
        raw = resp.read()
    if DATA_URL.endswith(".gz"):
        raw = gzip.decompress(raw)
    return json.loads(raw.decode("utf-8"))


@st.cache_data(ttl=DATA_TTL_SECONDS, show_spinner="Loading job data...")
def load_job_data():
    return fetch_job_data()


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


def build_ai_jobs_df(df, per_job_skills, ai_skills_set):
    """
    Filter df to jobs that mention at least one AI skill.
    Returns a copy with two added columns: ai_skills (list) and ai_skill_count (int).
    """
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
    return ai_jobs_df


def load_dashboard_data():
    """
    The shared pipeline every page starts from: load -> process -> dedupe.
    Returns (all_df, metadata). Stops the app with an error if the data cannot
    be loaded or is empty, so pages never render against nothing.
    """
    try:
        data = load_job_data()
    except Exception as exc:  # network error, bad file, ...
        st.error(f"Could not load job data: {exc}")
        st.stop()

    jobs = data.get("jobs", [])
    if not jobs:
        st.error("No jobs found in the dataset.")
        st.stop()

    all_df = clean_data(process_jobs(jobs))
    return all_df, data.get("search_metadata", {})


@st.cache_data
def extract_skills_cached(descriptions, groups):
    return extract_skills_per_job(descriptions, groups)
