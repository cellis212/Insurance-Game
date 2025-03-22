import numpy as np

class Asset:
    """Represents an investment asset in the game."""
    def __init__(self, name: str, current_price: float, dividend_yield: float, volatility: float):
        self.name = name
        self.current_price = current_price
        self.dividend_yield = dividend_yield
        self.volatility = volatility
        self.price_history = [current_price]  # Initialize price history with current price
        self.net_trades = 0  # Track net trades (buys - sells) for market pressure
    
    def update_price(self) -> None:
        """Update the asset price based on volatility and market pressure."""
        # Simple random walk with drift (80% of price movement)
        drift = 0.02 / 4  # 2% annual drift, divided by 4 for quarterly
        random_shock = np.random.normal(0, self.volatility / 2)  # Divide by 2 for quarterly
        random_move = self.current_price * (drift + random_shock)
        
        # Market pressure effect (20% of price movement)
        # Normalize net trades to a small percentage effect (-2% to +2%)
        market_pressure = np.clip(self.net_trades / 1000, -0.02, 0.02)
        market_move = self.current_price * market_pressure
        
        # Combine both effects
        total_change = (random_move * 0.8) + (market_move * 0.2)
        self.current_price = max(0.01, self.current_price + total_change)
        
        # Reset net trades for next period
        self.net_trades = 0
        
        # Update price history
        self.price_history.append(self.current_price)
    
    def get_quarterly_income(self, shares: int) -> float:
        """Calculate quarterly dividend/interest income."""
        return shares * self.current_price * (self.dividend_yield / 4)  # Divide by 4 for quarterly
    
    def record_trade(self, shares: int) -> None:
        """Record a trade for market pressure calculation. Positive for buys, negative for sells."""
        self.net_trades += shares 