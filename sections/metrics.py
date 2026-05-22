import streamlit as st


def render(df, ai_jobs_df, ai_skills, skill_counts):
    st.header("Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Jobs", len(df))
    with col2:
        pct_ai = (len(ai_jobs_df) / len(df) * 100) if len(df) > 0 else 0
        st.metric("Jobs with AI Keywords", len(ai_jobs_df), f"{pct_ai:.0f}% of total jobs", delta_color="off", delta_arrow="off")
    with col3:
        ai_jobs_specific_df = ai_jobs_df[ai_jobs_df['ai_skills'].apply(lambda skills: any(s != 'AI' for s in skills))]
        pct_ai_specific = (len(ai_jobs_specific_df) / len(df) * 100) if len(df) > 0 else 0
        st.metric("Jobs with AI Skills", len(ai_jobs_specific_df), f"{pct_ai_specific:.0f}% of total jobs", delta_color="off", delta_arrow="off")
    with col4:
        ai_skill_counts = {skill: skill_counts.get(skill, 0) for skill in ai_skills if skill != 'AI'}
        top_ai_skill = max(ai_skill_counts.items(), key=lambda x: x[1]) if ai_skill_counts else ("N/A", 0)
        top_ai_pct = (top_ai_skill[1] / len(df) * 100) if len(df) > 0 else 0
        st.metric("Top AI Skill", top_ai_skill[0], f"in {top_ai_pct:.0f}% of jobs", delta_color="off", delta_arrow="off")
    with col5:
        avg_ai_skills = ai_jobs_df['ai_skill_count'].mean() if len(ai_jobs_df) > 0 else 0
        st.metric("Avg AI Skills per Job", f"{avg_ai_skills:.1f}")
