import streamlit as st
import os
import pandas as pd
from io import BytesIO
import datetime as dt

# own methods
from main import do_all, do_one
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

####### FILE UPLOAD #######
with st.beta_expander("CSV File Upload"):
    file_csv = st.file_uploader("Upload a CSV file.\nMust contain columns 'WKN'",
                                type=([".csv"]))
    if file_csv:
        sepa = st.selectbox('Separator', options=[';', ','])
        date = st.date_input('Date',
                             max_value=dt.datetime.now()-dt.timedelta(days=1),
                             key='CSV',
                             value=dt.datetime.now()-dt.timedelta(days=1))
        df = pd.read_csv(BytesIO(file_csv.getvalue()),
                        encoding='utf8',
                        error_bad_lines=False,
                        sep=sepa)
        st.write(df)

        if st.button('Get Data'):
            st.write('Your upload is being processed.')

            df_fin = do_all(df=df, date=date)

            st.markdown(get_table_download_link(df_fin, sepa), unsafe_allow_html=True)

####### SINGLE CHECK #######
with st.beta_expander("Check one equity"):
    identifier = st.selectbox('Identifier', options=['WKN', 'ticker'])
    date_one = st.date_input('Date',
                             max_value=dt.datetime.now()-dt.timedelta(days=1),
                             key='single',
                             value=dt.datetime.now()-dt.timedelta(days=1))
    search = st.text_input('Type identifier here')
    if search:
        st.write('Looking for info.')
        df_one = do_one(search=search, date=date_one, ident=identifier)
        st.write(f'Your results are here!')
        st.write(df_one)


############# SIDEBAR ################
st.sidebar.title("Credits")
st.sidebar.write("App made by Moritz Geiger. Visit my GitHub <a href='https://github.com/moritzgeiger/' target='blank'>here</a>.",
        unsafe_allow_html=True)
st.sidebar.write(
    "Source code and notebook for this app can be found <a href='https://github.com/moritzgeiger/stockist' target='blank'>here</a>.",
    unsafe_allow_html=True)
st.sidebar.markdown('**Note**\n\nComputation times can be slow due to reduced performance by Heroku.')
