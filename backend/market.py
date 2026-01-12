import yfinance as yf
import time
from typing import Dict, List

class MarketSimulator:
    def __init__(self):
        # Map internal symbols to yfinance symbols
        self.symbol_map = {
            "AAPL": "AAPL",
            "GOOGL": "GOOGL",
            "BTC": "BTC-USD",
            "ETH": "ETH-USD",
        }
        self.assets = {symbol: {"price": 0.0} for symbol in self.symbol_map}
        self.history: Dict[str, List[float]] = {symbol: [] for symbol in self.symbol_map}
        
        # Initial fetch to populate data
        self.update_prices()

    def update_prices(self):
        for internal_symbol, yf_symbol in self.symbol_map.items():
            try:
                ticker = yf.Ticker(yf_symbol)
                # Using fast_info['lastPrice'] for speed
                price = ticker.fast_info['lastPrice']
                
                # If fast_info fails or returns 0, try history as fallback
                if price is None or price <= 0:
                    hist = ticker.history(period="1d")
                    if not hist.empty:
                        price = hist['Close'].iloc[-1]
                
                if price:
                    self.assets[internal_symbol]["price"] = float(price)
                    self.history[internal_symbol].append(float(price))
                    
                    if len(self.history[internal_symbol]) > 100:
                        self.history[internal_symbol].pop(0)
            except Exception as e:
                print(f"Error updating price for {internal_symbol} ({yf_symbol}): {e}")

    def get_prices(self) -> Dict[str, float]:
        return {symbol: data["price"] for symbol, data in self.assets.items()}

    def get_history(self) -> Dict[str, List[float]]:
        return self.history

market_sim = MarketSimulator()
