# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.

import pygame
import math
from .colors import Colors

class Background:
    """
    Create and render beautiful background patterns and gradients.
    """
    _patterns = {}  # Cache patterns
    
    @staticmethod
    def render_gradient(screen, rect, start_color, end_color, direction="vertical"):
        """
        Render a gradient background within the given rectangle.
        
        Args:
            screen: The pygame surface to draw on
            rect: The rectangle area to fill with gradient
            start_color: The color at the start of the gradient
            end_color: The color at the end of the gradient
            direction: Either "vertical", "horizontal", or "radial"
        """
        if direction == "vertical":
            for y in range(rect.height):
                # Calculate color for this line
                ratio = y / rect.height
                r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
                g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
                b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
                
                pygame.draw.line(screen, (r, g, b), 
                               (rect.left, rect.top + y), 
                               (rect.right, rect.top + y))
                               
        elif direction == "horizontal":
            for x in range(rect.width):
                # Calculate color for this line
                ratio = x / rect.width
                r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
                g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
                b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
                
                pygame.draw.line(screen, (r, g, b), 
                               (rect.left + x, rect.top), 
                               (rect.left + x, rect.bottom))
                               
        elif direction == "radial":
            # For radial gradients, we use the distance from center
            max_dist = math.sqrt((rect.width/2)**2 + (rect.height/2)**2)
            center = rect.center
            
            # Create a surface for the gradient
            surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            
            # Fill with end color
            surf.fill(end_color)
            
            # Draw circles from center outward
            for radius in range(int(max_dist), 0, -1):
                # Calculate color for this circle based on distance
                ratio = radius / max_dist
                r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
                g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
                b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
                
                pygame.draw.circle(surf, (r, g, b), (rect.width//2, rect.height//2), radius)
            
            # Blit the gradient surface
            screen.blit(surf, rect.topleft)
    
    @staticmethod
    def render_grid_pattern(screen, rect, color1, color2=None, grid_size=20, line_width=1):
        """
        Render a grid pattern within the given rectangle.
        
        Args:
            screen: The pygame surface to draw on
            rect: The rectangle area to fill with pattern
            color1: Main grid color
            color2: Secondary grid color (optional, for alternating)
            grid_size: Size of each grid cell
            line_width: Width of grid lines
        """
        # Create pattern if not already cached
        key = f"grid_{color1}_{color2}_{grid_size}_{line_width}"
        if key not in Background._patterns:
            # Create a pattern surface
            pattern_size = max(grid_size * 2, 100)  # Make pattern at least 100px
            pattern = pygame.Surface((pattern_size, pattern_size), pygame.SRCALPHA)
            
            # Draw horizontal lines
            for y in range(0, pattern_size, grid_size):
                line_color = color1 if (y // grid_size) % 2 == 0 or not color2 else color2
                pygame.draw.line(pattern, line_color, (0, y), (pattern_size, y), line_width)
            
            # Draw vertical lines
            for x in range(0, pattern_size, grid_size):
                line_color = color1 if (x // grid_size) % 2 == 0 or not color2 else color2
                pygame.draw.line(pattern, line_color, (x, 0), (x, pattern_size), line_width)
            
            Background._patterns[key] = pattern
        
        # Blit the pattern as a tiled background
        pattern = Background._patterns[key]
        pattern_rect = pattern.get_rect()
        
        for y in range(rect.top, rect.bottom, pattern_rect.height):
            for x in range(rect.left, rect.right, pattern_rect.width):
                screen.blit(pattern, (x, y))
    
    @staticmethod
    def render_dot_pattern(screen, rect, color, bg_color=None, dot_size=3, spacing=15):
        """
        Render a dot pattern within the given rectangle.
        
        Args:
            screen: The pygame surface to draw on
            rect: The rectangle area to fill with pattern
            color: Color of the dots
            bg_color: Background color (optional, transparent if None)
            dot_size: Size of each dot
            spacing: Space between dots
        """
        # Create pattern if not already cached
        key = f"dots_{color}_{bg_color}_{dot_size}_{spacing}"
        if key not in Background._patterns:
            # Create a pattern surface
            pattern_size = spacing * 2
            pattern = pygame.Surface((pattern_size, pattern_size), pygame.SRCALPHA)
            
            # Fill background if specified
            if bg_color:
                pattern.fill(bg_color)
            
            # Draw dots
            pygame.draw.circle(pattern, color, (spacing // 2, spacing // 2), dot_size)
            pygame.draw.circle(pattern, color, (spacing + spacing // 2, spacing // 2), dot_size)
            pygame.draw.circle(pattern, color, (spacing // 2, spacing + spacing // 2), dot_size)
            pygame.draw.circle(pattern, color, (spacing + spacing // 2, spacing + spacing // 2), dot_size)
            
            Background._patterns[key] = pattern
        
        # Blit the pattern as a tiled background
        pattern = Background._patterns[key]
        pattern_rect = pattern.get_rect()
        
        for y in range(rect.top, rect.bottom, pattern_rect.height):
            for x in range(rect.left, rect.right, pattern_rect.width):
                screen.blit(pattern, (x, y))
    
    @staticmethod
    def render_wave_pattern(screen, rect, color1, color2=None, amplitude=20, frequency=0.05, line_width=3):
        """
        Render a wave pattern within the given rectangle.
        
        Args:
            screen: The pygame surface to draw on
            rect: The rectangle area to fill with pattern
            color1: Main wave color
            color2: Secondary wave color (optional)
            amplitude: Wave height
            frequency: Wave frequency
            line_width: Width of wave line
        """
        # Create pattern if not already cached
        key = f"wave_{color1}_{color2}_{amplitude}_{frequency}_{line_width}"
        if key not in Background._patterns:
            # Calculate pattern width (one full wave)
            pattern_width = int(2 * math.pi / frequency)
            pattern_height = amplitude * 2 + line_width * 2
            
            # Create a pattern surface
            pattern = pygame.Surface((pattern_width, pattern_height), pygame.SRCALPHA)
            
            # Draw first wave
            points = []
            for x in range(pattern_width):
                y = amplitude * math.sin(x * frequency) + amplitude
                points.append((x, y))
            
            if len(points) > 1:
                pygame.draw.lines(pattern, color1, False, points, line_width)
            
            # Draw second wave if specified
            if color2:
                points2 = []
                for x in range(pattern_width):
                    y = amplitude * math.cos(x * frequency) + amplitude
                    points2.append((x, y))
                
                if len(points2) > 1:
                    pygame.draw.lines(pattern, color2, False, points2, line_width)
            
            Background._patterns[key] = pattern
        
        # Blit the pattern as a tiled background
        pattern = Background._patterns[key]
        pattern_rect = pattern.get_rect()
        
        for y in range(rect.top, rect.bottom, pattern_rect.height):
            for x in range(rect.left, rect.right, pattern_rect.width):
                screen.blit(pattern, (x, y))
    
    @staticmethod
    def render_insurance_theme(screen, rect):
        """
        Render an insurance-themed background pattern.
        
        Args:
            screen: The pygame surface to draw on
            rect: The rectangle area to fill with pattern
        """
        # Fill with a light color
        screen.fill(Colors.WHITE, rect)
        
        # Add a subtle grid pattern
        Background.render_grid_pattern(
            screen, 
            rect, 
            Colors.GRAY_LIGHTEST, 
            None, 
            grid_size=40, 
            line_width=1
        )
        
        # Add some subtle dots
        Background.render_dot_pattern(
            screen,
            rect,
            (200, 220, 240, 30),  # Very light blue with transparency
            None,
            dot_size=2,
            spacing=20
        ) 