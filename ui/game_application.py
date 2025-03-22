# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.
import pygame
import sys
from typing import Optional, Dict, List

from services.game_service import GameService
from services.market_service import MarketService
from ui.screen_manager import ScreenManager
from ui.screens.main_menu_screen import MainMenuScreen

class GameApplication:
    """
    Main application class for the Insurance Game.
    Acts as the entry point and coordinates all major components.
    """
    
    def __init__(self, width: int = 1200, height: int = 800, title: str = "Insurance Simulation Game"):
        """
        Initialize the game application.
        
        Args:
            width: Window width (default: 1200)
            height: Window height (default: 800)
            title: Window title (default: "Insurance Simulation Game")
        """
        # Initialize pygame
        pygame.init()
        
        # Set up display
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption(title)
        
        # Create services
        self.game_service = GameService()
        self.market_service = MarketService()
        
        # Set up UI
        self.screen_manager = ScreenManager(width, height)
        self._register_screens()
        
        # Game state
        self.clock = pygame.time.Clock()
        self.running = False
        self.fps = 60
        
        # Connect services
        self.game_service.add_observer(self._on_game_state_changed)
    
    def _register_screens(self) -> None:
        """Register all game screens with the screen manager."""
        # Main menu screen
        main_menu = MainMenuScreen(
            self.width, 
            self.height,
            on_new_game=self._on_new_game,
            on_load_game=self._on_load_game,
            on_options=self._on_options,
            on_quit=self._on_quit
        )
        self.screen_manager.add_screen("main_menu", main_menu)
        
        # TODO: Add more screens as they are implemented
    
    def _on_game_state_changed(self, game_state) -> None:
        """
        Called when the game state changes.
        Updates the market service with the new game state.
        
        Args:
            game_state: The updated game state
        """
        if game_state:
            self.market_service.set_game_state(game_state)
    
    def _on_new_game(self) -> None:
        """Called when the New Game button is clicked."""
        # TODO: Show company setup screen
        # For now, create a default new game
        self.game_service.new_game("Player Insurance Co.")
        
        # TODO: Navigate to game screen
        print("New game started!")
    
    def _on_load_game(self) -> None:
        """Called when the Load Game button is clicked."""
        # TODO: Show load game screen
        print("Load game!")
    
    def _on_options(self) -> None:
        """Called when the Options button is clicked."""
        # TODO: Show options screen
        print("Options!")
    
    def _on_quit(self) -> None:
        """Called when the Quit button is clicked."""
        self.quit()
    
    def run(self) -> None:
        """Run the game loop."""
        # Activate the main menu screen
        self.screen_manager.activate_screen("main_menu")
        
        # Main game loop
        self.running = True
        while self.running:
            # Calculate time delta
            delta_time = self.clock.tick(self.fps) / 1000.0
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    # Handle window resize
                    self.width, self.height = event.size
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                    self.screen_manager.resize(self.width, self.height)
                else:
                    # Pass event to screen manager
                    self.screen_manager.handle_event(event)
            
            # Update game state
            self.screen_manager.update(delta_time)
            
            # Render
            self.screen.fill((240, 240, 240))  # Light gray background
            self.screen_manager.draw(self.screen)
            pygame.display.flip()
        
        # Clean up
        pygame.quit()
    
    def quit(self) -> None:
        """Quit the game."""
        self.running = False

# Run the game if this module is executed directly
if __name__ == "__main__":
    app = GameApplication()
    app.run() 