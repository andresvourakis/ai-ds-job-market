# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Streamlit dashboard that analyzes Data Science and AI job market trends, extracting and categorizing skills from job postings using NLP (NLTK lemmatization).

## Commands

```bash
# Install dependencies (uses Poetry, requires Python ^3.10)
poetry install

# Run the dashboard
streamlit run app.py
```

## Architecture

- **app.py** — Main Streamlit dashboard: loads job data, displays posting trends, skill frequency analysis, and summary metrics. Uses `@st.cache_data` for caching.
- **analyse_job_market.py** — Core business logic: skill extraction via lemmatized keyword matching, data deduplication using semantic matching (title + company + description prefix), skill categorization into 9 groups (Programming Languages, AI/GenAI, Cloud Platforms, etc.), and keyword grouping (e.g., SQL variations → "SQL").
- **pages/1_AI_Skills_Analysis.py** — Extended analysis page: skill highlighting in job descriptions, job title normalization by seniority, AI specialization filtering.
- **data/jobs_merged.json** — Main dataset (~30MB) containing job postings with title, company, location, description, and metadata.
- **.streamlit/config.toml** — Theme configuration (blue/gray professional color scheme).

## Key Concepts

- **Skill extraction** uses NLTK `WordNetLemmatizer` to normalize word variations before matching against `keyword_groups` defined in `analyse_job_market.py`.
- **Deduplication** in `clean_data()` matches on title + company + first half of description to identify semantic duplicates.
- **`keyword_groups`** maps skill variations to canonical names (e.g., "postgresql", "psql" → "SQL"). **`keyword_categories`** organizes skills into display categories.
