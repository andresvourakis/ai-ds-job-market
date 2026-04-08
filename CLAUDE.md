# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Streamlit dashboard that analyzes how AI has disrupted the Data Science job market, by extracting and categorizing skills from Data Science job postings.

## Commands

```bash
make install   # Install dependencies (Poetry, Python ^3.10)
make run       # Run the dashboard
```

## Architecture

- **app.py** — Main Streamlit dashboard: job posting trends, skill frequency analysis (top 20 + by category), AI disruption analysis (seniority breakdown, salary comparison, skill combinations), interactive job explorer with skill highlighting, summary metrics. Uses `@st.cache_data` for caching.
- **analyse_job_market.py** — Core business logic: skill extraction, data deduplication, keyword definitions.
- **data/jobs_merged.json** — Dataset (~30MB, ~2,700 jobs) with title, company, location, description, and metadata. Hosted externally (see Releases).
- **.streamlit/config.toml** — Theme configuration (blue/gray color scheme).

## Key Concepts

- **Skill extraction** uses a single pre-compiled regex built from `keyword_groups` in `analyse_job_market.py`. Both original and NLTK-lemmatized forms are included in the pattern (e.g., "AI Agents" and "ai agent") so plural/variant matching works without runtime lemmatization. The core function is `extract_skills_per_job()` which returns both aggregate counts and per-job skill sets in one pass.
- **`keyword_groups`** maps skill variations to canonical names (e.g., "postgresql", "psql" → "SQL"). **`keyword_categories`** organizes skills into display categories for the UI. These two serve different purposes: groups aggregate for counting, categories separate for display.
- **Deduplication** in `clean_data()` matches on title + company + first half of description to identify semantic duplicates.
