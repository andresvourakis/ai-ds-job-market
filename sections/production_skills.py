import plotly.express as px
import streamlit as st

from lib import production
from lib.charts import BLUE_SCALE, style_horizontal_bar


def _bar(shares_df, title, height):
    """Standard blue horizontal bar of % of jobs, matching the AI page charts."""
    shares_df = shares_df.copy()
    shares_df['Percentage'] = shares_df['share'].round(1)
    fig = px.bar(
        shares_df,
        x='Percentage',
        y='skill',
        orientation='h',
        title=title,
        labels={'Percentage': '% of Job Postings', 'skill': ''},
        color='Percentage',
        color_continuous_scale=BLUE_SCALE,
        text='Percentage',
    )
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    style_horizontal_bar(fig, height=height)
    fig.update_xaxes(range=[0, shares_df['Percentage'].max() * 1.2], ticksuffix='%')
    return fig


def render(prod_df):
    st.header("Top Production Skills in Demand")

    if len(prod_df) == 0:
        st.info("No jobs to analyze.")
        return

    practices = production.skill_shares(prod_df, production.practice_skills())
    # Tools chart leaves cloud platforms out; they get their own section so they
    # don't crowd out the deployment tooling here.
    tools = production.skill_shares(prod_df, production.tool_skills() - set(production.CLOUD_PLATFORMS))
    tools = tools[tools['share'] > 0].head(10)

    chart_col1, chart_col2 = st.columns(2, gap="medium")
    with chart_col1:
        st.plotly_chart(_bar(practices, 'Production Practices (% of all jobs)', height=500), width="stretch")
    with chart_col2:
        st.plotly_chart(_bar(tools, 'Top 10 Production Tools (% of all jobs)', height=500), width="stretch")

    with st.expander("How skills are detected"):
        st.markdown("""
        Every skill is matched by exact phrases curated for this dashboard (for example, "model monitoring",
        "monitoring models", "model performance monitoring" all count as **Model Monitoring**), with plurals
        handled automatically.

        **Model Deployment** is the one exception. Postings describe it in too many ways for a phrase list
        ("deploy predictive models", "deploying ML solutions", "algorithms into production",
        "model productionalization"), so it is matched by a narrow pattern: the deploy verb within a few words
        of a model-like object, or an object going into production. Bare "deploy" or "production" do not match.

        Each keyword was checked against real postings before being included. The full list of decisions is in
        `docs/production_keyword_audit.md`.
        """)
