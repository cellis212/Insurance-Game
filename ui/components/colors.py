# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.

class Colors:
    """Color constants used throughout the application."""
    
    # Main colors
    PRIMARY = (33, 150, 243)        # Blue
    PRIMARY_LIGHT = (66, 165, 245)  # Light Blue
    PRIMARY_DARK = (25, 118, 210)   # Dark Blue
    
    SECONDARY = (46, 125, 50)       # Green
    SECONDARY_LIGHT = (76, 175, 80) # Light Green
    SECONDARY_DARK = (27, 94, 32)   # Dark Green
    
    TERTIARY = (156, 39, 176)       # Purple
    TERTIARY_LIGHT = (186, 104, 200)# Light Purple
    TERTIARY_DARK = (123, 31, 162)  # Dark Purple
    
    # Semantic colors
    SUCCESS = (46, 125, 50)         # Green
    WARNING = (255, 152, 0)         # Orange
    DANGER = (211, 47, 47)          # Red
    DANGER_LIGHT = (229, 115, 115)  # Light Red
    INFO = (33, 150, 243)           # Blue
    
    # Neutral colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY_LIGHT = (224, 224, 224)
    GRAY_MEDIUM = (158, 158, 158)
    GRAY_DARK = (66, 66, 66)
    
    # Background colors
    BACKGROUND_LIGHT = (250, 250, 250)
    BACKGROUND_DARK = (33, 33, 33)
    
    # Chart colors (for data visualization)
    CHART_BLUE = (33, 150, 243)
    CHART_GREEN = (76, 175, 80)
    CHART_ORANGE = (255, 152, 0)
    CHART_RED = (244, 67, 54)
    CHART_PURPLE = (156, 39, 176)
    CHART_YELLOW = (255, 235, 59)
    CHART_CYAN = (0, 188, 212)
    CHART_PINK = (233, 30, 99)
    
    # Insurance-specific semantic colors
    AUTO_INSURANCE = (25, 118, 210)  # Blue
    HOME_INSURANCE = (196, 30, 58)   # Red
    LIFE_INSURANCE = (46, 125, 50)   # Green
    HEALTH_INSURANCE = (0, 150, 136) # Teal
    
    # State-specific colors
    CA_COLOR = (239, 83, 80)         # Red (California)
    FL_COLOR = (255, 193, 7)         # Amber (Florida)
    
    # Backward compatibility aliases for existing code
    BLUE = PRIMARY
    GREEN = SUCCESS
    RED = DANGER
    LIGHT_BLUE = PRIMARY_LIGHT
    LIGHT_GRAY = GRAY_LIGHT
    ORANGE = WARNING
    GRAY = GRAY_MEDIUM
    GRAY_LIGHTEST = (240, 240, 240)
    
    # More backward compatibility
    BG_DEFAULT = WHITE
    BG_PANEL = GRAY_LIGHT
    BG_HEADER = PRIMARY_DARK
    
    TEXT_DEFAULT = GRAY_DARK
    TEXT_HEADER = WHITE
    TEXT_MUTED = GRAY_MEDIUM
    
    # Backward compatibility for more colors
    PRIMARY_DARKEST = (16, 42, 94)
    PRIMARY_LIGHTEST = (173, 214, 255)
    
    SUCCESS_DARK = (35, 120, 40)
    SUCCESS_LIGHT = (170, 230, 170)
    
    DANGER_DARK = (165, 29, 42)
    
    WARNING_DARK = (176, 120, 0)
    WARNING_LIGHT = (255, 239, 189)
    
    INFO_DARK = (0, 123, 147)
    INFO_LIGHT = (204, 240, 255)
    
    # Chart colors for backward compatibility
    CHART_COLORS = [
        CHART_BLUE,
        CHART_GREEN,
        CHART_RED,
        CHART_ORANGE,
        CHART_PURPLE,
        CHART_YELLOW,
        CHART_CYAN,
        CHART_PINK
    ]
    
    @classmethod
    def get_palette(cls, count: int) -> list:
        """
        Get a palette of colors based on how many are needed.
        
        Args:
            count: Number of colors needed
            
        Returns:
            List of RGB color tuples
        """
        palette = list(cls.CHART_COLORS)
        
        # If we need more colors than are in our palette, repeat with variations
        if count > len(palette):
            # Create lighter versions of each color
            for color in palette[:]:
                r, g, b = color
                lighter = (min(r + 60, 255), min(g + 60, 255), min(b + 60, 255))
                palette.append(lighter)
                
        return palette[:count] 