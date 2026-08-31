import streamlit as st

st.set_page_config(page_title="Data Science Job Market", layout="wide")

# One page per lens on the same postings. Each view loads the shared, cached
# data itself (lib.data.load_dashboard_data), so there is nothing to pass here.
pages = [
    st.Page("views/ai_in_data_science.py", title="AI in Data Science", icon=":material/psychology:", default=True),
    st.Page("views/ml_in_production.py", title="ML in Production", icon=":material/rocket_launch:"),
]

st.navigation(pages).run()
