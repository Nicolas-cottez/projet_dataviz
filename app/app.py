import streamlit as st

pg = st.navigation([st.Page("Price_Quantity.py"), st.Page("Country.py")])
pg.run()

# streamlit run app/app.py
