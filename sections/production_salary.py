import pandas as pd
import plotly.express as px
import streamlit as st

from lib.charts import TEXT_COLOR
from lib.titles import normalize_job_title

SENIORITY_ORDER = ['Junior', 'Mid', 'Senior', 'Staff+', 'Lead/Manager', 'Director+']

# Same minimums as the AI salary section, so both pages hold the same bar for
# what counts as enough salary data to compare.
MIN_PRODUCTION_JOBS = 20
MIN_OTHER_JOBS = 10
MIN_PER_LEVEL = 3


def render(prod_df):
    st.header("Salary Analysis: Production Skills vs Other Jobs")

    with_salary = prod_df[prod_df['salary_mid'].notna()].copy()
    with_salary['seniority'] = with_salary['title'].apply(lambda t: normalize_job_title(t)[0])

    production_jobs = with_salary[with_salary['requires_production']]
    other_jobs = with_salary[~with_salary['requires_production']]

    if len(production_jobs) < MIN_PRODUCTION_JOBS:
        st.info(f"Not enough production jobs with salary data ({len(production_jobs)} found, need at least {MIN_PRODUCTION_JOBS}).")
        return
    if len(other_jobs) < MIN_OTHER_JOBS:
        st.info(f"Not enough non-production jobs with salary data for comparison ({len(other_jobs)} found, need at least {MIN_OTHER_JOBS}).")
        return

    # Compare within each seniority level so experience differences don't
    # masquerade as a production premium.
    rows = []
    for seniority in SENIORITY_ORDER:
        prod_level = production_jobs[production_jobs['seniority'] == seniority]
        other_level = other_jobs[other_jobs['seniority'] == seniority]
        if len(prod_level) >= MIN_PER_LEVEL and len(other_level) >= MIN_PER_LEVEL:
            prod_median = prod_level['salary_mid'].median()
            other_median = other_level['salary_mid'].median()
            rows.append({
                'Seniority': seniority,
                'Production Jobs Median': prod_median,
                'Other Jobs Median': other_median,
                'Difference': prod_median - other_median,
                'Pct Difference': (prod_median - other_median) / other_median * 100,
                'Production Sample': len(prod_level),
                'Other Sample': len(other_level),
            })

    if not rows:
        st.info(f"Not enough data to compare salaries by seniority level (need at least {MIN_PER_LEVEL} jobs in each group).")
        return

    comparison = pd.DataFrame(rows)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Avg Salary Difference",
            f"{comparison['Pct Difference'].mean():+.1f}%",
            help="Average median-salary difference for jobs requiring production skills vs the rest, within the same seniority level. Positive means production jobs pay more.",
        )
    with col2:
        total_production = int(prod_df['requires_production'].sum())
        st.metric("Production Jobs with Salary Data", len(production_jobs),
                  f"{len(production_jobs) / total_production * 100:.0f}% of production jobs",
                  delta_color="off", delta_arrow="off")
    with col3:
        total_other = int((~prod_df['requires_production']).sum())
        st.metric("Other Jobs with Salary Data", len(other_jobs),
                  f"{len(other_jobs) / total_other * 100:.0f}% of other jobs",
                  delta_color="off", delta_arrow="off")

    chart_rows = []
    for _, row in comparison.iterrows():
        chart_rows.append({'Seniority': row['Seniority'], 'Category': 'Requires production skills',
                           'Median Salary': row['Production Jobs Median'], 'Sample Size': row['Production Sample']})
        chart_rows.append({'Seniority': row['Seniority'], 'Category': 'Other jobs',
                           'Median Salary': row['Other Jobs Median'], 'Sample Size': row['Other Sample']})
    chart_df = pd.DataFrame(chart_rows)

    fig = px.bar(
        chart_df,
        x='Seniority',
        y='Median Salary',
        color='Category',
        barmode='group',
        title='Median Salary by Seniority: Production Skills vs Other Jobs',
        color_discrete_map={'Requires production skills': '#2E4A6B', 'Other jobs': '#8BA5C0'},
        hover_data={'Sample Size': True},
    )
    for _, row in comparison.iterrows():
        fig.add_annotation(
            x=row['Seniority'],
            y=max(row['Production Jobs Median'], row['Other Jobs Median']),
            text=f"{row['Pct Difference']:+.1f}%",
            showarrow=False,
            yshift=15,
            font=dict(size=11, color=TEXT_COLOR, family='Arial Black'),
        )
    fig.update_layout(
        title_font_size=20,
        font=dict(color=TEXT_COLOR, size=12),
        xaxis=dict(categoryorder='array', categoryarray=SENIORITY_ORDER,
                   tickfont=dict(color=TEXT_COLOR, size=12), title_font=dict(color=TEXT_COLOR, size=13)),
        yaxis=dict(tickformat='$,.0f', tickfont=dict(color=TEXT_COLOR, size=12), title_font=dict(color=TEXT_COLOR, size=13)),
        legend=dict(title='', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=400,
    )
    st.plotly_chart(fig, width="stretch")

    with st.expander("Detailed Salary Comparison by Seniority"):
        display = comparison.copy()
        display['Production Jobs Median'] = display['Production Jobs Median'].apply(lambda x: f"${x:,.0f}")
        display['Other Jobs Median'] = display['Other Jobs Median'].apply(lambda x: f"${x:,.0f}")
        display['Difference'] = display['Difference'].apply(lambda x: f"${x:+,.0f}")
        display['Pct Difference'] = display['Pct Difference'].apply(lambda x: f"{x:+.1f}%")
        display = display.rename(columns={
            'Production Sample': 'Production Jobs (n)',
            'Other Sample': 'Other Jobs (n)',
            'Pct Difference': '% Difference',
        })
        st.dataframe(display, width="stretch", hide_index=True)
        share_with_salary = len(with_salary) / len(prod_df) * 100 if len(prod_df) else 0
        st.markdown(
            f"**Note:** Salary data is only available for about {share_with_salary:.0f}% of job postings. "
            "Comparisons are made within the same seniority level to control for experience differences."
        )
