# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.

import pygame
from .colors import Colors

class Panel:
    """
    A panel component with optional header, border, and shadow.
    Used to group related UI elements with a consistent style.
    """
    def __init__(self, rect, title=None, title_font=None, 
                 bg_color=Colors.BG_PANEL,
                 header_color=Colors.BG_HEADER,
                 border_color=Colors.GRAY_LIGHT,
                 shadow_size=3,
                 border_radius=8):
        self.rect = rect
        self.title = title
        self.title_font = title_font
        self.bg_color = bg_color
        self.header_color = header_color
        self.border_color = border_color
        self.shadow_size = shadow_size
        self.border_radius = border_radius
        self.content_rect = self._calculate_content_rect()
        
    def _calculate_content_rect(self):
        """Calculate the content rectangle based on whether we have a header."""
        if self.title and self.title_font:
            # Calculate header height based on font and some padding
            header_height = self.title_font.get_height() + 16
            
            # Create content rect with header taken into account
            return pygame.Rect(
                self.rect.left + 10,
                self.rect.top + header_height + 5,
                self.rect.width - 20,
                self.rect.height - header_height - 15
            )
        else:
            # No header, so content area just has some padding
            return pygame.Rect(
                self.rect.left + 10,
                self.rect.top + 10,
                self.rect.width - 20,
                self.rect.height - 20
            )
    
    def draw(self, screen):
        """Draw the panel with optional header, border and shadow."""
        # Draw shadow
        if self.shadow_size > 0:
            shadow_rect = self.rect.copy()
            shadow_rect.x += self.shadow_size
            shadow_rect.y += self.shadow_size
            pygame.draw.rect(screen, Colors.GRAY_DARK, shadow_rect, 
                            border_radius=self.border_radius)
        
        # Draw main panel background
        pygame.draw.rect(screen, self.bg_color, self.rect, 
                        border_radius=self.border_radius)
        
        # Draw border if specified
        if self.border_color:
            pygame.draw.rect(screen, self.border_color, self.rect, 
                            border_radius=self.border_radius, width=1)
        
        # Draw header if specified
        if self.title and self.title_font:
            # Calculate header rectangle
            header_height = self.title_font.get_height() + 16
            header_rect = pygame.Rect(
                self.rect.left, 
                self.rect.top, 
                self.rect.width, 
                header_height
            )
            
            # Draw header background with rounded top corners
            pygame.draw.rect(screen, self.header_color, header_rect, 
                            border_top_left_radius=self.border_radius,
                            border_top_right_radius=self.border_radius)
            
            # Draw header title
            title_surface = self.title_font.render(self.title, True, Colors.TEXT_HEADER)
            title_rect = title_surface.get_rect(
                center=(header_rect.centerx, header_rect.centery)
            )
            screen.blit(title_surface, title_rect)
    
    def get_content_rect(self):
        """Get the rectangle representing the content area of the panel."""
        return self.content_rect
    
    def contains_point(self, point):
        """Check if the panel contains the given point."""
        return self.rect.collidepoint(point)
        
    def set_title(self, title):
        """Update the panel title."""
        self.title = title
        # Recalculate content rect if title presence changes
        if (title and not self.title) or (not title and self.title):
            self.content_rect = self._calculate_content_rect() 