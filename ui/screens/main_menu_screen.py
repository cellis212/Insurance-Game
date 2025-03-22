# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.
import pygame
from typing import Callable

from ui.screens.base_screen import BaseScreen
from ui.components.button import Button
from ui.components.colors import Colors

class MainMenuScreen(BaseScreen):
    """Main menu screen for the game."""
    
    def __init__(self, width: int, height: int, 
                 on_new_game: Callable[[], None],
                 on_load_game: Callable[[], None],
                 on_options: Callable[[], None],
                 on_quit: Callable[[], None]):
        """
        Initialize the main menu screen.
        
        Args:
            width: Screen width
            height: Screen height
            on_new_game: Function to call when New Game is clicked
            on_load_game: Function to call when Load Game is clicked
            on_options: Function to call when Options is clicked
            on_quit: Function to call when Quit is clicked
        """
        super().__init__(width, height)
        self.background_color = Colors.BACKGROUND_DARK
        
        # Set up fonts
        self.title_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 36)
        
        # Set up action callbacks
        self.on_new_game = on_new_game
        self.on_load_game = on_load_game
        self.on_options = on_options
        self.on_quit = on_quit
        
        # Create UI elements
        self._create_ui()
    
    def _create_ui(self) -> None:
        """Create UI elements for the screen."""
        # Calculate button dimensions and positions
        button_width = 300
        button_height = 60
        button_spacing = 20
        
        # Center buttons horizontally
        button_x = (self.width - button_width) // 2
        
        # Start buttons from near the middle of the screen
        button_start_y = self.height // 2 - 50
        
        # Create buttons
        new_game_btn = Button(
            button_x, 
            button_start_y, 
            button_width, 
            button_height, 
            "New Game", 
            self.button_font,
            on_click=self.on_new_game,
            color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_LIGHT
        )
        self.add_component(new_game_btn)
        
        load_game_btn = Button(
            button_x, 
            button_start_y + button_height + button_spacing, 
            button_width, 
            button_height, 
            "Load Game", 
            self.button_font,
            on_click=self.on_load_game,
            color=Colors.SECONDARY,
            hover_color=Colors.SECONDARY_LIGHT
        )
        self.add_component(load_game_btn)
        
        options_btn = Button(
            button_x, 
            button_start_y + 2 * (button_height + button_spacing), 
            button_width, 
            button_height, 
            "Options", 
            self.button_font,
            on_click=self.on_options,
            color=Colors.TERTIARY,
            hover_color=Colors.TERTIARY_LIGHT
        )
        self.add_component(options_btn)
        
        quit_btn = Button(
            button_x, 
            button_start_y + 3 * (button_height + button_spacing), 
            button_width, 
            button_height, 
            "Quit", 
            self.button_font,
            on_click=self.on_quit,
            color=Colors.DANGER,
            hover_color=Colors.DANGER_LIGHT
        )
        self.add_component(quit_btn)
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the screen.
        
        Args:
            surface: Pygame surface to draw on
        """
        # First draw the base (background)
        super().draw(surface)
        
        # Draw title
        title_text = self.title_font.render("Insurance Simulation Game", True, Colors.WHITE)
        title_rect = title_text.get_rect(centerx=self.width // 2, y=100)
        surface.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_font = pygame.font.Font(None, 36)
        subtitle_text = subtitle_font.render("Build your insurance empire", True, Colors.GRAY_LIGHT)
        subtitle_rect = subtitle_text.get_rect(centerx=self.width // 2, y=180)
        surface.blit(subtitle_text, subtitle_rect)
    
    def set_size(self, width: int, height: int) -> None:
        """
        Resize the screen.
        
        Args:
            width: New width
            height: New height
        """
        old_width, old_height = self.width, self.height
        super().set_size(width, height)
        
        # If dimensions actually changed, recreate UI
        if width != old_width or height != old_height:
            self.components.clear()  # Remove old components
            self._create_ui()  # Recreate with new dimensions 