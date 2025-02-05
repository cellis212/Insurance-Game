from dataclasses import dataclass
from typing import Dict, List
import numpy as np

@dataclass
class StateCharacteristics:
    """Characteristics and risk factors for a state market."""
    name: str
    catastrophe_risk: float
    cat_severity: float
    market_size_multiplier: float
    entry_cost: float

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

class MarketDynamics:
    """Manages market conditions, demand, and risk factors."""
    def __init__(self):
        # Define states and their characteristics
        self.states: Dict[str, StateCharacteristics] = {
            "CA": StateCharacteristics(
                name="California",
                catastrophe_risk=0.01,  # 1% chance of earthquake per year
                cat_severity=np.log(500000),  # Average catastrophe claim $500k
                market_size_multiplier=1.5,  # Larger market
                entry_cost=500000  # $500k to enter
            ),
            "FL": StateCharacteristics(
                name="Florida",
                catastrophe_risk=0.05,  # 5% chance of hurricane per year
                cat_severity=np.log(250000),  # Average catastrophe claim $250k
                market_size_multiplier=1.0,  # Base market size
                entry_cost=300000  # $300k to enter
            )
        }
        
        # Initialize market segments for each state
        self.market_segments: Dict[str, MarketSegment] = {}
        self._initialize_market_segments()
        
        # Initialize base market rates
        self.base_market_rates = self._calculate_base_rates()
    
    def _initialize_market_segments(self) -> None:
        """Initialize market segments for each state."""
        for state_id, state_info in self.states.items():
            # Home insurance in this state
            self.market_segments[f"{state_id}_home"] = MarketSegment(
                name=f"Home Insurance - {state_info.name}",
                base_risk=0.05,  # 5% chance of regular claim per year
                price_sensitivity=1.2,
                market_size=int(2000 * state_info.market_size_multiplier),
                current_demand=int(1500 * state_info.market_size_multiplier)
            )
            # Auto insurance in this state
            self.market_segments[f"{state_id}_auto"] = MarketSegment(
                name=f"Auto Insurance - {state_info.name}",
                base_risk=0.15,  # 15% chance of claim per year
                price_sensitivity=1.5,
                market_size=int(5000 * state_info.market_size_multiplier),
                current_demand=int(4000 * state_info.market_size_multiplier)
            )
    
    def _calculate_base_rates(self) -> Dict[str, float]:
        """Calculate base market rates for each line in each state."""
        base_rates = {}
        for state_id, state_info in self.states.items():
            # Add catastrophe risk loading to home insurance
            cat_loading = state_info.catastrophe_risk * np.exp(state_info.cat_severity)
            
            base_rates[f"{state_id}_home"] = 1200 + cat_loading
            base_rates[f"{state_id}_auto"] = 900
        return base_rates
    
    def update_market_demand(self, current_turn: int) -> None:
        """Update market demand based on various factors."""
        for state_id, state_info in self.states.items():
            for line in ["home", "auto"]:
                segment = self.market_segments[f"{state_id}_{line}"]
                
                # Economic cycle effect (simple sine wave)
                economic_cycle = np.sin(current_turn / 8) * 0.1
                
                # State-specific seasonal effects
                if state_id == "FL":
                    # Florida has stronger seasonal effects (snowbirds)
                    seasonal_effect = np.sin(current_turn / 4) * 0.15
                else:
                    seasonal_effect = np.sin(current_turn / 4) * 0.05
                
                # Random market fluctuation
                market_fluctuation = np.random.normal(0, 0.05)
                
                # Combined effect
                total_effect = 1 + economic_cycle + seasonal_effect + market_fluctuation
                
                # Update demand with limits
                new_demand = int(segment.current_demand * total_effect)
                segment.current_demand = max(0, min(segment.market_size, new_demand))
    
    def get_claim_distribution(self, line_id: str) -> Dict:
        """Get claim distribution parameters for a specific line."""
        state_id = line_id.split("_")[0]
        state_info = self.states[state_id]
        
        if "_home" in line_id:
            return {
                "mean": np.log(24000),  # Average home claim $24,000
                "sigma": 0.7,           # Higher variation in home claims
                "cat_mean": state_info.cat_severity,  # Catastrophe severity
                "cat_risk": state_info.catastrophe_risk  # Catastrophe frequency
            }
        else:  # Auto insurance
            return {
                "mean": np.log(6000),   # Average auto claim $6,000
                "sigma": 0.5            # Lower variation in auto claims
            }
    
    def generate_catastrophe(self, state_id: str) -> bool:
        """Check if a catastrophe occurs in the given state this quarter."""
        quarterly_risk = self.states[state_id].catastrophe_risk / 4
        return np.random.random() < quarterly_risk 