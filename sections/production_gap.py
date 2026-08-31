import pandas as pd
import plotly.express as px
import streamlit as st

from lib import production
from lib.charts import TEXT_COLOR

PRACTICE_COLOR = '#2E4A6B'
TOOL_COLOR = '#8BA5C0'


def render(prod_df):
    st.header("Asking for the Work vs Naming the Tool")
    st.markdown(
        "For each area, how many jobs ask for the **practice** (for example, deploying models) "
        "and how many name a **specific tool** for it (for example, Docker). "
        "Companies ask for the capability far more often than they prescribe the stack."
    )

    summary = production.category_summary(prod_df)
    if summary.empty or len(prod_df) == 0:
        st.info("No jobs to summarize.")
        return

    # Cloud platforms have no practices by design, so the chart stays on the six skill areas.
    summary = summary[summary['category'] != production.CLOUD_CATEGORY]
    # Largest practice share on top; category_orders lists categories top to bottom.
    summary = summary.sort_values('practice_share', ascending=False)

    chart_df = pd.concat([
        pd.DataFrame({'Category': summary['category'], 'Share': summary['practice_share'],
                      'Measure': 'Asks for the practice'}),
        pd.DataFrame({'Category': summary['category'], 'Share': summary['tool_share'],
                      'Measure': 'Names a specific tool'}),
    ])
    chart_df['Label'] = chart_df['Share'].round(1).astype(str) + '%'

    fig = px.bar(
        chart_df,
        x='Share',
        y='Category',
        color='Measure',
        orientation='h',
        barmode='group',
        title='Practice vs Tool Mentions by Area (% of all jobs)',
        labels={'Share': '% of Job Postings', 'Category': ''},
        color_discrete_map={'Asks for the practice': PRACTICE_COLOR, 'Names a specific tool': TOOL_COLOR},
        category_orders={'Category': list(summary['category']),
                         'Measure': ['Asks for the practice', 'Names a specific tool']},
        text='Label',
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        height=450,
        title_font_size=20,
        font=dict(color=TEXT_COLOR, size=12),
        xaxis=dict(tickfont=dict(color=TEXT_COLOR, size=12), title_font=dict(color=TEXT_COLOR, size=13),
                   ticksuffix='%', range=[0, chart_df['Share'].max() * 1.25]),
        yaxis=dict(tickfont=dict(color=TEXT_COLOR, size=12)),
        legend=dict(title='', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    )
    st.plotly_chart(fig, width="stretch")

    with st.expander("What is in each area"):
        rows = []
        for name, category in production.PRODUCTION_CATEGORIES.items():
            rows.append({
                'Area': name,
                'Practices': ', '.join(category['practices']) or 'None (platforms only)',
                'Tools': ', '.join(category['tools']),
            })
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        st.markdown(
            "Cloud & ML Platforms is tracked in its own section below: it is made of platforms, "
            "not practices, so it has no bar here."
        )
