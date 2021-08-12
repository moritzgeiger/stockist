import pandas as pd
import numpy as np
import datetime as dt
import requests

def market_data(df=None, key=None, date=None):
    print(f'market_data was called for the date: \n{date}')
    '''
    searches for historical stock values for designated stocks with the help of the marketstack API.
    takes in:
    df: Pandas df which contains the column 'ticker' (max 100 rows)
    key: The API key for marketstack as string
    date: datetime date to be requested
    ___________
    returns a df with the columns ticker, wkn and the historical values for the requested dates.
    '''
    datestr = date.strftime('%Y-%m-%d')
    BASE = f'http://api.marketstack.com/v1/eod/{datestr}'

    # HANDLE DF
    df_copy = df.copy().dropna()
    tickers = [x.split()[0] for x in df_copy.ticker] # some tickers contain spaces
    stickers = ','.join(tickers) # yf requires space separated string

    # GET DATA
    if len(stickers) > 0:
        params = {
                  'access_key': key,
                  'symbols':stickers,
                  'limit': '500'
              }
        r = requests.get(BASE, params=params)
        if r.status_code == 200 and r.json().get('data', None):
            df_new = pd.DataFrame(r.json().get('data'))
        else:
            print(f'No data for entered values. Error {r.content}')
            return f'Could not find data from {datestr} \n\n{r.content}.'
    else:
        # if no tickers are available in initial df
        return f'No valid ticker was provided for \n{str(df.WKN[0])}.'


    if len(df_new) > 1: # implies that there was a bulk search
        # transform and add old cols
        df_new = df_copy.merge(df_new,
                               left_on='ticker',
                               right_on='symbol',
                               how='left')
        df_out = df_new[['symbol', 'WKN', 'close', 'date']]

        # set datetime
        df_out.date = pd.to_datetime(df_out.date)

    else:
        df_out = df_new[['symbol', 'close', 'date']]

    return df_out
