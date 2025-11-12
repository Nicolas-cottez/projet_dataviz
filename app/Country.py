import streamlit as st
import utils

st.set_page_config(page_title="PROJET ECE DATAVIZ 2025 - Gr3 - 0", layout='wide')

st.markdown("# Country")
st.sidebar.header("Country")
st.write("This is the second page")

df09, df10 = utils.load_data()
countries = df09['Country'].unique()

for element in countries:
    st.write(element)
