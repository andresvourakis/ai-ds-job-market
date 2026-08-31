"""
Production / MLOps analysis for the ML in Production page.

Everything specific to that page lives here: which skills count as production
skills, how they are grouped, the "requires production skills" headline rule,
and the calculations behind each chart. The keywords themselves are defined
with all the others in analyse_job_market.py (keyword_groups), because the
skill extraction uses one shared regex for every page.

Scope rule (agreed 2026-08-31): a skill belongs here if it would still matter
when the model is XGBoost instead of an LLM. LLM-specific skills (RAG,
prompting, guardrails, LLM observability) stay on the AI page.
"""

import re

import pandas as pd

from lib.titles import normalize_job_title

# Model Deployment is the one practice matched by a pattern instead of fixed
# phrases. Postings describe it with a verb plus a variable object ("deploy
# predictive models", "deploying ML solutions", "algorithms into production",
# "model productionalization"), so no phrase list is ever complete: fixed
# phrases found 16% of postings, this pattern finds 35%. It is deliberately
# narrow: the deploy verb must sit within three words of a model-like object,
# or the object must be going into production. Bare "deploy" / "production"
# (marketing campaigns deployed, oil production) do not match.
_DEPLOY_OBJECT = r"(?:models?|algorithms?|solutions?|pipelines?|machine learning|ml|ai)"
MODEL_DEPLOYMENT_PATTERN = re.compile(
    r"deploy\w*\W+(?:\w+\W+){0,3}" + _DEPLOY_OBJECT
    + r"|" + _DEPLOY_OBJECT + r"\W+(?:\w+\W+){0,2}(?:in|into|to)\W+production"
    + r"|deployed\W+in\W+production"
    + r"|productioni[sz]\w*|productionali[sz]\w*"
    + r"|(?:ml|machine learning|ai|models?)\W+(?:\w+\W+){0,2}in\W+production",
    re.IGNORECASE,
)


def mentions_model_deployment(description):
    """True if the posting describes deploying models (see pattern above)."""
    # Same hyphen/slash normalization as the keyword extraction.
    text = re.sub(r"[-/]", " ", description or "")
    return bool(MODEL_DEPLOYMENT_PATTERN.search(text))

# Every category lists its practices (the work a posting asks for) and its
# tools (the named stack) separately, because the page reports them as two
# tiers: practices give the headline demand, tools show how often the stack is
# actually named. The gap between the two is a finding in itself.
PRODUCTION_CATEGORIES = {
    "Deployment & Serving": {
        "practices": ["Model Deployment", "Model Serving", "Production-Ready"],
        "tools": ["FastAPI", "Flask", "AWS Lambda"],
    },
    "Containers & Infrastructure": {
        "practices": ["Containerization", "Infrastructure as Code"],
        "tools": ["Docker", "Kubernetes", "Terraform"],
    },
    "CI/CD & Automation": {
        "practices": ["CI/CD"],
        "tools": ["GitHub Actions", "Jenkins", "GitLab CI"],
    },
    "Experiment Tracking & Registry": {
        "practices": ["Experiment Tracking", "Model Registry"],
        "tools": ["MLflow", "Weights & Biases", "DVC"],
    },
    "Pipelines & Orchestration": {
        "practices": ["ML Pipelines"],
        "tools": ["Airflow", "Kubeflow", "Dagster", "Prefect", "Metaflow"],
    },
    "Monitoring & Drift": {
        "practices": ["Model Monitoring", "Drift Detection", "Model Retraining"],
        "tools": ["Arize"],
    },
    "Cloud & ML Platforms": {
        "practices": [],
        "tools": ["AWS", "Azure", "GCP", "Databricks", "SageMaker", "Vertex AI", "Azure Machine Learning"],
    },
}

# The platform category is handled differently from the rest (tracked, charted
# on its own, never a headline trigger except for the managed ML services).
CLOUD_CATEGORY = "Cloud & ML Platforms"
CLOUD_PLATFORMS = PRODUCTION_CATEGORIES[CLOUD_CATEGORY]["tools"]

# "MLOps" is a practice that doesn't belong to one category: a posting asking
# for MLOps is asking for the whole discipline. It counts toward the headline
# and is reported on its own.
CROSS_CUTTING_PRACTICES = ["MLOps"]

# Managed ML services that trigger the headline even though they sit in the
# tools tier: nobody names SageMaker or Vertex AI without deployment in mind.
# Bare AWS / GCP / Azure do NOT trigger it ("experience with AWS" can mean an
# S3 bucket), which is why the platform category is tracked but not a trigger.
HEADLINE_PLATFORMS = ["SageMaker", "Vertex AI", "Azure Machine Learning"]


