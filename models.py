from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Union
import numpy as np

@dataclass
class Company:
    """Represents an insurance company in the game."""
    name: str
    cash: float
    investments: Dict[str, int]  # Changed to store number of shares for each asset
    policies_sold: Dict[str, int]
    claims_history: List[Dict[str, Any]]
    premium_rates: Dict[str, float]
    advertising_budget: Dict[str, float]  # New: advertising budget per line
    
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

class AICompetitor(Company):
    """AI-controlled insurance company that competes with the player."""
    
    def __init__(self, name: str, cash: float, risk_profile: str = "balanced"):
        """
        Initialize an AI competitor.
        
        Args:
            name: Company name
            cash: Starting cash
            risk_profile: Strategy profile ("aggressive", "balanced", or "conservative")
        """
        super().__init__(
            name=name,
            cash=cash,
            investments={},
            policies_sold={},
            claims_history=[],
            premium_rates={},
            advertising_budget={}
        )
        self.risk_profile = risk_profile
        self.financial_history = []
        
        # Set target market share and strategy parameters based on risk profile
        if risk_profile == "aggressive":
            self.target_market_share = 0.4  # Aims for 40% market share
            self.price_sensitivity = 1.5  # More willing to cut prices
            self.advertising_ratio = 0.15  # Spends more on advertising (15% of revenue)
        elif risk_profile == "conservative":
            self.target_market_share = 0.2  # Content with 20% market share
            self.price_sensitivity = 0.8  # Less willing to cut prices
            self.advertising_ratio = 0.05  # Spends less on advertising (5% of revenue)
        else:  # balanced
            self.target_market_share = 0.3  # Aims for 30% market share
            self.price_sensitivity = 1.0  # Moderate price sensitivity
            self.advertising_ratio = 0.10  # Moderate advertising (10% of revenue)
    
    def make_decisions(self, game_state) -> None:
        """
        Make strategic decisions for the turn.
        
        Args:
            game_state: Current game state
        """
        self._update_pricing(game_state)
        self._update_advertising(game_state)
        self._make_investments(game_state)
    
    def _update_pricing(self, game_state) -> None:
        """Update premium rates based on market conditions and strategy."""
        for line_id, segment in game_state.market.market_segments.items():
            if line_id not in self.premium_rates:
                # Initialize with base market rate if no rate set
                self.premium_rates[line_id] = game_state.market.base_market_rates[line_id]
                continue
            
            # Get market data
            base_rate = game_state.market.base_market_rates[line_id]
            player_rate = game_state.player_company.premium_rates.get(line_id, base_rate)
            current_policies = self.policies_sold.get(line_id, 0)
            market_share = current_policies / segment.market_size if segment.market_size > 0 else 0
            
            # Calculate target rate based on strategy
            if market_share < self.target_market_share:
                # Undercut to gain market share
                target_rate = min(
                    player_rate * 0.95,  # 5% below player
                    base_rate * (1 - 0.1 * self.price_sensitivity)  # Up to 10-15% below base rate
                )
            else:
                # Maintain or increase rates
                target_rate = max(
                    base_rate,
                    player_rate * 1.02  # Slightly above player
                )
            
            # Ensure minimum profitability
            min_rate = base_rate * 0.85  # Don't go below 85% of base rate
            target_rate = max(target_rate, min_rate)
            
            # Gradually adjust rates (max 10% change per turn)
            current_rate = self.premium_rates[line_id]
            max_change = current_rate * 0.1
            new_rate = np.clip(
                target_rate,
                current_rate - max_change,
                current_rate + max_change
            )
            
            self.premium_rates[line_id] = new_rate
    
    def _update_advertising(self, game_state) -> None:
        """Update advertising budgets based on strategy and market conditions."""
        # Calculate total revenue per line
        revenue_by_line = {}
        for line_id, policies in self.policies_sold.items():
            revenue = policies * self.premium_rates.get(line_id, game_state.market.base_market_rates[line_id])
            revenue_by_line[line_id] = revenue
        
        for line_id, segment in game_state.market.market_segments.items():
            # Base advertising on revenue and strategy
            revenue = revenue_by_line.get(line_id, 0)
            base_budget = revenue * self.advertising_ratio
            
            # Adjust based on market share
            current_policies = self.policies_sold.get(line_id, 0)
            market_share = current_policies / segment.market_size if segment.market_size > 0 else 0
            
            if market_share < self.target_market_share:
                # Increase advertising to gain market share
                budget = base_budget * 1.5
            else:
                # Reduce advertising to maintain position
                budget = base_budget * 0.8
            
            # Ensure minimum advertising in active markets
            if revenue > 0:
                budget = max(budget, 10000)  # Minimum $10k per line
            else:
                budget = 5000  # Minimal presence in new markets
            
            # Cap advertising at 25% of cash
            budget = min(budget, self.cash * 0.25)
            
            self.advertising_budget[line_id] = budget
    
    def _make_investments(self, game_state) -> None:
        """Make investment decisions."""
        # TODO: Implement investment strategy
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert AI competitor to dictionary for serialization."""
        base_dict = super().to_dict()
        base_dict["risk_profile"] = self.risk_profile
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AICompetitor':
        """Create an AI competitor from a dictionary."""
        risk_profile = data.pop("risk_profile", "balanced")
        competitor = cls(
            name=data["name"],
            cash=data["cash"],
            risk_profile=risk_profile
        )
        competitor.investments = data["investments"]
        competitor.policies_sold = data["policies_sold"]
        competitor.claims_history = data["claims_history"]
        competitor.premium_rates = data["premium_rates"]
        competitor.advertising_budget = data["advertising_budget"]
        return competitor

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

class GameState:
    """Manages the overall game state and progression."""
    
    def __init__(self, initial_state="CA", company_name="Player Insurance Co."):
        self.current_turn = 0
        self.player_company = Company(
            name=company_name,
            cash=1000000.0,  # Starting with $1M
            investments={},  # Will store {asset_name: shares}
            policies_sold={},
            claims_history=[],
            premium_rates={},
            advertising_budget={}
        )
        
        # Initialize AI competitors
        self.ai_competitors = [
            AICompetitor("Aggressive Insurance Co.", cash=1000000.0, risk_profile="aggressive"),
            AICompetitor("Balanced Insurance Co.", cash=1000000.0, risk_profile="balanced"),
            AICompetitor("Conservative Insurance Co.", cash=1000000.0, risk_profile="conservative")
        ]
    
    def update(self):
        """Update game state for the current turn."""
        # Update AI competitors first
        for competitor in self.ai_competitors:
            competitor.make_decisions(self)
        
        self._update_policies()
        self._generate_claims()
        self._update_market_demand()
        self._calculate_investment_returns()
        self._generate_financial_report()
        self.current_turn += 1
    
    def _update_policies(self):
        """Update the number of policies based on premium rates and market conditions."""
        new_policies = {}
        
        for line_id, segment in self.market_segments.items():
            state_id = line_id.split("_")[0]
            # Only update policies for unlocked states
            if self.unlocked_states[state_id]:
                # Get all companies' premium rates for this line
                all_rates = [self.base_market_rates[line_id]]  # Base market rate
                all_rates.append(self.player_company.premium_rates.get(line_id, self.base_market_rates[line_id]))
                for competitor in self.ai_competitors:
                    all_rates.append(competitor.premium_rates.get(line_id, self.base_market_rates[line_id]))
                
                # Calculate market share for player
                player_premium = self.player_company.premium_rates.get(line_id, self.base_market_rates[line_id])
                relative_price = player_premium / np.mean(all_rates)
                potential_policies = segment.calculate_demand(player_premium, all_rates)
                
                # Add random variation (±10%)
                variation = np.random.uniform(0.9, 1.1)
                new_policies[line_id] = int(potential_policies * variation)
                
                # Update AI competitor policies
                remaining_demand = segment.market_size - new_policies[line_id]
                if remaining_demand > 0:
                    for competitor in self.ai_competitors:
                        competitor_premium = competitor.premium_rates.get(line_id, self.base_market_rates[line_id])
                        competitor_demand = segment.calculate_demand(competitor_premium, all_rates)
                        competitor_policies = int(min(competitor_demand, remaining_demand / len(self.ai_competitors)))
                        competitor.policies_sold[line_id] = competitor_policies
                        remaining_demand -= competitor_policies
            else:
                new_policies[line_id] = 0
                for competitor in self.ai_competitors:
                    competitor.policies_sold[line_id] = 0
        
        self.player_company.policies_sold = new_policies
    
    def _generate_claims(self):
        """Generate insurance claims based on line characteristics and catastrophes."""
        # Process claims for player company
        self._process_company_claims(self.player_company)
        
        # Process claims for AI competitors
        for competitor in self.ai_competitors:
            self._process_company_claims(competitor)
    
    def _process_company_claims(self, company):
        """Process claims for a specific company."""
        # First, collect premium revenue for the quarter
        premium_revenue = sum(
            company.premium_rates.get(line_id, self.base_market_rates[line_id]) * policies
            for line_id, policies in company.policies_sold.items()
        ) / 4  # Quarterly revenue
        
        # Add premium revenue to cash
        company.cash += premium_revenue
        
        claims = []
        
        # Generate regular claims
        for line_id, policies in company.policies_sold.items():
            segment = self.market_segments[line_id]
            base_risk = segment.base_risk
            
            # Calculate quarterly claim frequency (divide annual risk by 4)
            quarterly_risk = base_risk / 4
            claim_count = np.random.poisson(quarterly_risk * policies)
            
            # Generate regular claims
            dist = self.claim_distributions[line_id]
            for _ in range(claim_count):
                claim_amount = np.random.lognormal(
                    mean=dist["mean"],
                    sigma=dist["sigma"]
                )
                
                claims.append({
                    "line": line_id,
                    "amount": claim_amount,
                    "turn": self.current_turn,
                    "type": "regular"
                })
            
            # Generate catastrophe claims for home insurance
            if "_home" in line_id:  # Only home insurance has catastrophe risk
                state_id = line_id.split("_")[0]
                cat_risk = self.states[state_id]["catastrophe_risk"] / 4  # Quarterly risk
                
                if np.random.random() < cat_risk:  # Catastrophe occurs
                    # Affect 10-30% of policies in the state
                    affected_ratio = np.random.uniform(0.1, 0.3)
                    affected_policies = int(policies * affected_ratio)
                    
                    for _ in range(affected_policies):
                        claim_amount = np.random.lognormal(
                            mean=dist["cat_mean"],
                            sigma=0.5  # Less variation in catastrophe claims
                        )
                        
                        claims.append({
                            "line": line_id,
                            "amount": claim_amount,
                            "turn": self.current_turn,
                            "type": "catastrophe"
                        })
        
        company.process_claims(claims)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the game state to a dictionary for saving."""
        return {
            "current_turn": self.current_turn,
            "player_company": self.player_company.to_dict(),
            "ai_competitors": [comp.to_dict() for comp in self.ai_competitors],
            "market_segments": {key: {"name": seg.name, 
                                     "base_risk": seg.base_risk, 
                                     "price_sensitivity": seg.price_sensitivity,
                                     "market_size": seg.market_size, 
                                     "current_demand": seg.current_demand} 
                              for key, seg in self.market_segments.items()},
            "investment_assets": {name: {"name": asset.name, 
                                        "current_price": asset.current_price,
                                        "dividend_yield": asset.dividend_yield, 
                                        "volatility": asset.volatility} 
                                for name, asset in self.investment_assets.items()},
            "states": self.states,
            "base_market_rates": self.base_market_rates,
            "claim_distributions": self.claim_distributions,
            "unlocked_states": self.unlocked_states,
            "financial_history": [report.to_dict() for report in self.financial_history]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """Create a game state from a saved dictionary."""
        # Create a bare GameState
        game_state = cls.__new__(cls)
        
        # Set basic attributes
        game_state.current_turn = data["current_turn"]
        game_state.player_company = Company.from_dict(data["player_company"])
        game_state.ai_competitors = [AICompetitor.from_dict(comp) for comp in data["ai_competitors"]]
        
        # Reconstruct market segments
        game_state.market_segments = {}
        for key, seg_data in data["market_segments"].items():
            game_state.market_segments[key] = MarketSegment(**seg_data)
        
        # Reconstruct investment assets
        from asset import Asset
        game_state.investment_assets = {}
        for name, asset_data in data["investment_assets"].items():
            game_state.investment_assets[name] = Asset(**asset_data)
        
        # Set other attributes
        game_state.states = data["states"]
        game_state.base_market_rates = data["base_market_rates"]
        game_state.claim_distributions = data["claim_distributions"]
        game_state.unlocked_states = data["unlocked_states"]
        
        # Reconstruct financial history
        game_state.financial_history = [FinancialReport.from_dict(report) for report in data["financial_history"]]
        
        return game_state