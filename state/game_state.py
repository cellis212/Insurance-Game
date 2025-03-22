# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.
from typing import Dict, List, Any
import numpy as np

from data.models.company import Company
from data.models.ai_competitor import AICompetitor
from data.models.market_segment import MarketSegment
from data.models.financial_report import FinancialReport

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
        
        # These will be initialized elsewhere
        self.market_segments = {}
        self.investment_assets = {}
        self.states = {}
        self.base_market_rates = {}
        self.claim_distributions = {}
        self.unlocked_states = {}
        self.financial_history = []
    
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
    
    def _update_market_demand(self):
        """Update market demand based on economic cycle and seasonal factors."""
        # This will be implemented elsewhere and invoked from here
        pass
        
    def _calculate_investment_returns(self):
        """Calculate investment returns for the current turn."""
        # This will be implemented elsewhere and invoked from here
        pass
        
    def _generate_financial_report(self):
        """Generate financial report for the current turn."""
        # This will be implemented elsewhere and invoked from here
        pass
    
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