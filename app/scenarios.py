import streamlit as st
import pandas as pd
import utils
import plotly.graph_objects as go

st.markdown("# 🎛️ Simulation de Scénarios")

# Load and Filter Data
df = utils.load_data()
filtered_df = utils.render_filters(df)

if filtered_df.empty:
    st.warning("Aucune donnée pour les filtres sélectionnés.")
    st.stop()

# 1. Baseline Metrics Calculation
st.subheader("Paramètres Actuels (Baseline)")

# Calculate Baseline Inputs
avg_order_value = filtered_df.groupby('Invoice')['TotalAmount'].sum().mean()
purchase_freq = filtered_df.groupby('Customer ID')['Invoice'].nunique().mean()
retention_matrix, _, _ = utils.calculate_cohorts(filtered_df)
baseline_retention = retention_matrix.iloc[:, 1:].mean().mean() # Avg retention

col1, col2, col3 = st.columns(3)
col1.metric("Panier Moyen (AOV)", f"£{avg_order_value:.2f}")
col2.metric("Fréquence d'Achat", f"{purchase_freq:.2f}")
col3.metric("Taux de Rétention (r)", f"{baseline_retention:.1%}")

# 2. Simulation Controls
st.sidebar.markdown("### Paramètres de Simulation")
margin_sim = st.sidebar.slider("Marge Commerciale (%)", 0, 100, 20, 5) / 100
retention_delta = st.sidebar.slider("Variation Rétention (%)", -20, 20, 0, 1) / 100
discount_rate = st.sidebar.slider("Taux d'Actualisation (d)", 0, 20, 10, 1) / 100

# 3. Scenario Calculation
scenario_retention = min(max(baseline_retention * (1 + retention_delta), 0), 0.99) # Cap at 99% to avoid div by 0 if d=0 and r=1
# CLV Formula: (AOV * F * Margin * r) / (1 + d - r)

def calc_clv(aov, freq, margin, r, d):
    if (1 + d - r) <= 0: return 0
    return (aov * freq * margin * r) / (1 + d - r)

baseline_clv = calc_clv(avg_order_value, purchase_freq, margin_sim, baseline_retention, discount_rate)
scenario_clv = calc_clv(avg_order_value, purchase_freq, margin_sim, scenario_retention, discount_rate)

# 4. Results & Comparison
st.subheader("Résultats de la Simulation")

col_res1, col_res2, col_res3 = st.columns(3)

col_res1.metric("CLV Baseline", f"£{baseline_clv:.2f}")
col_res2.metric("CLV Scénario", f"£{scenario_clv:.2f}", delta=f"{(scenario_clv - baseline_clv):.2f} £")
col_res3.metric("Impact Rétention", f"{scenario_retention:.1%}", delta=f"{retention_delta*100:+.0f}% (relatif)")

# Chart Comparison
fig = go.Figure(data=[
    go.Bar(name='Baseline', x=['CLV'], y=[baseline_clv], marker_color='gray'),
    go.Bar(name='Scénario', x=['CLV'], y=[scenario_clv], marker_color='blue')
])
fig.update_layout(title="Comparaison CLV : Baseline vs Scénario", barmode='group')
st.plotly_chart(fig, use_container_width=True)

# Sensitivity Analysis (Optional)
st.markdown("### Analyse de Sensibilité")
st.caption("Impact de la variation du taux de rétention sur la CLV (toutes choses égales par ailleurs)")

r_range = [baseline_retention * (1 + i/100) for i in range(-20, 21, 5)]
clv_range = [calc_clv(avg_order_value, purchase_freq, margin_sim, r, discount_rate) for r in r_range]

fig_sens = go.Figure(data=go.Scatter(x=[r * 100 for r in r_range], y=clv_range, mode='lines+markers'))
fig_sens.update_layout(title="Sensibilité CLV vs Rétention", xaxis_title="Taux de Rétention (%)", yaxis_title="CLV (£)")
st.plotly_chart(fig_sens, use_container_width=True)
