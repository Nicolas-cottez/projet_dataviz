import streamlit as st
import pandas as pd
import utils
import plotly.express as px

st.markdown("# 📊 KPIs & Overview")

# Load and Filter Data
df = utils.load_data()
filtered_df = utils.render_filters(df)

if filtered_df.empty:
    st.warning("Aucune donnée pour les filtres sélectionnés.")
    st.stop()

# Calculate Metrics
total_revenue = filtered_df['TotalAmount'].sum()
active_customers = filtered_df['Customer ID'].nunique()
avg_order_value = filtered_df.groupby('Invoice')['TotalAmount'].sum().mean()

# Retention (Global Average for selected period)
retention_matrix, _, _ = utils.calculate_cohorts(filtered_df)
avg_retention = retention_matrix.iloc[:, 1:].mean().mean() # Avg of retention rates > month 0

# CLV (Empirical)
clv_curve = utils.calculate_clv_empirical(filtered_df)
avg_clv = clv_curve.max() if not clv_curve.empty else 0

# Layout Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Chiffre d'Affaires", f"£{total_revenue:,.0f}", help="Somme totale des ventes sur la période.")

with col2:
    st.metric("Clients Actifs", f"{active_customers:,}", help="Nombre de clients uniques ayant commandé.")

with col3:
    st.metric("Rétention Moyenne", f"{avg_retention:.1%}", help="Moyenne des taux de rétention (M+1 et plus).")

with col4:
    st.metric("CLV Moyenne (Empirique)", f"£{avg_clv:.1f}", help="Revenu cumulé moyen par client (historique).")

st.markdown("---")

# North Star Metric
st.subheader("⭐ North Star Metric : Revenu par Client Actif")
north_star = total_revenue / active_customers if active_customers > 0 else 0
st.metric("Revenue per Active Customer", f"£{north_star:.2f}", delta=None)
st.caption("Indicateur clé de la valeur générée par chaque client actif sur la période.")

# Visual Trends
st.subheader("Tendances")
daily_sales = filtered_df.groupby('InvoiceDate')['TotalAmount'].sum().reset_index()
fig = px.line(daily_sales, x='InvoiceDate', y='TotalAmount', title='Évolution du CA Quotidien')
st.plotly_chart(fig, use_container_width=True)

# Definitions
with st.expander("ℹ️ Définitions des Métriques"):
    st.markdown("""
    - **Chiffre d'Affaires** : Somme des (Quantité * Prix) pour toutes les transactions valides.
    - **Clients Actifs** : Nombre de clients uniques ayant effectué au moins un achat.
    - **Rétention Moyenne** : Pourcentage moyen de clients revenant acheter les mois suivants.
    - **CLV (Customer Lifetime Value)** : Valeur à vie du client, estimée ici par la somme des revenus cumulés divisée par le nombre de clients initiaux.
    """)
