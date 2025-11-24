import streamlit as st
import pandas as pd
import utils
import plotly.express as px

st.markdown("# 🎯 Segmentation RFM")

# Load and Filter Data
df = utils.load_data()
filtered_df = utils.render_filters(df)

if filtered_df.empty:
    st.warning("Aucune donnée pour les filtres sélectionnés.")
    st.stop()

# Calculate RFM
rfm_df = utils.calculate_rfm(filtered_df)

# Aggregation by Segment
segment_agg = rfm_df.groupby('Segment').agg({
    'Recency': 'mean',
    'Frequency': 'mean',
    'Monetary': 'sum',
    'RFM_Score': 'count' # Count of customers
}).rename(columns={'RFM_Score': 'Count'})

segment_agg['Avg Order Value'] = segment_agg['Monetary'] / (segment_agg['Frequency'] * segment_agg['Count'])
segment_agg['Share of Revenue'] = segment_agg['Monetary'] / segment_agg['Monetary'].sum()

# Display Summary
st.subheader("Vue d'ensemble des Segments")



st.dataframe(segment_agg.style.format({
    'Recency': '{:.1f} jours',
    'Frequency': '{:.1f}',
    'Monetary': '£{:,.0f}',
    'Avg Order Value': '£{:,.2f}',
    'Share of Revenue': '{:.1%}'
}), width='stretch')


fig_pie = px.pie(segment_agg, values='Count', names=segment_agg.index, title="Répartition des Clients")
st.plotly_chart(fig_pie, use_container_width=True)

# Treemap of Value
st.subheader("Valeur par Segment")
# Prepare data for treemap: We need individual customer data or just the agg
# Treemap of segments sized by Revenue
fig_tree = px.treemap(segment_agg.reset_index(), path=['Segment'], values='Monetary',
                      title="Part de Chiffre d'Affaires par Segment",
                      color='Monetary', color_continuous_scale='RdBu')
st.plotly_chart(fig_tree, use_container_width=True)

# Detailed List
with st.expander("Voir les détails des clients par segment"):
    selected_seg = st.selectbox("Choisir un segment :", segment_agg.index)
    st.dataframe(rfm_df[rfm_df['Segment'] == selected_seg][['Recency', 'Frequency', 'Monetary', 'RFM_Score']].sort_values('Monetary', ascending=False), width='stretch')
