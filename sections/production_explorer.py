import re

import streamlit as st

from lib import production
from lib.text import highlight_skills_in_text


def _highlight(description, skills):
    """Skill highlighting, plus the deployment pattern that has no fixed phrases."""
    text = highlight_skills_in_text(description, skills)
    if 'Model Deployment' in skills:
        text = production.MODEL_DEPLOYMENT_PATTERN.sub(lambda m: f"**:blue[{m.group(0)}]**", text)
    return text


def render(prod_df):
    st.header("Production Job Explorer")

    jobs = prod_df[prod_df['requires_production']].copy()
    jobs['skill_count'] = jobs['production_skills'].apply(len)

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_skill = st.selectbox("Filter by Production Skill", ["All"] + sorted(production.all_production_skills()))
    with col2:
        selected_area = st.selectbox("Filter by Area", ["All"] + list(production.PRODUCTION_CATEGORIES))
    with col3:
        max_skills = int(jobs['skill_count'].max()) if len(jobs) > 0 else 1
        min_skills = st.slider("Minimum Production Skills Mentioned", min_value=1, max_value=max(max_skills, 1), value=1)

    filtered = jobs
    if selected_skill != "All":
        filtered = filtered[filtered['production_skills'].apply(lambda found: selected_skill in found)]
    if selected_area != "All":
        area = production.PRODUCTION_CATEGORIES[selected_area]
        area_skills = set(area['practices']) | set(area['tools'])
        filtered = filtered[filtered['production_skills'].apply(lambda found: bool(area_skills & set(found)))]
    filtered = filtered[filtered['skill_count'] >= min_skills]

    st.subheader(f"Matching Jobs ({len(filtered)} found)")
    st.caption("Only jobs that require production skills are listed here.")

    if len(filtered) == 0:
        st.info("No jobs match the selected filters.")
        return

    display_df = filtered[['title', 'company_name', 'location', 'skill_count', 'production_skills']].copy()
    display_df['production_skills'] = display_df['production_skills'].apply(', '.join)
    display_df.columns = ['Job Title', 'Company', 'Location', 'Production Skills Count', 'Production Skills']

    event = st.dataframe(display_df, width="stretch", height=400, hide_index=True,
                         on_select="rerun", selection_mode="single-row")

    if not event.selection or len(event.selection.rows) == 0:
        st.info("Click on any row in the table above to view full job details with highlighted production skills")
        return

    selected_row = filtered.iloc[event.selection.rows[0]]

    st.markdown("---")
    st.subheader("Job Details")

    with st.container(border=True):
        st.markdown(f"### {selected_row['title']}")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"**Company**  \n{selected_row['company_name']}")
        with col_b:
            st.markdown(f"**Location**  \n{selected_row['location']}")
        with col_c:
            salary = selected_row.get('salary', 'N/A')
            if salary and salary != 'N/A':
                st.markdown(f"**Salary**  \n{salary}")
            else:
                st.markdown(f"**Production Skills**  \n{selected_row['skill_count']} detected")

        if selected_row['apply_options'] and len(selected_row['apply_options']) > 0:
            links = [f"[{opt['title']}]({opt['link']})" for opt in selected_row['apply_options']
                     if 'link' in opt and 'title' in opt]
            if links:
                st.markdown("**Apply via:** " + " | ".join(links))
        elif selected_row['share_link']:
            st.markdown(f"**[View Job Posting]({selected_row['share_link']})**")

    col1, col2 = st.columns([1, 3])
    with col1:
        with st.container(border=True):
            st.markdown("**Production Skills Found**")
            for skill in selected_row['production_skills']:
                st.markdown(f"- {skill}")
    with col2:
        with st.container(border=True):
            st.markdown("**Job Description**")
            highlighted = _highlight(selected_row['description'], selected_row['production_skills'])
            st.markdown(highlighted.replace('\n', '  \n'))
