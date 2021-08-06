# The Stock Price Finder
This app helps you to get historical stock prices of the last year given a CSV input file including the German WKN (Wertpapierkennnummer) of the security.

# Stack
I used the [OpenFIGI API](https://www.openfigi.com/) (usable with and without an API Key) to translate the ```WKN``` into the international ```ticker base``` and the [yfinance package](/ranaroussi/yfinance) from  Ran Aroussi to fetch the stock prices.

The app works with a [Streamlit](https://streamlit.io/) Framework and is deployed on [Heroku](https://www.heroku.com)

# Production
Visit the App on [https://stockomat.herokuapp.com/](https://stockomat.herokuapp.com/). Feel free to leave comments.
