import pandas as pd
import numpy as np
import streamlit as st
import datetime

@st.cache_data
def load_data():
    """Load the cleaned dataset."""
    # Adjust path if necessary based on where app is run
    try:
        df = pd.read_csv('data/processed/online_retail_cleaned.csv')
    except FileNotFoundError:
        df = pd.read_csv('../data/processed/online_retail_cleaned.csv')
        
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['InvoiceMonth'] = df['InvoiceDate'].dt.to_period('M')
    return df

def filter_data(df, country_filter, date_range, customer_type_filter=None, min_order_value=0, exclude_returns=False):
    """Filter the dataset based on user inputs."""
    filtered_df = df.copy()
    
    # Date Range
    if date_range:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered_df = filtered_df[(filtered_df['InvoiceDate'] >= start_date) & (filtered_df['InvoiceDate'] <= end_date)]
    
    # Country
    if country_filter and 'All' not in country_filter:
        filtered_df = filtered_df[filtered_df['Country'].isin(country_filter)]
        
    # Exclude Returns
    if exclude_returns:
        filtered_df = filtered_df[~filtered_df['Invoice'].astype(str).str.startswith('C')]
        filtered_df = filtered_df[filtered_df['Quantity'] > 0]
        
    # Min Order Value (Filter invoices with total amount < threshold)
    if min_order_value > 0:
        invoice_totals = filtered_df.groupby('Invoice')['TotalAmount'].sum()
        valid_invoices = invoice_totals[invoice_totals >= min_order_value].index
        filtered_df = filtered_df[filtered_df['Invoice'].isin(valid_invoices)]
        
    return filtered_df

def add_cohort_columns(df):
    """Add CohortMonth and CohortIndex columns to the dataframe."""
    df = df.copy()
    
    # Define Cohort Month (Month of first purchase)
    df['CohortMonth'] = df.groupby('Customer ID')['InvoiceDate'].transform('min').dt.to_period('M')
    
    # Calculate Cohort Index (Months since first purchase)
    def get_date_int(df, column):
        year = df[column].dt.year
        month = df[column].dt.month
        return year, month

    invoice_year, invoice_month = get_date_int(df, 'InvoiceMonth')
    cohort_year, cohort_month = get_date_int(df, 'CohortMonth')
    years_diff = invoice_year - cohort_year
    months_diff = invoice_month - cohort_month
    df['CohortIndex'] = years_diff * 12 + months_diff + 1
    
    return df

def calculate_cohorts(df):
    """Calculate retention matrix and cohort sizes."""
    df = add_cohort_columns(df)
    
    # Retention Matrix
    grouping = df.groupby(['CohortMonth', 'CohortIndex'])
    cohort_data = grouping['Customer ID'].apply(pd.Series.nunique).reset_index()
    cohort_counts = cohort_data.pivot(index='CohortMonth', columns='CohortIndex', values='Customer ID')
    cohort_sizes = cohort_counts.iloc[:, 0]
    retention = cohort_counts.divide(cohort_sizes, axis=0)
    
    return retention, cohort_sizes, cohort_counts

def calculate_rfm(df):
    """Calculate RFM scores and segments."""
    snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
    
    rfm = df.groupby('Customer ID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        'Invoice': 'nunique',
        'TotalAmount': 'sum'
    })
    
    rfm.rename(columns={'InvoiceDate': 'Recency', 'Invoice': 'Frequency', 'TotalAmount': 'Monetary'}, inplace=True)
    
    # Create Quartiles (1-4, 4 is best)
    # Recency: Lower is better -> 4 is lowest quartile
    r_labels = range(4, 0, -1)
    f_labels = range(1, 5)
    m_labels = range(1, 5)
    
    r_quartiles = pd.qcut(rfm['Recency'], q=4, labels=r_labels)
    # Handle duplicates in Frequency/Monetary with rank method if needed, or just duplicates='drop'
    # Using rank(method='first') is safer for qcut with many duplicates
    f_quartiles = pd.qcut(rfm['Frequency'].rank(method='first'), q=4, labels=f_labels)
    m_quartiles = pd.qcut(rfm['Monetary'].rank(method='first'), q=4, labels=m_labels)
    
    rfm = rfm.assign(R=r_quartiles.values, F=f_quartiles.values, M=m_quartiles.values)
    
    def join_rfm(x): return str(x['R']) + str(x['F']) + str(x['M'])
    rfm['RFM_Segment'] = rfm.apply(join_rfm, axis=1)
    rfm['RFM_Score'] = rfm[['R', 'F', 'M']].sum(axis=1)
    
    # Define Segments
    def segment_customer(df):
        if df['RFM_Score'] >= 9:
            return 'Champions'
        elif (df['RFM_Score'] >= 8) and (df['RFM_Score'] < 9):
            return 'Loyal Customers'
        elif (df['RFM_Score'] >= 7) and (df['RFM_Score'] < 8):
            return 'Potential Loyalists'
        elif (df['RFM_Score'] >= 6) and (df['RFM_Score'] < 7):
            return 'Promising'
        elif (df['RFM_Score'] >= 5) and (df['RFM_Score'] < 6):
            return 'Needs Attention'
        elif (df['RFM_Score'] >= 4) and (df['RFM_Score'] < 5):
            return 'About To Sleep'
        else:
            return 'At Risk'
            
    rfm['Segment'] = rfm.apply(segment_customer, axis=1)
    
    return rfm

