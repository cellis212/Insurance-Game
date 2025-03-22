import pygame
import sys
import os
import asyncio
from typing import Optional, Dict, Any, Union
from ui import GameUI, Colors
from game_logic import GameState
from utils import save_game_state, load_game_state
from analytics import generate_r_visualization

# Detect if we're running in a browser environment
IS_BROWSER = False
try:
    import platform
    IS_BROWSER = platform.system() == 'Emscripten'
except:
    pass

# Configure touch input for mobile devices
def setup_touch_input():
    """Configure touch input for mobile devices."""
    if IS_BROWSER:
        try:
            import javascript
            # Add a simple JavaScript helper to map touch events to mouse events
            js_code = """
            if ('ontouchstart' in window) {
                console.log("Touch device detected, enabling touch support");
                
                let canvas = document.getElementsByTagName('canvas')[0];
                
                canvas.addEventListener('touchstart', function(e) {
                    e.preventDefault();
                    let touch = e.touches[0];
                    let mouseEvent = new MouseEvent('mousedown', {
                        clientX: touch.clientX,
                        clientY: touch.clientY
                    });
                    canvas.dispatchEvent(mouseEvent);
                });
                
                canvas.addEventListener('touchend', function(e) {
                    e.preventDefault();
                    let mouseEvent = new MouseEvent('mouseup', {});
                    canvas.dispatchEvent(mouseEvent);
                });
                
                canvas.addEventListener('touchmove', function(e) {
                    e.preventDefault();
                    let touch = e.touches[0];
                    let mouseEvent = new MouseEvent('mousemove', {
                        clientX: touch.clientX,
                        clientY: touch.clientY
                    });
                    canvas.dispatchEvent(mouseEvent);
                });
            }
            """
            javascript.eval(js_code)
        except Exception as e:
            print(f"Could not set up touch input: {e}")

