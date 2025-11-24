import streamlit as st

st.set_page_config(page_title="Marketing Decision Support", layout="wide")

# Define pages
pages = [
    st.Page("kpi.py", title="KPIs (Overview)", icon="📊"),
    st.Page("cohortes.py", title="Cohortes (Diagnostiquer)", icon="🔍"),
    st.Page("segments.py", title="Segments (Prioriser)", icon="🎯"),
    st.Page("scenarios.py", title="Scénarios (Simuler)", icon="🎛️"),
    st.Page("action_plan.py", title="Plan d'Action (Exporter)", icon="📥"),
]

pg = st.navigation(pages)
pg.run()