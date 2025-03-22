# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.

import os
import json
from typing import Dict, Any, List, Union, Optional
import numpy as np
import pygame
import platform

# Detect if we're running in a browser environment (Pygbag)
IS_BROWSER = platform.system() == 'Emscripten'

def format_currency(value: float) -> str:
    """Format a value as currency with dollar sign."""
    return f"${value:,.2f}"

def format_percentage(value: float) -> str:
    """Format a value as percentage."""
    return f"{value * 100:.1f}%"

def calculate_loss_ratio(claims: float, premiums: float) -> float:
    """Calculate loss ratio (claims / premiums)."""
    if premiums == 0:
        return 0.0
    return claims / premiums

def calculate_combined_ratio(claims: float, expenses: float, premiums: float) -> float:
    """Calculate combined ratio ((claims + expenses) / premiums)."""
    if premiums == 0:
        return 0.0
    return (claims + expenses) / premiums

def log_normal_random(mean: float, sigma: float, size: int = 1) -> Union[float, np.ndarray]:
    """Generate random values from a log-normal distribution."""
    return np.random.lognormal(mean=mean, sigma=sigma, size=size)

def poisson_random(lam: float, size: int = 1) -> Union[int, np.ndarray]:
    """Generate random values from a Poisson distribution."""
    return np.random.poisson(lam=lam, size=size)

def render_text(screen: pygame.Surface, text: str, font: pygame.font.Font, 
                position: tuple, color: tuple, centered: bool = False) -> None:
    """Render text on the screen with optional centering."""
    text_surface = font.render(text, True, color)
    if centered:
        text_rect = text_surface.get_rect(center=position)
        screen.blit(text_surface, text_rect)
    else:
        screen.blit(text_surface, position)

def save_game_state(game_state: Any, filename: str) -> bool:
    """Save the game state to a file or browser localStorage."""
    try:
        # Convert game_state to a serializable dictionary
        state_dict = game_state.to_dict()
        
        if IS_BROWSER:
            # In browser, use localStorage
            import javascript
            from javascript import localStorage
            
            # Stringify the JSON and store it
            json_str = json.dumps(state_dict)
            localStorage.setItem(filename, json_str)
            print(f"Game saved to browser localStorage: {filename}")
        else:
            # On desktop, save to file
            # Create saves directory if it doesn't exist
            os.makedirs('saves', exist_ok=True)
            
            # Save to file
            save_path = os.path.join('saves', filename)
            with open(save_path, 'w') as f:
                json.dump(state_dict, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving game: {e}")
        return False

def load_game_state(filename: str) -> Optional[Dict[str, Any]]:
    """Load the game state from a file or browser localStorage."""
    try:
        if IS_BROWSER:
            # In browser, use localStorage
            import javascript
            from javascript import localStorage
            
            # Get the JSON string from localStorage
            json_str = localStorage.getItem(filename)
            if not json_str:
                print(f"No save found in localStorage: {filename}")
                return None
                
            # Parse the JSON string
            state_dict = json.loads(json_str)
            return state_dict
        else:
            # On desktop, load from file
            save_path = os.path.join('saves', filename)
            with open(save_path, 'r') as f:
                state_dict = json.load(f)
            return state_dict
    except Exception as e:
        print(f"Error loading game: {e}")
        return None 