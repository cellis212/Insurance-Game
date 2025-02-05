import pygame
import sys
from ui import GameUI, Colors
from game_logic import GameState

def main():
    """Main entry point for the Insurance Simulation Game."""
    # Initialize Pygame
    pygame.init()
    
    # Set up the display
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Insurance Simulation Game")
    
    # Initialize UI
    game_ui = GameUI(screen)
    game_state = None
    
    # Set up game clock
    clock = pygame.time.Clock()
    FPS = 60
    
    print("Game initialized successfully!")  # Debug print
    
    # Main game loop
    running = True
    while running:
        # Process all events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                print("Quit event received")  # Debug print
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    print("Escape key pressed")  # Debug print
            elif event.type == pygame.MOUSEBUTTONDOWN:
                print(f"Mouse click at {pygame.mouse.get_pos()}")  # Debug print
            
            # Pass event to UI
            startup_result = game_ui.handle_event(event)
            if startup_result and game_ui.in_startup:
                # Initialize game state with selected options
                game_state = GameState(
                    initial_state=startup_result["state"],
                    company_name=startup_result["name"]
                )
                
                # Initialize premium rates for the selected state
                game_state.player_company.premium_rates = {}
                state_id = startup_result["state"]
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
    
    print("Game closing...")  # Debug print
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 