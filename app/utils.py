import os
import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    '''Fonction to load the 2 dataframes'''
    df09 = pd.read_csv('./data/raw/data_2009.csv')
    df10 = pd.read_csv('./data/raw/data_2010.csv')
    return df09, df10
