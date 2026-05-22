from collections import Counter

import pandas as pd
import plotly.express as px
import streamlit as st

from lib.charts import BLUE_SCALE, style_horizontal_bar


def render(ai_jobs_df):
    _render_combinations(ai_jobs_df)
    _render_depth(ai_jobs_df)


def _render_combinations(ai_jobs_df):
    st.header("Most Common AI Skill Combinations")

    if len(ai_jobs_df) == 0:
        return

    skill_pairs = Counter()

    for skills_list in ai_jobs_df['ai_skills']:
        if len(skills_list) >= 2:
            sorted_skills = sorted(skills_list)
            for i in range(len(sorted_skills)):
                for j in range(i + 1, len(sorted_skills)):
                    skill_pairs[(sorted_skills[i], sorted_skills[j])] += 1

    if skill_pairs:
        top_pairs = skill_pairs.most_common(10)
        pairs_df = pd.DataFrame(
            [(f"{pair[0]} + {pair[1]}", count) for pair, count in top_pairs],
            columns=['Skill Combination', 'Frequency']
        )
        pairs_df['Percentage'] = (pairs_df['Frequency'] / len(ai_jobs_df) * 100).round(1)

        fig = px.bar(
            pairs_df,
            x='Frequency',
            y='Skill Combination',
            orientation='h',
            title='Top 10 AI Skill Pairs',
            labels={'Frequency': 'Number of Jobs'},
            color='Frequency',
            # Intentionally distinct from BLUE_SCALE — preserved from original.
            color_continuous_scale=[[0, '#E3EBF3'], [0.5, '#7A95B0'], [1, '#3B5F7F']],
            text='Percentage'
        )
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        style_horizontal_bar(fig, height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No skill combinations found (jobs have only single AI skills)")


def _render_depth(ai_jobs_df):
    st.header("AI Skill Depth Analysis")

    if len(ai_jobs_df) == 0:
        return

    skill_depth_bins = pd.cut(
        ai_jobs_df['ai_skill_count'],
        bins=[1, 3, 6, 11, float('inf')],
        labels=['1-2 skills', '3-5 skills', '6-10 skills', '11+ skills'],
        right=False
    )
    depth_counts = skill_depth_bins.value_counts().sort_index()

    depth_df = pd.DataFrame({
        'Skill Range': depth_counts.index,
        'Number of Jobs': depth_counts.values
    })
    depth_df['Percentage'] = (depth_df['Number of Jobs'] / len(ai_jobs_df) * 100).round(1)

    fig = px.bar(
        depth_df,
        x='Number of Jobs',
        y='Skill Range',
        orientation='h',
        title='Distribution of AI Skill Requirements',
        labels={'Number of Jobs': 'Number of Postings'},
        color='Number of Jobs',
        color_continuous_scale=BLUE_SCALE,
        text='Percentage'
    )
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    style_horizontal_bar(fig, height=300)
    st.plotly_chart(fig, use_container_width=True)
