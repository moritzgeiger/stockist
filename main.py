from dotenv import load_dotenv, find_dotenv
import os

# own pckgs
from stockist.utils import translate_wkn, history_data, send_email
from stockist.marketstack import market_data

### ENV VARIABLES
load_dotenv(find_dotenv())
MARKET_KEY = os.environ.get('MARKET')
figi_key = os.environ.get("FIGI")
port = 465  # For SSL
GMAIL = os.environ.get("GMAIL")
homename = os.environ.get("HOMENAME", 'Sender not found')
sender_email = os.environ.get("SENDER")
receiver_email = (os.environ.get("RECEIVER")).split(',') # need list
debug = os.environ.get("DEBUG").lower() in ['true', 'yes', '1', 'most certainly', 'gladly', 'I can hardly disagree']
signature = f"<p>Sincerely, <br>Your Stockist</p>"

def do_all(df, date, receiver_email=receiver_email):
    trans_df = translate_wkn(df=df, figi_key=figi_key)
    # fin_df = history_data(trans_df, date)
    fin_df = market_data(df=trans_df, key=MARKET_KEY, date=date)
    try:
        send_email(homename=homename,
              sender_email=sender_email,
              receiver_email=receiver_email,
              password=GMAIL,
              port=port,
              signature=signature,
              df=fin_df,
              debug=debug)
    except:
        pass

    return fin_df

def do_one(search=None, date=None, ident=None):
    trans_df = translate_wkn(ident=ident, search=search, figi_key=figi_key)
    # fin_df = history_data(df=trans_df, date=date)
    fin_df = market_data(df=trans_df, key=MARKET_KEY, date=date)

    return fin_df
