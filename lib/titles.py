import re


def normalize_job_title(title):
    """
    Normalize job titles to group similar Data Scientist positions together
    Returns: (seniority, ai_focused)

    Word-boundary matching on a normalized title, so "Generative"/"Predictive"
    never match IV, and "Leadership" never matches lead. Precedence runs from
    the most specific role signal down: a "Senior Manager" is a Manager and an
    "Associate Director" is a Director. Level-track numerals map to the ladder
    most US companies use: I = junior, II = mid, III/IV = senior.
    """
    title_lower = title.lower()
    # Normalize punctuation to spaces so \b works on "Sr.", "II-IV", "(L3)".
    t = " " + re.sub(r"[^a-z0-9]+", " ", title_lower) + " "

    # First match wins, so order encodes precedence. The ordering principle:
    # role-defining words beat level-modifying words. "Senior Manager" is a
    # Manager whose level is senior, so Manager must be checked before Senior;
    # same for "Associate Director" (Director+, not Junior) and "Senior Staff"
    # (Staff+). Intern goes first because an intern title is an intern role no
    # matter what else it says.
    #
    # Why word boundaries instead of plain substrings: the old substring rules
    # misfiled hundreds of postings ("Generative"/"Predictive"/"University"
    # contain "iv" and became Senior; "Leadership" contains "lead" and became
    # Tech Lead). Verified 2026-09-01: fixing this moved 11.5% of postings to a
    # different bucket.
    rules = [
        ('Intern', r"\bintern(ship)?\b"),
        ('Director+', r"\bdirector\b|\bvp\b|\bvice president\b|\bchief\b"),
        # People managers, split from hands-on tech leads on purpose: manager
        # postings require production skills far less often (44% vs 59% at the
        # time of the split), and one combined bucket hid that difference.
        ('Manager', r"\bmanager\b|\bhead\b"),
        ('Staff+', r"\bstaff\b|\bprincipal\b|\bdistinguished\b"),
        ('Tech Lead', r"\blead\b"),
        # Level-track numerals: III/IV, "Level 3-5", or a bare trailing 3/4
        # ("Data Scientist 4"). The trailing-digit rule is anchored to the end
        # of the title so "3 openings" or a year never matches.
        ('Senior', r"\bsenior\b|\bsr\b|\biii\b|\biv\b|\blevel\s*[3-5]\b|\b[34] $"),
        ('Junior', r"\bjunior\b|\bjr\b|\bentry\b|\bassociate\b|\bgraduate\b|\bi\b|\blevel\s*1\b"),
        # Explicit mid signals. "II" sits here, not in Junior: on the ladder
        # most US companies use, Data Scientist II is the mid rung (and the
        # data agrees: II postings behave like Mid, not Junior). Listing these
        # is documentation; the fallback below is Mid anyway.
        ('Mid', r"\bii\b|\blevel\s*2\b|\bmid\b"),
    ]
    seniority = 'Mid'
    for label, pattern in rules:
        if re.search(pattern, t):
            seniority = label
            break

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
