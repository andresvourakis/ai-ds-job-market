"""
Precision audit for AI keywords (AI in Data Science page): show real snippets
around each match so a human can judge whether the keyword means what we think.

For words under a context rule (analyse_job_market.CONTEXT_RULES), --rejected
shows the matches the rule throws away, to check it is not dropping real ones.

Usage:
    poetry run python audit_ai_keywords.py                        # every AI skill
    poetry run python audit_ai_keywords.py Orchestration          # one skill (canonical name)
    poetry run python audit_ai_keywords.py Orchestration --rejected
    poetry run python audit_ai_keywords.py --samples 30 --data path/to/jobs_merged.json[.gz]

Decisions are recorded in docs/ai_keyword_audit.md.
"""

import argparse
import gzip
import json
import logging
import random
import re

import streamlit  # noqa: F401  (imported first so its loggers exist; silenced below)

for _name in ("streamlit.runtime.caching.cache_data_api",
              "streamlit.runtime.scriptrunner_utils.script_run_context"):
    logging.getLogger(_name).setLevel(logging.ERROR)

from analyse_job_market import clean_data, iter_skill_matches, keyword_categories  # noqa: E402
from lib.data import fetch_job_data, process_jobs  # noqa: E402

CONTEXT_CHARS = 90
AI_SKILLS = [s for s in keyword_categories["Artificial Intelligence"] if s != "AI"]


def load_postings(path=None):
    """Deduplicated postings, from the dashboard's data source or a given file."""
    if path:
        raw = open(path, "rb").read()
        data = json.loads(gzip.decompress(raw) if path.endswith(".gz") else raw)
    else:
        data = fetch_job_data()
    return clean_data(process_jobs(data["jobs"]))


def snippets_for(skill, df, samples, rejected=False, seed=0):
    """Random context windows around the skill's matches, one per posting."""
    hits = []
    for _, row in df.iterrows():
        desc = row["description"] or ""
        for canonical, _, start, end, counted in iter_skill_matches(desc):
            if canonical == skill and counted != rejected:
                text = re.sub(r"[-/]", " ", desc)
                window = text[max(0, start - CONTEXT_CHARS):end + CONTEXT_CHARS]
                hits.append(f"  [{row['company_name']}] ...{' '.join(window.split())}...")
                break
    random.Random(seed).shuffle(hits)
    return len(hits), hits[:samples]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("skill", nargs="?", help="Audit only this skill")
    parser.add_argument("--samples", type=int, default=15)
    parser.add_argument("--rejected", action="store_true", help="Show matches dropped by the context rule")
    parser.add_argument("--data", help="Local jobs_merged.json(.gz) instead of the dashboard's data source")
    args = parser.parse_args()

    if args.skill and args.skill not in AI_SKILLS:
        raise SystemExit(f"Unknown skill {args.skill!r}. Use a canonical name:\n  " + "\n  ".join(AI_SKILLS))

    df = load_postings(args.data)
    for skill in [args.skill] if args.skill else AI_SKILLS:
        total, snippets = snippets_for(skill, df, args.samples, rejected=args.rejected)
        label = "postings where the context rule dropped it" if args.rejected else "postings"
        print(f"\n=== {skill}  ({total} {label}) ===")
        print("\n".join(snippets) if snippets else "  no matches")
