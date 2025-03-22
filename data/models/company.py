# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Company:
    """Represents an insurance company in the game."""
    name: str
    cash: float
    investments: Dict[str, int]  # Stores number of shares for each asset
    policies_sold: Dict[str, int]
    claims_history: List[Dict[str, Any]]
    premium_rates: Dict[str, float]
    advertising_budget: Dict[str, float]  # Advertising budget per line
    
    def calculate_revenue(self) -> float:
        """Calculate total revenue from premiums."""
        return sum(self.premium_rates[market] * count 
                  for market, count in self.policies_sold.items())
    
    def process_claims(self, claims: List[Dict[str, Any]]) -> float:
        """Process and pay claims, return total amount paid."""
        total_claims = sum(claim["amount"] for claim in claims)
        self.cash -= total_claims
        self.claims_history.extend(claims)
        return total_claims
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert company object to a dictionary for serialization."""
        return {
            "name": self.name,
            "cash": self.cash,
            "investments": self.investments,
            "policies_sold": self.policies_sold,
            "claims_history": self.claims_history,
            "premium_rates": self.premium_rates,
            "advertising_budget": self.advertising_budget
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Company':
        """Create a company object from a dictionary."""
        return cls(
            name=data["name"],
            cash=data["cash"],
            investments=data["investments"],
            policies_sold=data["policies_sold"],
            claims_history=data["claims_history"],
            premium_rates=data["premium_rates"],
            advertising_budget=data["advertising_budget"]
        ) 