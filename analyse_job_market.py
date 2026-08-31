"""
Skill keywords and categories for job market analysis.
Uses lemmatization for robust keyword matching.
"""
import re
from collections import Counter
import nltk
nltk.download('wordnet', quiet=True)
from nltk.stem import WordNetLemmatizer

# Initialize the WordNet lemmatizer
lemmatizer = WordNetLemmatizer()

# ============================================================================
# KEYWORD_GROUPS: Aggregated skill counting
# ============================================================================
# Design rationale: Group related skills together to avoid fragmentation in top skills.
# Example: ('SQL', 'SQL Server', 'PostgreSQL', 'MySQL') → all count as "SQL"
# Why? We want "SQL skills mentioned in 300 jobs", not split across 4 entries.
#
# Structure: List of tuples (first item = canonical name, rest = variations)
# When adding: Group semantically similar skills that represent the same core competency
# ============================================================================
keyword_groups = [
    ('Machine Learning', 'ML'), ('Python', 'Python3'), ('R',), ('RStudio',), ('SQL', 'SQL Server', 'PostgreSQL', 'MySQL'),
    ('NoSQL',), ('BigQuery', 'Google BigQuery'), ('GCP', 'Google Cloud Platform', 'Google Cloud'),
    ('AWS', 'Amazon Web Services'), ('ETL', 'ELT'), ('Tableau', 'Tableau Desktop', 'Tableau Server'), ('PowerBI', 'Power BI'),
    ('Looker',), ('Looker Studio',), ('Google Sheets', 'Google Spreadsheets'), ('Excel', 'Microsoft Excel', 'Excel VBA', 'Spreadsheets'),
    ('Omni',), ('Steep',), ('LightDash',), ('Evidence',), ('Hex',), ('Mode',), ('Preset',), ('Metabase',), ('ThoughtSpot',),
    ('Databricks',), ('Spark', 'Apache Spark', 'PySpark'), ('Pytorch',), ('Tensorflow',),
    ('A/B Testing', 'experiments', 'Experimental Design', 'A/B Test', 'A/B'), ('Statistical Models',), ('ggplot', 'ggplot2'), ('matplotlib',),
    ('Pandas',), ('Seaborn',), ('GenAI', 'Generative AI'), ('ChatGPT', 'GPT-3', 'GPT-4'), ('Deep Learning', 'DL'),
    ('NLP', 'Natural Language Processing'), ('AI', 'Artificial Intelligence'), ('LLMs', 'Large Language Models'), ('sLMs', 'Small Language Models'),
    ('Java',), ('Scala',), ('Julia',), ('C++',), ('C#',), ('MATLAB',), ('SAS',), ('TypeScript',), ('Keras',), ('Scikit-learn',),
    ('XGBoost',), ('LightGBM',), ('H2O.ai',), ('CatBoost',), ('Hadoop',), ('Hive',), ('Kafka',), ('Flink',), ('Storm',), ('Presto',),
    ('HBase',), ('Cassandra',), ('MongoDB',), ('Redis',), ('Azure', 'Azure Data Lake'), ('Azure Machine Learning', 'Azure ML'), ('Amazon S3',),
    ('Amazon Redshift',), ('Google Cloud AI Platform',), ('IBM Watson',), ('D3.js',), ('Plotly',), ('QlikView',), ('Vertex AI',),
    ('MicroStrategy',), ('Snowflake',), ('Teradata',), ('Alteryx',), ('KNIME',), ('Docker',), ('Kubernetes', 'K8s'),
    ('Jenkins',), ('Git', 'GitHub', 'Bitbucket'), ('Airflow',), ('Luigi',), ('MLflow',), ('TensorBoard',),
    ('Jupyter Notebook',), ('Zeppelin Notebooks',), ('Anaconda', 'Conda'), ('Supervised Learning',), ('Unsupervised Learning',),
    ('Reinforcement Learning',), ('Feature Engineering',),
    ('Model Deployment', 'Deploying Models', 'Deploy Models', 'Deploying Machine Learning Models', 'Deploy Machine Learning Models',
     'Deploying ML Models', 'Deploy ML Models', 'Models into Production', 'Models in Production', 'Productionize', 'Productionalize'),
    ('Model Monitoring', 'Monitoring Models', 'Monitor Models', 'Model Performance Monitoring'),
    ('Transfer Learning',),
    ('Evaluation', 'Model Evaluation'), ('RAG', 'Retrieval Augmented Generation', 'Retrieval-Augmented Generation'),
    ('Vector Database', 'Vector DB', 'Embeddings Database'), ('Embeddings', 'Embedding Models'),
    ('Prompt Engineering',), ('Fine-tuning', 'Model Fine-tuning'),
    ('RLHF', 'Reinforcement Learning from Human Feedback'), ('DPO', 'Direct Preference Optimization'), ('Guardrails', 'AI Guardrails', 'LLM Guardrails'),
    ('LLM Observability', 'AI Observability'), ('Tracing', 'LLM Tracing'),
    ('AI Agents', 'LLM Agents', 'Agentic AI'), ('Orchestration', 'LLM Orchestration'),
    ('LangChain',), ('LlamaIndex',), ('Pinecone',), ('Weaviate',), ('Chroma', 'ChromaDB'),
    ('vLLM',), ('Hugging Face', 'HuggingFace'), ('OpenAI API',), ('Anthropic', 'Claude'),
    ('Semantic Search',), ('Context Window',), ('Token Optimization',), ('Hallucination Detection',),
    ('Inference Optimization',), ('Model Quantization',), ('LoRA', 'Low-Rank Adaptation'),
    ('Semantic Layer', 'Semantic Model', 'Semantic Modeling', 'Semantic Layer Model'),
    ('Agentic Analytics', 'Agent-Based Analytics', 'Agent Based Analytics', 'Agent-driven Analytics', 'Agent Driven Analytics'),
    ('Ontology', 'Ontologies'),
    ('Context Engineering', 'Context Design', 'Context Management', 'Prompt Context Engineering'),
    ('AI Workflow', 'AI Workflows', 'LLM Workflow', 'LLM Workflows', 'GenAI Workflow', 'GenAI Workflows'),
    ('Claude Code',),
    ('Codex', 'OpenAI Codex'),
    ('MCP', 'Model Context Protocol'), ('A2A', 'Agent to Agent'), ('LangGraph',), ('ADK', 'Agent Development Kit', 'Google ADK'),
    ('Agents SDK', 'OpenAI Agents SDK'), ('AutoML', ), ('Foundation Models',),

    # --- Production / MLOps skills (ML in Production page) -----------------
    # Practices describe the work (deploying, monitoring, CI/CD); tools name
    # the stack. lib/production.py decides which is which and which count
    # toward the "requires production skills" headline. Phrases are spelled
    # the way postings write them; plurals are handled by lemmatization.
    ('MLOps', 'ML Ops', 'Machine Learning Operations'),
    ('Model Serving', 'Real-time Inference', 'Batch Inference'),
    ('Production-Ready',), ('Microservices',),
    ('Containerization', 'Containerized', 'Containerize'), ('Infrastructure as Code',),
    ('CI/CD', 'Continuous Integration', 'Continuous Deployment', 'Continuous Delivery'),
    ('Automated Testing', 'Unit Testing'),
    ('Experiment Tracking',), ('Model Registry', 'Model Versioning'),
    ('ML Pipelines', 'Machine Learning Pipelines', 'Training Pipelines', 'End-to-end Machine Learning'),
    ('Drift Detection', 'Data Drift', 'Model Drift', 'Concept Drift'),
    ('Model Retraining', 'Retraining'),
    ('FastAPI',), ('Flask',), ('AWS Lambda',), ('Terraform',),
    ('GitHub Actions',), ('GitLab CI',),
    ('Weights & Biases', 'wandb'), ('DVC',),
    ('Kubeflow',), ('Dagster',), ('Prefect',), ('Metaflow',),
    ('Evidently',), ('Arize',),
    ('SageMaker', 'Amazon SageMaker'),
]

