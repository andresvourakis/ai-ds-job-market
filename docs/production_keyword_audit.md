# Production keyword audit

How the production / MLOps keywords (ML in Production page) were validated,
and why some candidates were left out. Re-run any check with:

    poetry run python audit_production_keywords.py "<canonical name>" --samples 20

Method: for every keyword, read a random sample of real matched snippets from
the deduplicated Data Scientist postings and judge whether the match means what
the keyword claims. Keep at roughly 90% precision or better; drop or tighten
anything below. Rarity alone never removes a keyword: the Data-Scientist-only
population decides relevance, the audit only decides correctness.

Audited 2026-08-31 on 6,110 deduplicated postings.

## Scope rule

A skill belongs on the production page if it would still matter when the
model is XGBoost instead of an LLM. LLM-specific skills (RAG, prompting,
guardrails, LLM observability, vLLM) stay on the AI page.

## Headline rule

A posting "requires production skills" if it mentions at least one practice,
or one managed ML platform (SageMaker, Vertex AI, Azure Machine Learning).
Tools alone and bare AWS / GCP / Azure do not count: "experience with AWS"
can mean an S3 bucket.

## The one pattern-matched practice

Model Deployment is matched by `MODEL_DEPLOYMENT_PATTERN` in
`lib/production.py`, not by fixed phrases. Postings describe deployment with
a verb plus a variable object ("deploy predictive models", "deploying ML
solutions", "algorithms into production", "model productionalization"), so a
phrase list found 16% of postings while a bounded pattern finds 36%. Sampled
24 matches: 22 clearly about deploying models, 2 vague. Bare "deploy" or
"production" (marketing campaigns deployed, oil production) do not match.

## Kept (sampled, precision at or above the bar)

| Keyword | Notes |
|---|---|
| MLOps, CI/CD, Containerization, Infrastructure as Code | Unambiguous |
| Experiment Tracking, Model Registry (incl. "model versioning") | Unambiguous |
| ML Pipelines (incl. "end-to-end machine learning") | Unambiguous |
| Model Monitoring, Drift Detection, Model Retraining | "retraining" was a worry; all sampled uses were model retraining |
| Model Serving (incl. real-time / batch inference) | Unambiguous |
| Production-Ready | ~10 of 12 about production models/solutions; borderline but kept |
| Flask | 1 of 12 was "Hydro Flask" (a brand); otherwise APIs and app frameworks |
| Docker, Kubernetes, Terraform, Jenkins, GitHub Actions, GitLab CI | Proper nouns |
| MLflow, Weights & Biases, DVC, Airflow, Kubeflow, Dagster, Prefect, Metaflow | Proper nouns; Prefect never matched a typo of "perfect" |
| Arize, FastAPI, AWS Lambda | Proper nouns |
| AWS, Azure, GCP, Databricks, SageMaker, Vertex AI, Azure Machine Learning | Proper nouns; tracked, only the last three trigger the headline |

## Dropped

| Candidate | Why |
|---|---|
| Microservices | Mostly generic Java / Spring Boot software postings; not a signal of deploying models |
| Automated Testing / Unit Testing | Generic software hygiene, like Git; does not indicate production ML work |
| Evidently | One match in the whole dataset, and the word is an English adverb waiting to become false positives |
| Neptune | Matches Amazon Neptune (graph database), not neptune.ai |
| Bare "vertex", bare "lambda" | Python lambdas and the word vertex; the full names are used instead |
| BentoML, Seldon, KServe, TorchServe, Ray Serve, Triton, ONNX, Feast, Tecton, Great Expectations, WhyLabs, Comet, CircleCI, Argo, ECS/EKS/GKE/Cloud Run | Zero or near-zero matches; easy to add later |
| Git / GitHub | Table stakes for everyone; tracked elsewhere, never a production signal |
