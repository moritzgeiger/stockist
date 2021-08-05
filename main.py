from dotenv import load_dotenv, find_dotenv
import os

# own pckgs
from stockist.utils import translate_wkn, history_data, send_email

### ENV VARIABLES
load_dotenv(find_dotenv())
figi_key = os.environ.get("FIGI")
port = 465  # For SSL
GMAIL = os.environ.get("GMAIL")
homename = os.environ.get("HOMENAME", 'Sender not found')
sender_email = os.environ.get("SENDER")
receiver_email = (os.environ.get("RECEIVER")).split(',') # need list
debug = os.environ.get("DEBUG").lower() in ['true', 'yes', '1', 'most certainly', 'gladly', 'I can hardly disagree']
signature = f"<p>Sincerely, <br>Your Stockist</p>"

def do_all(df, receiver_email=receiver_email):
    trans_df = translate_wkn(df, figi_key=figi_key)
    fin_df = history_data(trans_df)

    send_email(homename=homename,
              sender_email=sender_email,
              receiver_email=receiver_email,
              password=GMAIL,
              port=port,
              signature=signature,
              df=fin_df,
              debug=debug)
    return fin_df