# Add a loading screen for browser version
def show_loading_screen(screen, progress):
    """Show a loading screen with progress bar."""
    # Fill screen with a light blue background
    bg_color = (230, 240, 250)
    screen.fill(bg_color)
    
    # Calculate screen dimensions
    width, height = screen.get_size()
    
    # Draw title
    font_large = pygame.font.SysFont('Arial', 48, bold=True)
    title = font_large.render("Insurance Simulation Game", True, (30, 60, 120))
    title_rect = title.get_rect(center=(width // 2, height // 3))
    screen.blit(title, title_rect)
    
    # Draw subtitle
    font_medium = pygame.font.SysFont('Arial', 24)
    subtitle = font_medium.render("Loading game assets...", True, (60, 90, 150))
    subtitle_rect = subtitle.get_rect(center=(width // 2, height // 3 + 60))
    screen.blit(subtitle, subtitle_rect)
    
    # Draw progress bar border
    bar_width = width * 0.7
    bar_height = 30
    bar_rect = pygame.Rect((width - bar_width) // 2, height * 0.6, bar_width, bar_height)
    pygame.draw.rect(screen, (100, 100, 100), bar_rect, 2)
    
    # Draw progress bar fill
    fill_width = bar_width * max(0.0, min(1.0, progress))
    fill_rect = pygame.Rect((width - bar_width) // 2, height * 0.6, fill_width, bar_height)
    pygame.draw.rect(screen, (50, 150, 50), fill_rect)
    
    # Draw progress percentage
    percentage = font_medium.render(f"{int(progress * 100)}%", True, (30, 60, 120))
    percentage_rect = percentage.get_rect(center=(width // 2, height * 0.6 + 50))
    screen.blit(percentage, percentage_rect)
    
    # Draw a tip at the bottom
    tips = [
        "Tip: Set your premium rates based on risk exposure in each state",
        "Tip: Catastrophes happen rarely but can be devastating",
        "Tip: Diversify your investment portfolio to manage risk",
        "Tip: Start with conservative pricing until you build capital",
        "Tip: You can now play offline after the first load!",
        "Tip: Add to home screen for app-like experience",
        "Tip: Balance growth with profitability for long-term success"
    ]
    import random
    tip_text = random.choice(tips)
    font_small = pygame.font.SysFont('Arial', 18)
    tip = font_small.render(tip_text, True, (80, 80, 80))
    tip_rect = tip.get_rect(center=(width // 2, height * 0.8))
    screen.blit(tip, tip_rect)
    
    # Update display
    pygame.display.flip()

async def main():
    """Main entry point for the Insurance Simulation Game."""
    # Initialize Pygame
    pygame.init()
    
    # Set up the display - use a canvas size that works well for browsers
    screen_width = 1280
    screen_height = 720
    flags = pygame.SCALED | pygame.RESIZABLE  # Better browser viewport handling
    screen = pygame.display.set_mode((screen_width, screen_height), flags)
    pygame.display.set_caption("Insurance Simulation Game")
    
    # Show loading screen if in browser
    if IS_BROWSER:
        # Initial loading screen
        show_loading_screen(screen, 0.1)
        await asyncio.sleep(0)  # Allow the browser to update display
    
    # Initialize UI with delayed loading in browser
    if IS_BROWSER:
        show_loading_screen(screen, 0.3)
        await asyncio.sleep(0)
    
    game_ui = GameUI(screen)
    
    if IS_BROWSER:
        show_loading_screen(screen, 0.5)
        await asyncio.sleep(0)
    
    game_state = None
    
    # Set up game clock
    clock = pygame.time.Clock()
    FPS = 60
    
    # Setup touch input for mobile devices if in browser
    if IS_BROWSER:
        show_loading_screen(screen, 0.7)
        setup_touch_input()
        await asyncio.sleep(0)
    
    # Create saves directory if it doesn't exist
    try:
        if IS_BROWSER:
            show_loading_screen(screen, 0.8)
            
        os.makedirs('saves', exist_ok=True)
        
        # Auto-load last save if it exists
        autosave_path = os.path.join('saves', 'autosave.json')
        if os.path.exists(autosave_path):
            load_data = load_game_state('autosave.json')
            if load_data:
                game_state = GameState.from_dict(load_data)
                game_ui.in_startup = False
    except Exception as e:
        # Handle browser environment where file access might be restricted
        print(f"Save/load initialization error: {e}")
    
    # Final loading progress
    if IS_BROWSER:
        show_loading_screen(screen, 1.0)
        await asyncio.sleep(0.5)  # Short pause at 100% for visual feedback
    
    print("Game initialized successfully!")  # Debug print
    if IS_BROWSER:
        try:
            import javascript
            javascript.console.log("Game running in browser environment")
        except:
            pass
    
    # Main game loop
    running = True
    while running:
        # Process all events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Auto-save before quitting
                try:
                    if game_state and not game_ui.in_startup:
                        save_game_state(game_state, 'autosave.json')
                except Exception as e:
                    print(f"Save error: {e}")
                running = False
                print("Quit event received")  # Debug print
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    print("Escape key pressed")  # Debug print
                elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # Save game on Ctrl+S
                    try:
                        if game_state and not game_ui.in_startup:
                            success = save_game_state(game_state, 'autosave.json')
                            print(f"Game saved: {success}")
                    except Exception as e:
                        print(f"Save error: {e}")
                elif event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # Load game on Ctrl+L
                    try:
                        load_data = load_game_state('autosave.json')
                        if load_data:
                            game_state = GameState.from_dict(load_data)
                            game_ui.in_startup = False
                            print("Game loaded successfully")
                    except Exception as e:
                        print(f"Load error: {e}")
                elif event.key == pygame.K_a and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # Generate analytics with Ctrl+A
                    if game_state and not game_ui.in_startup and len(game_state.financial_history) > 0:
                        try:
                            output_dir = generate_r_visualization(game_state)
                            if output_dir:
                                game_ui.show_save_load_message(f"Analytics generated in {output_dir}", Colors.GREEN)
                                # Try to open the folder with the default file explorer
                                try:
                                    if not IS_BROWSER:
                                        os.startfile(os.path.abspath(output_dir))
                                except Exception as e:
                                    print(f"Could not open output directory: {e}")
                            else:
                                game_ui.show_save_load_message("Failed to generate analytics", Colors.RED)
                        except Exception as e:
                            game_ui.show_save_load_message(f"Analytics error: {str(e)}", Colors.RED)
                            print(f"Analytics error: {e}")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                print(f"Mouse click at {pygame.mouse.get_pos()}")  # Debug print
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize event
                screen = pygame.display.set_mode((event.w, event.h), flags)
            
            # Pass event to UI
            result = game_ui.handle_event(event)
            
            # Handle UI results - check type first
            if result == "end_turn" and game_state:
                # Save game before updating
                try:
                    save_game_state(game_state, 'autosave.json')
                except Exception as e:
                    print(f"Save error: {e}")
                
                # Update game state for the next turn
                game_state.update()
                
                # Show turn summary
                game_ui.show_turn_summary(game_state)
            elif isinstance(result, str) and result.startswith("save:") and game_state:
                # Handle save command from UI
                try:
                    filename = result.split(":")[1]
                    if not filename.endswith('.json'):
                        filename += '.json'
                    success = save_game_state(game_state, filename)
                    if success:
                        game_ui.show_save_load_message(f"Game saved as {filename}", Colors.GREEN)
                        print(f"Game saved as {filename}")
                    else:
                        game_ui.show_save_load_message("Failed to save game", Colors.RED)
                        print("Failed to save game")
                except Exception as e:
                    game_ui.show_save_load_message(f"Error: {str(e)}", Colors.RED)
                    print(f"Save error: {e}")
            elif isinstance(result, str) and result.startswith("load:"):
                # Handle load command from UI
                try:
                    filename = result.split(":")[1]
                    load_data = load_game_state(filename)
                    if load_data:
                        game_state = GameState.from_dict(load_data)
                        game_ui.showing_save_load = False
                        game_ui.in_startup = False
                        print(f"Game loaded from {filename}")
                    else:
                        game_ui.show_save_load_message("Failed to load game", Colors.RED)
                        print("Failed to load game")
                except Exception as e:
                    game_ui.show_save_load_message(f"Error: {str(e)}", Colors.RED)
                    print(f"Load error: {e}")
            elif result == "analytics" and game_state and not game_ui.in_startup:
                # Handle analytics request from UI
                try:
                    if len(game_state.financial_history) > 0:
                        output_dir = generate_r_visualization(game_state)
                        if output_dir:
                            game_ui.show_save_load_message(f"Analytics generated in {output_dir}", Colors.GREEN)
                            # Try to open the folder with the default file explorer
                            try:
                                if not IS_BROWSER:
                                    os.startfile(os.path.abspath(output_dir))
                            except Exception as e:
                                print(f"Could not open output directory: {e}")
                        else:
                            game_ui.show_save_load_message("Failed to generate analytics", Colors.RED)
                    else:
                        game_ui.show_save_load_message("Not enough data for analytics", Colors.YELLOW)
                except Exception as e:
                    game_ui.show_save_load_message(f"Analytics error: {str(e)}", Colors.RED)
                    print(f"Analytics error: {e}")
            elif result and game_ui.in_startup and isinstance(result, dict):
                # Initialize game state with selected options
                game_state = GameState(
                    initial_state=result["state"],
                    company_name=result["name"]
                )
                
                # Initialize premium rates for the selected state
                game_state.player_company.premium_rates = {}
                state_id = result["state"]
                game_state.player_company.premium_rates[f"{state_id}_home"] = game_state.base_market_rates[f"{state_id}_home"]
                game_state.player_company.premium_rates[f"{state_id}_auto"] = game_state.base_market_rates[f"{state_id}_auto"]
                
                # Initialize starting policies for the selected state
                game_state.player_company.policies_sold = {}
                game_state.player_company.policies_sold[f"{state_id}_home"] = 500
                game_state.player_company.policies_sold[f"{state_id}_auto"] = 1000
                
                # Exit startup mode
                game_ui.in_startup = False
        
        # Update display
        screen.fill(Colors.WHITE)  # Clear screen
        game_ui.render(game_state)
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(FPS)
        
        # This is essential for Pygbag to work in browser context
        await asyncio.sleep(0)
    
    # Final autosave before closing
    try:
        if game_state and not game_ui.in_startup:
            save_game_state(game_state, 'autosave.json')
    except Exception as e:
        print(f"Final save error: {e}")
    
    print("Game closing...")  # Debug print
    pygame.quit()
    return 0  # Return 0 instead of sys.exit() for better browser compatibility

# For Pygbag, we need to make this an async entry point
if __name__ == "__main__":
    asyncio.run(main()) 