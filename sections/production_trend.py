import plotly.express as px
import streamlit as st

from lib import production
from lib.charts import TEXT_COLOR

LINE_COLOR = '#2E4A6B'


def render(prod_df):
    st.header("Production Skills Over Time")

    trend = production.monthly_trend(prod_df)
    if len(trend) < 2:
        st.info("Not enough dated postings to show a trend.")
        return

    trend['Percentage'] = trend['share'].round(1)
    trend['Postings'] = trend['postings']

    fig = px.line(
        trend,
        x='month',
        y='Percentage',
        markers=True,
        title='Jobs Requiring Production Skills by Posting Month (% of jobs that month)',
        labels={'month': 'Posting Month', 'Percentage': '% of Job Postings'},
        hover_data={'Postings': True, 'Percentage': ':.1f'},
        text='Percentage',
    )
    fig.update_traces(line=dict(color=LINE_COLOR, width=3), marker=dict(size=9, color=LINE_COLOR),
                      texttemplate='%{text}%', textposition='top center')
    fig.update_layout(
        height=420,
        title_font_size=20,
        font=dict(color=TEXT_COLOR, size=12),
        xaxis=dict(tickfont=dict(color=TEXT_COLOR, size=12), title_font=dict(color=TEXT_COLOR, size=13),
                   type='category'),
        yaxis=dict(tickfont=dict(color=TEXT_COLOR, size=12), title_font=dict(color=TEXT_COLOR, size=13),
                   ticksuffix='%', range=[0, max(60, trend['Percentage'].max() * 1.2)]),
    )
    st.plotly_chart(fig, width="stretch")

    undated = int(prod_df['posted_at_date'].isna().sum())
    st.caption(
        f"Months with fewer than {production.MIN_POSTINGS_PER_MONTH} postings are left out so a handful of jobs "
        f"cannot swing the line. {undated:,} jobs ({undated / len(prod_df) * 100:.0f}%) have no posting date "
        "from the source and are excluded here."
    )
