import pygame
from .colors import Colors

class Button:
    """
    Modern button component with rounded corners and hover effects.
    """
    def __init__(self, rect, text, font, 
                 color=Colors.PRIMARY,
                 hover_color=Colors.PRIMARY_LIGHT, 
                 text_color=Colors.WHITE,
                 border_radius=8,
                 icon=None,
                 icon_padding=5,
                 disabled=False):
        self.rect = rect
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.icon = icon  # Surface object for icon
        self.icon_padding = icon_padding
        self.disabled = disabled
        self.is_hovered = False
        self.is_pressed = False
        
        # Shadow and border
        self.shadow_color = Colors.GRAY_DARK
        self.shadow_offset = 2
        self.border_color = None  # Optional border
    
    def draw(self, screen):
        # Determine button color based on state
        if self.disabled:
            color = Colors.GRAY_MEDIUM
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
            pygame.draw.rect(screen, self.shadow_color, shadow_rect, 
                            border_radius=self.border_radius, width=0)
        
        # Draw button background
        pygame.draw.rect(screen, color, rect, border_radius=self.border_radius)
        
        # Draw border if specified
        if self.border_color:
            pygame.draw.rect(screen, self.border_color, rect, 
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
            screen.blit(self.icon, (x, icon_y))
            
            # Draw text
            screen.blit(text_surface, (x + icon_width, rect.centery - text_surface.get_height() // 2))
        else:
            # Just center the text
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        """Handle mouse events and return True if clicked."""
        if self.disabled:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.is_pressed = True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.is_pressed
            self.is_pressed = False
            
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos) and was_pressed:
                return True
                
        return False
    
    def set_text(self, text):
        """Update the button text."""
        self.text = text
        
    def set_disabled(self, disabled):
        """Enable or disable the button."""
        self.disabled = disabled
    
    def set_icon(self, icon):
        """Set the button icon."""
        self.icon = icon 