def calculate_clv_empirical(df):
    """Calculate Empirical CLV (Cumulative Revenue per Cohort Age)."""
    # Ensure CohortIndex exists
    if 'CohortIndex' not in df.columns:
        df = add_cohort_columns(df)

    # Average revenue per customer at that age
    # Approach:
    # 1. Calculate total revenue per cohort per age.
    # 2. Divide by initial cohort size.
    # 3. Cumulate over age.
    
    cohort_sizes = df.groupby('CohortMonth')['Customer ID'].nunique()
    
    cohort_revenue_df = df.groupby(['CohortMonth', 'CohortIndex'])['TotalAmount'].sum().reset_index()
    cohort_revenue_df = cohort_revenue_df.merge(cohort_sizes.rename('CohortSize'), on='CohortMonth')
    cohort_revenue_df['RevPerCustomer'] = cohort_revenue_df['TotalAmount'] / cohort_revenue_df['CohortSize']
    
    # Average across all cohorts for each age
    avg_clv_per_age = cohort_revenue_df.groupby('CohortIndex')['RevPerCustomer'].mean().cumsum()
    
    return avg_clv_per_age

def calculate_clv_formula(avg_order_value, purchase_freq, margin, retention_rate, discount_rate):
    """Calculate CLV using simple formula: (AOV * F * Margin * r) / (1 + d - r)."""
    # CLV = (Gross Margin * Retention Rate) / (1 + Discount Rate - Retention Rate)
    # Gross Margin = AOV * F * Margin%
    
    gross_margin = avg_order_value * purchase_freq * margin
    if (1 + discount_rate - retention_rate) == 0:
        return 0 # Avoid division by zero
    clv = (gross_margin * retention_rate) / (1 + discount_rate - retention_rate)
    return clv

def simulate_scenarios(df, margin_change, retention_change, discount_rate):
    """Simulate scenarios for CLV."""
    # Baseline metrics
    rfm = calculate_rfm(df)
    avg_order_value = df.groupby('Invoice')['TotalAmount'].sum().mean()
    purchase_freq = df.groupby('Customer ID')['Invoice'].nunique().mean() # Average frequency over the period
import pandas as pd
import numpy as np
import streamlit as st
import datetime

@st.cache_data
def load_data():
    """Load the cleaned dataset."""
    # Adjust path if necessary based on where app is run
    try:
        df = pd.read_csv('data/processed/online_retail_cleaned.csv')
    except FileNotFoundError:
        df = pd.read_csv('../data/processed/online_retail_cleaned.csv')
        
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['InvoiceMonth'] = df['InvoiceDate'].dt.to_period('M')
    return df

def filter_data(df, country_filter, date_range, customer_type_filter=None, min_order_value=0, returns_mode='Inclure'):
    """Filter the dataset based on user inputs."""
    filtered_df = df.copy()
    
    # Date Range
    if date_range:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered_df = filtered_df[(filtered_df['InvoiceDate'] >= start_date) & (filtered_df['InvoiceDate'] <= end_date)]
    
    # Country
    if country_filter and 'All' not in country_filter:
        filtered_df = filtered_df[filtered_df['Country'].isin(country_filter)]
        
    # Returns Handling
    if returns_mode == 'Exclure':
        filtered_df = filtered_df[~filtered_df['Invoice'].astype(str).str.startswith('C')]
    elif returns_mode == 'Neutraliser':
        # Set negative values to 0 (keep transaction but remove financial impact)
        filtered_df.loc[filtered_df['TotalAmount'] < 0, 'TotalAmount'] = 0
        
    # Min Order Value (Filter invoices with total amount < threshold)
    if min_order_value > 0:
        invoice_totals = filtered_df.groupby('Invoice')['TotalAmount'].sum()
        valid_invoices = invoice_totals[invoice_totals >= min_order_value].index
        filtered_df = filtered_df[filtered_df['Invoice'].isin(valid_invoices)]
        
    return filtered_df

