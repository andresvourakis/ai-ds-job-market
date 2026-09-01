import re


def normalize_job_title(title):
    """
    Normalize job titles to group similar Data Scientist positions together
    Returns: (seniority, ai_focused)
    """
    title_lower = title.lower()

    seniority = 'Mid'
    if any(x in title_lower for x in ['senior', 'sr.', 'sr ', 'iii', 'iv']):
        seniority = 'Senior'
    elif any(x in title_lower for x in ['staff', 'principal', 'distinguished']):
        seniority = 'Staff+'
    elif any(x in title_lower for x in ['manager', 'head']):
        # People managers. Checked before 'lead' so "Lead Manager" lands here.
        seniority = 'Manager'
    elif 'lead' in title_lower:
        # Hands-on tech leads (Lead Data Scientist, Technical Lead), not people managers.
        seniority = 'Tech Lead'
    elif any(x in title_lower for x in ['director', 'vp', 'chief']):
        seniority = 'Director+'
    elif any(x in title_lower for x in ['junior', 'jr.', 'jr ', 'entry', 'associate', ' i ', ' ii ']):
        seniority = 'Junior'
    elif any(x in title_lower for x in ['intern']):
        seniority = 'Intern'

    ai_focused = bool(re.search(r'\bai\b|\bartificial intelligence\b|\bgenai\b|\bgenerative\b|\bllm\b|\bnlp\b|\bagentic\b', title_lower))

    return seniority, ai_focused


def extract_ai_specialization(title):
    """
    Extract specific AI specialization keywords mentioned in the title
    """
    title_lower = title.lower()
    specializations = []

    if re.search(r'\bgenai\b|\bgenerative ai\b|\bgen ai\b', title_lower):
        specializations.append('GenAI')
    if re.search(r'\bllm\b|\blarge language model\b', title_lower):
        specializations.append('LLM')
    if re.search(r'\bnlp\b|\bnatural language processing\b', title_lower):
        specializations.append('NLP')
    if re.search(r'\bagentic\b|\bai agent\b', title_lower):
        specializations.append('Agentic AI')
    if re.search(r'\bmachine learning\b|\bml\b', title_lower):
        specializations.append('Machine Learning')

    if re.search(r'\bai\b|\bartificial intelligence\b', title_lower):
        specializations.append('AI')

    if not specializations:
        specializations.append('General')

    return specializations


def categorize_title_type(title):
    """
    Categorize job title as either 'General' or 'AI-Specialized'
    """
    specializations = extract_ai_specialization(title)
    if specializations == ['General']:
        return 'General'
    return 'AI-Specialized'


def format_normalized_title(seniority, ai_focused):
    """Format the normalized title for display"""
    title = f"{seniority} Data Scientist"
    if ai_focused:
        title += " (AI-focused)"
    return title