def practice_skills():
    """All practices across categories, plus the cross-cutting ones."""
    skills = set(CROSS_CUTTING_PRACTICES)
    for category in PRODUCTION_CATEGORIES.values():
        skills.update(category["practices"])
    return skills


def tool_skills():
    """All tools across categories."""
    skills = set()
    for category in PRODUCTION_CATEGORIES.values():
        skills.update(category["tools"])
    return skills


def headline_skills():
    """Skills that make a posting count as 'requires production skills'."""
    return practice_skills() | set(HEADLINE_PLATFORMS)


def all_production_skills():
    return practice_skills() | tool_skills()


def build_production_jobs_df(df, per_job_skills):
    """
    Add production columns to every posting (the full df is kept, unlike the
    AI page, because shares are computed against all postings):
      - production_skills: list of production skills found in the posting
      - requires_production: True if the posting mentions a headline skill
      - names_tool: True if the posting names at least one production tool
    per_job_skills is positional, one set per row of df, as returned by
    extract_skills_per_job.
    """
    production_set = all_production_skills()
    headline_set = headline_skills()
    tool_set = tool_skills()

    found = []
    for description, skills in zip(df["description"], per_job_skills):
        skills = {s for s in skills if s in production_set}
        if mentions_model_deployment(description):
            skills.add("Model Deployment")
        found.append(sorted(skills))

    prod_df = df.copy()
    prod_df["production_skills"] = found
    prod_df["requires_production"] = [any(s in headline_set for s in skills) for skills in found]
    prod_df["names_tool"] = [any(s in tool_set for s in skills) for skills in found]
    return prod_df


def production_share(prod_df):
    """The headline: % of postings that require production skills."""
    if len(prod_df) == 0:
        return 0.0
    return 100 * prod_df["requires_production"].mean()


def skill_shares(prod_df, skills):
    """One row per skill: % of postings mentioning it, sorted high to low."""
    n = len(prod_df)
    counts = {skill: 0 for skill in skills}
    for found in prod_df["production_skills"]:
        for skill in found:
            if skill in counts:
                counts[skill] += 1
    rows = [{"skill": skill, "share": 100 * count / n if n else 0.0} for skill, count in counts.items()]
    return pd.DataFrame(rows).sort_values("share", ascending=False).reset_index(drop=True)


def category_summary(prod_df):
    """
    One row per category: % of postings asking for any of its practices and
    % naming any of its tools. This is the practices-vs-tools gap chart.
    """
    n = len(prod_df)
    rows = []
    for name, category in PRODUCTION_CATEGORIES.items():
        practices = set(category["practices"])
        tools = set(category["tools"])
        any_practice = sum(1 for found in prod_df["production_skills"] if practices & set(found))
        any_tool = sum(1 for found in prod_df["production_skills"] if tools & set(found))
        rows.append({
            "category": name,
            "practice_share": 100 * any_practice / n if n else 0.0,
            "tool_share": 100 * any_tool / n if n else 0.0,
        })
    return pd.DataFrame(rows)


def seniority_breakdown(prod_df):
    """
    % requiring production skills by seniority, using the same title
    normalization as the AI page so the two pages bucket titles identically.
    """
    seniority = prod_df["title"].apply(lambda t: normalize_job_title(t)[0])
    grouped = prod_df.groupby(seniority)["requires_production"].agg(["size", "mean"])
    grouped = grouped.rename(columns={"size": "postings", "mean": "share"})
    grouped["share"] = 100 * grouped["share"]
    return grouped.reset_index().rename(columns={"title": "seniority"})


# Months with fewer postings than this are dropped from the trend: a handful
# of postings makes a share swing by ten points and reads as a fake movement.
MIN_POSTINGS_PER_MONTH = 50


def monthly_trend(prod_df, min_postings=MIN_POSTINGS_PER_MONTH):
    """% requiring production skills per posting month (undated postings excluded)."""
    dated = prod_df.dropna(subset=["posted_at_date"])
    month = dated["posted_at_date"].dt.to_period("M")
    grouped = dated.groupby(month)["requires_production"].agg(["size", "mean"])
    grouped = grouped[grouped["size"] >= min_postings]
    grouped = grouped.rename(columns={"size": "postings", "mean": "share"})
    grouped["share"] = 100 * grouped["share"]
    grouped.index = grouped.index.astype(str)
    return grouped.reset_index().rename(columns={"posted_at_date": "month"})
