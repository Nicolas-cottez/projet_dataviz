import streamlit as st
from matplotlib import pyplot as plt
import utils

st.set_page_config(page_title="PROJET ECE DATAVIZ 2025 - Gr3 - 0", layout='wide')

st.markdown("# Price vs Quantity")
st.sidebar.header("Price vs Quantity")
st.write("This is the first page")

df09, df10 = utils.load_data()
x = df09['Quantity']
y = df09['Price']


col_left, col_right = st.columns(2, gap='small')
with col_left:
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title("Quantity / Price")
    st.pyplot(fig)

col_right.write("This is a super graph")