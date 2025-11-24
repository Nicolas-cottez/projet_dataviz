import streamlit as st
import pandas as pd
import utils

st.markdown("# 📥 Plan d'Action & Exports")

# Load and Filter Data
df = utils.load_data()
filtered_df = utils.render_filters(df)

if filtered_df.empty:
    st.warning("Aucune donnée pour les filtres sélectionnés.")
    st.stop()

# Calculate RFM for all filtered customers
st.info("Calcul des segments sur la population filtrée...")
rfm_df = utils.calculate_rfm(filtered_df)

# Display Table
st.subheader("Liste Activable")
st.write("Utilisez cette liste pour vos campagnes marketing (emailing, relance, etc.).")

# Filter by Segment in the page
segments = ['All'] + sorted(rfm_df['Segment'].unique().tolist())
selected_segment = st.selectbox("Filtrer par Segment :", segments)

if selected_segment != 'All':
    display_df = rfm_df[rfm_df['Segment'] == selected_segment]
else:
    display_df = rfm_df

# Select columns to display
cols = ['Recency', 'Frequency', 'Monetary', 'RFM_Score', 'Segment', 'RFM_Segment']
display_df = display_df[cols].sort_values('Monetary', ascending=False)

st.dataframe(display_df, width='stretch')

# Export Button
csv = display_df.to_csv().encode('utf-8')

st.download_button(
    label="📥 Télécharger la liste (CSV)",
    data=csv,
    file_name=f'action_plan_{selected_segment}.csv',
    mime='text/csv',
)

st.markdown("### 📸 Export des Graphiques")
st.write("Pour exporter les graphiques des autres pages, utilisez le menu '...' en haut à droite de chaque graphique (fonctionnalité native Plotly/Streamlit).")
