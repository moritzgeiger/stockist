import streamlit as st
import os
import pandas as pd
from io import BytesIO

# own methods
from main import do_all
from stockist.utils import get_table_download_link
########## PAGE CONFIG ##############
st.set_page_config(
    page_title="Stock Price Finder",
    page_icon="💸",
    layout="centered",
    initial_sidebar_state="collapsed")

####### INDEX PAGE ########
st.title('Welcome to the Stock Price Finder')
# filename = st.text_input('Please select a file:')

file_csv = st.file_uploader("Upload a CSV file.\nMust contain columns 'WKN' and 'Land'", type=([".csv"]))
if file_csv:
    df = pd.read_csv(BytesIO(file_csv.getvalue()),
                     encoding='utf8',
                     error_bad_lines=False,
                     sep=';')
    st.write(df)

    if st.button('Get Data'):
        st.write('Your upload is being processed.')

        df_fin = do_all(df)

        st.markdown(get_table_download_link(df_fin), unsafe_allow_html=True)




############# SIDEBAR ################
st.sidebar.title("Credits")
st.sidebar.write("App made by Moritz Geiger. Visit my GitHub <a href='https://github.com/moritzgeiger/' target='blank'>here</a>.",
        unsafe_allow_html=True)
st.sidebar.write(
    "Source code and notebook for this app can be found <a href='https://github.com/moritzgeiger/stockist' target='blank'>here</a>.",
    unsafe_allow_html=True)
st.sidebar.markdown('**Note**\n\nComputation times can be slow due to reduced performance by Heroku.')
