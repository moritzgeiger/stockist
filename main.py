from dotenv import load_dotenv, find_dotenv
import os

# own pckgs
from stockist.utils import translate_wkn, history_data, send_email

### ENV VARIABLES
load_dotenv(find_dotenv())
figi_key = os.environ.get("FIGI")

load_dotenv(find_dotenv())
port = 465  # For SSL
GMAIL = os.environ.get("GMAIL")
homename = os.environ.get("HOMENAME", 'Sender not found')
sender_email = os.environ.get("SENDER")
receiver_email = (os.environ.get("RECEIVER")).split(',') # need list
debug = os.environ.get("DEBUG").lower() in ['true', 'yes', '1', 'most certainly', 'gladly', 'I can hardly disagree']
signature = f"<p>Sincerely, <br>Your Stockist</p>"


