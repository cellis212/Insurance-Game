# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.
#!/usr/bin/env python3
"""
Insurance Simulation Game - New Architecture Entry Point
This file provides a new implementation of the game using the refactored architecture.
It can run alongside the original code without modifying it.
"""

import sys
import os
import pygame

# Define new path for running only the new modules
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PACKAGE_DIR = os.path.join(SCRIPT_DIR, 'ui')
if os.path.exists(UI_PACKAGE_DIR):
    sys.path.insert(0, SCRIPT_DIR)

from ui.game_application import GameApplication

def main():
    """Main entry point for the application."""
    try:
        # Initialize pygame with required components
        pygame.init()
        pygame.font.init()
        
        # Create and run the application
        app = GameApplication(width=1280, height=800, title="Insurance Simulation Game (New Architecture)")
        app.run()
    except Exception as e:
        import traceback
        print(f"Error running game: {e}")
        traceback.print_exc()
    finally:
        pygame.quit()

if __name__ == "__main__":
    main() 