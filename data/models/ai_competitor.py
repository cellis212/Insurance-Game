# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.
import numpy as np
from typing import Dict, Any, List

from data.models.company import Company

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
        """Make investment decisions based on risk profile and market conditions."""
        # Skip if we have very little cash
        if self.cash < 50000:
            return
            
        # Determine how much to invest based on risk profile and cash position
        cash_to_invest_ratio = 0.0
        if self.risk_profile == "aggressive":
            cash_to_invest_ratio = 0.8  # Invest up to 80% of available cash
        elif self.risk_profile == "conservative":
            cash_to_invest_ratio = 0.4  # Invest up to 40% of available cash
        else:  # balanced
            cash_to_invest_ratio = 0.6  # Invest up to 60% of available cash
            
        # Limit investment to available cash while keeping operating reserves
        reserves_needed = sum(self.policies_sold.values()) * 100  # $100 per policy as reserve
        reserves_needed = max(reserves_needed, 100000)  # At least $100k
        
        max_to_invest = max(0, self.cash - reserves_needed)
        cash_to_invest = min(max_to_invest, self.cash * cash_to_invest_ratio) 