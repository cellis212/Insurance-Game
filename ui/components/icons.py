# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.

import pygame
import os
from .colors import Colors

class Icons:
    """
    Icon utility for the UI.
    Icons are loaded once and cached for better performance.
    """
    _instance = None
    _icons = {}
    _default_size = (24, 24)
    
    # Use a singleton pattern to avoid loading icons multiple times
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Icons, cls).__new__(cls)
            cls._instance._load_icons()
        return cls._instance
    
    def _load_icons(self):
        """Load icons from icon pack or create them using Pygame."""
        # Check if we have an icon directory
        icon_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icons")
        has_icon_dir = os.path.exists(icon_dir)
        
        # If we have icons, load them
        if has_icon_dir:
            self._load_from_directory(icon_dir)
        else:
            # Otherwise, create them using pygame
            self._create_default_icons()
    
    def _load_from_directory(self, icon_dir):
        """Load icons from the specified directory."""
        # Implement icon loading from files if you have icon assets
        pass
    
    def _create_default_icons(self):
        """Create default icons using Pygame drawing functions."""
        # Create a set of basic icons
        
        # Home icon
        home_surf = pygame.Surface(self._default_size, pygame.SRCALPHA)
        # Draw house shape
        pygame.draw.polygon(home_surf, Colors.PRIMARY_DARK, [
            (2, 14), (2, 22), (22, 22), (22, 14), (12, 4)
        ])
        # Draw door
        pygame.draw.rect(home_surf, Colors.WHITE, (10, 15, 4, 7))
        self._icons['home'] = home_surf
        
        # Car/Auto icon
        car_surf = pygame.Surface(self._default_size, pygame.SRCALPHA)
        # Draw car body
        pygame.draw.rect(car_surf, Colors.INFO_DARK, (2, 10, 20, 8), border_radius=2)
        # Draw car roof
        pygame.draw.rect(car_surf, Colors.INFO_DARK, (5, 4, 14, 6), border_radius=1)
        # Draw wheels
        pygame.draw.circle(car_surf, Colors.GRAY_DARK, (6, 18), 3)
        pygame.draw.circle(car_surf, Colors.GRAY_DARK, (18, 18), 3)
        self._icons['auto'] = car_surf
        
        # Settings/Gear icon
        gear_surf = pygame.Surface(self._default_size, pygame.SRCALPHA)
        # Draw gear circle
        pygame.draw.circle(gear_surf, Colors.GRAY_DARK, (12, 12), 8)
        pygame.draw.circle(gear_surf, Colors.WHITE, (12, 12), 5)
        # Draw gear teeth (simplified)
        for i in range(8):
            angle = i * 45
            x = 12 + int(10 * pygame.math.Vector2(1, 0).rotate(angle).x)
            y = 12 + int(10 * pygame.math.Vector2(1, 0).rotate(angle).y)
            pygame.draw.rect(gear_surf, Colors.GRAY_DARK, (x-2, y-2, 4, 4))
        self._icons['settings'] = gear_surf
        
        # Save icon
        save_surf = pygame.Surface(self._default_size, pygame.SRCALPHA)
        # Draw floppy disk
        pygame.draw.rect(save_surf, Colors.SUCCESS, (2, 2, 20, 20), border_radius=2)
        # Draw label
        pygame.draw.rect(save_surf, Colors.WHITE, (5, 5, 14, 10))
        pygame.draw.rect(save_surf, Colors.WHITE, (8, 15, 8, 4))
        self._icons['save'] = save_surf
        
        # Analytics/Chart icon
        chart_surf = pygame.Surface(self._default_size, pygame.SRCALPHA)
        # Draw chart bars
        pygame.draw.rect(chart_surf, Colors.PRIMARY, (4, 14, 4, 6))
        pygame.draw.rect(chart_surf, Colors.PRIMARY_LIGHT, (10, 8, 4, 12))
        pygame.draw.rect(chart_surf, Colors.PRIMARY_DARK, (16, 4, 4, 16))
        # Draw baseline
        pygame.draw.line(chart_surf, Colors.GRAY_DARK, (2, 20), (22, 20), 2)
        self._icons['analytics'] = chart_surf
        
        # Investment icon
        investment_surf = pygame.Surface(self._default_size, pygame.SRCALPHA)
        # Draw stack of coins
        for i in range(4):
            y = 18 - i * 4
            pygame.draw.ellipse(investment_surf, Colors.WARNING, (4, y-2, 16, 4))
            pygame.draw.ellipse(investment_surf, Colors.WARNING_DARK, (4, y-2, 16, 4), 1)
        # Draw up arrow
        pygame.draw.polygon(investment_surf, Colors.SUCCESS, [
            (16, 8), (20, 12), (18, 12), (18, 16), (14, 16), (14, 12), (12, 12)
        ])
        self._icons['investment'] = investment_surf
        
        # Reports icon
        reports_surf = pygame.Surface(self._default_size, pygame.SRCALPHA)
        # Draw document
        pygame.draw.rect(reports_surf, Colors.WHITE, (4, 2, 16, 20), border_radius=1)
        pygame.draw.rect(reports_surf, Colors.PRIMARY_LIGHT, (4, 2, 16, 20), 1, border_radius=1)
        # Draw text lines
        for i in range(5):
            y = 6 + i * 3
            pygame.draw.line(reports_surf, Colors.GRAY_LIGHT, (7, y), (17, y), 1)
        self._icons['reports'] = reports_surf
        
        # Share icon
        share_surf = pygame.Surface(self._default_size, pygame.SRCALPHA)
        # Draw three connected dots
        pygame.draw.circle(share_surf, Colors.PRIMARY, (16, 6), 4)
        pygame.draw.circle(share_surf, Colors.PRIMARY, (16, 18), 4)
        pygame.draw.circle(share_surf, Colors.PRIMARY, (6, 12), 4)
        # Draw connecting lines
        pygame.draw.line(share_surf, Colors.PRIMARY, (6, 12), (16, 6), 2)
        pygame.draw.line(share_surf, Colors.PRIMARY, (6, 12), (16, 18), 2)
        self._icons['share'] = share_surf
        
        # Warning/Alert icon
        warning_surf = pygame.Surface(self._default_size, pygame.SRCALPHA)
        # Draw warning triangle
        pygame.draw.polygon(warning_surf, Colors.WARNING, [
            (12, 2), (22, 22), (2, 22)
        ])
        # Draw exclamation mark
        pygame.draw.rect(warning_surf, Colors.BLACK, (11, 8, 2, 8))
        pygame.draw.rect(warning_surf, Colors.BLACK, (11, 18, 2, 2))
        self._icons['warning'] = warning_surf
    
    def get(self, name, size=None):
        """Get an icon by name, optionally scaled to the specified size."""
        if name not in self._icons:
            # Return an empty surface if icon doesn't exist
            return pygame.Surface((1, 1), pygame.SRCALPHA)
        
        icon = self._icons[name]
        
        if size and size != icon.get_size():
            # Scale if needed
            return pygame.transform.smoothscale(icon, size)
        
        return icon 