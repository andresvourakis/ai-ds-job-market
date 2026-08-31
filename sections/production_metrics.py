import streamlit as st

from lib import production


def render(prod_df):
    st.header("Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)

    total = len(prod_df)
    requiring = int(prod_df['requires_production'].sum())
    naming_tool = int(prod_df['names_tool'].sum())
    pct = lambda count: (count / total * 100) if total > 0 else 0

    with col1:
        st.metric("Total Jobs", total)
    with col2:
        st.metric("Jobs Requiring Production Skills", requiring, f"{pct(requiring):.0f}% of total jobs",
                  delta_color="off", delta_arrow="off")
    with col3:
        st.metric("Jobs Naming a Production Tool", naming_tool, f"{pct(naming_tool):.0f}% of total jobs",
                  delta_color="off", delta_arrow="off")
    # Skill names like "Model Deployment" are too long for a metric value, so the
    # share is the value and the name sits underneath it.
    with col4:
        practices = production.skill_shares(prod_df, production.practice_skills())
        top = practices.iloc[0] if len(practices) else None
        st.metric("Top Practice", f"{top['share']:.0f}% of jobs" if top is not None else "N/A",
                  top['skill'] if top is not None else None, delta_color="off", delta_arrow="off")
    with col5:
        clouds = production.skill_shares(prod_df, production.CLOUD_PLATFORMS)
        top = clouds.iloc[0] if len(clouds) else None
        st.metric("Most Requested Cloud", f"{top['share']:.0f}% of jobs" if top is not None else "N/A",
                  top['skill'] if top is not None else None, delta_color="off", delta_arrow="off")

    with st.expander("What counts as requiring production skills"):
        st.markdown("""
        A job **requires production skills** when its description asks for at least one production
        practice (deploying models, model serving, CI/CD, experiment tracking, ML pipelines,
        monitoring, and so on) or names a managed ML platform (SageMaker, Vertex AI, Azure Machine Learning).

        Naming a tool alone is not enough. "Experience with AWS" can mean a storage bucket, so bare
        AWS, Azure, or GCP mentions are tracked but do not count toward this number.
        """)
