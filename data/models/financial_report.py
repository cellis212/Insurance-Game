# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.
from dataclasses import dataclass, asdict
from typing import Dict, Any, Union

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
    
    def generate_summary(self) -> Dict[str, Union[int, float]]:
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the financial report to a dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FinancialReport':
        """Create a financial report from a dictionary."""
        return cls(**data) 