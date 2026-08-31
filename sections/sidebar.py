import streamlit as st


def render(all_df, metadata):
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

        st.subheader("Resources")
        st.markdown(
            '<div style="background-color: #e8f0fe; border-radius: 8px; padding: 14px 16px; border: 1px solid #c4d7f2;">'
            'Develop the judgment, systems thinking, and applied AI skills that keep data scientists ahead. '
            '<a href="https://futureproofds.com" target="_blank"><b>futureproofds.com</b></a>'
            '</div>',
            unsafe_allow_html=True,
        )

    return df
