"""
UI Components package for Insurance Simulation Game.
Contains reusable UI elements for building game screens.
"""

from .colors import Colors
from .button import Button
from .panel import Panel
from .slider import Slider
from .icons import Icons
from .background import Background
from .share_dialog import ShareDialog
from ui.components.base_component import BaseComponent

__all__ = [
    'Colors',
    'Button',
    'Panel',
    'Slider',
    'Icons',
    'Background',
    'ShareDialog',
    'BaseComponent'
]

import pygame

class Colors:
    """Color constants used in the UI."""
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    BLUE = (0, 100, 200)
    GREEN = (50, 150, 50)
    RED = (200, 50, 50)
    LIGHT_BLUE = (100, 150, 255)
    ORANGE = (255, 140, 0)

class Button:
    def __init__(self, rect, text, font, color=Colors.BLUE, hover_color=Colors.LIGHT_BLUE):
        self.rect = rect
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        text_surface = self.font.render(self.text, True, Colors.WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.is_hovered = self.rect.collidepoint(mouse_pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                return True
        return False 