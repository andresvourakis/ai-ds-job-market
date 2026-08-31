"""
Print the numbers behind the ML in Production page, without Streamlit.

Runs the exact pipeline the dashboard uses (process_jobs -> clean_data ->
extract_skills_per_job), so what prints here is what the page will show.

Usage:
    poetry run python production_report.py
"""

import logging
from pathlib import Path

import streamlit  # noqa: F401  (imported first so its loggers exist, see below)

# lib.data caches with @st.cache_data; outside Streamlit that logs "No runtime
# found" warnings the moment lib.data is imported, which would bury the report.
# Streamlit gives each of its loggers an explicit level, so they are silenced
# by name, after streamlit creates them and before lib.data is imported.
for _name in ("streamlit.runtime.caching.cache_data_api",
              "streamlit.runtime.scriptrunner_utils.script_run_context"):
    logging.getLogger(_name).setLevel(logging.ERROR)

from analyse_job_market import clean_data, extract_skills_per_job, keyword_groups  # noqa: E402
from lib import production  # noqa: E402
from lib.data import load_job_data, process_jobs  # noqa: E402


def load_production_df():
    file_path = Path("data") / "jobs_merged.json"
    data = load_job_data(file_path, file_path.stat().st_mtime)
    df = clean_data(process_jobs(data["jobs"]))
    _, per_job_skills = extract_skills_per_job(df["description"].tolist(), keyword_groups)
    return production.build_production_jobs_df(df, per_job_skills)


def print_table(title, frame, fmt):
    print(f"\n{title}")
    print(frame.to_string(index=False, formatters=fmt))


if __name__ == "__main__":
    prod_df = load_production_df()
    n = len(prod_df)
    pct = "{:.1f}%".format

    print(f"Deduplicated Data Scientist postings: {n:,}")
    print(f"\nHEADLINE: {production.production_share(prod_df):.1f}% require production skills")
    print(f"          {100 * prod_df['names_tool'].mean():.1f}% name at least one production tool")

    print_table(
        "By category (% asking for the practice vs % naming a tool):",
        production.category_summary(prod_df),
        {"practice_share": pct, "tool_share": pct},
    )

    print_table("Practices:", production.skill_shares(prod_df, production.practice_skills()), {"share": pct})
    print_table("Tools:", production.skill_shares(prod_df, production.tool_skills()), {"share": pct})

    print_table("By seniority:", production.seniority_breakdown(prod_df), {"share": pct})
    print_table("By month:", production.monthly_trend(prod_df), {"share": pct})