# ============================================================================
# KEYWORD_CATEGORIES: Granular skill organization
# ============================================================================
# Design rationale: Show specific skills within categories for detailed breakdown.
# Example: "Data Storage and Databases": ['SQL Server', 'PostgreSQL', 'MySQL']
# Why separate here? In categories, we want granularity to see which specific tools appear.
#
# Key difference from keyword_groups:
# - keyword_groups: Aggregate for counting (SQL + PostgreSQL + MySQL = "SQL")
# - keyword_categories: Separate for categorization (show each database system)
#
# When adding: Use canonical name from keyword_groups, place in appropriate category
# ============================================================================
keyword_categories = {
    "Programming Languages": [
        'Python', 'R', 'SQL',
        'Java', 'Scala', 'Julia', 'C++', 'C#', 'MATLAB', 'SAS', 'TypeScript'
    ],
    "Data Storage and Databases": [
        'SQL Server', 'PostgreSQL', 'MySQL', 'NoSQL', 'BigQuery',
        'Amazon S3', 'Amazon Redshift', 'Snowflake', 'Teradata',
        'HBase', 'Cassandra', 'MongoDB', 'Redis', 'Azure Data Lake'
    ],
    "Data Processing and ETL": [
        'ETL', 'Databricks', 'Spark',
        'Hadoop', 'Kafka', 'Airflow', 'Luigi', 'Alteryx', 'KNIME',
        'Hive', 'Flink', 'Storm', 'Presto'
    ],
    "Data Visualization": [
        'Tableau', 'PowerBI',
        'Looker', 'Looker Studio', 'Google Sheets',
        'Excel', 'D3.js',
        'Plotly', 'ggplot', 'matplotlib', 'Seaborn', 'QlikView',
        'MicroStrategy', 'Omni', 'Steep', 'LightDash', 'Evidence',
        'Hex', 'Mode', 'Preset', 'Metabase', 'ThoughtSpot'
    ],
    "ML/DL Frameworks and Libraries": [
        'TensorFlow', 'Pytorch', 'Keras', 'Scikit-learn', 'XGBoost',
        'LightGBM', 'H2O.ai', 'CatBoost', 'Spark MLlib'
    ],
    "Cloud Platforms": [
        'GCP', 'AWS',
        'Azure', 'Google Cloud AI Platform', 'IBM Watson', 'Azure Machine Learning'
    ],
    "Development Tools": [
        'RStudio', 'Jupyter Notebook', 'Zeppelin Notebooks', 'Anaconda',
        'Visual Studio Code', 'Git', 'Bitbucket', 'GitLab'
    ],
    "DevOps and MLOps": [
        'Docker', 'Kubernetes', 'Jenkins', 'MLflow', 'TensorBoard',
        'Model Deployment', 'Model Monitoring'
    ],
    "Core Data Science Skills": [
        'Machine Learning', 'Deep Learning', 'A/B test',
        'Statistical Models',
        'Supervised Learning', 'Unsupervised Learning', 'Reinforcement Learning',
        'Feature Engineering', 'Transfer Learning'
    ],
    "Artificial Intelligence": [
        'GenAI', 'ChatGPT', 'AI', 'LLMs', 'sLMs',
        'NLP', 'RAG', 'Vector Database', 'Embeddings',
        'Prompt Engineering', 'Fine-tuning', 'RLHF', 'DPO', 'LLM Alignment',
        'Semantic Layer', 'Agentic Analytics', 'Ontology',
        'Context Engineering', 'AI Workflow', 'Claude Code', 'Codex',
        'Guardrails', 'LLM Observability', 'Tracing', 'AI Agents', 'Orchestration',
        'LangChain', 'LlamaIndex', 'Pinecone', 'Weaviate', 'Chroma',
        'vLLM', 'Hugging Face', 'OpenAI API', 'Anthropic', 'Semantic Search',
        'Context Window', 'Token Optimization', 'Hallucination Detection',
        'Inference Optimization', 'Model Quantization', 'LoRA', 'MCP', 'A2A',
        'LangGraph', 'ADK', 'Agents SDK', 'AutoML', 'Foundation Models'
    ]
}

