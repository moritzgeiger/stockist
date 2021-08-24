import pandas as pd
import numpy as np
import datetime as dt
import requests

def market_data(df=None, key=None, date_start=None, date_end=None):
    print(f'market_data was called for the dates: \n{date_start} - {date_end}')
    '''
    searches for historical stock values for designated stocks with the help of the marketstack API.
    takes in:
    df: Pandas df which contains the column 'ticker' (max 100 rows)
    key: The API key for marketstack as string
    date_start and date_end: datetime date to be requested
    ___________
    returns a df with the columns ticker, wkn and the historical values for the requested dates.
    '''
    date_start_str = date_start.strftime('%Y-%m-%d')
    date_end_str = date_end.strftime('%Y-%m-%d')
    BASE = f'http://api.marketstack.com/v1/eod'


    # HANDLE DF
    df_copy = df.copy().dropna()
    tickers = [x.split()[0] for x in df_copy.ticker] # some tickers contain spaces
    stickers = ','.join(tickers) # marketstack requires comma separated tickers

    # GET DATA
    if len(stickers) > 0:
        params = {
                  'access_key': key,
                  'date_from':date_start_str,
                  'date_to':date_end_str,
                  'symbols':stickers,
                  'limit': '1000'
              }
        r = requests.get(BASE, params=params)
        if r.status_code == 200 and r.json().get('data', None):
            df_new = pd.DataFrame(r.json().get('data'))
        else:
            print(f'No data for entered values. Error {r.content}')
            return f'Could not find data from {date_start_str} to {date_end_str} \n\n{r.content}.'
    else:
        # if no tickers are available in initial df
        return f'No valid ticker was provided for \n{str(df.WKN[0])}.'


    if len(df_new) > 1: # implies that there was a bulk search
        # transform and add old cols
        df_new = df_copy.merge(df_new,
                               left_on='ticker',
                               right_on='symbol',
                               how='left', )
        df_out = df_new[['ticker', 'WKN', 'close', 'date']]

        # all requests come from NYSE
        df_out.loc[:,'country'] = 'US'

        # set datetime
        df_out.date = pd.to_datetime(df_out.date)

    else:
        df_out = df_new[['symbol', 'close', 'date']]
        df_out.loc[:,'country'] = 'US'

    return df_out
