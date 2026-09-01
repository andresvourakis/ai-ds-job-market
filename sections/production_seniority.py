import plotly.express as px
import streamlit as st

from lib import production
from lib.charts import style_horizontal_bar

SENIORITY_ORDER = ['Intern', 'Junior', 'Mid', 'Senior', 'Staff+', 'Tech Lead', 'Manager', 'Director+']

# One solid color on purpose: every other bar chart on this page is a share of
# all jobs with a light-to-dark ranking scale. This chart compares independent
# rates, and looking different is what stops it from being read the same way.
BAR_COLOR = '#2E4A6B'


def render(prod_df):
    st.header("Production Skills by Seniority Level")
    st.markdown(
        "Each bar is its own group: the share of postings **at that level** that require production skills. "
        "The bars are not parts of a whole, so they do not add up to 100%."
    )

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
        title='Share of Jobs at Each Seniority Level That Require Production Skills',
        labels={'Percentage': '% of Job Postings at That Level', 'seniority': ''},
        text='Percentage',
        hover_data={'Postings': True, 'Percentage': ':.1f'},
    )
    fig.update_traces(marker_color=BAR_COLOR, texttemplate='%{text}%', textposition='outside')
    style_horizontal_bar(fig, height=400)
    # Seniority is an ordered scale, so keep the career order instead of sorting by value.
    fig.update_yaxes(categoryorder='array', categoryarray=SENIORITY_ORDER[::-1])
    fig.update_xaxes(range=[0, breakdown['Percentage'].max() * 1.2], ticksuffix='%')
    st.plotly_chart(fig, width="stretch")

    by_level = breakdown.set_index('seniority')
    counts = ', '.join(f"{level}: {by_level.loc[level, 'postings']:,}" for level in SENIORITY_ORDER if level in by_level.index)
    example = ""
    if 'Senior' in by_level.index:
        example = (f" Example: of the {by_level.loc['Senior', 'postings']:,} Senior postings, "
                   f"{by_level.loc['Senior', 'Percentage']}% require production skills.")
    st.caption(f"Postings per level: {counts}.{example}")

    with st.expander("Seniority Keywords Used"):
        st.markdown("""
        - **Intern**: intern
        - **Junior**: junior, jr., jr, entry, associate, I, II
        - **Mid**: (default if no other seniority keyword found)
        - **Senior**: senior, sr., sr, III, IV
        - **Staff+**: staff, principal, distinguished
        - **Tech Lead**: lead (hands-on technical leads)
        - **Manager**: manager, head
        - **Director+**: director, vp, chief
        """)
