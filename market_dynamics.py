from dataclasses import dataclass
from typing import Dict, List, Optional
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
class Consumer:
    """Represents an individual insurance consumer with preferences and history."""
    id: str
    state: str
    line: str
    price_sensitivity: float  # How sensitive they are to price differences
    loyalty: float  # How much they value staying with current provider
    current_provider: Optional[str]  # None or company name
    satisfaction: float  # Current satisfaction with provider (0-1)

@dataclass
class MarketSegment:
    """Represents a market segment with specific risk characteristics."""
    name: str
    base_risk: float
    market_size: int
    current_demand: int
    consumers: List[Consumer]
    
    def calculate_consumer_choice(self, consumer: Consumer, companies: Dict[str, float], 
                                advertising: Dict[str, float]) -> str:
        """Calculate which company a consumer will choose based on their preferences."""
        best_score = float('-inf')
        best_company = None
        
        base_price = min(companies.values())  # Use lowest price as reference
        
        for company_name, price in companies.items():
            # Calculate relative price (compared to lowest in market)
            price_factor = (base_price / price) if price > 0 else 1.0
            
            # Calculate loyalty factor
            loyalty_factor = 1.0
            if consumer.current_provider == company_name:
                loyalty_factor = 1.0 + (consumer.loyalty * consumer.satisfaction)
            
            # Calculate advertising factor (diminishing returns)
            ad_budget = advertising.get(company_name, 0)
            ad_factor = 1.0 + (0.2 * np.log1p(ad_budget / 10000))  # Normalize by 10k for reasonable scaling
            
            # Combined score with individual weights
            score = (
                price_factor ** consumer.price_sensitivity *  # Price sensitivity
                loyalty_factor *  # Loyalty to current provider
                ad_factor  # Advertising effect
            )
            
            # Add small random variation
            score *= np.random.uniform(0.95, 1.05)
            
            if score > best_score:
                best_score = score
                best_company = company_name
        
        return best_company
    
    def update_demand(self, companies: Dict[str, float], advertising: Dict[str, float]) -> Dict[str, int]:
        """Update demand based on consumer choices."""
        policies_by_company = {name: 0 for name in companies.keys()}
        
        for consumer in self.consumers:
            chosen_company = self.calculate_consumer_choice(consumer, companies, advertising)
            if chosen_company:
                policies_by_company[chosen_company] += 1
                
                # Update consumer's provider and satisfaction
                old_provider = consumer.current_provider
                consumer.current_provider = chosen_company
                
                # Satisfaction is higher if they stayed (loyalty rewarded)
                if old_provider == chosen_company:
                    consumer.satisfaction = min(1.0, consumer.satisfaction + 0.1)
                else:
                    consumer.satisfaction = 0.5  # Reset satisfaction with new provider
        
        return policies_by_company

