import pandas as pd
import numpy as np
import requests
from yahoo_fin.stock_info import get_data
import yfinance as yf
import itertools
import os
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
import tempfile
import tempfile
from os.path import basename
import smtplib
import ssl
import datetime as dt
import time


def translate_wkn(df=None, search=None, ident=None, figi_key=None):
    print('translate_wkn was called.')
    '''
    translates the wkn to the intl stock ticker code.
    uses openfigi api to get the info
    takes in a df with a "WKN" and "Land" column and figi api key.
    removes duplicates from df.
    if no key provided only 10 requests (rows) can be processed. Else 100 can be processed at a time.
    _____________
    returns enriched df by "ticker" code.
    '''
    # BASE
    openfigi_url = 'https://api.openfigi.com/v1/mapping'
    openfigi_headers = {'Content-Type': 'text/json'}

    if ident == 'ticker':
        return pd.DataFrame({'ticker':[search]})

    if ident == 'WKN':
        # implies that we are looking for only one entry
        df_new = pd.DataFrame({'WKN':[search]})

    if not ident:
        # DF handle (drop duplicates to avoid double requests)
        df_new = df.copy().drop_duplicates(subset=['WKN']).dropna(subset=['WKN'])

    # INIT JOBS
    jobs = []
    for i, row in df_new.iterrows():
        jobs.append({"idType":"ID_WERTPAPIER","idValue":str(row.WKN)}) # don't define country

    # slice jobs into junks of 100 or 10 depending on API key
    if figi_key:
        openfigi_headers['X-OPENFIGI-APIKEY'] = figi_key
        sjobs = [jobs[i:i + 100] for i in range(0, len(jobs), 100)] # very cool slicer!

    else:
        sjobs = [jobs[i:i + 10] for i in range(0, len(jobs), 10)]

    # REQUEST
    responses = []

    for i, jobs in enumerate(sjobs):
        print(f'\n\nhandling job batch {i} of {len(jobs)}')
        print(f'Len job: {len(jobs)}')
        r = requests.post(url=openfigi_url, headers=openfigi_headers,
                    json=jobs)

        if r.status_code == 200:
            re = r.json()
            for n in range(len(re)):
                try:
                    responses.append(re[n].get('data')[0].get('ticker'))
                except:
                    print(f'Error for row {n}.\n{re[n].get("error")}')
                    responses.append(np.nan) # fill the list to match the df
        else:
            print(f'Couldnt reach figi. Error {r.content}')
            _ = [responses.append(np.nan) for x in range(len(jobs))]

        if not figi_key:
            time.sleep(10)


    df_new['ticker'] = responses

    return df_new.reset_index(drop=True)


def history_data(df=None, date=None):
    print(f'history_data was called for the date: \n{date}')
    '''
    searches for historical stock values for designated stocks with the help of yfinance (yahoo).
    takes in a df which contains the column 'ticker'
    ___________
    returns a df with the columns ticker, wkn and the historical values.
    '''

    # HANDLE DF
    df_new = df.copy().dropna()
    tickers = [x.split()[0] for x in df_new.ticker] # some tickers contain spaces
    stickers = ' '.join(tickers) # yf requires space separated string

    # GET DATA
    if len(stickers) > 0:
        selected_date = date.strftime('%Y-%m-%d')
        end =(date + dt.timedelta(days=1)).strftime('%Y-%m-%d')
        df_concat = yf.download(tickers=stickers,
                            start=end,
                            end=end,
                            # period='1d',
                            # interval='1d',
                            show_errors=True,
                            progress=True)

    else:
        print(stickers)
        return f'Could not find data from \n{str(df.WKN[0])}.'


    if len(df_new) > 1: # implies that there was a bulk search
        # only get the closing price and remove double indexing
        new = df_concat.loc[:,('Close', slice(None))]
        new.columns = [x[1] for x in new.columns] # remove duplex columns

        # transform and add old cols
        df_trans = new.T.rename_axis('ticker')#.reset_index()
        df_out = df_trans.merge(df_new[['WKN', 'ticker']], left_index=True, right_on='ticker')
        df_out = df_out.set_index(['WKN', 'ticker'])

        # set datetime
        df_out.columns = pd.to_datetime(df_out.columns)

    else:
        df_out = df_concat
        df_out.columns = pd.MultiIndex.from_product([df_new.ticker, df_out.columns])

    return df_out

def get_table_download_link(df, sepa):
    print('get_table_download_link was called')
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    if sepa == ';':
        comma = ','
    else:
        comma = '.'

    csv = df.to_csv(sep=sepa,
                    decimal=comma,
                    index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="results.csv">Download results here!</a>'
    return href


def send_email(homename, sender_email, receiver_email, password, port, signature, df, debug):
    """
    Compiles an Email with the email.mime library and sends it through a Google Mail smtp server.
    Takes in variables for the mail content [homename (str), lvl_results (dict), signature (str)]
    and settings to send the email [sender_email, receiver_email, password, port]
    There is a debug argument to test the email function despite a trigger isn't reached.
    """
    print('send email was called.')
    # check, if there is alert level 2 was reached in the checkpoints
    if debug:#or an email was received:
        print('data was requested via mail')
        # init msg
        init = "<p>***Stock prices request***, \
                <br><br>Please find requested historical stock prices attached.<br><br></p>"

        # Record the MIME types of text/html.
        text = MIMEMultipart('alternative')
        text.attach(MIMEText(init + signature, 'html', _charset="utf-8"))

        # compile email msg
        now = dt.datetime.now().strftime("%y-%m-%d %H:%M")
        msg = MIMEMultipart('mixed')

        # avoid automized email ruling by subject when testing
        if debug:
            msg['Subject'] = f"-TESTRUN- Stock prices {now}"
        else:
            msg['Subject'] = f"-RESULTS- Stock Prices - {now}"
        msg['From'] = f'{homename} <{sender_email}>'
        msg['To'] = ','.join(receiver_email)

        # add all parts to msg
        msg.attach(text)

        # create tables as .csv from temp files
        tempdir = tempfile.gettempdir()
        filename = f'{tempdir}/results.csv'

        # filter and save csv tables
        save_file = df.to_csv(filename)

        with open(filename, "rb") as fil:
            part = MIMEApplication(
                    fil.read(),
                    Name=basename(filename))

            part['Content-Disposition'] = f'attachment; filename={basename(filename)}'
            msg.attach(part)

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())

        print(f'successfully sent email to {receiver_email}')
    else:
        print(f'There was no request via email.')
        print('Exit function without sending mail.')
