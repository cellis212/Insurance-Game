import pygame
from .colors import Colors

class Slider:
    """
    A modern slider component with value labels and smooth interaction.
    """
    def __init__(self, rect, min_value, max_value, current_value,
                 track_color=Colors.GRAY_LIGHT,
                 handle_color=Colors.PRIMARY,
                 handle_hover_color=Colors.PRIMARY_LIGHT,
                 handle_active_color=Colors.PRIMARY_DARK,
                 label_font=None,
                 show_value=True,
                 value_format="${:.2f}",
                 show_min_max=True,
                 step=None,
                 on_change=None):
        self.rect = rect
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = max(min_value, min(max_value, current_value))  # Clamp to range
        self.track_color = track_color
        self.track_fill_color = handle_color
        self.handle_color = handle_color
        self.handle_hover_color = handle_hover_color
        self.handle_active_color = handle_active_color
        self.label_font = label_font
        self.show_value = show_value
        self.value_format = value_format
        self.show_min_max = show_min_max
        self.step = step
        self.on_change = on_change
        
        self.active = False
        self.hovered = False
        self.handle_radius = min(rect.height // 2, 12)  # Handle radius based on height, max 12px
        self.track_height = max(4, rect.height // 4)    # Track height, min 4px
    
    def draw(self, screen):
        """Draw the slider with track, handle, and optional labels."""
        # Calculate track rects
        track_y = self.rect.centery - self.track_height // 2
        track_rect = pygame.Rect(
            self.rect.left,
            track_y,
            self.rect.width,
            self.track_height
        )
        
        # Calculate the position of the handle
        value_ratio = (self.current_value - self.min_value) / (self.max_value - self.min_value)
        handle_x = self.rect.left + int(value_ratio * self.rect.width)
        handle_pos = (handle_x, self.rect.centery)
        
        # Calculate filled part of track
        fill_rect = pygame.Rect(
            self.rect.left,
            track_y,
            handle_x - self.rect.left,
            self.track_height
        )
        
        # Draw track background (gray)
        pygame.draw.rect(screen, self.track_color, track_rect, 
                        border_radius=self.track_height // 2)
        
        # Draw filled part of track
        if fill_rect.width > 0:
            pygame.draw.rect(screen, self.track_fill_color, fill_rect, 
                            border_radius=self.track_height // 2)
        
        # Determine handle color based on state
        if self.active:
            handle_color = self.handle_active_color
        elif self.hovered:
            handle_color = self.handle_hover_color
        else:
            handle_color = self.handle_color
        
        # Draw handle with a slight 3D effect
        # Shadow
        pygame.draw.circle(screen, Colors.GRAY_DARK, 
                          (handle_pos[0] + 1, handle_pos[1] + 1), 
                          self.handle_radius)
        # Main handle
        pygame.draw.circle(screen, handle_color, handle_pos, self.handle_radius)
        # Highlight (top-left quadrant)
        highlight_radius = self.handle_radius - 2
        if highlight_radius > 2:
            highlight_rect = pygame.Rect(
                handle_pos[0] - highlight_radius,
                handle_pos[1] - highlight_radius,
                highlight_radius,
                highlight_radius
            )
            pygame.draw.ellipse(screen, Colors.WHITE, highlight_rect, 1)
        
        # Draw labels if font is provided
        if self.label_font:
            # Current value label centered above the handle
            if self.show_value:
                value_text = self.value_format.format(self.current_value)
                value_surface = self.label_font.render(value_text, True, Colors.TEXT_DEFAULT)
                value_rect = value_surface.get_rect(center=(handle_x, self.rect.top - 5))
                screen.blit(value_surface, value_rect)
            
            # Min and max labels at the ends
            if self.show_min_max:
                min_text = self.value_format.format(self.min_value)
                min_surface = self.label_font.render(min_text, True, Colors.TEXT_MUTED)
                min_rect = min_surface.get_rect(midtop=(self.rect.left, self.rect.bottom + 5))
                screen.blit(min_surface, min_rect)
                
                max_text = self.value_format.format(self.max_value)
                max_surface = self.label_font.render(max_text, True, Colors.TEXT_MUTED)
                max_rect = max_surface.get_rect(midtop=(self.rect.right, self.rect.bottom + 5))
                screen.blit(max_surface, max_rect)
    
    def handle_event(self, event):
        """Handle mouse events for slider interaction."""
        result = False
        
        # Calculate handle position for hit testing
        value_ratio = (self.current_value - self.min_value) / (self.max_value - self.min_value)
        handle_x = self.rect.left + int(value_ratio * self.rect.width)
        handle_pos = (handle_x, self.rect.centery)
        
        # Create a rect for the handle to make collision detection easier
        handle_rect = pygame.Rect(
            handle_pos[0] - self.handle_radius,
            handle_pos[1] - self.handle_radius,
            self.handle_radius * 2,
            self.handle_radius * 2
        )
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check if clicked on handle or track
            if handle_rect.collidepoint(mouse_pos):
                self.active = True
                result = True
            elif self.rect.collidepoint(mouse_pos):
                # Clicked somewhere on the track, move handle there
                self._update_value_from_x(mouse_pos[0])
                self.active = True
                result = True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.active:
                self.active = False
                result = True
                
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check if hovering over handle
            prev_hovered = self.hovered
            self.hovered = handle_rect.collidepoint(mouse_pos)
            
            # Update value if dragging
            if self.active:
                prev_value = self.current_value
                self._update_value_from_x(mouse_pos[0])
                
                # Call on_change handler if value changed
                if self.current_value != prev_value and self.on_change:
                    self.on_change(self.current_value)
                    
                result = True
                
        return result
    
    def _update_value_from_x(self, x_pos):
        """Update slider value based on x position."""
        # Clamp x to slider bounds
        x = max(self.rect.left, min(x_pos, self.rect.right))
        
        # Calculate value based on position
        ratio = (x - self.rect.left) / self.rect.width
        new_value = self.min_value + ratio * (self.max_value - self.min_value)
        
        # Apply step if specified
        if self.step:
            new_value = round(new_value / self.step) * self.step
            
        # Clamp to range
        self.current_value = max(self.min_value, min(self.max_value, new_value))
        
    def get_value(self):
        """Get the current slider value."""
        return self.current_value
    
    def set_value(self, value, trigger_callback=True):
        """Set the slider value and optionally trigger the on_change callback."""
        prev_value = self.current_value
        self.current_value = max(self.min_value, min(self.max_value, value))
        
        if trigger_callback and self.on_change and prev_value != self.current_value:
            self.on_change(self.current_value) 