class MarketDynamics:
    """Manages market conditions, demand, and risk factors."""
    def __init__(self):
        # Define states and their characteristics
        self.states = {
            "CA": {
                "name": "California",
                "catastrophe_risk": 0.01,  # 1% chance of earthquake per year
                "cat_severity": np.log(500000),  # Average catastrophe claim $500k
                "market_size_multiplier": 1.5,  # Larger market
                "entry_cost": 500000,  # $500k to enter
                "consumer_traits": {
                    "price_sensitivity": (1.0, 0.3),  # (mean, std) of price sensitivity
                    "loyalty": (0.3, 0.1),  # (mean, std) of loyalty factor
                }
            },
            "FL": {
                "name": "Florida",
                "catastrophe_risk": 0.05,  # 5% chance of hurricane per year
                "cat_severity": np.log(250000),  # Average catastrophe claim $250k
                "market_size_multiplier": 1.0,  # Base market size
                "entry_cost": 300000,  # $300k to enter
                "consumer_traits": {
                    "price_sensitivity": (1.2, 0.3),  # More price sensitive
                    "loyalty": (0.2, 0.1),  # Less loyal
                }
            }
        }
        
        # Initialize market segments and consumers
        self.market_segments = {}
        self._initialize_market_segments()
        
        # Initialize base market rates
        self.base_market_rates = self._calculate_base_rates()
    
    def _initialize_market_segments(self):
        """Initialize market segments and generate consumers for each segment."""
        for state_id, state_info in self.states.items():
            # Generate consumers for home insurance
            home_consumers = self._generate_consumers(
                state_id, "home",
                int(2000 * state_info["market_size_multiplier"]),
                state_info["consumer_traits"]
            )
            
            self.market_segments[f"{state_id}_home"] = MarketSegment(
                name=f"Home Insurance - {state_info['name']}",
                base_risk=0.05,  # 5% chance of regular claim per year
                market_size=len(home_consumers),
                current_demand=len(home_consumers),
                consumers=home_consumers
            )
            
            # Generate consumers for auto insurance
            auto_consumers = self._generate_consumers(
                state_id, "auto",
                int(5000 * state_info["market_size_multiplier"]),
                state_info["consumer_traits"]
            )
            
            self.market_segments[f"{state_id}_auto"] = MarketSegment(
                name=f"Auto Insurance - {state_info['name']}",
                base_risk=0.15,  # 15% chance of claim per year
                market_size=len(auto_consumers),
                current_demand=len(auto_consumers),
                consumers=auto_consumers
            )
    
    def _generate_consumers(self, state_id: str, line: str, count: int, traits: Dict) -> List[Consumer]:
        """Generate a list of consumers with varying preferences."""
        consumers = []
        for i in range(count):
            # Generate random traits based on state characteristics
            price_sens_mean, price_sens_std = traits["price_sensitivity"]
            loyalty_mean, loyalty_std = traits["loyalty"]
            
            consumer = Consumer(
                id=f"{state_id}_{line}_{i}",
                state=state_id,
                line=line,
                price_sensitivity=max(0.1, np.random.normal(price_sens_mean, price_sens_std)),
                loyalty=max(0, min(1, np.random.normal(loyalty_mean, loyalty_std))),
                current_provider=None,
                satisfaction=0.5  # Initial neutral satisfaction
            )
            consumers.append(consumer)
        
        return consumers
    
    def _calculate_base_rates(self) -> Dict[str, float]:
        """Calculate base market rates for each line in each state."""
        base_rates = {}
        for state_id, state_info in self.states.items():
            # Add catastrophe risk loading to home insurance
            cat_loading = state_info["catastrophe_risk"] * np.exp(state_info["cat_severity"])
            
            base_rates[f"{state_id}_home"] = 1200 + cat_loading
            base_rates[f"{state_id}_auto"] = 900
        return base_rates
    
    def update_market(self, player_company, ai_competitors, advertising_budgets: Dict[str, Dict[str, float]]):
        """Update market conditions and consumer choices."""
        for line_id, segment in self.market_segments.items():
            # Gather all companies' premium rates
            company_rates = {
                player_company.name: player_company.premium_rates.get(line_id, self.base_market_rates[line_id])
            }
            
            for competitor in ai_competitors:
                company_rates[competitor.name] = competitor.premium_rates.get(
                    line_id, self.base_market_rates[line_id]
                )
            
            # Process advertising budgets for this line_id
            line_advertising = {}
            for company_name, company_budget in advertising_budgets.items():
                line_advertising[company_name] = company_budget.get(line_id, 0)
            
            # Update consumer choices and demand
            new_policies = segment.update_demand(company_rates, line_advertising)
            
            # Update policies for all companies
            player_company.policies_sold[line_id] = new_policies[player_company.name]
            for competitor in ai_competitors:
                competitor.policies_sold[line_id] = new_policies[competitor.name]
            
            # Update segment demand
            segment.current_demand = sum(new_policies.values())
    
    def get_claim_distribution(self, line_id: str) -> Dict:
        """Get claim distribution parameters for a specific line."""
        state_id = line_id.split("_")[0]
        state_info = self.states[state_id]
        
        if "_home" in line_id:
            return {
                "mean": np.log(24000),  # Average home claim $24,000
                "sigma": 0.7,           # Higher variation in home claims
                "cat_mean": state_info["cat_severity"],  # Catastrophe severity
                "cat_risk": state_info["catastrophe_risk"]  # Catastrophe frequency
            }
        else:  # Auto insurance
            return {
                "mean": np.log(6000),   # Average auto claim $6,000
                "sigma": 0.5            # Lower variation in auto claims
            }
    
    def generate_catastrophe(self, state_id: str) -> bool:
        """Check if a catastrophe occurs in the given state this quarter."""
        quarterly_risk = self.states[state_id]["catastrophe_risk"] / 4
        return np.random.random() < quarterly_risk 