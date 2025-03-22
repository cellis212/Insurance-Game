# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.
import pygame
from typing import Dict, Optional, List

from ui.screens.base_screen import BaseScreen

class ScreenManager:
    """Manages game screens and navigation between them."""
    
    def __init__(self, width: int, height: int):
        """
        Initialize the screen manager.
        
        Args:
            width: Screen width
            height: Screen height
        """
        self.width = width
        self.height = height
        self.screens: Dict[str, BaseScreen] = {}
        self.active_screen: Optional[str] = None
        self.screen_history: List[str] = []
        self.max_history = 10  # Maximum number of screens to remember
    
    def add_screen(self, name: str, screen: BaseScreen) -> None:
        """
        Add a screen to the manager.
        
        Args:
            name: Screen identifier
            screen: The screen to add
        """
        self.screens[name] = screen
        screen.set_size(self.width, self.height)
    
    def remove_screen(self, name: str) -> None:
        """
        Remove a screen from the manager.
        
        Args:
            name: Screen identifier
        """
        if name in self.screens:
            if self.active_screen == name:
                self.deactivate_screen()
            del self.screens[name]
    
    def get_screen(self, name: str) -> Optional[BaseScreen]:
        """
        Get a screen by name.
        
        Args:
            name: Screen identifier
            
        Returns:
            The screen or None if not found
        """
        return self.screens.get(name)
    
    def activate_screen(self, name: str) -> None:
        """
        Activate a screen.
        
        Args:
            name: Screen identifier
        """
        if name not in self.screens:
            return
            
        # Deactivate current screen
        self.deactivate_screen()
        
        # Activate new screen
        self.active_screen = name
        self.screens[name].activate()
        
        # Add to history
        if self.active_screen and self.active_screen != name:
            self.screen_history.append(self.active_screen)
            if len(self.screen_history) > self.max_history:
                self.screen_history.pop(0)
    
    def deactivate_screen(self) -> None:
        """Deactivate the current screen."""
        if self.active_screen and self.active_screen in self.screens:
            self.screens[self.active_screen].deactivate()
            self.active_screen = None
    
    def go_back(self) -> bool:
        """
        Navigate back to the previous screen.
        
        Returns:
            True if successfully navigated back, False otherwise
        """
        if not self.screen_history:
            return False
            
        previous_screen = self.screen_history.pop()
        if previous_screen in self.screens:
            self.activate_screen(previous_screen)
            return True
            
        return False
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the active screen.
        
        Args:
            surface: Pygame surface to draw on
        """
        if self.active_screen and self.active_screen in self.screens:
            self.screens[self.active_screen].draw(surface)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle a pygame event, passing it to the active screen.
        
        Args:
            event: The pygame event
            
        Returns:
            True if the event was handled, False otherwise
        """
        if self.active_screen and self.active_screen in self.screens:
            return self.screens[self.active_screen].handle_event(event)
            
        return False
    
    def update(self, delta_time: float) -> None:
        """
        Update the active screen.
        
        Args:
            delta_time: Time elapsed since last update
        """
        if self.active_screen and self.active_screen in self.screens:
            self.screens[self.active_screen].update(delta_time)
    
    def resize(self, width: int, height: int) -> None:
        """
        Resize all screens.
        
        Args:
            width: New width
            height: New height
        """
        self.width = width
        self.height = height
        
        for screen in self.screens.values():
            screen.set_size(width, height) 