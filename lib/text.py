import re

from analyse_job_market import keyword_groups


def highlight_skills_in_text(text, found_skills):
    """
    Highlight skills in text using word boundaries to avoid partial matches.
    """
    skill_variations = {}
    for group in keyword_groups:
        canonical_name = group[0]
        if canonical_name in found_skills:
            skill_variations[canonical_name] = list(group)

    all_variations = []
    for variations in skill_variations.values():
        all_variations.extend(variations)

    all_variations.sort(key=len, reverse=True)

    highlighted_text = text
    for variation in all_variations:
        pattern = r'\b' + re.escape(variation) + r'\b'
        highlighted_text = re.sub(
            pattern,
            lambda m: f"**:blue[{m.group(0)}]**",
            highlighted_text,
            flags=re.IGNORECASE
        )

    return highlighted_text
