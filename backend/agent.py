from typing import Dict, List, Optional
import time
import market

class TradingAgent:
    def __init__(self, initial_capital: float = 100000.0):
        self.capital = initial_capital
        self.portfolio: Dict[str, float] = {symbol: 0.0 for symbol in market.market_sim.assets.keys()}
        self.trade_history: List[Dict] = []
        self.capital_history: List[Dict] = [{"time": time.time(), "value": initial_capital}]

    def make_decisions(self):
        prices = market.market_sim.get_prices()
        history = market.market_sim.get_history()
        
        for symbol, current_price in prices.items():
            if len(history[symbol]) < 10:
                continue
            
            # Simple Logic: Mean Reversion / Trend following
            recent_prices = history[symbol][-10:]
            avg_price = sum(recent_prices) / len(recent_prices)
            
            # Decision threshold: 0.02% deviation for demonstration purposes
            diff_pct = (current_price - avg_price) / avg_price
            # print(f"Debug: {symbol} Price: {current_price}, Avg: {avg_price:.2f}, Diff: {diff_pct:.4%}")
            
            if diff_pct < -0.0002:
                # Buy
                reason = f"Price ({current_price:.2f}) is {abs(diff_pct):.2%} below 10-period average ({avg_price:.2f}). Mean reversion strategy triggers a BUY signal."
                print(f"Signal: BUY {symbol} at {current_price} (Avg: {avg_price}, Diff: {diff_pct:.4%})")
                self.buy(symbol, current_price, reason)
            elif diff_pct > 0.0002:
                # Sell
                reason = f"Price ({current_price:.2f}) is {diff_pct:.2%} above 10-period average ({avg_price:.2f}). Mean reversion strategy triggers a SELL signal."
                print(f"Signal: SELL {symbol} at {current_price} (Avg: {avg_price}, Diff: {diff_pct:.4%})")
                self.sell(symbol, current_price, reason)
        
        self.update_capital_history(prices)

    def buy(self, symbol: str, price: float, reason: str):
        # Buy with 10% of available capital
        amount_to_spend = self.capital * 0.1
        if amount_to_spend < 100: # Minimum trade
            return
            
        quantity = amount_to_spend / price
        self.capital -= amount_to_spend
        self.portfolio[symbol] += quantity
        self.trade_history.append({
            "id": len(self.trade_history) + 1,
            "time": time.time(),
            "symbol": symbol,
            "type": "BUY",
            "quantity": quantity,
            "price": price,
            "total": amount_to_spend,
            "reason": reason
        })

    def sell(self, symbol: str, price: float, reason: str):
        quantity = self.portfolio[symbol]
        if quantity <= 0:
            return
            
        # Sell half of holdings
        amount_to_sell = quantity * 0.5
        revenue = amount_to_sell * price
        self.capital += revenue
        self.portfolio[symbol] -= amount_to_sell
        self.trade_history.append({
            "id": len(self.trade_history) + 1,
            "time": time.time(),
            "symbol": symbol,
            "type": "SELL",
            "quantity": amount_to_sell,
            "price": price,
            "total": revenue,
            "reason": reason
        })

    def update_capital_history(self, prices: Dict[str, float]):
        total_value = self.capital
        for symbol, quantity in self.portfolio.items():
            total_value += quantity * prices[symbol]
        
        self.capital_history.append({
            "time": time.time(),
            "value": total_value
        })
        if len(self.capital_history) > 100:
            self.capital_history.pop(0)

    def get_status(self):
        prices = market.market_sim.get_prices()
        total_value = self.capital
        for symbol, quantity in self.portfolio.items():
            total_value += quantity * prices[symbol]
            
        return {
            "capital": self.capital,
            "portfolio": self.portfolio,
            "total_value": total_value,
            "trade_history": self.trade_history[-20:], # Last 20 trades
            "capital_history": self.capital_history
        }

trading_agent = TradingAgent()
