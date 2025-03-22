# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.
import pygame
from typing import Tuple, Optional, Dict, Any, Callable

class BaseComponent:
    """Base class for all UI components."""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        """
        Initialize the UI component.
        
        Args:
            x: X position
            y: Y position
            width: Width of the component
            height: Height of the component
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
        self.enabled = True
        self.parent = None
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the component on the provided surface.
        
        Args:
            surface: Pygame surface to draw on
        """
        pass  # Implement in derived classes
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle a pygame event.
        
        Args:
            event: The pygame event
            
        Returns:
            True if the event was handled, False otherwise
        """
        return False  # Implement in derived classes
    
    def update(self, delta_time: float) -> None:
        """
        Update component state.
        
        Args:
            delta_time: Time elapsed since last update
        """
        pass  # Implement in derived classes
    
    def is_point_inside(self, point: Tuple[int, int]) -> bool:
        """
        Check if a point is inside the component.
        
        Args:
            point: (x, y) coordinates
            
        Returns:
            True if the point is inside the component, False otherwise
        """
        if not self.visible:
            return False
            
        return self.rect.collidepoint(point)
    
    def set_position(self, x: int, y: int) -> None:
        """
        Set the position of the component.
        
        Args:
            x: New X position
            y: New Y position
        """
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
    
    def set_size(self, width: int, height: int) -> None:
        """
        Set the size of the component.
        
        Args:
            width: New width
            height: New height
        """
        self.width = width
        self.height = height
        self.rect.width = width
        self.rect.height = height
    
    def set_rect(self, rect: pygame.Rect) -> None:
        """
        Set the component's rect directly.
        
        Args:
            rect: New pygame Rect
        """
        self.rect = rect
        self.x = rect.x
        self.y = rect.y
        self.width = rect.width
        self.height = rect.height
    
    def show(self) -> None:
        """Make the component visible."""
        self.visible = True
    
    def hide(self) -> None:
        """Hide the component."""
        self.visible = False
    
    def enable(self) -> None:
        """Enable the component."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable the component."""
        self.enabled = False
    
    def set_parent(self, parent: 'BaseComponent') -> None:
        """
        Set the parent component.
        
        Args:
            parent: The parent component
        """
        self.parent = parent 