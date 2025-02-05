from dataclasses import dataclass
from typing import List, Dict
import numpy as np

class Asset:
    """Represents a specific investment asset with price and income characteristics."""
    def __init__(self, name: str, current_price: float, dividend_yield: float, volatility: float):
        self.name = name
        self.current_price = current_price
        self.dividend_yield = dividend_yield  # Annual yield
        self.volatility = volatility  # Standard deviation for price changes
        self.price_history: List[float] = [current_price]

    def update_price(self) -> None:
        """Update the asset price with random walk and volatility."""
        # Random walk with drift
        drift = 0.05  # 5% annual expected return
        daily_drift = drift / 252  # Convert to daily
        daily_vol = self.volatility / np.sqrt(252)  # Convert to daily
        
        # Generate random return
        random_return = np.random.normal(daily_drift, daily_vol)
        self.current_price *= (1 + random_return)
        self.price_history.append(self.current_price)
    
    def get_quarterly_income(self, shares: int) -> float:
        """Calculate quarterly dividend/interest income."""
        return (self.dividend_yield * self.current_price * shares) / 4

class InvestmentPortfolio:
    """Manages a collection of investment assets and portfolio operations."""
    def __init__(self):
        self.assets: Dict[str, Asset] = {
            "SP500": Asset(
                name="S&P 500 ETF",
                current_price=450.0,
                dividend_yield=0.015,  # 1.5% dividend yield
                volatility=0.15  # 15% annual volatility
            ),
            "CORP_BONDS": Asset(
                name="Corporate Bond ETF",
                current_price=100.0,
                dividend_yield=0.045,  # 4.5% yield
                volatility=0.08  # 8% annual volatility
            ),
            "LONG_TREASURY": Asset(
                name="Long-Term Treasury ETF",
                current_price=90.0,
                dividend_yield=0.035,  # 3.5% yield
                volatility=0.12  # 12% annual volatility
            ),
            "SHORT_TREASURY": Asset(
                name="Short-Term Treasury ETF",
                current_price=50.0,
                dividend_yield=0.02,  # 2% yield
                volatility=0.03  # 3% annual volatility
            ),
            "REIT": Asset(
                name="Real Estate Investment Trust ETF",
                current_price=80.0,
                dividend_yield=0.06,  # 6% dividend yield
                volatility=0.20  # 20% annual volatility
            )
        }
        self.holdings: Dict[str, int] = {}  # {asset_id: number_of_shares}
    
    def buy_asset(self, asset_id: str, shares: int, available_cash: float) -> tuple[bool, float]:
        """
        Attempt to buy shares of an asset.
        Returns (success, cost) tuple.
        """
        if asset_id not in self.assets:
            return False, 0.0
        
        asset = self.assets[asset_id]
        cost = asset.current_price * shares
        
        if cost > available_cash:
            return False, 0.0
        
        current_shares = self.holdings.get(asset_id, 0)
        self.holdings[asset_id] = current_shares + shares
        return True, cost
    
    def sell_asset(self, asset_id: str, shares: int) -> tuple[bool, float]:
        """
        Attempt to sell shares of an asset.
        Returns (success, proceeds) tuple.
        """
        if asset_id not in self.assets:
            return False, 0.0
        
        current_shares = self.holdings.get(asset_id, 0)
        if shares > current_shares:
            return False, 0.0
        
        asset = self.assets[asset_id]
        proceeds = asset.current_price * shares
        
        self.holdings[asset_id] = current_shares - shares
        return True, proceeds
    
    def update_prices(self) -> None:
        """Update prices for all assets."""
        for asset in self.assets.values():
            asset.update_price()
    
    def calculate_returns(self) -> tuple[float, float]:
        """
        Calculate quarterly returns from investments.
        Returns (income, unrealized_gains) tuple.
        """
        total_income = 0.0
        unrealized_gains = 0.0
        
        for asset_id, asset in self.assets.items():
            shares = self.holdings.get(asset_id, 0)
            if shares > 0:
                # Calculate quarterly income (dividends/interest)
                income = asset.get_quarterly_income(shares)
                total_income += income
                
                # Update price and calculate unrealized gains
                old_price = asset.current_price
                asset.update_price()
                price_change = asset.current_price - old_price
                unrealized_gains += price_change * shares
        
        return total_income, unrealized_gains
    
    def get_total_value(self) -> float:
        """Calculate total market value of all holdings."""
        return sum(
            self.assets[asset_id].current_price * shares
            for asset_id, shares in self.holdings.items()
        ) 