# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.

import pygame
from typing import Optional, Tuple, Union

from ui.components.base_component import BaseComponent
from ui.components.colors import Colors

class Panel(BaseComponent):
    """
    A panel component with optional header, border, and shadow.
    Used to group related UI elements with a consistent style.
    """
    def __init__(self, 
                 x_or_rect: Union[int, pygame.Rect], 
                 y: Optional[int] = None, 
                 width: Optional[int] = None, 
                 height: Optional[int] = None,
                 title: Optional[str] = None,
                 font: Optional[pygame.font.Font] = None,
                 color: Tuple[int, int, int] = Colors.BG_PANEL,
                 border_color: Optional[Tuple[int, int, int]] = Colors.GRAY_LIGHT,
                 text_color: Tuple[int, int, int] = Colors.TEXT_DEFAULT,
                 border_radius: int = 8,
                 title_height: int = 30,
                 # Legacy parameters for compatibility
                 title_font: Optional[pygame.font.Font] = None,
                 bg_color: Optional[Tuple[int, int, int]] = None,
                 header_color: Optional[Tuple[int, int, int]] = None,
                 shadow_size: int = 3):
        """
        Initialize the panel.
        
        Args:
            x_or_rect: X position or Rect object
            y: Y position (not used if x_or_rect is a Rect)
            width: Width of the panel (not used if x_or_rect is a Rect)
            height: Height of the panel (not used if x_or_rect is a Rect)
            title: Optional title text
            font: Font for the title
            color: Background color
            border_color: Border color (None for no border)
            text_color: Text color
            border_radius: Border radius for rounded corners
            title_height: Height of the title bar
            
            # Legacy parameters
            title_font: Font for the title (legacy)
            bg_color: Background color (legacy)
            header_color: Title bar color (legacy)
            shadow_size: Shadow size (legacy)
        """
        # Handle both new and legacy initialization
        if isinstance(x_or_rect, pygame.Rect):
            rect = x_or_rect
            super().__init__(rect.x, rect.y, rect.width, rect.height)
        else:
            super().__init__(x_or_rect, y, width, height)
        
        # Handle legacy parameters
        self.title = title
        self.font = font or title_font
        self.color = bg_color or color
        self.border_color = border_color
        self.text_color = text_color
        self.border_radius = border_radius
        
        # Title bar configuration
        self.title_bg_color = header_color or Colors.BG_HEADER
        self.title_height = title_height
        
        # Shadow configuration
        self.shadow_color = Colors.GRAY_DARK
        self.shadow_offset = shadow_size
        self.shadow_enabled = shadow_size > 0
        
        # Calculate content rectangle
        self.content_rect = self._calculate_content_rect()
        
    def _calculate_content_rect(self):
        """Calculate the content rectangle based on whether we have a header."""
        if self.title and self.font:
            # Calculate header height based on font and some padding
            header_height = self.font.get_height() + 16
            
            # Create content rect with header taken into account
            return pygame.Rect(
                self.x + 10,
                self.y + header_height + 5,
                self.width - 20,
                self.height - header_height - 15
            )
        else:
            # No header, so content area just has some padding
            return pygame.Rect(
                self.x + 10,
                self.y + 10,
                self.width - 20,
                self.height - 20
            )
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the panel.
        
        Args:
            surface: Pygame surface to draw on
        """
        if not self.visible:
            return
            
        # Draw shadow
        if self.shadow_enabled:
            shadow_rect = self.rect.move(self.shadow_offset, self.shadow_offset)
            pygame.draw.rect(surface, self.shadow_color, shadow_rect, 
                            border_radius=self.border_radius)
        
        # Draw panel background
        pygame.draw.rect(surface, self.color, self.rect, border_radius=self.border_radius)
        
        # Draw border
        if self.border_color:
            pygame.draw.rect(surface, self.border_color, self.rect, 
                            border_radius=self.border_radius, width=1)
        
        # Draw title bar
        if self.title and self.font:
            # Calculate header height based on font and some padding
            header_height = self.font.get_height() + 16
            
            # Draw title background
            title_rect = pygame.Rect(self.x, self.y, self.width, header_height)
            pygame.draw.rect(surface, self.title_bg_color, title_rect, 
                            border_top_left_radius=self.border_radius,
                            border_top_right_radius=self.border_radius)
            
            # Draw title text
            title_text = self.font.render(self.title, True, Colors.TEXT_HEADER)
            title_text_rect = title_text.get_rect(
                center=(self.x + self.width // 2, self.y + header_height // 2)
            )
            surface.blit(title_text, title_text_rect)
    
    def get_content_rect(self) -> pygame.Rect:
        """
        Get the rectangle for the content area (excluding title bar).
        
        Returns:
            Pygame Rect for the content area
        """
        return self.content_rect
    
    def contains_point(self, point):
        """Check if the panel contains the given point."""
        return self.rect.collidepoint(point)
        
    def set_title(self, title: str) -> None:
        """
        Set or change the panel title.
        
        Args:
            title: New title text
        """
        self.title = title
        self.content_rect = self._calculate_content_rect() 