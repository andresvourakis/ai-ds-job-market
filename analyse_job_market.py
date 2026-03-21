"""
Skill keywords and categories for job market analysis.
Uses lemmatization for robust keyword matching.
"""
import re
from collections import Counter
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
    ('HBase',), ('Cassandra',), ('MongoDB',), ('Redis',), ('Azure', 'Azure Data Lake'), ('Azure Machine Learning',), ('Amazon S3',),
    ('Amazon Redshift',), ('Google Cloud AI Platform',), ('IBM Watson',), ('D3.js',), ('Plotly',), ('QlikView',), ('Vertext AI',),
    ('MicroStrategy',), ('Snowflake',), ('Teradata',), ('Alteryx',), ('KNIME',), ('Docker',), ('Kubernetes',),
    ('Jenkins',), ('Git', 'GitHub', 'Bitbucket'), ('Airflow',), ('Luigi',), ('MLflow',), ('TensorBoard',),
    ('Jupyter Notebook',), ('Zeppelin Notebooks',), ('Anaconda', 'Conda'), ('Supervised Learning',), ('Unsupervised Learning',),
    ('Reinforcement Learning',), ('Feature Engineering',), ('Model Deployment',), ('Model Monitoring',), ('Transfer Learning',),
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
    ('Agents SDK', 'OpenAI Agents SDK'), ('AutoML', ), ('Foundation Models')
]

