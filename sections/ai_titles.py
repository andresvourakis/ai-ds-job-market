import pandas as pd
import plotly.express as px
import streamlit as st

from lib.charts import BLUE_SCALE, style_horizontal_bar
from lib.titles import categorize_title_type, extract_ai_specialization, normalize_job_title


def render(ai_jobs_df):
    st.header("Job Titles Requiring AI Skills")

    if len(ai_jobs_df) == 0:
        st.info("No AI-specialized jobs found")
        return

    ai_jobs_df['seniority'], ai_jobs_df['ai_in_title'] = zip(*ai_jobs_df['title'].apply(normalize_job_title))

    st.subheader("By Seniority Level")
    seniority_counts = ai_jobs_df['seniority'].value_counts()
    seniority_df = pd.DataFrame({
        'Seniority': seniority_counts.index,
        'Frequency': seniority_counts.values
    })
    seniority_df['Percentage'] = (seniority_df['Frequency'] / len(ai_jobs_df) * 100).round(1)

    fig1 = px.bar(
        seniority_df,
        x='Frequency',
        y='Seniority',
        orientation='h',
        title='AI Jobs by Seniority Level',
        labels={'Frequency': 'Number of Postings'},
        color='Frequency',
        color_continuous_scale=BLUE_SCALE,
        text='Percentage',
        hover_data={'Percentage': ':.1f', 'Frequency': True}
    )
    fig1.update_traces(texttemplate='%{text}%', textposition='outside')
    style_horizontal_bar(fig1, height=400)
    st.plotly_chart(fig1, use_container_width=True)

    with st.expander("Seniority Keywords Used"):
        st.markdown("""
        - **Intern**: intern
        - **Junior**: junior, jr., jr, entry, associate, I, II
        - **Mid**: (default if no other seniority keyword found)
        - **Senior**: senior, sr., sr, III, IV
        - **Staff+**: staff, principal, distinguished
        - **Lead/Manager**: lead, manager, head
        - **Director+**: director, vp, chief
        """)

    st.subheader("General vs AI-Specialized Titles")
    ai_jobs_df['title_category'] = ai_jobs_df['title'].apply(categorize_title_type)
    title_type_counts = ai_jobs_df['title_category'].value_counts()
    title_type_df = pd.DataFrame({
        'Title Type': title_type_counts.index,
        'Frequency': title_type_counts.values
    })
    title_type_df['Percentage'] = (title_type_df['Frequency'] / len(ai_jobs_df) * 100).round(1)

    fig2 = px.bar(
        title_type_df,
        x='Frequency',
        y='Title Type',
        orientation='h',
        title='General vs AI-Specialized Job Titles',
        labels={'Frequency': 'Number of Postings'},
        color='Frequency',
        color_continuous_scale=BLUE_SCALE,
        text='Percentage',
        hover_data={'Percentage': ':.1f', 'Frequency': True}
    )
    fig2.update_traces(texttemplate='%{text}%', textposition='outside')
    style_horizontal_bar(fig2, height=300)
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("Categorization Logic"):
        st.markdown("""
        - **AI-Specialized**: Titles mentioning specific AI keywords (GenAI, LLM, NLP, Machine Learning, Agentic AI, or AI/Artificial Intelligence)
        - **General**: Titles without AI specialization keywords (e.g., "Data Scientist", "Senior Data Scientist")
        """)

    st.subheader("Specific AI Specialization Types")

    all_specializations = []
    for title in ai_jobs_df['title']:
        specs = extract_ai_specialization(title)
        specific_specs = [s for s in specs if s != 'General']
        all_specializations.extend(specific_specs)

    if all_specializations:
        spec_counts = pd.Series(all_specializations).value_counts()
        spec_df = pd.DataFrame({
            'Specialization': spec_counts.index,
            'Frequency': spec_counts.values
        })
        ai_specialized_count = len(ai_jobs_df[ai_jobs_df['title_category'] == 'AI-Specialized'])
        spec_df['Percentage'] = (spec_df['Frequency'] / ai_specialized_count * 100).round(1)

        fig3 = px.bar(
            spec_df,
            x='Frequency',
            y='Specialization',
            orientation='h',
            title='Breakdown of AI Specialization Types',
            labels={'Frequency': 'Number of Job Titles'},
            color='Frequency',
            color_continuous_scale=BLUE_SCALE,
            text='Percentage',
            hover_data={'Percentage': ':.1f', 'Frequency': True}
        )
        fig3.update_traces(texttemplate='%{text}%', textposition='outside')
        style_horizontal_bar(fig3, height=350)
        st.plotly_chart(fig3, use_container_width=True)

        with st.expander("Specialization Keywords Used"):
            st.markdown("""
            - **AI**: ai, artificial intelligence
            - **GenAI**: genai, generative ai, gen ai
            - **LLM**: llm, large language model
            - **NLP**: nlp, natural language processing
            - **Agentic AI**: agentic, ai agent
            - **Machine Learning**: machine learning, ml

            *Note: This chart only shows AI-specialized jobs (excludes General titles). A single job can be counted in multiple categories if it mentions multiple specializations.*
            """)
    else:
        st.info("No specific AI specialization keywords found in titles")
