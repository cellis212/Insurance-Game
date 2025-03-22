import pygame
from typing import Optional, Tuple, Callable, Union

from ui.components.base_component import BaseComponent
from ui.components.colors import Colors

class Slider(BaseComponent):
    """Interactive slider component for selecting numeric values."""
    
    def __init__(self, 
                 x_or_rect: Union[int, pygame.Rect], 
                 y: Optional[int] = None, 
                 width: Optional[int] = None, 
                 height: Optional[int] = None,
                 min_value: float = 0.0,
                 max_value: float = 100.0,
                 initial_value: Optional[float] = None,
                 step: Optional[float] = None,
                 on_change: Optional[Callable[[float], None]] = None,
                 label: Optional[str] = None,
                 font: Optional[pygame.font.Font] = None,
                 show_value: bool = True,
                 track_color: Tuple[int, int, int] = Colors.GRAY_LIGHT,
                 handle_color: Tuple[int, int, int] = Colors.PRIMARY,
                 hover_color: Tuple[int, int, int] = Colors.PRIMARY_LIGHT,
                 text_color: Tuple[int, int, int] = Colors.TEXT_DEFAULT,
                 handle_radius: int = 10):
        """
        Initialize the slider.
        
        Args:
            x_or_rect: X position or Rect object
            y: Y position (not used if x_or_rect is a Rect)
            width: Width of the panel (not used if x_or_rect is a Rect)
            height: Height of the panel (not used if x_or_rect is a Rect)
            min_value: Minimum value
            max_value: Maximum value
            initial_value: Initial value (defaults to min_value)
            step: Optional step size (None for continuous)
            on_change: Function to call when value changes
            label: Optional label text
            font: Font for label and value text
            show_value: Whether to display the current value
            track_color: Color of the slider track
            handle_color: Color of the slider handle
            hover_color: Color of the handle when hovered
            text_color: Color of the label and value text
            handle_radius: Radius of the handle circle
        """
        # Handle both new and legacy initialization
        if isinstance(x_or_rect, pygame.Rect):
            rect = x_or_rect
            super().__init__(rect.x, rect.y, rect.width, rect.height)
        else:
            super().__init__(x_or_rect, y, width, height)
        
        # Slider range and value
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value if initial_value is not None else min_value
        self.step = step
        
        # Callback
        self.on_change = on_change
        
        # Appearance
        self.label = label
        self.font = font
        self.show_value = show_value
        self.track_color = track_color
        self.handle_color = handle_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.handle_radius = handle_radius
        
        # State
        self.is_dragging = False
        self.is_hovered = False
        
        # Track dimensions
        self.track_height = 4
        self.track_rect = pygame.Rect(
            self.x + self.handle_radius,
            self.y + (self.height - self.track_height) // 2,
            self.width - 2 * self.handle_radius,
            self.track_height
        )
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the slider.
        
        Args:
            surface: Pygame surface to draw on
        """
        if not self.visible:
            return
            
        # Draw label if specified and font is available
        if self.label and self.font:
            label_text = self.font.render(self.label, True, self.text_color)
            label_rect = label_text.get_rect(x=self.x, y=self.y - 25)
            surface.blit(label_text, label_rect)
        
        # Draw track
        pygame.draw.rect(surface, self.track_color, self.track_rect, border_radius=self.track_height // 2)
        
        # Draw handle
        handle_x = self._value_to_x(self.value)
        handle_y = self.y + self.height // 2
        handle_color = self.hover_color if self.is_hovered or self.is_dragging else self.handle_color
        pygame.draw.circle(surface, handle_color, (handle_x, handle_y), self.handle_radius)
        
        # Draw value if specified and font is available
        if self.show_value and self.font:
            # Format value based on step (integer if step is integer)
            if self.step and self.step.is_integer():
                value_text = f"{int(self.value)}"
            else:
                value_text = f"{self.value:.1f}"
                
            value_surface = self.font.render(value_text, True, self.text_color)
            value_rect = value_surface.get_rect(
                midright=(self.x + self.width, self.y + self.height // 2)
            )
            surface.blit(value_surface, value_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for the slider.
        
        Args:
            event: The pygame event
            
        Returns:
            True if the event was handled, False otherwise
        """
        if not self.visible or not self.enabled:
            return False
            
        # Track mouse position for hover state
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            handle_x = self._value_to_x(self.value)
            handle_y = self.y + self.height // 2
            
            # Check if mouse is over handle
            handle_rect = pygame.Rect(
                handle_x - self.handle_radius,
                handle_y - self.handle_radius,
                self.handle_radius * 2,
                self.handle_radius * 2
            )
            self.is_hovered = handle_rect.collidepoint(mouse_pos)
            
            # Update value if dragging
            if self.is_dragging:
                self._update_value_from_x(mouse_pos[0])
                return True
        
        # Start dragging on mouse down
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            handle_x = self._value_to_x(self.value)
            handle_y = self.y + self.height // 2
            
            # Check if mouse is over handle or track
            handle_rect = pygame.Rect(
                handle_x - self.handle_radius,
                handle_y - self.handle_radius,
                self.handle_radius * 2,
                self.handle_radius * 2
            )
            track_rect = pygame.Rect(
                self.track_rect.x - self.handle_radius,
                self.track_rect.y - self.handle_radius,
                self.track_rect.width + 2 * self.handle_radius,
                self.track_rect.height + 2 * self.handle_radius
            )
            
            if handle_rect.collidepoint(mouse_pos):
                self.is_dragging = True
                return True
            elif track_rect.collidepoint(mouse_pos):
                self._update_value_from_x(mouse_pos[0])
                self.is_dragging = True
                return True
        
        # Stop dragging on mouse up
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                return True
                
        return False
    
    def _value_to_x(self, value: float) -> int:
        """Convert a value to an x-coordinate."""
        # Calculate the position within the track
        track_width = self.track_rect.width
        value_ratio = (value - self.min_value) / (self.max_value - self.min_value)
        x_offset = int(track_width * value_ratio)
        
        # Add track left position and account for handle radius
        return self.track_rect.left + x_offset
    
    def _update_value_from_x(self, x: int) -> None:
        """Update the value based on an x-coordinate."""
        # Constrain x to track bounds
        x = max(self.track_rect.left, min(x, self.track_rect.right))
        
        # Calculate value based on position
        track_width = self.track_rect.width
        x_ratio = (x - self.track_rect.left) / track_width
        new_value = self.min_value + x_ratio * (self.max_value - self.min_value)
        
        # Apply step if specified
        if self.step:
            new_value = round(new_value / self.step) * self.step
        
        # Constrain to min/max
        new_value = max(self.min_value, min(new_value, self.max_value))
        
        # Only update if value actually changed
        if new_value != self.value:
            self.value = new_value
            if self.on_change:
                self.on_change(new_value)
    
    def set_value(self, value: float) -> None:
        """
        Set the slider value.
        
        Args:
            value: New value
        """
        # Constrain to min/max
        value = max(self.min_value, min(value, self.max_value))
        
        # Apply step if specified
        if self.step:
            value = round(value / self.step) * self.step
            
        # Only update if value actually changed
        if value != self.value:
            self.value = value
            if self.on_change:
                self.on_change(value)
    
    def get_value(self) -> float:
        """
        Get the current slider value.
        
        Returns:
            The current value
        """
        return self.value 