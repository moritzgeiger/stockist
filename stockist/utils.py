import pandas as pd
import numpy as np
import requests
from yahoo_fin.stock_info import get_data
import yfinance as yf
import itertools
import os
import matplotlib.pyplot as plt
import seaborn as sns





def translate_wkn(df, figi_key=None):
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



    # DF handle (drop duplicates to avoid double requests)
    df_new = df.copy().drop_duplicates(subset=['WKN', 'Land']).dropna(subset=['WKN'])

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

    for jobs in sjobs:
        r = requests.post(url=openfigi_url, headers=openfigi_headers,
                    json=jobs).json()

        for i in range(len(r)):
            try:
                responses.append(r[i].get('data')[0].get('ticker'))
            except:
                responses.append('n/a') # fill the list to match the df

    df_new['ticker'] = responses

    return df_new.reset_index(drop=True)


def history_data(df):
    print('history_data was called')
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
    df_concat = yf.download(tickers=stickers,
                          period='1y',
                          interval='1d',
                          show_errors=True,
                           progress=True)

    # only get the closing price and remove double indexing
    new = df_concat.loc[:,('Close', slice(None))]
    new.columns = [x[1] for x in new.columns] # remove duplex columns

    # transform and add old cols
    df_trans = new.T.rename_axis('ticker')#.reset_index()
    df_out = df_trans.merge(df_new[['WKN', 'ticker']], left_index=True, right_on='ticker')
    df_out = df_out.set_index(['WKN', 'ticker'])

    # set datetime
    df_out.columns = pd.to_datetime(df_out.columns)

    return df_out


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
