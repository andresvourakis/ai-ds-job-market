import plotly.express as px
import streamlit as st

from lib.charts import BLUE_SCALE


def render(all_df):
    st.header("Job Postings Distribution by Date")

    all_df_with_dates = all_df[all_df['posted_at_date'].notna()].copy()
    all_jobs_without_date = len(all_df) - len(all_df_with_dates)

    if len(all_df_with_dates) > 0:
        date_counts = all_df_with_dates['posted_at_date'].dt.date.value_counts().sort_index()

        fig = px.bar(
            x=date_counts.index,
            y=date_counts.values,
            labels={'x': 'Posted Date', 'y': 'Number of Jobs'},
            title=f'Job Postings Distribution by Date ({len(all_df_with_dates)} jobs)',
            color=date_counts.values,
            color_continuous_scale=BLUE_SCALE
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            height=500,
            title_font_size=20,
            font=dict(color='#1F2937', size=12),
            xaxis=dict(tickfont=dict(color='#1F2937', size=12), title_font=dict(color='#1F2937', size=13)),
            yaxis=dict(tickfont=dict(color='#1F2937', size=12), title_font=dict(color='#1F2937', size=13)),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

        st.caption(f"Based on {len(all_df_with_dates)} jobs with posting dates ({len(all_df_with_dates)/len(all_df)*100:.0f}% of total). "
                   f"{all_jobs_without_date} jobs ({all_jobs_without_date/len(all_df)*100:.0f}%) do not have date information from the source.")
    else:
        st.warning("No jobs with valid posted dates found.")
