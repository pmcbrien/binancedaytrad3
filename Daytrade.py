import ccxt
import pandas as pd
import time

# Initialize the exchange
exchange = ccxt.binance({
    'rateLimit': 1000,
    'enableRateLimit': True,
    'options': {'adjustForTimeDifference': True},
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET_KEY',
})

# Set up the moving average window
MA_WINDOW = 10

# Set up the news feed API
NEWS_API_KEY = 'YOUR_NEWS_API_KEY'
NEWS_API_ENDPOINT = 'https://newsapi.org/v2/everything?q=cryptocurrency&apiKey=' + NEWS_API_KEY

# Define a function to get the latest news
def get_news():
    response = requests.get(NEWS_API_ENDPOINT)
    data = response.json()
    return data['articles']

# Define a function to calculate the moving average
def calculate_ma(closes):
    ma = closes.rolling(window=MA_WINDOW).mean()
    return ma.iloc[-1]

# Set up the initial variables
last_ma = None
last_price = None

while True:
    try:
        # Get the latest ticker data
        ticker = exchange.fetch_ticker('BTC/USDT')
        price = ticker['last']

        # Calculate the moving average
        closes = pd.DataFrame(exchange.fetch_ohlcv('BTC/USDT', timeframe='1h'), columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        closes['timestamp'] = pd.to_datetime(closes['timestamp'], unit='ms')
        closes.set_index('timestamp', inplace=True)
        ma = calculate_ma(closes['close'])

        # Check if there is a new trend
        if last_ma is not None and last_price is not None:
            if price > last_price and ma > last_ma:
                # Buy signal
                amount = 100 / price  # Buy 100 USDT worth of BTC
                exchange.create_market_buy_order('BTC/USDT', amount)
            elif price < last_price and ma < last_ma:
                # Sell signal
                amount = 100 / price  # Sell 100 USDT worth of BTC
                exchange.create_market_sell_order('BTC/USDT', amount)

        # Update the last price and moving average
        last_price = price
        last_ma = ma

        # Get the latest news and print them
        news = get_news()
        print('Latest news:')
        for article in news:
            print(article['title'])

        # Wait for 1 hour before checking again
        time.sleep(3600)
        
    except Exception as e:
        print(e)
