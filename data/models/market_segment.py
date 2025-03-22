# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.
from dataclasses import dataclass
from typing import List
import numpy as np

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