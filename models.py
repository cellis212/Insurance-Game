from dataclasses import dataclass
from typing import List, Dict
import numpy as np

@dataclass
class Company:
    """Represents an insurance company in the game."""
    name: str
    cash: float
    investments: Dict[str, int]  # Changed to store number of shares for each asset
    policies_sold: Dict[str, int]
    claims_history: List[Dict]
    premium_rates: Dict[str, float]
    
    def calculate_revenue(self) -> float:
        """Calculate total revenue from premiums."""
        return sum(self.premium_rates[market] * count 
                  for market, count in self.policies_sold.items())
    
    def process_claims(self, claims: List[Dict]) -> float:
        """Process and pay claims, return total amount paid."""
        total_claims = sum(claim["amount"] for claim in claims)
        self.cash -= total_claims
        self.claims_history.extend(claims)
        return total_claims

@dataclass
class MarketSegment:
    """Represents a market segment with specific risk characteristics."""
    name: str
    base_risk: float
    price_sensitivity: float
    market_size: int
    current_demand: int
    
    def calculate_demand(self, premium: float, competitor_premiums: List[float]) -> int:
        """Calculate demand based on premium pricing and competition."""
        relative_price = premium / np.mean(competitor_premiums) if competitor_premiums else 1.0
        demand_factor = np.exp(-self.price_sensitivity * (relative_price - 1))
        return int(min(self.market_size, self.current_demand * demand_factor))

@dataclass
class FinancialReport:
    """Represents a company's financial report for a given period."""
    period: int
    revenue: float
    claims_paid: float
    investment_returns: float  # Realized returns (dividends/interest)
    unrealized_gains: float   # Unrealized capital gains/losses
    operating_expenses: float
    
    @property
    def net_income(self) -> float:
        """Calculate net income for the period (excluding unrealized gains)."""
        return self.revenue + self.investment_returns - self.claims_paid - self.operating_expenses
    
    def generate_summary(self) -> Dict:
        """Generate a summary of the financial report."""
        return {
            "period": self.period,
            "revenue": self.revenue,
            "claims_paid": self.claims_paid,
            "investment_returns": self.investment_returns,
            "unrealized_gains": self.unrealized_gains,
            "operating_expenses": self.operating_expenses,
            "net_income": self.net_income,
            "loss_ratio": self.claims_paid / self.revenue if self.revenue > 0 else float('inf')
        } 