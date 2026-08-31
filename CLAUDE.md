# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A two-page Streamlit dashboard built on Data Science job postings: how AI has disrupted the Data Science job market (skill extraction and categorization), and how often roles now require ML in Production skills (deployment, serving, monitoring, CI/CD, cloud platforms).

## Commands

```bash
make install   # Install dependencies (Poetry, Python ^3.10)
make run       # Run the dashboard
```

## Architecture

- **app.py** — Entrypoint. Registers the two pages with `st.navigation`; each page is a script in `views/`.
- **views/ai_in_data_science.py** — The AI page: skill frequency analysis (top 20 + AI skills), AI disruption analysis (seniority breakdown, salary comparison, skill combinations), interactive job explorer with skill highlighting, summary metrics.
- **views/ml_in_production.py** — The ML in Production page: how often Data Scientist postings require production skills (headline), practices vs named tools by area, top practices and tools, cloud platforms, seniority, monthly trend, and a job explorer limited to production jobs. Sections live in `sections/production_*.py`.
- **lib/data.py** — Shared, cached pipeline both pages start from (`load_dashboard_data`: load -> process -> dedupe; `extract_skills_cached`).
- **analyse_job_market.py** — Core business logic: skill extraction, data deduplication, keyword definitions.
- **lib/production.py** — Logic for the ML in Production page: production skill categories (practices vs tools), the "requires production skills" headline rule, and the calculations behind each chart. Scope rule: a skill belongs here if it would still matter when the model is XGBoost instead of an LLM; LLM-specific skills stay on the AI page.
- **production_report.py** — Prints every number behind the ML in Production page without Streamlit (same pipeline as the dashboard). **audit_production_keywords.py** shows real matched snippets per production keyword so precision can be judged by a human; decisions are recorded in `docs/production_keyword_audit.md`.
- **data/jobs_merged.json** — Dataset (~8.8k raw jobs, ~6.1k after dedup) with title, company, location, description, and metadata. Hosted externally (see Releases).
- **.streamlit/config.toml** — Theme configuration (blue/gray color scheme).

## Key Concepts

- **Skill extraction** uses a single pre-compiled regex built from `keyword_groups` in `analyse_job_market.py`. Both original and NLTK-lemmatized forms are included in the pattern (e.g., "AI Agents" and "ai agent") so plural/variant matching works without runtime lemmatization. Hyphens and slashes are replaced with spaces in both descriptions and keyword forms before matching, so "CI/CD", "Fine-tuning" and "fine tuning" all match the same skill. The core function is `extract_skills_per_job()` which returns both aggregate counts and per-job skill sets in one pass.
- **`keyword_groups`** maps skill variations to canonical names (e.g., "postgresql", "psql" → "SQL"). **`keyword_categories`** organizes skills into display categories for the UI. These two serve different purposes: groups aggregate for counting, categories separate for display.
- **Deduplication** in `clean_data()` matches on title + company + first half of description to identify semantic duplicates.