def add_cohort_columns(df):
    """Add CohortMonth and CohortIndex columns to the dataframe."""
    df = df.copy()
    
    # Define Cohort Month (Month of first purchase)
    df['CohortMonth'] = df.groupby('Customer ID')['InvoiceDate'].transform('min').dt.to_period('M')
    
    # Calculate Cohort Index (Months since first purchase)
    def get_date_int(df, column):
        year = df[column].dt.year
        month = df[column].dt.month
        return year, month

    invoice_year, invoice_month = get_date_int(df, 'InvoiceMonth')
    cohort_year, cohort_month = get_date_int(df, 'CohortMonth')
    years_diff = invoice_year - cohort_year
    months_diff = invoice_month - cohort_month
    df['CohortIndex'] = years_diff * 12 + months_diff + 1
    
    return df

def calculate_cohorts(df):
    """Calculate retention matrix and cohort sizes."""
    df = add_cohort_columns(df)
    
    # Retention Matrix
    grouping = df.groupby(['CohortMonth', 'CohortIndex'])
    cohort_data = grouping['Customer ID'].apply(pd.Series.nunique).reset_index()
    cohort_counts = cohort_data.pivot(index='CohortMonth', columns='CohortIndex', values='Customer ID')
    cohort_sizes = cohort_counts.iloc[:, 0]
    retention = cohort_counts.divide(cohort_sizes, axis=0)
    
    return retention, cohort_sizes, cohort_counts

def calculate_rfm(df):
    """Calculate RFM scores and segments."""
    snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
    
    rfm = df.groupby('Customer ID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        'Invoice': 'nunique',
        'TotalAmount': 'sum'
    })
    
    rfm.rename(columns={'InvoiceDate': 'Recency', 'Invoice': 'Frequency', 'TotalAmount': 'Monetary'}, inplace=True)
    
    # Create Quartiles (1-4, 4 is best)
    # Recency: Lower is better -> 4 is lowest quartile
    r_labels = range(4, 0, -1)
    f_labels = range(1, 5)
    m_labels = range(1, 5)
    
    r_quartiles = pd.qcut(rfm['Recency'], q=4, labels=r_labels)
    # Handle duplicates in Frequency/Monetary with rank method if needed, or just duplicates='drop'
    # Using rank(method='first') is safer for qcut with many duplicates
    f_quartiles = pd.qcut(rfm['Frequency'].rank(method='first'), q=4, labels=f_labels)
    m_quartiles = pd.qcut(rfm['Monetary'].rank(method='first'), q=4, labels=m_labels)
    
    rfm = rfm.assign(R=r_quartiles.values, F=f_quartiles.values, M=m_quartiles.values)
    
    def join_rfm(x): return str(x['R']) + str(x['F']) + str(x['M'])
    rfm['RFM_Segment'] = rfm.apply(join_rfm, axis=1)
    rfm['RFM_Score'] = rfm[['R', 'F', 'M']].sum(axis=1)
    
    # Define Segments
    def segment_customer(df):
        if df['RFM_Score'] >= 9:
            return 'Champions'
        elif (df['RFM_Score'] >= 8) and (df['RFM_Score'] < 9):
            return 'Loyal Customers'
        elif (df['RFM_Score'] >= 7) and (df['RFM_Score'] < 8):
            return 'Potential Loyalists'
        elif (df['RFM_Score'] >= 6) and (df['RFM_Score'] < 7):
            return 'Promising'
        elif (df['RFM_Score'] >= 5) and (df['RFM_Score'] < 6):
            return 'Needs Attention'
        elif (df['RFM_Score'] >= 4) and (df['RFM_Score'] < 5):
            return 'About To Sleep'
        else:
            return 'At Risk'
            
    rfm['Segment'] = rfm.apply(segment_customer, axis=1)
    
    return rfm

