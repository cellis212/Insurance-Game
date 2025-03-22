# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import math

from state.game_state import GameState
from data.models.market_segment import MarketSegment

class MarketService:
    """
    Service responsible for market-related operations like market dynamics,
    demand calculations, and economic cycles.
    """
    
    def __init__(self, game_state: Optional[GameState] = None):
        self._game_state = game_state
        self._economic_cycle_phase = 0.0  # 0 to 2π, representing position in economic cycle
        self._economic_cycle_period = 20.0  # Quarters per full economic cycle
        self._seasonal_effects = {
            # Quarter-specific multipliers for claim frequency (Q1 = winter, etc.)
            "auto": [1.1, 0.9, 1.0, 1.2],  # More auto claims in winter and fall
            "home": [1.2, 0.9, 0.8, 1.1]   # More home claims in winter
        }
    
    def set_game_state(self, game_state: GameState) -> None:
        """Set the game state reference."""
        self._game_state = game_state
    
    def update_market_demand(self) -> None:
        """
        Update market demand based on economic conditions and seasonality.
        This affects the maximum potential market size.
        """
        if not self._game_state:
            return
            
        # Update economic cycle position
        self._economic_cycle_phase += (2 * math.pi) / self._economic_cycle_period
        if self._economic_cycle_phase > 2 * math.pi:
            self._economic_cycle_phase -= 2 * math.pi
            
        # Calculate economic cycle effect (±15% swing)
        economic_factor = 1.0 + 0.15 * math.sin(self._economic_cycle_phase)
        
        # Get current quarter (0-3)
        current_quarter = self._game_state.current_turn % 4
        
        # Update each market segment
        for line_id, segment in self._game_state.market_segments.items():
            # Get line type (auto or home)
            line_type = "auto" if "_auto" in line_id else "home"
            
            # Get state
            state_id = line_id.split("_")[0]
            state_data = self._game_state.states[state_id]
            
            # Calculate seasonal effect
            seasonal_factor = self._seasonal_effects[line_type][current_quarter]
            
            # Calculate growth factor based on state growth rate
            turns_passed = self._game_state.current_turn / 4  # Years
            growth_factor = (1 + state_data["growth_rate"]) ** turns_passed
            
            # Calculate base market size with long-term growth
            base_size = segment.market_size * growth_factor
            
            # Apply economic cycle and seasonal effects to demand (not size)
            segment.current_demand = int(base_size * economic_factor * seasonal_factor)
    
    def calculate_market_share(self, line_id: str) -> Dict[str, float]:
        """
        Calculate market share for all companies in a specific line.
        
        Args:
            line_id: The line ID to calculate market share for
            
        Returns:
            A dictionary mapping company names to market share percentages
        """
        if not self._game_state:
            return {}
            
        segment = self._game_state.market_segments.get(line_id)
        if not segment:
            return {}
            
        # Get total policies in this line
        player_policies = self._game_state.player_company.policies_sold.get(line_id, 0)
        competitor_policies = {}
        for competitor in self._game_state.ai_competitors:
            competitor_policies[competitor.name] = competitor.policies_sold.get(line_id, 0)
            
        total_policies = player_policies + sum(competitor_policies.values())
        if total_policies == 0:
            return {self._game_state.player_company.name: 0.0}
            
        # Calculate market shares
        market_shares = {
            self._game_state.player_company.name: player_policies / total_policies
        }
        for name, policies in competitor_policies.items():
            market_shares[name] = policies / total_policies
            
        return market_shares
    
    def get_economic_indicators(self) -> Dict[str, Any]:
        """
        Get current economic indicators based on the economic cycle.
        
        Returns:
            A dictionary of economic indicators
        """
        # Calculate cycle position as percentage
        cycle_position = (self._economic_cycle_phase / (2 * math.pi)) * 100
        
        # Calculate growth rate from cycle position
        economic_growth = 3.0 * math.sin(self._economic_cycle_phase)  # -3% to +3%
        
        # Calculate interest rate (inverse relationship with growth, lagged)
        interest_rate = 2.0 - 1.5 * math.sin(self._economic_cycle_phase - math.pi/6)  # 0.5% to 3.5%
        
        # Calculate unemployment rate (inverse relationship with growth, lagged more)
        unemployment = 5.0 - 2.0 * math.sin(self._economic_cycle_phase - math.pi/4)  # 3% to 7%
        
        # Calculate inflation rate (follows growth with lag)
        inflation = 2.0 + 1.0 * math.sin(self._economic_cycle_phase - math.pi/3)  # 1% to 3%
        
        # Determine market phase description
        if 0 <= cycle_position < 25:
            market_phase = "Early Recovery"
        elif 25 <= cycle_position < 50:
            market_phase = "Expansion"
        elif 50 <= cycle_position < 75:
            market_phase = "Late Cycle"
        else:
            market_phase = "Contraction"
            
        return {
            "cycle_position": cycle_position,
            "market_phase": market_phase,
            "economic_growth": economic_growth,
            "interest_rate": interest_rate,
            "unemployment": unemployment,
            "inflation": inflation
        }
        
    def get_competitive_analysis(self) -> Dict[str, Any]:
        """
        Get competitive analysis data for all market segments.
        
        Returns:
            A dictionary containing competitive analysis data
        """
        if not self._game_state:
            return {}
            
        analysis = {}
        
        for line_id, segment in self._game_state.market_segments.items():
            # Skip if state is not unlocked
            state_id = line_id.split("_")[0]
            if not self._game_state.unlocked_states.get(state_id, False):
                continue
                
            # Get market shares
            market_shares = self.calculate_market_share(line_id)
            
            # Get premium rates
            player_rate = self._game_state.player_company.premium_rates.get(line_id, 0)
            competitor_rates = {}
            for competitor in self._game_state.ai_competitors:
                competitor_rates[competitor.name] = competitor.premium_rates.get(line_id, 0)
                
            # Calculate relative rates (vs market average)
            all_rates = [player_rate] + list(competitor_rates.values())
            avg_rate = sum(all_rates) / len(all_rates)
            
            relative_rates = {
                self._game_state.player_company.name: player_rate / avg_rate
            }
            for name, rate in competitor_rates.items():
                relative_rates[name] = rate / avg_rate
                
            # Get advertising budgets
            player_ad = self._game_state.player_company.advertising_budget.get(line_id, 0)
            competitor_ads = {}
            for competitor in self._game_state.ai_competitors:
                competitor_ads[competitor.name] = competitor.advertising_budget.get(line_id, 0)
                
            analysis[line_id] = {
                "market_size": segment.market_size,
                "current_demand": segment.current_demand,
                "market_shares": market_shares,
                "premium_rates": {
                    self._game_state.player_company.name: player_rate,
                    **competitor_rates
                },
                "relative_rates": relative_rates,
                "advertising_budgets": {
                    self._game_state.player_company.name: player_ad,
                    **competitor_ads
                }
            }
            
        return analysis 