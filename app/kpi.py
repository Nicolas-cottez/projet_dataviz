import streamlit as st
import pandas as pd
import utils

st.set_page_config(page_title="PROJET ECE DATAVIZ 2025 - Gr3 - 0", layout='wide')

st.markdown("# KPI")
st.sidebar.header("KPI")

df = utils.load_data()
df = utils.create_cohort(df)
df = utils.cohort_period(df)
df = utils.cohort_actif(df)
actifs = utils.clients_actifs_par_mois(df)
retention = utils.retention(df)
ca = utils.calcul_ca(df)

st.write(f"Chiffre d'affaires : £{ca:,.2f} ≈ £{int(round(ca, -6)):,.2f}".replace(",", " "))
st.write("Clients actifs :", actifs)
st.write("Rétention moyenne :", retention.mean())
st.write("CLV moyenne :")
st.write("Segments RFM :")
