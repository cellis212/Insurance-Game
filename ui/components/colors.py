# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.

class Colors:
    """Color constants used in the UI."""
    # Base colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    
    # Gray scale
    GRAY_DARK = (48, 48, 48)
    GRAY = (96, 96, 96)
    GRAY_MEDIUM = (128, 128, 128)
    GRAY_LIGHT = (200, 200, 200)
    GRAY_LIGHTEST = (240, 240, 240)
    
    # Primary colors - professional blue theme
    PRIMARY_DARKEST = (16, 42, 94)    # Very dark blue
    PRIMARY_DARK = (25, 65, 133)      # Dark blue
    PRIMARY = (37, 99, 171)           # Medium blue
    PRIMARY_LIGHT = (85, 140, 199)    # Light blue
    PRIMARY_LIGHTEST = (173, 214, 255) # Very light blue
    
    # Accent colors
    SUCCESS_DARK = (35, 120, 40)      # Dark green
    SUCCESS = (46, 158, 53)           # Medium green
    SUCCESS_LIGHT = (170, 230, 170)   # Light green
    
    DANGER_DARK = (165, 29, 42)       # Dark red
    DANGER = (220, 53, 69)            # Medium red
    DANGER_LIGHT = (248, 215, 218)    # Light red
    
    WARNING_DARK = (176, 120, 0)      # Dark amber
    WARNING = (255, 174, 0)           # Medium amber
    WARNING_LIGHT = (255, 239, 189)   # Light amber
    
    INFO_DARK = (0, 123, 147)         # Dark teal
    INFO = (0, 170, 204)              # Medium teal
    INFO_LIGHT = (204, 240, 255)      # Light teal
    
    # Legacy color mappings for backward compatibility
    BLUE = PRIMARY
    GREEN = SUCCESS 
    RED = DANGER
    LIGHT_BLUE = PRIMARY_LIGHT
    LIGHT_GRAY = GRAY_LIGHT
    ORANGE = WARNING
    
    # Background colors
    BG_DEFAULT = WHITE
    BG_PANEL = GRAY_LIGHTEST
    BG_HEADER = PRIMARY_DARK
    
    # Text colors
    TEXT_DEFAULT = GRAY_DARK
    TEXT_HEADER = WHITE
    TEXT_MUTED = GRAY
    
    # Chart colors for analytics
    CHART_COLORS = [
        (37, 99, 171),    # Primary blue
        (46, 158, 53),    # Success green
        (220, 53, 69),    # Danger red
        (255, 174, 0),    # Warning amber
        (0, 170, 204),    # Info teal
        (121, 82, 179),   # Purple
        (108, 117, 125),  # Gray
        (152, 95, 13)     # Brown
    ] 