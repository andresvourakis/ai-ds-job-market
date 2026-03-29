# DS/AI Job Market Analysis

An interactive dashboard that analyzes how AI has disrupted the Data Science job market. Built with Streamlit, it extracts skills from Data Science job postings using NLP to reveal how AI skills have reshaped what employers are looking for.

## Features

**Job Market Overview**
- Job posting distribution by date
- Top 20 most in-demand skills with frequency analysis
- Skills broken down by category (Programming Languages, Cloud Platforms, AI/GenAI, etc.)

**AI Disruption Analysis**
- How many Data Science jobs now require AI skills
- Seniority-level breakdown of AI skill demand
- General Data Scientist vs AI-specialized titles
- Salary premium for AI-skilled Data Scientists vs those without
- Most common AI skill combinations appearing in job postings
- Interactive job explorer with skill highlighting in descriptions

## Getting Started

### Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)

### Installation

```bash
git clone https://github.com/andresvourakis/ds-ai-job-market-analysis.git
cd ds-ai-job-market-analysis
make install
```

### Running the Dashboard

```bash
make run
```

The dashboard will open at `http://localhost:8501`.

## Data

The dashboard reads from `data/jobs_merged.json`, which contains job postings collected via Google's Jobs API. Each posting includes:

- Job title, company, and location
- Full job description
- Salary information (when available)
- Posting date and schedule type

## How Skill Extraction Works

Skills are identified by matching job descriptions against a curated set of ~230 keyword groups defined in `analyse_job_market.py`. Each group maps variations of a skill to a canonical name (e.g., "PostgreSQL", "psql" → "SQL"). Both original and lemmatized forms are matched to handle plurals and word variations (e.g., "AI Agents" ↔ "AI Agent").

Skills are organized into 10 categories:

| Category | Examples |
|---|---|
| Programming Languages | Python, R, SQL, Java, Scala |
| Data Storage & Databases | PostgreSQL, MongoDB, Snowflake, Redis |
| Data Processing & ETL | Spark, Kafka, Airflow, Databricks |
| Data Visualization | Tableau, Power BI, Looker, Plotly |
| ML/DL Frameworks | PyTorch, TensorFlow, Scikit-learn, XGBoost |
| Cloud Platforms | AWS, GCP, Azure |
| Development Tools | Git, Jupyter Notebook, Anaconda |
| DevOps & MLOps | Docker, Kubernetes, MLflow |
| Core Data Science | Machine Learning, A/B Testing, Feature Engineering |
| Artificial Intelligence | LLMs, GenAI, RAG, Prompt Engineering, LangChain |

## Tech Stack

- **[Streamlit](https://streamlit.io/)** — Web framework
- **[Pandas](https://pandas.pydata.org/)** — Data manipulation
- **[Plotly](https://plotly.com/python/)** — Interactive visualizations
- **[NLTK](https://www.nltk.org/)** — Lemmatization for keyword matching

## License

This project is open source. See [LICENSE](LICENSE) for details.