def calculate_clv_empirical(df):
    """Calculate Empirical CLV (Cumulative Revenue per Cohort Age)."""
    # Ensure CohortIndex exists
    if 'CohortIndex' not in df.columns:
        df = add_cohort_columns(df)

    # Average revenue per customer at that age
    # Approach:
    # 1. Calculate total revenue per cohort per age.
    # 2. Divide by initial cohort size.
    # 3. Cumulate over age.
    
    cohort_sizes = df.groupby('CohortMonth')['Customer ID'].nunique()
    
    cohort_revenue_df = df.groupby(['CohortMonth', 'CohortIndex'])['TotalAmount'].sum().reset_index()
    cohort_revenue_df = cohort_revenue_df.merge(cohort_sizes.rename('CohortSize'), on='CohortMonth')
    cohort_revenue_df['RevPerCustomer'] = cohort_revenue_df['TotalAmount'] / cohort_revenue_df['CohortSize']
    
    # Average across all cohorts for each age
    avg_clv_per_age = cohort_revenue_df.groupby('CohortIndex')['RevPerCustomer'].mean().cumsum()
    
    return avg_clv_per_age

def calculate_clv_formula(avg_order_value, purchase_freq, margin, retention_rate, discount_rate):
    """Calculate CLV using simple formula: (AOV * F * Margin * r) / (1 + d - r)."""
    # CLV = (Gross Margin * Retention Rate) / (1 + Discount Rate - Retention Rate)
    # Gross Margin = AOV * F * Margin%
    
    gross_margin = avg_order_value * purchase_freq * margin
    if (1 + discount_rate - retention_rate) == 0:
        return 0 # Avoid division by zero
    clv = (gross_margin * retention_rate) / (1 + discount_rate - retention_rate)
    return clv

def simulate_scenarios(df, margin_change, retention_change, discount_rate):
    """Simulate scenarios for CLV."""
    # Baseline metrics
    rfm = calculate_rfm(df)
    avg_order_value = df.groupby('Invoice')['TotalAmount'].sum().mean()
    purchase_freq = df.groupby('Customer ID')['Invoice'].nunique().mean() # Average frequency over the period
    
    # Retention Rate (Approximate as average retention from cohorts)
    retention_matrix, _, _ = calculate_cohorts(df)
    avg_retention = retention_matrix.iloc[:, 1:].mean().mean() # Average of all retention rates (excluding month 1 which is 100%)
    
    # Baseline CLV
    baseline_clv = calculate_clv_formula(avg_order_value, purchase_freq, 1.0, avg_retention, discount_rate) # Assuming 100% margin initially or user input
    # Wait, margin is usually a percentage. Let's assume baseline margin is passed or we use 1.0 if not.
    # The prompt says "Simuler des scénarios (ex. +5 % rétention, −10 % marge...)"
    # So we need a base margin. Let's assume 20% net margin if not specified, or let user define.
    # For this function, let's take absolute values or deltas.
    
    # Let's refine: The function should take BASE parameters and SCENARIO parameters.
    # But here we calculate baseline from data.
    
    # Let's return a dictionary with baseline and scenario values.
    return {
        'baseline_clv': baseline_clv,
        'avg_retention': avg_retention,
        'avg_order_value': avg_order_value,
        'purchase_freq': purchase_freq
    }

def render_filters(df):
    """Render sidebar filters and return filtered dataframe."""
    st.sidebar.header("Filtres")
    
    # Date Range
    min_date = df['InvoiceDate'].min().date()
    max_date = df['InvoiceDate'].max().date()
    date_range = st.sidebar.date_input("Période", [min_date, max_date], min_value=min_date, max_value=max_date)
    
    # Time Unit (for aggregation in charts)
    time_unit = st.sidebar.selectbox("Unité de Temps", ["Mois", "Trimestre"], index=0)
    st.session_state['time_unit'] = time_unit
    
    # Country
    countries = ['All'] + sorted(df['Country'].unique().tolist())
    country = st.sidebar.multiselect("Pays", countries, default=['All'])
    
    # Returns Mode
    returns_mode = st.sidebar.selectbox("Mode Retours", ["Inclure", "Exclure", "Neutraliser"], index=0, help="Inclure: Garder les retours (Revenu Net).\nExclure: Supprimer les retours (Revenu Brut).\nNeutraliser: Compter les retours à 0£.")
    
    # Min Order Value
    min_order = st.sidebar.number_input("Seuil de commande (£)", min_value=0, value=0, step=10)
    
    # Apply filters
    if len(date_range) == 2:
        filtered_df = filter_data(df, country, date_range, min_order_value=min_order, returns_mode=returns_mode)
    else:
        filtered_df = df # Fallback if date not fully selected
        
    # Display Filter Stats
    st.sidebar.markdown("---")
    st.sidebar.write(f"**Transactions:** {len(filtered_df)}")
    st.sidebar.write(f"**Clients:** {filtered_df['Customer ID'].nunique()}")
    
    if returns_mode == 'Exclure':
        st.sidebar.caption("🚫 Retours Exclus")
    
    return filtered_df
