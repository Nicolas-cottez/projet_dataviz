import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    '''Fonction to load the 2 dataframes'''
    df09 = pd.read_csv('./data/raw/data_2009.csv')
    df10 = pd.read_csv('./data/raw/data_2010.csv')
    df_merge = pd.concat([df09, df10])
    df_merge['InvoiceDate'] = pd.to_datetime(df_merge['InvoiceDate'])
    return df_merge

def create_cohort(df):
    first_purchase = df.groupby('Customer ID')['InvoiceDate'].min().reset_index()
    first_purchase.columns = ['Customer ID', 'CohortDate']

    df = df.merge(first_purchase, on='Customer ID')

    df['CohortMonth'] = df['CohortDate'].dt.to_period('M')
    df['InvoiceMonth'] = df['InvoiceDate'].dt.to_period('M')
    return df

def cohort_period(df):
    cohort_year = df['CohortMonth'].dt.year
    cohort_month = df['CohortMonth'].dt.month
    invoice_year = df['InvoiceMonth'].dt.year
    invoice_month = df['InvoiceMonth'].dt.month
    
    df['CohortPeriod'] = (invoice_year - cohort_year) * 12 + (invoice_month - cohort_month) + 1
    return df

def cohort_actif(df):
    actif = (
        df.groupby(['Customer ID', 'InvoiceMonth'])
        .size()  # compte les transactions
        .reset_index(name='NbTransactions')
    )

    actif['CohortActif'] = actif['NbTransactions'] > 0
    df = df.merge(actif[['Customer ID', 'InvoiceMonth', 'CohortActif']], on=['Customer ID', 'InvoiceMonth'], how='left')
    return df

@st.cache_data
def clients_actifs_par_mois(df):
    actifs = (
        df[df['CohortActif'] == True]
        .groupby(['CohortMonth', 'CohortPeriod'])['Customer ID']
        .nunique()
        .reset_index(name='ClientsActifs')
    )
    return actifs

def retention(df):
    df_actifs = clients_actifs_par_mois(df)
    cohort_pivot = df_actifs.pivot(index='CohortMonth', columns='CohortPeriod', values='ClientsActifs')
    cohort_size = cohort_pivot.iloc[:, 0]
    return cohort_pivot.divide(cohort_size, axis=0)

@st.cache_data
def calcul_ca(df):
    return sum(df["Quantity"] * df["Price"])
