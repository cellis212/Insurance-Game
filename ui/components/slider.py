import pygame
from .colors import Colors

class Slider:
    def __init__(self, rect, min_value=0.8, max_value=1.5, initial_value=1.0):
        self.rect = rect
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.handle_radius = 8
        self.is_dragging = False
        
        # Calculate handle position
        self.handle_x = self._value_to_x(initial_value)
    
    def _value_to_x(self, value):
        """Convert a value to x position"""
        ratio = (value - self.min_value) / (self.max_value - self.min_value)
        return self.rect.left + int(ratio * self.rect.width)
    
    def _x_to_value(self, x):
        """Convert x position to value"""
        ratio = (x - self.rect.left) / self.rect.width
        return self.min_value + ratio * (self.max_value - self.min_value)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            handle_rect = pygame.Rect(
                self.handle_x - self.handle_radius,
                self.rect.centery - self.handle_radius,
                self.handle_radius * 2,
                self.handle_radius * 2
            )
            if handle_rect.collidepoint(mouse_pos):
                self.is_dragging = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False
        
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            mouse_x = pygame.mouse.get_pos()[0]
            # Constrain to slider bounds
            mouse_x = max(self.rect.left, min(self.rect.right, mouse_x))
            self.handle_x = mouse_x
            self.value = self._x_to_value(mouse_x)
            # Round to 2 decimal places
            self.value = round(self.value, 2)
            return True
        
        return False
    
    def draw(self, screen):
        # Draw track
        pygame.draw.rect(screen, Colors.GRAY, self.rect, 2)
        
        # Draw handle
        pygame.draw.circle(screen, Colors.BLUE, (self.handle_x, self.rect.centery), self.handle_radius) 