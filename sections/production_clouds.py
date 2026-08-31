import plotly.express as px
import streamlit as st

from lib import production
from lib.charts import BLUE_SCALE, style_horizontal_bar


def render(prod_df):
    st.header("Cloud Platforms Companies Ask For")

    if len(prod_df) == 0:
        return

    clouds = production.skill_shares(prod_df, production.CLOUD_PLATFORMS)
    clouds['Percentage'] = clouds['share'].round(1)

    fig = px.bar(
        clouds,
        x='Percentage',
        y='skill',
        orientation='h',
        title='Cloud and ML Platforms Mentioned (% of all jobs)',
        labels={'Percentage': '% of Job Postings', 'skill': ''},
        color='Percentage',
        color_continuous_scale=BLUE_SCALE,
        text='Percentage',
    )
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    style_horizontal_bar(fig, height=380)
    fig.update_xaxes(range=[0, clouds['Percentage'].max() * 1.2], ticksuffix='%')
    st.plotly_chart(fig, width="stretch")

    st.caption(
        "AWS, Azure, and GCP are counted whenever they are named, even for storage or data work. "
        "Only the managed ML services (SageMaker, Vertex AI, Azure Machine Learning) count toward "
        "\"requires production skills\", because naming one of those implies deployment work."
    )
