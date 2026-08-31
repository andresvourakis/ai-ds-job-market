import streamlit as st

from lib import production

# A metric value is one big line with no wrapping, so skill names longer than
# about ten characters get cut off on a laptop screen. Only the names that need it.
SHORT_NAMES = {
    "Model Deployment": "Deployment",
    "Experiment Tracking": "Exp. Tracking",
    "Infrastructure as Code": "IaC",
}


def render(prod_df):
    st.header("Key Metrics")
    # Four metrics, not five: skill names need the extra width to stay readable
    # on a laptop screen. How many jobs name a tool is covered by the next section.
    col1, col2, col3, col4 = st.columns(4)

    total = len(prod_df)
    requiring = int(prod_df['requires_production'].sum())
    pct = lambda count: (count / total * 100) if total > 0 else 0

    with col1:
        st.metric("Total Jobs", total)
    with col2:
        st.metric("Jobs Requiring Production Skills", requiring, f"{pct(requiring):.0f}% of total jobs",
                  delta_color="off", delta_arrow="off")
    with col3:
        practices = production.skill_shares(prod_df, production.practice_skills())
        top = practices.iloc[0] if len(practices) else None
        st.metric("Top Practice", SHORT_NAMES.get(top['skill'], top['skill']) if top is not None else "N/A",
                  f"in {top['share']:.0f}% of jobs" if top is not None else None,
                  delta_color="off", delta_arrow="off")
    with col4:
        clouds = production.skill_shares(prod_df, production.CLOUD_PLATFORMS)
        top = clouds.iloc[0] if len(clouds) else None
        st.metric("Top Cloud Platform", top['skill'] if top is not None else "N/A",
                  f"in {top['share']:.0f}% of jobs" if top is not None else None,
                  delta_color="off", delta_arrow="off")

    with st.expander("What counts as requiring production skills"):
        st.markdown("""
        A job **requires production skills** when its description asks for at least one production
        practice (deploying models, model serving, CI/CD, experiment tracking, ML pipelines,
        monitoring, and so on) or names a managed ML platform (SageMaker, Vertex AI, Azure Machine Learning).

        Naming a tool alone is not enough. "Experience with AWS" can mean a storage bucket, so bare
        AWS, Azure, or GCP mentions are tracked but do not count toward this number.
        """)
