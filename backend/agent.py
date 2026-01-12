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
        
        # Calculate total portfolio value for allocation decisions
        total_val = self.get_status()["total_value"]
        
        for symbol, current_price in prices.items():
            if len(history[symbol]) < 30:
                continue
            
            prices_list = history[symbol]
            current_holdings = self.portfolio.get(symbol, 0)
            
            # --- RISK MANAGEMENT: Take Profit / Stop Loss ---
            if current_holdings > 0:
                # Simple tracking: comparing to last trade price if available
                # For this demo, we'll use the deviation from the 20-period SMA as a proxy for 'overextended'
                sma_20 = sum(prices_list[-20:]) / 20
                dev = (current_price - sma_20) / sma_20
                if dev > 0.02: # 2% profit target relative to SMA
                    self.sell(symbol, current_price, f"Take Profit: Price is 2% above 20-period SMA.")
                    continue
                elif dev < -0.01: # 1% stop loss relative to SMA
                    self.sell(symbol, current_price, f"Stop Loss: Price dropped 1% below 20-period SMA.")
                    continue

            # --- STRATEGY 1: Mean Reversion (Tightened to 0.5%) ---
            avg_price = sum(prices_list[-10:]) / 10
            diff_pct = (current_price - avg_price) / avg_price
            if diff_pct < -0.005: # 0.5% deviation
                self.buy(symbol, current_price, f"High Conviction Mean Reversion: Price is {abs(diff_pct):.2%} below 10-period average.")
                continue
            elif diff_pct > 0.005:
                self.sell(symbol, current_price, f"High Conviction Mean Reversion: Price is {diff_pct:.2%} above 10-period average.")
                continue

            # --- STRATEGY 2: SMA Crossover (5/20) - Requires 0.1% separation ---
            sma_fast = sum(prices_list[-5:]) / 5
            sma_slow = sum(prices_list[-20:]) / 20
            if sma_fast > sma_slow * 1.001: # 0.1% buffer for conviction
                self.buy(symbol, current_price, f"SMA Crossover: Fast SMA(5) is >0.1% above Slow SMA(20).")
                continue
            elif sma_fast < sma_slow * 0.999:
                self.sell(symbol, current_price, f"SMA Crossover: Fast SMA(5) is >0.1% below Slow SMA(20).")
                continue

            # --- STRATEGY 3: RSI (Tightened to 20/80) ---
            rsi = self.calculate_rsi(prices_list, 14)
            if rsi < 20: # Extreme oversold
                self.buy(symbol, current_price, f"Extreme RSI: Asset extremely oversold at RSI {rsi:.2f}.")
                continue
            elif rsi > 80: # Extreme overbought
                self.sell(symbol, current_price, f"Extreme RSI: Asset extremely overbought at RSI {rsi:.2f}.")
                continue

            # --- STRATEGY 6: Momentum (Breakout 0.1%) ---
            high_20 = max(prices_list[-21:-1])
            low_20 = min(prices_list[-21:-1])
            if current_price >= high_20 * 1.001:
                self.buy(symbol, current_price, f"Momentum Breakout: Price cleared 20-period high by >0.1%.")
            elif current_price <= low_20 * 0.999:
                self.sell(symbol, current_price, f"Momentum Breakdown: Price cleared 20-period low by >0.1%.")

        self.update_capital_history(prices)

    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        if len(prices) < period + 1: return 50.0
        gains = []
        losses = []
        for i in range(len(prices) - period, len(prices)):
            diff = prices[i] - prices[i-1]
            gains.append(max(diff, 0))
            losses.append(max(-diff, 0))
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        if avg_loss == 0: return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def calculate_macd(self, prices: List[float]) -> (float, float):
        # Unchanged from previous version
        ema_12 = self.calculate_ema(prices, 12)
        ema_26 = self.calculate_ema(prices, 26)
        macd = ema_12 - ema_26
        signal = self.calculate_ema(prices[-30:], 9) * 0.1
        return macd, signal

    def calculate_ema(self, prices: List[float], period: int) -> float:
        if not prices: return 0.0
        multiplier = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        return ema

    def buy(self, symbol: str, price: float, reason: str):
        # --- POSITION LIMITS ---
        open_positions = [s for s, q in self.portfolio.items() if q > 0]
        if len(open_positions) >= 10:
            return
        
        # Don't add to existing positions for this demo to encourage diversity
        if self.portfolio.get(symbol, 0) > 0:
            return

        # Allocate 10% of total portfolio value
        total_val = self.get_status()["total_value"]
        amount_to_spend = total_val * 0.1
        
        if self.capital < amount_to_spend:
            amount_to_spend = self.capital
            
        if amount_to_spend < 500: # Increased minimum trade size to $500
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
        print(f"Executed SIGNIFICANT BUY: {symbol} | Amount: ${amount_to_spend:.2f} | Reason: {reason}")

    def sell(self, symbol: str, price: float, reason: str):
        quantity = self.portfolio[symbol]
        if quantity <= 0:
            return
            
        # Sell entire holding for significant impact
        amount_to_sell = quantity
        revenue = amount_to_sell * price
        self.capital += revenue
        self.portfolio[symbol] = 0.0
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
        print(f"Executed SIGNIFICANT SELL: {symbol} | Revenue: ${revenue:.2f} | Reason: {reason}")

    def update_capital_history(self, prices: Dict[str, float]):
        total_value = self.capital
        for symbol, quantity in self.portfolio.items():
            if symbol in prices:
                total_value += quantity * prices[symbol]
        
        self.capital_history.append({
            "time": time.time(),
            "value": total_value
        })
        if len(self.capital_history) > 200:
            self.capital_history.pop(0)

    def get_status(self):
        prices = market.market_sim.get_prices()
        total_value = self.capital
        for symbol, quantity in self.portfolio.items():
            if symbol in prices:
                total_value += quantity * prices[symbol]
            
        return {
            "capital": self.capital,
            "portfolio": self.portfolio,
            "total_value": total_value,
            "trade_history": self.trade_history[-20:], # Last 20 trades
            "capital_history": self.capital_history
        }

trading_agent = TradingAgent()
