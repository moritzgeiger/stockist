import streamlit as st
import os
import pandas as pd
from io import BytesIO
import datetime as dt

# own modules
from main import do_all, do_one, do_pdf
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
    file_csv = st.file_uploader("Upload a CSV file.\nMust contain column 'WKN'",
                                type=([".csv"]))
    if file_csv:
        sepa = st.selectbox('Separator', options=[';', ','])
        date_start = st.date_input('Date start',
                             max_value=dt.datetime.now()-dt.timedelta(days=1),
                             key='CSV_1',
                             value=dt.datetime.now()-dt.timedelta(days=1))
        date_end = st.date_input('Date end',
                      max_value=dt.datetime.now()-dt.timedelta(days=1),
                      min_value=date_start,
                      key='CSV_2',
                      value=dt.datetime.now()-dt.timedelta(days=1))
        interval = st.selectbox('Interval (Beta)',
                                options=['Please select', '1m','2m','5m','15m','30m','60m','90m','1h','1d','5d','1wk','1mo','3mo'],
                                )
        df = pd.read_csv(BytesIO(file_csv.getvalue()),
                        encoding='utf8',
                        error_bad_lines=False,
                        sep=sepa)
        st.write(df)

        if st.button('Get Data'):
            st.write('Your upload is being processed.')
            st.markdown('<font color="red">Please note that a maximum result of 1000 rows will be computed.</font>',
                        unsafe_allow_html=True)

            df_fin = do_all(df=df, date_start=date_start, date_end=date_end, interval=interval)

            st.markdown(get_table_download_link(df_fin, sepa), unsafe_allow_html=True)

            try:
                missing = [x for x in set(df.WKN) if x not in set(df_fin.WKN)]
                if missing:
                    st.write(f"The following WKNs couldn't be found:")
                    st.write(pd.DataFrame(missing))

            except:
                pass

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


######## PDF PARSING ########
with st.beta_expander("PDF Reader (Beta)"):
    files = st.file_uploader("Upload one ZIP file containing pdfs or a set of PDF files to read.",
                                type=([".pdf", ".zip"]),
                                accept_multiple_files=True)
    if files:
        st.write(files[0].name)
        if st.button('Parse Data'):
            df = do_pdf(files)
            st.write(df)

            st.markdown(get_table_download_link(df, sepa=';'), unsafe_allow_html=True)



############# SIDEBAR ################
st.sidebar.title("Credits")
st.sidebar.write("App made by Moritz Geiger. Visit my GitHub <a href='https://github.com/moritzgeiger/' target='blank'>here</a>.",
        unsafe_allow_html=True)
st.sidebar.write(
    "Source code and notebook for this app can be found <a href='https://github.com/moritzgeiger/stockist' target='blank'>here</a>.",
    unsafe_allow_html=True)
st.sidebar.markdown('**Note**\n\nComputation times can be slow due to reduced performance by Heroku.')
