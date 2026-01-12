import yfinance as yf
import time
from typing import Dict, List
import numpy as np

class MarketSimulator:
    def __init__(self):
        # Map internal symbols to yfinance symbols
        # Curated list of 100 volatile global securities (Tech, Crypto, Indices, ETFs)
        self.symbol_map = {
            # US Tech & Growth (35)
            "AAPL": "AAPL", "GOOGL": "GOOGL", "MSFT": "MSFT", "AMZN": "AMZN", "TSLA": "TSLA",
            "NVDA": "NVDA", "META": "META", "NFLX": "NFLX", "AMD": "AMD", "INTC": "INTC",
            "PYPL": "PYPL", "SHOP": "SHOP", "SNOW": "SNOW", "COIN": "COIN", "PLTR": "PLTR",
            "MSTR": "MSTR", "ROKU": "ROKU", "TDOC": "TDOC", "ZM": "ZM", "CRM": "CRM",
            "ADBE": "ADBE", "TEAM": "TEAM", "OKTA": "OKTA", "CRWD": "CRWD", "DDOG": "DDOG",
            "NET": "NET", "SE": "SE", "MELI": "MELI", "BABA": "BABA", "JD": "JD",
            "PDD": "PDD", "NIO": "NIO", "LI": "LI", "XPEV": "XPEV", "HOOD": "HOOD",
            # Crypto (20)
            "BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD", "ADA": "ADA-USD", "XRP": "XRP-USD",
            "DOT": "DOT-USD", "DOGE": "DOGE-USD", "SHIB": "SHIB-USD", "AVAX": "AVAX-USD", "LINK": "LINK-USD",
            "LTC": "LTC-USD", "NEAR": "NEAR-USD", "ALGO": "ALGO-USD", "ATOM": "ATOM-USD", "OP": "OP-USD",
            "ARB": "ARB-USD", "FIL": "FIL-USD", "ETC": "ETC-USD", "BCH": "BCH-USD", "VET": "VET-USD",
            # Indices & Global (20)
            "NIKKEI": "^N225", "HANGSENG": "^HSI", "ASX": "^AXJO", "STOXX50": "^STOXX50E", "FTSE": "^FTSE",
            "DAX": "^GDAXI", "CAC40": "^FCHI", "IBEX": "^IBEX", "AORD": "^AORD", "SENSEX": "^BSESN",
            "JKSE": "^JKSE", "KOSPI": "^KS11", "STI": "^STI", "KLSE": "^KLSE", "SET": "^SET.BK",
            "NZ50": "^NZ50", "SP500": "^GSPC", "NASDAQ": "^IXIC", "DOW": "^DJI", "VIX": "^VIX",
            # Volatile ETFs & Sectors (25)
            "XLE": "XLE", "GDX": "GDX", "GDXJ": "GDXJ", "KRE": "KRE", "XBI": "XBI",
            "LABU": "LABU", "LABD": "LABD", "GUSH": "GUSH", "DRIP": "DRIP", "SQQQ": "SQQQ",
            "TQQQ": "TQQQ", "SOXL": "SOXL", "SOXS": "SOXS", "QLD": "QLD", "SPXU": "SPXU",
            "UVXY": "UVXY", "SVXY": "SVXY", "BOIL": "BOIL", "KOLD": "KOLD", "UNG": "UNG",
            "CGC": "CGC", "ACB": "ACB", "TLRY": "TLRY", "TLT": "TLT", "EEM": "EEM"
        }
        
        self.assets = {symbol: {"price": 0.0} for symbol in self.symbol_map}
        self.history: Dict[str, List[float]] = {symbol: [] for symbol in self.symbol_map}
        
        # Initial pre-population of history
        self.pre_populate_history()
        
        # Initial fetch to populate current data
        self.update_prices()

    def pre_populate_history(self):
        print(f"Pre-populating market history for {len(self.symbol_map)} assets...")
        tickers = list(self.symbol_map.values())
        try:
            # Batch fetch 1-minute data
            data = yf.download(tickers, period="1d", interval="1m", group_by='ticker', progress=False)
            
            for internal_symbol, yf_symbol in self.symbol_map.items():
                if yf_symbol in data.columns.levels[0]:
                    ticker_data = data[yf_symbol]
                    if not ticker_data.empty:
                        prices = ticker_data['Close'].dropna().tail(100).tolist()
                        if prices:
                            self.history[internal_symbol] = [float(p) for p in prices]
                            self.assets[internal_symbol]["price"] = float(prices[-1])
            print("Pre-population complete.")
        except Exception as e:
            print(f"Error in batch pre-population: {e}")

    def update_prices(self):
        tickers = list(self.symbol_map.values())
        try:
            # Batch fetch current prices (using 1d period to get latest)
            data = yf.download(tickers, period="1d", group_by='ticker', progress=False)
            
            for internal_symbol, yf_symbol in self.symbol_map.items():
                try:
                    if yf_symbol in data.columns.levels[0]:
                        ticker_data = data[yf_symbol]
                        if not ticker_data.empty:
                            price = ticker_data['Close'].iloc[-1]
                            if price and not np.isnan(price):
                                self.assets[internal_symbol]["price"] = float(price)
                                self.history[internal_symbol].append(float(price))
                                if len(self.history[internal_symbol]) > 200:
                                    self.history[internal_symbol].pop(0)
                except Exception as e:
                    continue
        except Exception as e:
            print(f"Error in batch update: {e}")

    def get_prices(self) -> Dict[str, float]:
        return {symbol: data["price"] for symbol, data in self.assets.items()}

    def get_history(self) -> Dict[str, List[float]]:
        return self.history

market_sim = MarketSimulator()
