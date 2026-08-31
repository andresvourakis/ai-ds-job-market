"""
Export every chart from the Streamlit dashboard as a high-resolution PNG.

Usage:
    poetry run python export_charts.py [--output-dir output/charts] [--scale 3]
"""

import argparse
import re
from collections import Counter
from pathlib import Path

import pandas as pd
import plotly.express as px

from lib.data import fetch_job_data
from analyse_job_market import (
    keyword_groups,
    keyword_categories,
    extract_skills_per_job,
    clean_data,
)


def normalize_job_title(title):
    title_lower = title.lower()
    seniority = "Mid"
    if any(x in title_lower for x in ["senior", "sr.", "sr ", "iii", "iv"]):
        seniority = "Senior"
    elif any(x in title_lower for x in ["staff", "principal", "distinguished"]):
        seniority = "Staff+"
    elif any(x in title_lower for x in ["lead", "manager", "head"]):
        seniority = "Lead/Manager"
    elif any(x in title_lower for x in ["director", "vp", "chief"]):
        seniority = "Director+"
    elif any(x in title_lower for x in ["junior", "jr.", "jr ", "entry", "associate", " i ", " ii "]):
        seniority = "Junior"
    elif "intern" in title_lower:
        seniority = "Intern"
    ai_focused = bool(re.search(
        r"\bai\b|\bartificial intelligence\b|\bgenai\b|\bgenerative\b|\bllm\b|\bnlp\b|\bagentic\b",
        title_lower,
    ))
    return seniority, ai_focused


def extract_ai_specialization(title):
    title_lower = title.lower()
    specs = []
    if re.search(r"\bgenai\b|\bgenerative ai\b|\bgen ai\b", title_lower):
        specs.append("GenAI")
    if re.search(r"\bllm\b|\blarge language model\b", title_lower):
        specs.append("LLM")
    if re.search(r"\bnlp\b|\bnatural language processing\b", title_lower):
        specs.append("NLP")
    if re.search(r"\bagentic\b|\bai agent\b", title_lower):
        specs.append("Agentic AI")
    if re.search(r"\bmachine learning\b|\bml\b", title_lower):
        specs.append("Machine Learning")
    if re.search(r"\bai\b|\bartificial intelligence\b", title_lower):
        specs.append("AI")
    if not specs:
        specs.append("General")
    return specs


def categorize_title_type(title):
    return "General" if extract_ai_specialization(title) == ["General"] else "AI-Specialized"


def parse_salary(salary_str):
    if not salary_str:
        return None, None
    salary_str = salary_str.lower().replace(",", "").replace("$", "")
    is_hourly = "hour" in salary_str
    k_matches = re.findall(r"(\d+\.?\d*)\s*k", salary_str)
    plain_matches = re.findall(r"(\d{4,})", salary_str.replace("k", ""))
    values = []
    if k_matches:
        values = [float(n) * 1000 for n in k_matches]
    elif plain_matches:
        values = [float(n) for n in plain_matches]
    elif is_hourly:
        for n in re.findall(r"(\d+\.?\d*)", salary_str):
            v = float(n)
            if v < 500:
                values.append(v * 2080)
    if not values:
        return None, None
    if len(values) == 1:
        return values[0], values[0]
    return min(values[:2]), max(values[:2])


def build_dataframe(jobs):
    processed = []
    for job in jobs:
        ext = job.get("detected_extensions", {}) or {}
        salary_raw = ext.get("salary") if isinstance(ext, dict) else None
        salary_min, salary_max = parse_salary(salary_raw)
        salary_mid = (salary_min + salary_max) / 2 if salary_min and salary_max else None
        processed.append({
            "title": job.get("title", "N/A"),
            "company_name": job.get("company_name", "N/A"),
            "location": job.get("location", "N/A"),
            "description": job.get("description", ""),
            "posted_at": ext.get("posted_at", "N/A") if isinstance(ext, dict) else "N/A",
            "salary": salary_raw or "N/A",
            "salary_min": salary_min,
            "salary_max": salary_max,
            "salary_mid": salary_mid,
        })
    df = pd.DataFrame(processed)
    df["posted_at_date"] = pd.to_datetime(df["posted_at"], errors="coerce")
    return clean_data(df)


def write(fig, out_dir: Path, name: str, width: int, height: int, scale: int):
    out_path = out_dir / f"{name}.png"
    fig.write_image(str(out_path), width=width, height=height, scale=scale)
    print(f"  wrote {out_path}  ({width * scale}x{height * scale}px)")


