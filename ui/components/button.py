import pygame
from typing import Optional, Callable, Tuple

from ui.components.base_component import BaseComponent
from ui.components.colors import Colors

class Button(BaseComponent):
    """
    Modern button component with rounded corners and hover effects.
    """
    def __init__(self, 
                 x: int, 
                 y: int, 
                 width: int, 
                 height: int, 
                 text: str, 
                 font: pygame.font.Font,
                 on_click: Optional[Callable[[], None]] = None,
                 color: Tuple[int, int, int] = Colors.PRIMARY,
                 hover_color: Tuple[int, int, int] = Colors.PRIMARY_LIGHT, 
                 text_color: Tuple[int, int, int] = Colors.WHITE,
                 border_radius: int = 8,
                 icon: Optional[pygame.Surface] = None,
                 icon_padding: int = 5):
        super().__init__(x, y, width, height)
        self.text = text
        self.font = font
        self.on_click = on_click
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.icon = icon  # Surface object for icon
        self.icon_padding = icon_padding
        self.is_hovered = False
        self.is_pressed = False
        
        # Shadow and border
        self.shadow_color = Colors.GRAY_DARK
        self.shadow_offset = 2
        self.border_color = None  # Optional border
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the button on the provided surface.
        
        Args:
            surface: Pygame surface to draw on
        """
        if not self.visible:
            return
            
        # Determine button color based on state
        if not self.enabled:
            color = Colors.GRAY_MEDIUM
            rect = self.rect
        elif self.is_pressed and self.is_hovered:
            color = self.color  # Darker when pressed
            # Move button slightly to give pressed effect
            rect = self.rect.move(1, 1)
        elif self.is_hovered:
            color = self.hover_color
            rect = self.rect
        else:
            color = self.color
            rect = self.rect
        
        # Draw shadow (if not pressed)
        if not (self.is_pressed and self.is_hovered):
            shadow_rect = self.rect.move(self.shadow_offset, self.shadow_offset)
            pygame.draw.rect(surface, self.shadow_color, shadow_rect, 
                            border_radius=self.border_radius, width=0)
        
        # Draw button background
        pygame.draw.rect(surface, color, rect, border_radius=self.border_radius)
        
        # Draw border if specified
        if self.border_color:
            pygame.draw.rect(surface, self.border_color, rect, 
                            border_radius=self.border_radius, width=1)
        
        # Calculate text position
        if self.icon:
            # If we have an icon, position text to the right of it
            icon_width = self.icon.get_width() + self.icon_padding
            text_surface = self.font.render(self.text, True, self.text_color)
            
            # Center the icon+text combination
            total_width = icon_width + text_surface.get_width()
            x = rect.centerx - total_width // 2
            
            # Draw icon
            icon_y = rect.centery - self.icon.get_height() // 2
            surface.blit(self.icon, (x, icon_y))
            
            # Draw text
            surface.blit(text_surface, (x + icon_width, rect.centery - text_surface.get_height() // 2))
        else:
            # Just center the text
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for the button.
        
        Args:
            event: The pygame event
            
        Returns:
            True if the event was handled, False otherwise
        """
        if not self.visible or not self.enabled:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.is_pressed = True
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.is_pressed
            self.is_pressed = False
            
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos) and was_pressed:
                if self.on_click:
                    self.on_click()
                return True
                
        return False
    
    def set_text(self, text: str) -> None:
        """Update the button text."""
        self.text = text
    
    def set_on_click(self, on_click: Callable[[], None]) -> None:
        """Set the button's click handler."""
        self.on_click = on_click
    
    def set_icon(self, icon: pygame.Surface) -> None:
        """Set the button icon."""
        self.icon = icon
        
    def set_border(self, color: Tuple[int, int, int]) -> None:
        """Set the button border color."""
        self.border_color = color 