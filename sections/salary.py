import pandas as pd
import plotly.express as px
import streamlit as st

from lib.titles import normalize_job_title


def render(df, ai_jobs_df):
    st.header("Salary Analysis: AI Skills Premium")

    jobs_with_salary = ai_jobs_df[ai_jobs_df['salary_mid'].notna()].copy()

    if len(jobs_with_salary) >= 20:
        jobs_with_salary['seniority'] = jobs_with_salary['title'].apply(lambda t: normalize_job_title(t)[0])

        non_ai_jobs = df[~df.index.isin(ai_jobs_df.index)]
        non_ai_with_salary = non_ai_jobs[non_ai_jobs['salary_mid'].notna()].copy()

        if len(non_ai_with_salary) >= 10:
            non_ai_with_salary['seniority'] = non_ai_with_salary['title'].apply(lambda t: normalize_job_title(t)[0])

            comparison_data = []
            seniority_order = ['Junior', 'Mid', 'Senior', 'Staff+', 'Tech Lead', 'Manager', 'Director+']

            for seniority in seniority_order:
                ai_sen = jobs_with_salary[jobs_with_salary['seniority'] == seniority]
                non_ai_sen = non_ai_with_salary[non_ai_with_salary['seniority'] == seniority]

                if len(ai_sen) >= 3 and len(non_ai_sen) >= 3:
                    ai_median = ai_sen['salary_mid'].median()
                    non_ai_median = non_ai_sen['salary_mid'].median()
                    diff = ai_median - non_ai_median
                    pct_diff = (diff / non_ai_median) * 100

                    comparison_data.append({
                        'Seniority': seniority,
                        'AI Jobs Median': ai_median,
                        'Non-AI Jobs Median': non_ai_median,
                        'Difference': diff,
                        'Pct Difference': pct_diff,
                        'AI Sample': len(ai_sen),
                        'Non-AI Sample': len(non_ai_sen)
                    })

            if comparison_data:
                comparison_df = pd.DataFrame(comparison_data)

                col1, col2, col3 = st.columns(3)

                with col1:
                    avg_premium = comparison_df['Pct Difference'].mean()
                    st.metric(
                        "Avg AI Salary Premium",
                        f"{avg_premium:+.1f}%",
                        help="Average salary difference for AI-skilled jobs vs non-AI jobs, controlling for seniority"
                    )

                with col2:
                    total_ai_salary_jobs = len(jobs_with_salary)
                    pct_ai_salary = (total_ai_salary_jobs / len(ai_jobs_df) * 100) if len(ai_jobs_df) > 0 else 0
                    st.metric(
                        "AI Jobs with Salary Data",
                        total_ai_salary_jobs,
                        f"{pct_ai_salary:.0f}% of AI jobs", delta_color="off", delta_arrow="off"
                    )

                with col3:
                    total_non_ai_salary_jobs = len(non_ai_with_salary)
                    pct_non_ai_salary = (total_non_ai_salary_jobs / len(non_ai_jobs) * 100) if len(non_ai_jobs) > 0 else 0
                    st.metric(
                        "Non-AI Jobs with Salary Data",
                        total_non_ai_salary_jobs,
                        f"{pct_non_ai_salary:.0f}% of non-AI jobs", delta_color="off", delta_arrow="off"
                    )

                chart_data = []
                for _, row in comparison_df.iterrows():
                    chart_data.append({
                        'Seniority': row['Seniority'],
                        'Category': 'AI Jobs',
                        'Median Salary': row['AI Jobs Median'],
                        'Sample Size': row['AI Sample']
                    })
                    chart_data.append({
                        'Seniority': row['Seniority'],
                        'Category': 'Non-AI Jobs',
                        'Median Salary': row['Non-AI Jobs Median'],
                        'Sample Size': row['Non-AI Sample']
                    })

                chart_df = pd.DataFrame(chart_data)

                fig = px.bar(
                    chart_df,
                    x='Seniority',
                    y='Median Salary',
                    color='Category',
                    barmode='group',
                    title='Median Salary by Seniority: AI vs Non-AI Jobs',
                    color_discrete_map={'AI Jobs': '#2E4A6B', 'Non-AI Jobs': '#8BA5C0'},
                    hover_data={'Sample Size': True}
                )

                for _, row in comparison_df.iterrows():
                    sen = row['Seniority']
                    pct = row['Pct Difference']
                    ai_median = row['AI Jobs Median']
                    non_ai_median = row['Non-AI Jobs Median']
                    max_salary = max(ai_median, non_ai_median)

                    fig.add_annotation(
                        x=sen,
                        y=max_salary,
                        text=f"{pct:+.1f}%",
                        showarrow=False,
                        yshift=15,
                        font=dict(size=11, color='#1F2937', family='Arial Black')
                    )

                fig.update_layout(
                    title_font_size=20,
                    font=dict(color='#1F2937', size=12),
                    xaxis=dict(
                        categoryorder='array',
                        categoryarray=seniority_order,
                        tickfont=dict(color='#1F2937', size=12),
                        title_font=dict(color='#1F2937', size=13)
                    ),
                    yaxis=dict(
                        tickformat='$,.0f',
                        tickfont=dict(color='#1F2937', size=12),
                        title_font=dict(color='#1F2937', size=13)
                    ),
                    legend=dict(
                        orientation='h',
                        yanchor='bottom',
                        y=1.02,
                        xanchor='right',
                        x=1
                    ),
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True)

                with st.expander("Detailed Salary Comparison by Seniority"):
                    display_df = comparison_df.copy()
                    display_df['AI Jobs Median'] = display_df['AI Jobs Median'].apply(lambda x: f"${x:,.0f}")
                    display_df['Non-AI Jobs Median'] = display_df['Non-AI Jobs Median'].apply(lambda x: f"${x:,.0f}")
                    display_df['Difference'] = display_df['Difference'].apply(lambda x: f"${x:+,.0f}")
                    display_df['Pct Difference'] = display_df['Pct Difference'].apply(lambda x: f"{x:+.1f}%")
                    display_df = display_df.rename(columns={
                        'AI Sample': 'AI Jobs (n)',
                        'Non-AI Sample': 'Non-AI Jobs (n)',
                        'Pct Difference': '% Difference'
                    })
                    st.dataframe(display_df, use_container_width=True, hide_index=True)

                    st.markdown("""
                    **Note:** Salary data is only available for ~35% of job postings.
                    Comparisons are made within the same seniority level to control for experience differences.
                    """)
            else:
                st.info("Not enough data to compare salaries by seniority level (need at least 3 jobs in each category).")
        else:
            st.info(f"Not enough non-AI jobs with salary data for comparison ({len(non_ai_with_salary)} found, need at least 10).")
    else:
        st.info(f"Not enough AI jobs with salary data ({len(jobs_with_salary)} found, need at least 20).")
