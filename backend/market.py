import random
import time
from typing import Dict, List

class MarketSimulator:
    def __init__(self):
        self.assets = {
            "AAPL": {"price": 180.0, "volatility": 0.002, "drift": 0.0001},
            "GOOGL": {"price": 140.0, "volatility": 0.003, "drift": 0.0001},
            "BTC": {"price": 45000.0, "volatility": 0.01, "drift": 0.0002},
            "ETH": {"price": 2500.0, "volatility": 0.015, "drift": 0.0002},
        }
        self.history: Dict[str, List[float]] = {symbol: [data["price"]] for symbol, data in self.assets.items()}

    def update_prices(self):
        for symbol, data in self.assets.items():
            change_percent = random.normalvariate(data["drift"], data["volatility"])
            data["price"] *= (1 + change_percent)
            self.history[symbol].append(data["price"])
            if len(self.history[symbol]) > 100:
                self.history[symbol].pop(0)

    def get_prices(self) -> Dict[str, float]:
        return {symbol: data["price"] for symbol, data in self.assets.items()}

    def get_history(self) -> Dict[str, List[float]]:
        return self.history

market_sim = MarketSimulator()
