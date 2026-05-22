import pandas as pd
import plotly.express as px
import streamlit as st

from lib.charts import BLUE_SCALE, style_horizontal_bar


def render(df, ai_skills, skill_counts):
    st.header("Top Skills in Demand")

    ai_skill_counts_sorted = sorted(
        [(skill, skill_counts.get(skill, 0)) for skill in ai_skills if skill != 'AI'],
        key=lambda x: x[1],
        reverse=True
    )[:10]

    if not ai_skill_counts_sorted:
        return

    ai_skills_df = pd.DataFrame(ai_skill_counts_sorted, columns=['Skill', 'Frequency'])
    ai_skills_df['Percentage'] = (ai_skills_df['Frequency'] / len(df) * 100).round(1)
    ai_skills_df['Label'] = ai_skills_df.apply(
        lambda row: f"{row['Skill']} ({row['Percentage']}%)", axis=1
    )

    all_skills_df = pd.DataFrame(
        skill_counts.most_common(20),
        columns=['Skill', 'Frequency']
    )
    all_skills_df['Percentage'] = (all_skills_df['Frequency'] / len(df) * 100).round(1)

    chart_col1, chart_col2 = st.columns(2, gap="medium")

    with chart_col1:
        fig = px.bar(
            all_skills_df,
            x='Frequency',
            y='Skill',
            orientation='h',
            title='Top 20 Most Mentioned Skills (% of all jobs)',
            labels={'Frequency': 'Number of Job Postings'},
            color='Frequency',
            color_continuous_scale=BLUE_SCALE,
            text='Percentage'
        )
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        style_horizontal_bar(fig, height=500)
        st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        fig = px.bar(
            ai_skills_df,
            x='Frequency',
            y='Skill',
            orientation='h',
            title='Top 10 AI Skills in Data Science Jobs (% of all jobs)',
            labels={'Frequency': 'Number of Job Postings'},
            color='Frequency',
            color_continuous_scale=BLUE_SCALE,
            text='Percentage'
        )
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        style_horizontal_bar(fig, height=500)
        st.plotly_chart(fig, use_container_width=True)
