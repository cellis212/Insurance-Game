# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.

import pygame

def create_icon():
    """Create a simple icon for the game."""
    # Initialize pygame
    pygame.init()
    
    # Set icon size (standard 192x192 for web)
    size = 192
    icon = pygame.Surface((size, size))
    
    # Fill background with a blue color
    bg_color = (30, 60, 120)
    icon.fill(bg_color)
    
    # Draw a simple dollar symbol
    font = pygame.font.SysFont('Arial', size // 2, bold=True)
    text = font.render('$', True, (255, 255, 255))
    text_rect = text.get_rect(center=(size // 2, size // 2))
    icon.blit(text, text_rect)
    
    # Draw a chart line (green for growth)
    line_start = (size // 4, size * 3 // 4)
    line_mid = (size // 2, size // 3)
    line_end = (size * 3 // 4, size // 2)
    pygame.draw.line(icon, (50, 180, 50), line_start, line_mid, 5)
    pygame.draw.line(icon, (50, 180, 50), line_mid, line_end, 5)
    
    # Save the icon
    pygame.image.save(icon, 'icon.png')
    print("Icon created successfully!")

if __name__ == "__main__":
    create_icon() 