import plotly.express as px
import streamlit as st

from lib import production
from lib.charts import BLUE_SCALE, style_horizontal_bar

SENIORITY_ORDER = ['Intern', 'Junior', 'Mid', 'Senior', 'Staff+', 'Lead/Manager', 'Director+']


def render(prod_df):
    st.header("Production Skills by Seniority Level")

    if len(prod_df) == 0:
        return

    breakdown = production.seniority_breakdown(prod_df)
    breakdown = breakdown[breakdown['seniority'].isin(SENIORITY_ORDER)]
    breakdown['Percentage'] = breakdown['share'].round(1)
    breakdown['Postings'] = breakdown['postings']

    fig = px.bar(
        breakdown,
        x='Percentage',
        y='seniority',
        orientation='h',
        title='Jobs Requiring Production Skills by Seniority (% of jobs at that level)',
        labels={'Percentage': '% of Job Postings at This Level', 'seniority': ''},
        color='Percentage',
        color_continuous_scale=BLUE_SCALE,
        text='Percentage',
        hover_data={'Postings': True, 'Percentage': ':.1f'},
    )
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    style_horizontal_bar(fig, height=400)
    # Seniority is an ordered scale, so keep the career order instead of sorting by value.
    fig.update_yaxes(categoryorder='array', categoryarray=SENIORITY_ORDER[::-1])
    fig.update_xaxes(range=[0, breakdown['Percentage'].max() * 1.2], ticksuffix='%')
    st.plotly_chart(fig, width="stretch")

    by_level = breakdown.set_index('seniority')['postings']
    counts = ', '.join(f"{level}: {by_level[level]:,}" for level in SENIORITY_ORDER if level in by_level)
    st.caption(f"Postings per level: {counts}.")

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
