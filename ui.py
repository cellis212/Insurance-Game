import pygame
from game_logic import GameState
import numpy as np
from ui.components.colors import Colors
from ui.components.button import Button
from ui.components.share_dialog import ShareDialog
from utils import save_game_state, load_game_state
from analytics import track_pageview, track_event

# Import all UI components from their proper modules
from ui.screens import (
    StartupScreen,
    PremiumScreen,
    InvestmentScreen,
    TurnSummaryPopup,
    ReportsScreen,
    SaveLoadScreen
)

class GameUI:
    """Main UI class that manages all screens and UI components."""
    
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # Initialize fonts
        pygame.font.init()
        self.main_font = pygame.font.SysFont('Arial', 20)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 16)
        
        # Initialize screens
        self.startup_screen = StartupScreen(
            pygame.Rect(self.width//2 - 300, self.height//2 - 200, 600, 400),
            self.title_font,
            self.main_font
        )
        
        # Initialize game screen
        self.premium_screen = PremiumScreen(
            pygame.Rect(0, 100, self.width, self.height - 150),
            self.main_font,
            self.small_font
        )
        
        self.investment_screen = InvestmentScreen(
            pygame.Rect(0, 100, self.width, self.height - 150),
            self.main_font,
            self.small_font
        )
        
        self.reports_screen = ReportsScreen(
            pygame.Rect(0, 100, self.width, self.height - 150),
            self.main_font,
            self.small_font
        )
        
        # Create a turn summary popup
        self.turn_summary = TurnSummaryPopup(
            pygame.Rect(self.width//2 - 300, self.height//2 - 200, 600, 400),
            self.title_font,
            self.main_font
        )
        
        # Create save/load screen
        self.save_load_screen = SaveLoadScreen(
            pygame.Rect(self.width//2 - 400, self.height//2 - 250, 800, 500),
            self.title_font,
            self.main_font
        )
        
        # Create share dialog
        self.share_dialog = ShareDialog(
            pygame.Rect(0, 0, self.width, self.height),
            self.title_font,
            self.main_font
        )
        
        # Create main navigation buttons
        button_width = 120
        button_height = 40
        button_spacing = 10
        start_x = (self.width - (button_width * 7 + button_spacing * 6)) // 2  # Updated for 7 buttons
        
        self.premium_button = Button(
            pygame.Rect(start_x, 40, button_width, button_height),
            "Premium Rates",
            self.main_font
        )
        
        self.investment_button = Button(
            pygame.Rect(start_x + button_width + button_spacing, 40, button_width, button_height),
            "Investments",
            self.main_font
        )
        
        self.reports_button = Button(
            pygame.Rect(start_x + (button_width + button_spacing) * 2, 40, button_width, button_height),
            "Financial Reports",
            self.main_font
        )
        
        self.save_load_button = Button(
            pygame.Rect(start_x + (button_width + button_spacing) * 3, 40, button_width, button_height),
            "Save / Load",
            self.main_font
        )
        
        self.analytics_button = Button(
            pygame.Rect(start_x + (button_width + button_spacing) * 4, 40, button_width, button_height),
            "Analytics",
            self.main_font,
            color=(70, 130, 180)  # Steel blue
        )
        
        self.share_button = Button(
            pygame.Rect(start_x + (button_width + button_spacing) * 5, 40, button_width, button_height),
            "Share",
            self.main_font,
            color=(29, 161, 242)  # Twitter blue
        )
        
        self.next_turn_button = Button(
            pygame.Rect(start_x + (button_width + button_spacing) * 6, 40, button_width, button_height),
            "End Turn",
            self.main_font,
            color=Colors.GREEN
        )
        
        # UI state
        self.in_startup = True
        self.current_screen = "premium"  # Default screen after startup
        self.showing_turn_summary = False
        self.showing_save_load = False
        self.showing_share = False
        
        # Track initial page view
        track_pageview("startup")
        
    def handle_event(self, event):
        """Handle pygame events."""
        if self.in_startup:
            return self.startup_screen.handle_event(event)
        
        if self.showing_turn_summary:
            result = self.turn_summary.handle_event(event)
            if result:
                self.showing_turn_summary = False
            return None
        
        if self.showing_save_load:
            result = self.save_load_screen.handle_event(event)
            if result:
                if result == "close":
                    self.showing_save_load = False
                elif result.startswith("save:"):
                    # Track save event
                    track_event("game", "save", result.split(":")[1])
                    return result
                elif result.startswith("load:"):
                    # Track load event
                    track_event("game", "load", result.split(":")[1])
                    return result
            return None
        
        if self.showing_share:
            result = self.share_dialog.handle_event(event)
            if result == "close":
                self.showing_share = False
            return None
        
        # Handle navigation buttons
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.premium_button.handle_event(event):
                self.current_screen = "premium"
                track_pageview("premium_rates")
                return None
            
            if self.investment_button.handle_event(event):
                self.current_screen = "investment"
                track_pageview("investments")
                return None
                
            if self.reports_button.handle_event(event):
                self.current_screen = "reports"
                track_pageview("financial_reports")
                return None
            
            if self.save_load_button.handle_event(event):
                self.showing_save_load = True
                track_pageview("save_load")
                return None
            
            if self.analytics_button.handle_event(event):
                track_event("navigation", "analytics")
                return "analytics"
            
            if self.share_button.handle_event(event):
                self.showing_share = True
                track_pageview("share")
                track_event("social", "open_share_dialog")
                return None
                
            if self.next_turn_button.handle_event(event):
                track_event("game", "end_turn")
                return "end_turn"
        
        # Handle current screen events
        if self.current_screen == "premium":
            return self.premium_screen.handle_event(event)
        elif self.current_screen == "investment":
            return self.investment_screen.handle_event(event)
        elif self.current_screen == "reports":
            return self.reports_screen.handle_event(event)
        
        return None
    
    def render(self, game_state):
        """Render the current UI state."""
        self.screen.fill(Colors.WHITE)
        
        if self.in_startup:
            self.startup_screen.render(self.screen)
            return
        
        # If we have a game state, update share dialog data
        if game_state:
            company_data = {
                'name': game_state.player_company.name,
                'cash': game_state.player_company.cash,
                'total_policies': sum(game_state.player_company.policies_sold.values()),
                'states': [state_id for state_id, is_unlocked in game_state.unlocked_states.items() if is_unlocked],
                'turn': game_state.current_turn
            }
            self.share_dialog.update_company_data(company_data)
        
        # Draw top info bar
        if game_state:
            self._draw_info_bar(game_state)
        
        # Draw navigation buttons
        self.premium_button.draw(self.screen)
        self.investment_button.draw(self.screen)
        self.reports_button.draw(self.screen)
        self.save_load_button.draw(self.screen)
        self.analytics_button.draw(self.screen)
        self.share_button.draw(self.screen)
        self.next_turn_button.draw(self.screen)
        
        # Highlight active button
        if self.current_screen == "premium":
            pygame.draw.rect(self.screen, Colors.BLUE, self.premium_button.rect, 3)
        elif self.current_screen == "investment":
            pygame.draw.rect(self.screen, Colors.BLUE, self.investment_button.rect, 3)
        elif self.current_screen == "reports":
            pygame.draw.rect(self.screen, Colors.BLUE, self.reports_button.rect, 3)
        
        # Draw current screen
        if not self.showing_save_load and not self.showing_turn_summary and not self.showing_share:
            if self.current_screen == "premium":
                self.premium_screen.render(self.screen, game_state)
            elif self.current_screen == "investment":
                self.investment_screen.render(self.screen, game_state)
            elif self.current_screen == "reports":
                self.reports_screen.render(self.screen, game_state)
        
        # Draw turn summary popup if active
        if self.showing_turn_summary:
            self.turn_summary.render(self.screen)
        
        # Draw save/load screen if active
        if self.showing_save_load:
            self.save_load_screen.render(self.screen)
        
        # Draw share dialog if active
        if self.showing_share:
            self.share_dialog.render(self.screen)
    
    def show_turn_summary(self, game_state):
        """Show turn summary popup."""
        self.showing_turn_summary = True
        self.turn_summary.update(game_state)
        track_pageview("turn_summary")
        track_event("game", "complete_turn", value=game_state.current_turn)
    
    def show_save_load_message(self, message, color=Colors.BLACK):
        """Show a message on the save/load screen."""
        self.save_load_screen.show_message(message, color)
    
    def _draw_info_bar(self, game_state):
        """Draw the information bar at the top of the screen."""
        if not game_state:
            return
            
        # Draw background
        info_bar_rect = pygame.Rect(0, 0, self.width, 30)
        pygame.draw.rect(self.screen, Colors.LIGHT_GRAY, info_bar_rect)
        
        # Draw current turn
        turn_text = f"Turn: {game_state.current_turn}"
        turn_surface = self.small_font.render(turn_text, True, Colors.BLACK)
        self.screen.blit(turn_surface, (10, 5))
        
        # Draw company name
        company_text = f"Company: {game_state.player_company.name}"
        company_surface = self.small_font.render(company_text, True, Colors.BLACK)
        self.screen.blit(company_surface, (120, 5))
        
        # Draw cash
        cash_text = f"Cash: ${game_state.player_company.cash:,.2f}"
        cash_surface = self.small_font.render(cash_text, True, Colors.BLACK)
        self.screen.blit(cash_surface, (400, 5))
        
        # Draw total policies
        total_policies = sum(game_state.player_company.policies_sold.values())
        policies_text = f"Total Policies: {total_policies:,}"
        policies_surface = self.small_font.render(policies_text, True, Colors.BLACK)
        self.screen.blit(policies_surface, (650, 5))
        
        # If we have financial history, show some key metrics
        if game_state.financial_history:
            latest_report = game_state.financial_history[-1]
            
            # Show loss ratio
            loss_ratio = latest_report.claims_paid / latest_report.revenue if latest_report.revenue > 0 else 0
            ratio_text = f"Loss Ratio: {loss_ratio:.1%}"
            ratio_color = Colors.GREEN if loss_ratio < 0.7 else Colors.ORANGE if loss_ratio < 0.9 else Colors.RED
            ratio_surface = self.small_font.render(ratio_text, True, ratio_color)
            self.screen.blit(ratio_surface, (850, 5))
            
            # Show net income
            income_text = f"Net Income: ${latest_report.net_income:,.2f}"
            income_color = Colors.GREEN if latest_report.net_income > 0 else Colors.RED
            income_surface = self.small_font.render(income_text, True, income_color)
            self.screen.blit(income_surface, (1020, 5)) 