def clean_data(jobs_df):
    """
    Clean and filter job data.
    Adjusted for current project's data structure (job_id, posted_at fields).
    """
    # Create a composite key for semantic deduplication
    # Uses title + company + first half of description to catch true duplicates
    # even if job_id differs (e.g., reposts, relists)
    jobs_df['description_prefix'] = jobs_df['description'].fillna('').apply(
        lambda x: x[:len(x)//2] if x else ''
    )

    # Remove duplicate rows based on title + company + description prefix
    jobs_df = jobs_df.drop_duplicates(subset=['title', 'company_name', 'description_prefix'])

    # Drop the temporary column
    jobs_df = jobs_df.drop(columns=['description_prefix'])

    return jobs_df

def _build_skill_regex(keyword_groups):
    """
    Pre-compile a single regex and lookup table for all skill matching.
    Includes both original and lemmatized forms for each keyword variation.

    Returns:
        (compiled_regex, form_to_canonical) where form_to_canonical maps
        each lowercased matched form to its canonical skill name.
    """
    form_to_canonical = {}
    all_forms = []

    for group in keyword_groups:
        canonical_name = group[0]
        # Skip single-letter skills to avoid false matches
        if len(canonical_name) <= 1:
            continue

        for keyword in group:
            # Descriptions get hyphens/slashes replaced with spaces before matching
            # (see extract_skills_per_job), so keyword forms need the same treatment
            # or "CI/CD" and "Fine-tuning" would never match anything.
            lower = re.sub(r'[-/]', ' ', keyword.lower())
            lemmatized = ' '.join([lemmatizer.lemmatize(w) for w in lower.split()])
            for form in (lower, lemmatized):
                if form not in form_to_canonical:
                    form_to_canonical[form] = canonical_name
                    all_forms.append(form)

    # Sort longest first so regex matches longer variants before shorter ones
    all_forms.sort(key=len, reverse=True)
    pattern = re.compile(
        r'\b(?:' + '|'.join(re.escape(f) for f in all_forms) + r')\b',
        re.IGNORECASE
    )
    return pattern, form_to_canonical

# Pre-compile at module load (runs once)
_skill_regex, _form_to_canonical = _build_skill_regex(keyword_groups)


def extract_skills_per_job(descriptions, keyword_groups):
    """
    Extract skills from job descriptions using a single pre-compiled regex.
    Returns both per-job skill sets and aggregate counts in a single pass.

    Args:
        descriptions: List of job description strings
        keyword_groups: List of tuples containing keyword variations

    Returns:
        (skill_counts, per_job_skills) where:
        - skill_counts: Counter with aggregate skill frequencies
        - per_job_skills: List of sets, one per description, with canonical skill names
    """
    skill_counts = Counter()
    per_job_skills = []

    for desc in descriptions:
        if not desc or desc == '':
            per_job_skills.append(set())
            continue

        # Replace hyphens/slashes with spaces so "AI-powered" and "AI/ML" match
        normalized = re.sub(r'[-/]', ' ', desc)
        matches = _skill_regex.findall(normalized)
        found_skills = set(_form_to_canonical[m.lower()] for m in matches)

        per_job_skills.append(found_skills)
        for skill in found_skills:
            skill_counts[skill] += 1

    return skill_counts, per_job_skills