def style_horizontal(fig, height: int, left_margin: int = 160):
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(
        yaxis={
            "categoryorder": "total ascending",
            "tickfont": dict(color="#1F2937", size=12),
            "title_font": dict(color="#1F2937", size=13),
            "automargin": True,
        },
        height=height,
        title_font_size=20,
        font=dict(color="#1F2937", size=12),
        xaxis=dict(tickfont=dict(color="#1F2937", size=12), title_font=dict(color="#1F2937", size=13)),
        coloraxis_showscale=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=left_margin, r=60, t=80, b=60),
    )


def export_all(out_dir: Path, scale: int):
    out_dir.mkdir(parents=True, exist_ok=True)

    jobs = fetch_job_data().get("jobs", [])
    df = build_dataframe(jobs)
    print(f"Loaded {len(df):,} jobs")

    skill_counts, per_job_skills = extract_skills_per_job(df["description"].tolist(), keyword_groups)
    ai_skills = keyword_categories.get("Artificial Intelligence", [])
    ai_skills_set = set(ai_skills)

    ai_indices = []
    ai_job_skills = {}
    for i, idx in enumerate(df.index):
        found = [s for s in per_job_skills[i] if s in ai_skills_set]
        if found:
            ai_indices.append(idx)
            ai_job_skills[idx] = found

    ai_jobs_df = df.loc[ai_indices].copy()
    ai_jobs_df["ai_skills"] = ai_jobs_df.index.map(lambda idx: ai_job_skills.get(idx, []))
    ai_jobs_df["ai_skill_count"] = ai_jobs_df["ai_skills"].apply(len)

    color_scale_main = [[0, "#D9E5F1"], [0.5, "#6B88A8"], [1, "#2E4A6B"]]
    color_scale_pairs = [[0, "#E3EBF3"], [0.5, "#7A95B0"], [1, "#3B5F7F"]]

    base_w = 1100

    # 1. Top 20 most mentioned skills
    print("Building chart: top_20_skills")
    all_skills_df = pd.DataFrame(skill_counts.most_common(20), columns=["Skill", "Frequency"])
    all_skills_df["Percentage"] = (all_skills_df["Frequency"] / len(df) * 100).round(1)
    fig = px.bar(
        all_skills_df, x="Frequency", y="Skill", orientation="h",
        title="Top 20 Most Mentioned Skills (% of all jobs)",
        labels={"Frequency": "Number of Job Postings"},
        color="Frequency", color_continuous_scale=color_scale_main, text="Percentage",
    )
    style_horizontal(fig, 700)
    write(fig, out_dir, "01_top_20_skills", base_w, 700, scale)

    # 2. Top 10 AI skills
    print("Building chart: top_10_ai_skills")
    ai_skill_counts_sorted = sorted(
        [(s, skill_counts.get(s, 0)) for s in ai_skills if s != "AI"],
        key=lambda x: x[1], reverse=True,
    )[:10]
    ai_skills_df = pd.DataFrame(ai_skill_counts_sorted, columns=["Skill", "Frequency"])
    ai_skills_df["Percentage"] = (ai_skills_df["Frequency"] / len(df) * 100).round(1)
    fig = px.bar(
        ai_skills_df, x="Frequency", y="Skill", orientation="h",
        title="Top 10 AI Skills in Data Science Jobs (% of all jobs)",
        labels={"Frequency": "Number of Job Postings"},
        color="Frequency", color_continuous_scale=color_scale_main, text="Percentage",
    )
    style_horizontal(fig, 600)
    write(fig, out_dir, "02_top_10_ai_skills", base_w, 600, scale)

    if len(ai_jobs_df) > 0:
        ai_jobs_df["seniority"], ai_jobs_df["ai_in_title"] = zip(*ai_jobs_df["title"].apply(normalize_job_title))

        # 3. AI jobs by seniority
        print("Building chart: ai_jobs_by_seniority")
        seniority_counts = ai_jobs_df["seniority"].value_counts()
        seniority_df = pd.DataFrame({"Seniority": seniority_counts.index, "Frequency": seniority_counts.values})
        seniority_df["Percentage"] = (seniority_df["Frequency"] / len(ai_jobs_df) * 100).round(1)
        fig = px.bar(
            seniority_df, x="Frequency", y="Seniority", orientation="h",
            title="AI Jobs by Seniority Level", labels={"Frequency": "Number of Postings"},
            color="Frequency", color_continuous_scale=color_scale_main, text="Percentage",
        )
        style_horizontal(fig, 500)
        write(fig, out_dir, "03_ai_jobs_by_seniority", base_w, 500, scale)

        # 4. General vs AI-specialized
        print("Building chart: general_vs_ai_specialized")
        ai_jobs_df["title_category"] = ai_jobs_df["title"].apply(categorize_title_type)
        title_type_counts = ai_jobs_df["title_category"].value_counts()
        title_type_df = pd.DataFrame({"Title Type": title_type_counts.index, "Frequency": title_type_counts.values})
        title_type_df["Percentage"] = (title_type_df["Frequency"] / len(ai_jobs_df) * 100).round(1)
        fig = px.bar(
            title_type_df, x="Frequency", y="Title Type", orientation="h",
            title="General vs AI-Specialized Job Titles", labels={"Frequency": "Number of Postings"},
            color="Frequency", color_continuous_scale=color_scale_main, text="Percentage",
        )
        style_horizontal(fig, 400)
        write(fig, out_dir, "04_general_vs_ai_specialized", base_w, 400, scale)

        # 5. Specific AI specialization types
        print("Building chart: ai_specialization_types")
        all_specializations = []
        for title in ai_jobs_df["title"]:
            specs = [s for s in extract_ai_specialization(title) if s != "General"]
            all_specializations.extend(specs)
        if all_specializations:
            spec_counts = pd.Series(all_specializations).value_counts()
            spec_df = pd.DataFrame({"Specialization": spec_counts.index, "Frequency": spec_counts.values})
            ai_specialized_count = len(ai_jobs_df[ai_jobs_df["title_category"] == "AI-Specialized"])
            spec_df["Percentage"] = (spec_df["Frequency"] / ai_specialized_count * 100).round(1)
            fig = px.bar(
                spec_df, x="Frequency", y="Specialization", orientation="h",
                title="Breakdown of AI Specialization Types", labels={"Frequency": "Number of Job Titles"},
                color="Frequency", color_continuous_scale=color_scale_main, text="Percentage",
            )
            style_horizontal(fig, 450)
            write(fig, out_dir, "05_ai_specialization_types", base_w, 450, scale)

        # 6. Top 10 AI skill pairs
        print("Building chart: top_10_ai_skill_pairs")
        skill_pairs = Counter()
        for skills_list in ai_jobs_df["ai_skills"]:
            if len(skills_list) >= 2:
                sorted_skills = sorted(skills_list)
                for i in range(len(sorted_skills)):
                    for j in range(i + 1, len(sorted_skills)):
                        skill_pairs[(sorted_skills[i], sorted_skills[j])] += 1
        if skill_pairs:
            top_pairs = skill_pairs.most_common(10)
            pairs_df = pd.DataFrame(
                [(f"{p[0]} + {p[1]}", c) for p, c in top_pairs],
                columns=["Skill Combination", "Frequency"],
            )
            pairs_df["Percentage"] = (pairs_df["Frequency"] / len(ai_jobs_df) * 100).round(1)
            fig = px.bar(
                pairs_df, x="Frequency", y="Skill Combination", orientation="h",
                title="Top 10 AI Skill Pairs", labels={"Frequency": "Number of Jobs"},
                color="Frequency", color_continuous_scale=color_scale_pairs, text="Percentage",
            )
            style_horizontal(fig, 550, left_margin=200)
            write(fig, out_dir, "06_top_10_ai_skill_pairs", base_w, 550, scale)

        # 7. AI skill depth
        print("Building chart: ai_skill_depth")
        skill_depth_bins = pd.cut(
            ai_jobs_df["ai_skill_count"],
            bins=[1, 3, 6, 11, float("inf")],
            labels=["1-2 skills", "3-5 skills", "6-10 skills", "11+ skills"],
            right=False,
        )
        depth_counts = skill_depth_bins.value_counts().sort_index()
        depth_df = pd.DataFrame({"Skill Range": depth_counts.index, "Number of Jobs": depth_counts.values})
        depth_df["Percentage"] = (depth_df["Number of Jobs"] / len(ai_jobs_df) * 100).round(1)
        fig = px.bar(
            depth_df, x="Number of Jobs", y="Skill Range", orientation="h",
            title="Distribution of AI Skill Requirements", labels={"Number of Jobs": "Number of Postings"},
            color="Number of Jobs", color_continuous_scale=color_scale_main, text="Percentage",
        )
        style_horizontal(fig, 400)
        write(fig, out_dir, "07_ai_skill_depth", base_w, 400, scale)

        # 8. Salary comparison: AI vs non-AI
        print("Building chart: salary_ai_vs_non_ai")
        jobs_with_salary = ai_jobs_df[ai_jobs_df["salary_mid"].notna()].copy()
        if len(jobs_with_salary) >= 20:
            jobs_with_salary["seniority"] = jobs_with_salary["title"].apply(lambda t: normalize_job_title(t)[0])
            non_ai_jobs = df[~df.index.isin(ai_jobs_df.index)]
            non_ai_with_salary = non_ai_jobs[non_ai_jobs["salary_mid"].notna()].copy()
            if len(non_ai_with_salary) >= 10:
                non_ai_with_salary["seniority"] = non_ai_with_salary["title"].apply(lambda t: normalize_job_title(t)[0])
                seniority_order = ["Junior", "Mid", "Senior", "Staff+", "Lead/Manager", "Director+"]
                comparison = []
                for sen in seniority_order:
                    a = jobs_with_salary[jobs_with_salary["seniority"] == sen]
                    n = non_ai_with_salary[non_ai_with_salary["seniority"] == sen]
                    if len(a) >= 3 and len(n) >= 3:
                        am, nm = a["salary_mid"].median(), n["salary_mid"].median()
                        comparison.append({
                            "Seniority": sen, "AI Jobs Median": am, "Non-AI Jobs Median": nm,
                            "Pct Difference": (am - nm) / nm * 100,
                            "AI Sample": len(a), "Non-AI Sample": len(n),
                        })
                if comparison:
                    comparison_df = pd.DataFrame(comparison)
                    chart_data = []
                    for _, row in comparison_df.iterrows():
                        chart_data.append({"Seniority": row["Seniority"], "Category": "AI Jobs",
                                           "Median Salary": row["AI Jobs Median"], "Sample Size": row["AI Sample"]})
                        chart_data.append({"Seniority": row["Seniority"], "Category": "Non-AI Jobs",
                                           "Median Salary": row["Non-AI Jobs Median"], "Sample Size": row["Non-AI Sample"]})
                    chart_df = pd.DataFrame(chart_data)
                    fig = px.bar(
                        chart_df, x="Seniority", y="Median Salary", color="Category", barmode="group",
                        title="Median Salary by Seniority: AI vs Non-AI Jobs",
                        color_discrete_map={"AI Jobs": "#2E4A6B", "Non-AI Jobs": "#8BA5C0"},
                        hover_data={"Sample Size": True},
                    )
                    for _, row in comparison_df.iterrows():
                        max_salary = max(row["AI Jobs Median"], row["Non-AI Jobs Median"])
                        fig.add_annotation(
                            x=row["Seniority"], y=max_salary, text=f"{row['Pct Difference']:+.1f}%",
                            showarrow=False, yshift=15,
                            font=dict(size=11, color="#1F2937", family="Arial Black"),
                        )
                    fig.update_layout(
                        title_font_size=20,
                        font=dict(color="#1F2937", size=12),
                        xaxis=dict(categoryorder="array", categoryarray=seniority_order,
                                   tickfont=dict(color="#1F2937", size=12),
                                   title_font=dict(color="#1F2937", size=13)),
                        yaxis=dict(tickformat="$,.0f",
                                   tickfont=dict(color="#1F2937", size=12),
                                   title_font=dict(color="#1F2937", size=13),
                                   automargin=True),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        height=500,
                        plot_bgcolor="white",
                        paper_bgcolor="white",
                        margin=dict(l=140, r=60, t=80, b=60),
                    )
                    write(fig, out_dir, "08_salary_ai_vs_non_ai", base_w, 500, scale)
                else:
                    print("  skipped: not enough seniority overlap for salary comparison")
            else:
                print(f"  skipped: only {len(non_ai_with_salary)} non-AI jobs with salary data")
        else:
            print(f"  skipped: only {len(jobs_with_salary)} AI jobs with salary data")

    # 9. Job postings distribution by date
    print("Building chart: job_postings_by_date")
    all_df_with_dates = df[df["posted_at_date"].notna()].copy()
    if len(all_df_with_dates) > 0:
        date_counts = all_df_with_dates["posted_at_date"].dt.date.value_counts().sort_index()
        fig = px.bar(
            x=date_counts.index, y=date_counts.values,
            labels={"x": "Posted Date", "y": "Number of Jobs"},
            title=f"Job Postings Distribution by Date ({len(all_df_with_dates)} jobs)",
            color=date_counts.values, color_continuous_scale=color_scale_main,
        )
        fig.update_layout(
            xaxis_tickangle=-45, height=600, title_font_size=20,
            font=dict(color="#1F2937", size=12),
            xaxis=dict(tickfont=dict(color="#1F2937", size=12), title_font=dict(color="#1F2937", size=13)),
            yaxis=dict(tickfont=dict(color="#1F2937", size=12), title_font=dict(color="#1F2937", size=13),
                       automargin=True),
            coloraxis_showscale=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=130, r=60, t=80, b=80),
        )
        write(fig, out_dir, "09_job_postings_by_date", base_w, 600, scale)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="output/charts", type=Path)
    parser.add_argument("--scale", default=3, type=int,
                        help="Resolution multiplier (1=1x, 3=3x, 4=4x). Higher = sharper PNGs.")
    args = parser.parse_args()
    print(f"Exporting at scale={args.scale}x to {args.output_dir.resolve()}")
    export_all(args.output_dir, args.scale)
    print("Done.")


if __name__ == "__main__":
    main()
