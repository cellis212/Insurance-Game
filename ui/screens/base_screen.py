# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.
import pygame
from typing import List, Optional, Dict, Any, Callable

from ui.components.base_component import BaseComponent

class BaseScreen(BaseComponent):
    """Base class for all game screens."""
    
    def __init__(self, width: int, height: int):
        """
        Initialize the screen.
        
        Args:
            width: Screen width
            height: Screen height
        """
        super().__init__(0, 0, width, height)
        self.components: List[BaseComponent] = []
        self.background_color = (240, 240, 240)  # Light gray background
        self.active = False
    
    def add_component(self, component: BaseComponent) -> None:
        """
        Add a UI component to the screen.
        
        Args:
            component: The component to add
        """
        self.components.append(component)
        component.set_parent(self)
    
    def remove_component(self, component: BaseComponent) -> None:
        """
        Remove a UI component from the screen.
        
        Args:
            component: The component to remove
        """
        if component in self.components:
            self.components.remove(component)
            component.set_parent(None)
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the screen and all its components.
        
        Args:
            surface: Pygame surface to draw on
        """
        if not self.visible:
            return
            
        # Fill background
        surface.fill(self.background_color, self.rect)
        
        # Draw all components
        for component in self.components:
            if component.visible:
                component.draw(surface)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle a pygame event, passing it to child components.
        
        Args:
            event: The pygame event
            
        Returns:
            True if the event was handled, False otherwise
        """
        if not self.visible or not self.active:
            return False
            
        # Pass event to components in reverse order (top component first)
        for component in reversed(self.components):
            if component.visible and component.enabled and component.handle_event(event):
                return True
                
        # Handle screen-level events
        return self._handle_screen_event(event)
    
    def _handle_screen_event(self, event: pygame.event.Event) -> bool:
        """
        Handle screen-level events.
        
        Args:
            event: The pygame event
            
        Returns:
            True if the event was handled, False otherwise
        """
        # Default implementation does nothing
        return False
    
    def update(self, delta_time: float) -> None:
        """
        Update the screen and all its components.
        
        Args:
            delta_time: Time elapsed since last update
        """
        if not self.visible or not self.active:
            return
            
        # Update all components
        for component in self.components:
            if component.visible and component.enabled:
                component.update(delta_time)
    
    def activate(self) -> None:
        """Activate the screen."""
        self.active = True
        self.visible = True
    
    def deactivate(self) -> None:
        """Deactivate the screen."""
        self.active = False
    
    def set_size(self, width: int, height: int) -> None:
        """
        Set the size of the screen.
        
        Args:
            width: New width
            height: New height
        """
        super().set_size(width, height)
        # Subclasses should override to reposition components as needed 