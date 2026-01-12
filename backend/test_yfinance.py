import yfinance as yf

symbols = ["AAPL", "GOOGL", "BTC-USD", "ETH-USD"]

for symbol in symbols:
    print(f"Fetching {symbol}...")
    ticker = yf.Ticker(symbol)
    # Use fast_info for more efficient price fetching
    try:
        price = ticker.fast_info['lastPrice']
        print(f"{symbol}: {price}")
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        # Fallback to history if fast_info fails
        data = ticker.history(period="1d")
        if not data.empty:
            print(f"{symbol} (History): {data['Close'].iloc[-1]}")
        else:
            print(f"{symbol}: No data found")