keyword_variations = [
    ('Python', 'Python3'), ('R',), ('SQL',),
    ('Java',), ('Scala',), ('Julia',), ('C++',), ('C#',), ('MATLAB',), ('SAS',),
    ('SQL Server',), ('PostgreSQL',), ('MySQL',), ('NoSQL',), ('BigQuery', 'Google BigQuery'),
    ('Amazon S3',), ('Amazon Redshift',), ('Snowflake',), ('Teradata',),
    ('HBase',), ('Cassandra',), ('MongoDB',), ('Redis',), ('Azure Data Lake',),
    ('ETL', 'ELT'), ('Databricks',), ('Spark', 'Apache Spark', 'PySpark'),
    ('Hadoop',), ('Kafka',), ('Airflow',), ('Luigi',), ('Alteryx',), ('KNIME',),
    ('Tableau', 'Tableau Desktop', 'Tableau Server'), ('PowerBI', 'Power BI'),
    ('Looker',), ('Looker Studio',), ('Google Sheets', 'Google Spreadsheets'),
    ('Excel', 'Microsoft Excel', 'Excel VBA', 'Spreadsheets'), ('D3.js',),
    ('Plotly',), ('ggplot', 'ggplot2'), ('matplotlib',), ('Seaborn',), ('QlikView',),
    ('MicroStrategy',),
    ('TensorFlow',), ('Pytorch',), ('Keras',), ('Scikit-learn',), ('XGBoost',),
    ('LightGBM',), ('H2O.ai',), ('CatBoost',), ('Spark MLlib',),
    ('Hadoop',), ('Spark',), ('Hive',), ('Flink',), ('Storm',), ('Presto',),
    ('GCP', 'Google Cloud Platform', 'Google Cloud'), ('AWS', 'Amazon Web Services'),
    ('Azure',), ('Google Cloud AI Platform',), ('IBM Watson',), ('Azure Machine Learning',),
    ('RStudio',), ('Jupyter Notebook',), ('Zeppelin Notebooks',), ('Anaconda', 'Conda'),
    ('Visual Studio Code',),
    ('Git', 'GitHub'), ('Bitbucket',), ('GitLab',),
    ('Docker',), ('Kubernetes',), ('Jenkins',), ('MLflow',), ('TensorBoard',),
    ('Model Deployment',), ('Model Monitoring',),
    ('Machine Learning', 'ML'), ('A/B Testing', 'experiments', 'Experimental Design', 'A/B Test', 'A/B'),
    ('Statistical Models',), ('GenAI',), ('ChatGPT', 'GPT-3', 'GPT-4'),
    ('Deep Learning', 'DL'), ('NLP', 'Natural Language Processing'),
    ('AI', 'Artificial Intelligence'), ('LLMs', 'Large Language Models'),
    ('Semantic Layer', 'Semantic Model', 'Semantic Modeling', 'Semantic Layer Model'),
    ('Agentic Analytics', 'Agent-Based Analytics', 'Agent Based Analytics', 'Agent-driven Analytics', 'Agent Driven Analytics'),
    ('Ontology', 'Ontologies'),
    ('Context Engineering', 'Context Design', 'Context Management', 'Prompt Context Engineering'),
    ('AI Workflow', 'AI Workflows', 'LLM Workflow', 'LLM Workflows', 'GenAI Workflow', 'GenAI Workflows'),
    ('Claude Code',),
    ('Codex', 'OpenAI Codex'),
    ('Supervised Learning',), ('Unsupervised Learning',), ('Reinforcement Learning',),
    ('Feature Engineering',), ('Transfer Learning',)
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

#===========

# Define the custom function
def format_title(title):
    """Categorize job titles into standard categories"""
    if 'Data Scien' in title:
        return 'Data Scientist'
    elif 'Analyst' in title:
        return 'Data Analyst'
    elif 'Engineer' in title:
        return 'Data Engineer'
    elif 'Machine Learning' in title or 'ML Engineer' in title:
        return 'ML Engineer'
    else:
        return 'Other'

# Define the custom function
def format_experience_level(experience_level):
    if 'mid_senior' in experience_level:
        return 'Mid-Senior'
    elif 'entry' in experience_level:
        return 'Entry'
    else:
        return experience_level

def lemmatize_keyword_groups(keyword_groups):
    # Lemmatize keywords and prepare the patterns
    keyword_patterns = {}
    for group in keyword_groups:
        lemmatized_keywords = [' '.join([lemmatizer.lemmatize(word.lower()) for word in keyword.split()]) for keyword in group]
        first_keyword = group[0]
        pattern = r'\b(' + '|'.join(re.escape(keyword) for keyword in lemmatized_keywords) + r')\b'
        keyword_patterns[first_keyword] = pattern

    return keyword_patterns

def lemmatize_keyword_variations(keyword_variations):
    # Lemmatize keywords and prepare the patterns
    keyword_patterns = {}
    for variations in keyword_variations:
        first_keyword = variations[0]
        lemmatized_keywords = [' '.join([lemmatizer.lemmatize(word.lower()) for word in keyword.split()]) for keyword in variations]
        pattern = r'\b(' + '|'.join(re.escape(keyword) for keyword in lemmatized_keywords) + r')\b'
        keyword_patterns[first_keyword] = pattern

    return keyword_patterns

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

def process_data(jobs_df):
    """
    Process job data and add formatted columns.
    Adjusted for current project's data structure.
    """
    # Add formatted title category
    jobs_df['title_formatted'] = jobs_df['title'].apply(format_title)

    return jobs_df

def extract_skills_with_lemmatization(descriptions, keyword_groups):
    """
    Extract skills from job descriptions using lemmatized keyword matching.
    More robust than simple string matching as it handles word variations.

    Args:
        descriptions: List of job description strings
        keyword_groups: List of tuples containing keyword variations

    Returns:
        Counter object with skill frequencies
    """
    # Build a lookup of lemmatized keywords to canonical names
    keyword_lookup = {}
    for group in keyword_groups:
        canonical_name = group[0]
        # Skip single-letter skills to avoid false matches
        if len(canonical_name) <= 1:
            continue

        for keyword in group:
            # Lemmatize multi-word keywords as a single unit
            lemmatized = ' '.join([lemmatizer.lemmatize(word.lower()) for word in keyword.split()])
            keyword_lookup[lemmatized] = canonical_name

    skill_counts = Counter()
    for desc in descriptions:
        if not desc or desc == '':
            continue

        # Tokenize description into words, preserving multi-word phrases
        # Split on whitespace and punctuation but keep word boundaries
        raw_words = re.findall(r'\b[\w\-/]+\b', desc.lower())

        # Further split on hyphens and slashes to catch terms like "AI-powered" or "AI/ML"
        words = []
        for word in raw_words:
            # Split on hyphens and slashes
            parts = re.split(r'[-/]', word)
            words.extend([p for p in parts if p])  # Add non-empty parts

        # Track which skills have been found in this description (to count once per job)
        found_skills = set()

        # Check single words
        for word in words:
            lemmatized_word = lemmatizer.lemmatize(word)
            if lemmatized_word in keyword_lookup:
                found_skills.add(keyword_lookup[lemmatized_word])

        # Check multi-word phrases (2-5 words)
        for n in range(2, 6):
            for i in range(len(words) - n + 1):
                phrase = ' '.join(words[i:i+n])
                lemmatized_phrase = ' '.join([lemmatizer.lemmatize(w) for w in phrase.split()])
                if lemmatized_phrase in keyword_lookup:
                    found_skills.add(keyword_lookup[lemmatized_phrase])

        # Increment counts for all found skills
        for skill in found_skills:
            skill_counts[skill] += 1

    return skill_counts
