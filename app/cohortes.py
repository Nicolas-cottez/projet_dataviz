import streamlit as st
import pandas as pd
import utils
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

st.markdown("# 🔍 Analyse des Cohortes")

# Load and Filter Data
df = utils.load_data()
filtered_df = utils.render_filters(df)

if filtered_df.empty:
    st.warning("Aucune donnée pour les filtres sélectionnés.")
    st.stop()

# Calculate Cohorts
retention_matrix, cohort_sizes, cohort_counts = utils.calculate_cohorts(filtered_df)

# 1. Retention Heatmap
st.subheader("Heatmap de Rétention")

# Toggle for absolute vs percentage
view_option = st.radio("Affichage :", ["Pourcentage (%)", "Nombre Absolu (N)"], horizontal=True)

if view_option == "Pourcentage (%)":
    fig = px.imshow(retention_matrix, 
                    labels=dict(x="Mois après acquisition", y="Cohorte", color="Rétention"),
                    x=retention_matrix.columns,
                    y=retention_matrix.index.astype(str),
                    color_continuous_scale="Blues",
                    text_auto='.0%')
else:
    fig = px.imshow(cohort_counts, 
                    labels=dict(x="Mois après acquisition", y="Cohorte", color="Clients"),
                    x=cohort_counts.columns,
                    y=cohort_counts.index.astype(str),
                    color_continuous_scale="Blues",
                    text_auto=True)

fig.update_layout(height=600)
st.plotly_chart(fig, use_container_width=True)

# 2. Revenue per Cohort
st.subheader("Revenu par Cohorte")

# Calculate revenue per cohort per month
# Calculate revenue per cohort per month
filtered_df = utils.add_cohort_columns(filtered_df)
cohort_revenue = filtered_df.groupby(['CohortMonth', 'CohortIndex'])['TotalAmount'].sum().reset_index()
cohort_revenue['CohortMonth'] = cohort_revenue['CohortMonth'].astype(str)

fig_rev = px.line(cohort_revenue, x='CohortIndex', y='TotalAmount', color='CohortMonth',
                  title="Évolution du CA par Cohorte (en valeur absolue)",
                  labels={'CohortIndex': 'Mois après acquisition', 'TotalAmount': 'Revenu (£)'})
st.plotly_chart(fig_rev, use_container_width=True)

# Focus Cohorte
st.subheader("Focus Cohorte")
cohorts_list = sorted(filtered_df['CohortMonth'].unique().astype(str))
selected_cohort = st.selectbox("Sélectionner une cohorte pour détails :", cohorts_list)

if selected_cohort:
    cohort_df = filtered_df[filtered_df['CohortMonth'].astype(str) == selected_cohort]
    st.write(f"**Détails pour la cohorte {selected_cohort}**")
    st.write(f"- Nombre de clients initiaux : {cohort_sizes[pd.Period(selected_cohort, 'M')]}")
    st.write(f"- CA Total généré : £{cohort_df['TotalAmount'].sum():,.2f}")
    st.write(f"- Panier moyen : £{cohort_df['TotalAmount'].mean():,.2f}")
