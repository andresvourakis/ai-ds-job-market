import streamlit as st


# One promo per page: the AI page points to the AI Workflows workshops, the
# ML in Production page to the MLOps course.
PROMOS = {
    "ai": {
        "heading": "Free Workshops",
        "title": "From Chat Window to AI Analyst",
        "text": "Get AI to run real analysis, query your database, and answer business questions right.",
        "url": "https://futureproofds.com/resources/ai-workflows-workshops?utm_source=dashboard&utm_medium=sidebar",
        "cta": "Get the free workshops",
    },
    "mlops": {
        "heading": "Free Course",
        "title": "MLOps for Data Scientists",
        "text": "Take a model from your notebook to a monitored system running in production.",
        "url": "https://futureproofds.com/resources/mlops-for-data-scientists?utm_source=dashboard&utm_medium=sidebar",
        "cta": "Get the free course",
    },
}


def render(all_df, metadata, promo="ai"):
    """
    Render the sidebar (about, date filter, resources).
    Returns the date-filtered dataframe.
    """
    with st.sidebar:
        # Subheaders and no dividers keep the sidebar compact enough that the
        # Resources box is visible on a laptop screen without scrolling.
        st.subheader("About the Data")
        st.markdown(
            f"**Search query:** {metadata.get('query', 'N/A')}<br>"
            f"**Location:** {metadata.get('location', 'N/A')}<br>"
            f"**Total postings:** {len(all_df):,}",
            unsafe_allow_html=True,
        )

        st.subheader("Filters")
        df_with_valid_dates = all_df[all_df['posted_at_date'].notna()]
        if len(df_with_valid_dates) > 0:
            min_date = df_with_valid_dates['posted_at_date'].min().date()
            max_date = df_with_valid_dates['posted_at_date'].max().date()

            start_col, end_col = st.columns(2)
            with start_col:
                start_date = st.date_input("Start date", value=min_date, min_value=min_date, max_value=max_date)
            with end_col:
                end_date = st.date_input("End date", value=max_date, min_value=min_date, max_value=max_date)

            is_full_range = (start_date == min_date and end_date == max_date)
            if is_full_range:
                df = all_df
            else:
                dated_mask = (
                    (all_df['posted_at_date'].notna()) &
                    (all_df['posted_at_date'].dt.date >= start_date) &
                    (all_df['posted_at_date'].dt.date <= end_date)
                )
                df = all_df[dated_mask]
                st.caption(f"Showing {len(df)} of {len(all_df)} jobs. Jobs without posting dates are excluded when filtering by date.")
        else:
            df = all_df

        p = PROMOS[promo]
        st.subheader(p["heading"])
        st.markdown(
            '<div style="background-color: #e8f0fe; border-radius: 8px; padding: 14px 16px; border: 1px solid #c4d7f2;">'
            f'<b>{p["title"]}</b><br>'
            f'{p["text"]}<br>'
            f'<a href="{p["url"]}" target="_blank"><b>{p["cta"]}</b></a>'
            '</div>',
            unsafe_allow_html=True,
        )

    return df
