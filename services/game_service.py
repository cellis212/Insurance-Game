# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.
from typing import Optional, Dict, Any, List, Callable
import json
import os

from state.game_state import GameState
from data.models.company import Company
from data.models.market_segment import MarketSegment

class GameService:
    """
    Service responsible for coordinating game logic and state management.
    Acts as a facade for game operations, abstracting implementation details.
    """
    
    def __init__(self):
        self._game_state: Optional[GameState] = None
        self._observers: List[Callable[[GameState], None]] = []
    
    def new_game(self, company_name: str, initial_state: str = "CA") -> GameState:
        """
        Start a new game with the given company name and initial state.
        
        Args:
            company_name: The player's company name
            initial_state: The initial state to start in (default: CA)
            
        Returns:
            The newly created GameState
        """
        self._game_state = GameState(initial_state=initial_state, company_name=company_name)
        self._initialize_game_state()
        self._notify_observers()
        return self._game_state
    
    def _initialize_game_state(self) -> None:
        """Initialize market segments, assets, and other game state elements."""
        if not self._game_state:
            return
            
        # Initialize states
        self._game_state.states = {
            "CA": {
                "name": "California",
                "population": 39_000_000,
                "catastrophe_risk": 0.05,  # 5% annual earthquake risk
                "growth_rate": 0.01,
                "price_sensitivity": 1.2
            },
            "FL": {
                "name": "Florida",
                "population": 21_000_000,
                "catastrophe_risk": 0.15,  # 15% annual hurricane risk
                "growth_rate": 0.02,
                "price_sensitivity": 1.0
            }
        }
        
        # Initialize unlocked states (only CA is available at start)
        self._game_state.unlocked_states = {
            "CA": True,
            "FL": False
        }
        
        # Initialize market segments
        self._game_state.market_segments = {
            "CA_auto": MarketSegment(
                name="California Auto Insurance",
                base_risk=0.05,  # 5% annual claim rate
                price_sensitivity=1.2,
                market_size=2_000_000,  # 2 million policies total
                current_demand=2_000_000
            ),
            "CA_home": MarketSegment(
                name="California Home Insurance",
                base_risk=0.03,  # 3% annual claim rate
                price_sensitivity=0.9,
                market_size=1_500_000,  # 1.5 million policies total
                current_demand=1_500_000
            ),
            "FL_auto": MarketSegment(
                name="Florida Auto Insurance",
                base_risk=0.06,  # 6% annual claim rate
                price_sensitivity=1.1,
                market_size=1_200_000,  # 1.2 million policies total
                current_demand=1_200_000
            ),
            "FL_home": MarketSegment(
                name="Florida Home Insurance",
                base_risk=0.08,  # 8% annual claim rate (higher than CA)
                price_sensitivity=0.8,
                market_size=1_000_000,  # 1 million policies total
                current_demand=1_000_000
            )
        }
        
        # Initialize market rates
        self._game_state.base_market_rates = {
            "CA_auto": 1200,  # $1,200 annual premium
            "CA_home": 1500,  # $1,500 annual premium
            "FL_auto": 1500,  # $1,500 annual premium
            "FL_home": 2200   # $2,200 annual premium
        }
        
        # Initialize player premium rates to match market rates
        self._game_state.player_company.premium_rates = dict(self._game_state.base_market_rates)
        
        # Initialize advertising budgets (initial zero budgets)
        for line_id in self._game_state.market_segments.keys():
            self._game_state.player_company.advertising_budget[line_id] = 0.0
            
        # Set up claim distributions
        self._game_state.claim_distributions = {
            "CA_auto": {
                "mean": 7.3,  # Log-normal mean (≈1,500 average claim)
                "sigma": 0.8,  # Log-normal sigma (spread of claims)
                "cat_mean": 0.0  # Not applicable for auto
            },
            "CA_home": {
                "mean": 8.0,  # Log-normal mean (≈3,000 average claim)
                "sigma": 1.0,  # Log-normal sigma (spread of claims)
                "cat_mean": 9.5,  # ≈15,000 average catastrophe claim
            },
            "FL_auto": {
                "mean": 7.4,  # Log-normal mean (≈1,650 average claim)
                "sigma": 0.8,  # Log-normal sigma (spread of claims)
                "cat_mean": 0.0  # Not applicable for auto
            },
            "FL_home": {
                "mean": 8.2,  # Log-normal mean (≈3,650 average claim)
                "sigma": 1.0,  # Log-normal sigma (spread of claims)
                "cat_mean": 10.0,  # ≈22,000 average catastrophe claim
            }
        }
        
        # Initialize financial history
        self._game_state.financial_history = []
    
    def end_turn(self) -> Dict[str, Any]:
        """
        Process the end of a turn, updating the game state.
        
        Returns:
            A dictionary containing turn summary information
        """
        if not self._game_state:
            raise ValueError("Game not initialized")
            
        # Process AI decisions first (they're reactive to player)
        for competitor in self._game_state.ai_competitors:
            competitor.make_decisions(self._game_state)
            
        # Update game state
        self._game_state.update()
        
        # Notify observers that the game state has changed
        self._notify_observers()
        
        # Return turn summary info
        if self._game_state.financial_history:
            latest_report = self._game_state.financial_history[-1]
            return latest_report.generate_summary()
        else:
            return {"message": "No financial data available yet"}
    
    def save_game(self, filename: str = "save.json") -> None:
        """
        Save the current game state to a file.
        
        Args:
            filename: The name of the save file
        """
        if not self._game_state:
            raise ValueError("No game to save")
            
        # Make sure saves directory exists
        os.makedirs("saves", exist_ok=True)
            
        # Convert game state to dict
        game_data = self._game_state.to_dict()
        
        # Save to file
        with open(os.path.join("saves", filename), "w") as f:
            json.dump(game_data, f, indent=2)
    
    def load_game(self, filename: str = "save.json") -> GameState:
        """
        Load a game state from a file.
        
        Args:
            filename: The name of the save file
            
        Returns:
            The loaded GameState
        """
        # Load from file
        with open(os.path.join("saves", filename), "r") as f:
            game_data = json.load(f)
        
        # Create game state from dict
        self._game_state = GameState.from_dict(game_data)
        
        # Notify observers
        self._notify_observers()
        
        return self._game_state
    
    def get_game_state(self) -> Optional[GameState]:
        """
        Get the current game state.
        
        Returns:
            The current GameState or None if no game is in progress
        """
        return self._game_state
    
    def add_observer(self, observer: Callable[[GameState], None]) -> None:
        """
        Add an observer to be notified when the game state changes.
        
        Args:
            observer: A function that takes a GameState as an argument
        """
        self._observers.append(observer)
    
    def remove_observer(self, observer: Callable[[GameState], None]) -> None:
        """
        Remove an observer.
        
        Args:
            observer: The observer to remove
        """
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _notify_observers(self) -> None:
        """Notify all observers that the game state has changed."""
        for observer in self._observers:
            observer(self._game_state) 