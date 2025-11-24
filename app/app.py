import streamlit as st

pg = st.navigation([st.Page("kpi.py"), st.Page("cohortes.py"), st.Page("segments.py")])
pg.run()

# streamlit run app/app.py