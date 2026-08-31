"""
Precision audit for production keywords: show real snippets around each match
so a human can judge whether the keyword means what we think it means.

Usage:
    poetry run python audit_production_keywords.py                 # every production skill
    poetry run python audit_production_keywords.py "Model Retraining"    # one skill (canonical name)
    poetry run python audit_production_keywords.py --samples 30
"""

import argparse
import random
import re

from analyse_job_market import keyword_groups
from lib import production
from production_report import load_production_df

CONTEXT_CHARS = 90


def variations_for(skill):
    for group in keyword_groups:
        if group[0] == skill:
            return list(group)
    return [skill]


def snippets_for(skill, prod_df, samples, seed=0):
    """Random context windows around the skill's variations, one per posting."""
    # Same normalization as extraction, so the snippet shows what actually matched.
    forms = [re.sub(r"[-/]", " ", v.lower()) for v in variations_for(skill)]
    pattern = re.compile(r"\b(?:" + "|".join(re.escape(f) for f in sorted(forms, key=len, reverse=True)) + r")\b")

    hits = prod_df[prod_df["production_skills"].apply(lambda found: skill in found)]
    rows = hits.sample(n=min(samples, len(hits)), random_state=seed)

    out = []
    for _, row in rows.iterrows():
        text = re.sub(r"[-/]", " ", row["description"].lower())
        text = re.sub(r"\s+", " ", text)
        match = pattern.search(text)
        if not match:
            continue
        start = max(0, match.start() - CONTEXT_CHARS)
        end = min(len(text), match.end() + CONTEXT_CHARS)
        out.append(f"  [{row['company_name']}] ...{text[start:end]}...")
    return len(hits), out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("skill", nargs="?", help="Audit only this skill")
    parser.add_argument("--samples", type=int, default=15)
    args = parser.parse_args()

    known = sorted(production.all_production_skills())
    if args.skill and args.skill not in known:
        raise SystemExit(f"Unknown skill {args.skill!r}. Use a canonical name:\n  " + "\n  ".join(known))

    prod_df = load_production_df()
    skills = [args.skill] if args.skill else known

    for skill in skills:
        total, snippets = snippets_for(skill, prod_df, args.samples)
        print(f"\n=== {skill}  ({total} postings) ===")
        print("\n".join(snippets) if snippets else "  no matches")
