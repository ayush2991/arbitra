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
            if len(history[symbol]) < 30: # Need at least 30 for most indicators
                continue
            
            prices_list = history[symbol]
            
            # --- STRATEGY 1: Mean Reversion (Original) ---
            avg_price = sum(prices_list[-10:]) / 10
            diff_pct = (current_price - avg_price) / avg_price
            if diff_pct < -0.0002:
                self.buy(symbol, current_price, f"Mean Reversion: Price is {abs(diff_pct):.2%} below 10-period average.")
                continue
            elif diff_pct > 0.0002:
                self.sell(symbol, current_price, f"Mean Reversion: Price is {diff_pct:.2%} above 10-period average.")
                continue

            # --- STRATEGY 2: SMA Crossover (5/20) ---
            sma_fast = sum(prices_list[-5:]) / 5
            sma_slow = sum(prices_list[-20:]) / 20
            prev_sma_fast = sum(prices_list[-6:-1]) / 5
            prev_sma_slow = sum(prices_list[-21:-1]) / 20
            
            if prev_sma_fast <= prev_sma_slow and sma_fast > sma_slow:
                self.buy(symbol, current_price, f"SMA Crossover: Fast SMA(5) crossed above Slow SMA(20).")
                continue
            elif prev_sma_fast >= prev_sma_slow and sma_fast < sma_slow:
                self.sell(symbol, current_price, f"SMA Crossover: Fast SMA(5) crossed below Slow SMA(20).")
                continue

            # --- STRATEGY 3: RSI (14) ---
            rsi = self.calculate_rsi(prices_list, 14)
            if rsi < 30:
                self.buy(symbol, current_price, f"RSI: Asset oversold at RSI {rsi:.2f}.")
                continue
            elif rsi > 70:
                self.sell(symbol, current_price, f"RSI: Asset overbought at RSI {rsi:.2f}.")
                continue

            # --- STRATEGY 4: Bollinger Bands (20) ---
            sma_20 = sum(prices_list[-20:]) / 20
            std_dev = (sum((p - sma_20)**2 for p in prices_list[-20:]) / 20)**0.5
            upper_band = sma_20 + (2 * std_dev)
            lower_band = sma_20 - (2 * std_dev)
            
            if current_price <= lower_band:
                self.buy(symbol, current_price, f"Bollinger: Price touched Lower Band (SMA 20 - 2SD).")
                continue
            elif current_price >= upper_band:
                self.sell(symbol, current_price, f"Bollinger: Price touched Upper Band (SMA 20 + 2SD).")
                continue

            # --- STRATEGY 5: MACD (12, 26, 9) ---
            macd, signal = self.calculate_macd(prices_list)
            if macd > signal and prices_list[-2] <= self.calculate_macd(prices_list[:-1])[1]:
                self.buy(symbol, current_price, f"MACD: Bullish signal/MACD crossover.")
                continue
            elif macd < signal and prices_list[-2] >= self.calculate_macd(prices_list[:-1])[1]:
                self.sell(symbol, current_price, f"MACD: Bearish signal/MACD crossover.")
                continue

            # --- STRATEGY 6: Momentum (20) ---
            high_20 = max(prices_list[-20:])
            low_20 = min(prices_list[-20:])
            if current_price >= high_20:
                self.buy(symbol, current_price, f"Momentum: Price hit 20-period high.")
            elif current_price <= low_20:
                self.sell(symbol, current_price, f"Momentum: Price hit 20-period low.")

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
        ema_12 = self.calculate_ema(prices, 12)
        ema_26 = self.calculate_ema(prices, 26)
        macd = ema_12 - ema_26
        # Signal is EMA 9 of MACD (simplified)
        signal = self.calculate_ema(prices[-30:], 9) * 0.1 # Placeholder simplified signal
        return macd, signal

    def calculate_ema(self, prices: List[float], period: int) -> float:
        if not prices: return 0.0
        multiplier = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        return ema

    def buy(self, symbol: str, price: float, reason: str):
        # Buy with 10% of available capital
        amount_to_spend = self.capital * 0.1
        if amount_to_spend < 10: # Minimum trade
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
