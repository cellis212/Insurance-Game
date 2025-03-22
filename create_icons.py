# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.

import pygame

def create_icons():
    """Create icons for the game in multiple sizes."""
    # Initialize pygame
    pygame.init()
    
    # Define icon sizes
    icon_sizes = [16, 32, 64, 192, 512]
    
    for size in icon_sizes:
        # Create surface for the icon
        icon = pygame.Surface((size, size))
        
        # Fill background with a blue color
        bg_color = (30, 60, 120)
        icon.fill(bg_color)
        
        # Draw a simple dollar symbol
        font_size = max(size // 2, 8)  # Scale font size with icon, but minimum 8px
        font = pygame.font.SysFont('Arial', font_size, bold=True)
        text = font.render('$', True, (255, 255, 255))
        text_rect = text.get_rect(center=(size // 2, size // 2))
        icon.blit(text, text_rect)
        
        # Draw a chart line (green for growth) if icon is large enough
        if size >= 64:
            line_thickness = max(1, size // 40)
            line_start = (size // 4, size * 3 // 4)
            line_mid = (size // 2, size // 3)
            line_end = (size * 3 // 4, size // 2)
            pygame.draw.line(icon, (50, 180, 50), line_start, line_mid, line_thickness)
            pygame.draw.line(icon, (50, 180, 50), line_mid, line_end, line_thickness)
        
        # Save the icon with the appropriate name
        if size == 16:
            filename = "favicon.ico"
        elif size == 192:
            # Regular icon.png for the main app icon
            if size == 192:
                pygame.image.save(icon, "icon.png")
            filename = f"icon-{size}.png"
        else:
            filename = f"icon-{size}.png"
        
        pygame.image.save(icon, filename)
        print(f"Created icon: {filename} ({size}x{size})")

if __name__ == "__main__":
    create_icons()
    print("All icons created successfully!") 