import streamlit as st

from lib.text import highlight_skills_in_text
from lib.titles import extract_ai_specialization


def render(ai_jobs_df, ai_skills):
    st.header("AI Job Explorer")

    col1, col2, col3 = st.columns(3)

    with col1:
        selected_skill = st.selectbox(
            "Filter by AI Skill",
            ["All"] + sorted(ai_skills)
        )

    with col2:
        ai_specialization_options = ["All", "GenAI", "LLM", "NLP", "Agentic AI", "Machine Learning", "AI", "General"]
        selected_specialization = st.selectbox(
            "Filter by AI Specialization in Title",
            ai_specialization_options
        )

    with col3:
        min_skills = st.slider(
            "Minimum AI Skills Required",
            min_value=1,
            max_value=int(ai_jobs_df['ai_skill_count'].max()) if len(ai_jobs_df) > 0 else 10,
            value=1
        )

    filtered_jobs = ai_jobs_df.copy()

    if selected_specialization != "All":
        filtered_jobs = filtered_jobs[
            filtered_jobs['title'].apply(lambda title: selected_specialization in extract_ai_specialization(title))
        ]

    if selected_skill != "All":
        filtered_jobs = filtered_jobs[filtered_jobs['ai_skills'].apply(lambda x: selected_skill in x)]

    if selected_specialization == "All":
        filtered_jobs = filtered_jobs[filtered_jobs['ai_skill_count'] >= min_skills]

    st.subheader(f"Matching Jobs ({len(filtered_jobs)} found)")

    if len(filtered_jobs) > 0:
        display_df = filtered_jobs[['title', 'company_name', 'location', 'ai_skill_count', 'ai_skills']].copy()
        display_df['ai_skills'] = display_df['ai_skills'].apply(lambda x: ', '.join(x))
        display_df.columns = ['Job Title', 'Company', 'Location', 'AI Skills Count', 'AI Skills']

        event = st.dataframe(
            display_df,
            use_container_width=True,
            height=400,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        if event.selection and len(event.selection.rows) > 0:
            selected_row_idx = event.selection.rows[0]
            selected_row = filtered_jobs.iloc[selected_row_idx]

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
                        st.markdown(f"**AI Skills**  \n{selected_row['ai_skill_count']} detected")

                if selected_row['apply_options'] and len(selected_row['apply_options']) > 0:
                    links = [f"[{opt['title']}]({opt['link']})" for opt in selected_row['apply_options'] if 'link' in opt and 'title' in opt]
                    if links:
                        st.markdown("**Apply via:** " + " | ".join(links))
                elif selected_row['share_link']:
                    st.markdown(f"**[View Job Posting]({selected_row['share_link']})**")

            col1, col2 = st.columns([1, 3])

            with col1:
                with st.container(border=True):
                    st.markdown("**AI Skills Found**")
                    for skill in selected_row['ai_skills']:
                        st.markdown(f"- {skill}")

            with col2:
                with st.container(border=True):
                    st.markdown("**Job Description**")

                    description = selected_row['description']
                    highlighted_desc = highlight_skills_in_text(description, selected_row['ai_skills'])
                    highlighted_desc = highlighted_desc.replace('\n', '  \n')

                    st.markdown(highlighted_desc)
        else:
            st.info("Click on any row in the table above to view full job details with highlighted AI skills")
    else:
        st.info("No jobs match the selected filters.")
