import pygame
from game_logic import GameState
import numpy as np
from ui.components.colors import Colors
from ui.components.button import Button
from ui.components.panel import Panel
from ui.components.share_dialog import ShareDialog
from ui.components.icons import Icons
from ui.components.background import Background
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
        
        # Load icons
        self.icons = Icons()
        
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
        button_width = 130
        button_height = 40
        button_spacing = 10
        start_x = (self.width - (button_width * 7 + button_spacing * 6)) // 2  # Updated for 7 buttons
        
        # Define icon size
        icon_size = (20, 20)
        
        self.premium_button = Button(
            pygame.Rect(start_x, 40, button_width, button_height),
            "Premium Rates",
            self.main_font,
            icon=self.icons.get('home', icon_size)
        )
        
        self.investment_button = Button(
            pygame.Rect(start_x + button_width + button_spacing, 40, button_width, button_height),
            "Investments",
            self.main_font,
            icon=self.icons.get('investment', icon_size)
        )
        
        self.reports_button = Button(
            pygame.Rect(start_x + (button_width + button_spacing) * 2, 40, button_width, button_height),
            "Reports",
            self.main_font,
            icon=self.icons.get('reports', icon_size)
        )
        
        self.save_load_button = Button(
            pygame.Rect(start_x + (button_width + button_spacing) * 3, 40, button_width, button_height),
            "Save / Load",
            self.main_font,
            icon=self.icons.get('save', icon_size)
        )
        
        self.analytics_button = Button(
            pygame.Rect(start_x + (button_width + button_spacing) * 4, 40, button_width, button_height),
            "Analytics",
            self.main_font,
            color=(70, 130, 180),  # Steel blue
            icon=self.icons.get('analytics', icon_size)
        )
        
        self.share_button = Button(
            pygame.Rect(start_x + (button_width + button_spacing) * 5, 40, button_width, button_height),
            "Share",
            self.main_font,
            color=(29, 161, 242),  # Twitter blue
            icon=self.icons.get('share', icon_size)
        )
        
        self.next_turn_button = Button(
            pygame.Rect(start_x + (button_width + button_spacing) * 6, 40, button_width, button_height),
            "End Turn",
            self.main_font,
            color=Colors.SUCCESS,
            hover_color=Colors.SUCCESS_DARK,
            icon=self.icons.get('settings', icon_size)
        )
        
        # Header panel for improved appearance
        self.header_panel = Panel(
            pygame.Rect(0, 0, self.width, 30),
            bg_color=Colors.PRIMARY_DARK,
            border_radius=0
        )
        
        # Footer panel for status messages
        self.footer_panel = Panel(
            pygame.Rect(0, self.height - 30, self.width, 30),
            bg_color=Colors.GRAY_LIGHTEST,
            border_color=Colors.GRAY_LIGHT,
            border_radius=0
        )
        
        # UI state
        self.in_startup = True
        self.current_screen = "premium"  # Default screen after startup
        self.showing_turn_summary = False
        self.showing_save_load = False
        self.showing_share = False
        self.status_message = ""
        self.status_message_color = Colors.TEXT_DEFAULT
        self.status_message_timer = 0
        
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
        # Draw background pattern
        Background.render_insurance_theme(self.screen, pygame.Rect(0, 0, self.width, self.height))
        
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
        
        # Draw header panel
        self.header_panel.draw(self.screen)
        
        # Draw company name in header
        if game_state:
            header_text = f"{game_state.player_company.name} - Quarter {game_state.current_turn + 1}"
            header_surface = self.small_font.render(header_text, True, Colors.WHITE)
            header_rect = header_surface.get_rect(midleft=(20, self.header_panel.rect.centery))
            self.screen.blit(header_surface, header_rect)
        
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
            pygame.draw.rect(self.screen, Colors.PRIMARY, self.premium_button.rect, 3, border_radius=8)
        elif self.current_screen == "investment":
            pygame.draw.rect(self.screen, Colors.PRIMARY, self.investment_button.rect, 3, border_radius=8)
        elif self.current_screen == "reports":
            pygame.draw.rect(self.screen, Colors.PRIMARY, self.reports_button.rect, 3, border_radius=8)
        
        # Draw current screen
        if not self.showing_save_load and not self.showing_turn_summary and not self.showing_share:
            if self.current_screen == "premium":
                self.premium_screen.render(self.screen, game_state)
            elif self.current_screen == "investment":
                self.investment_screen.render(self.screen, game_state)
            elif self.current_screen == "reports":
                self.reports_screen.render(self.screen, game_state)
        
        # Draw overlays
        if self.showing_turn_summary:
            # Dim background
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            self.screen.blit(overlay, (0, 0))
            self.turn_summary.render(self.screen, game_state)
        
        if self.showing_save_load:
            # Dim background
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            self.screen.blit(overlay, (0, 0))
            self.save_load_screen.render(self.screen)
        
        if self.showing_share:
            # Dim background
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            self.screen.blit(overlay, (0, 0))
            self.share_dialog.render(self.screen)
        
        # Draw footer with status message
        self.footer_panel.draw(self.screen)
        
        if self.status_message:
            status_surface = self.small_font.render(self.status_message, True, self.status_message_color)
            status_rect = status_surface.get_rect(center=(self.width // 2, self.height - 15))
            self.screen.blit(status_surface, status_rect)
            
            # Decrease timer
            self.status_message_timer -= 1
            if self.status_message_timer <= 0:
                self.status_message = ""
    
    def _draw_info_bar(self, game_state):
        """Draw the information bar with key metrics."""
        # Create info panel
        info_panel = Panel(
            pygame.Rect(20, 95, self.width - 40, 40),
            bg_color=Colors.PRIMARY_LIGHTEST,
            border_radius=5
        )
        info_panel.draw(self.screen)
        
        # Define metrics to display
        metrics = [
            {"label": "Cash", "value": f"${game_state.player_company.cash:,.2f}",
             "color": Colors.SUCCESS if game_state.player_company.cash >= 100000 else Colors.DANGER},
            {"label": "Policies", "value": f"{sum(game_state.player_company.policies_sold.values()):,}"},
            {"label": "States", "value": f"{sum(1 for state in game_state.unlocked_states.values() if state)}/{len(game_state.unlocked_states)}"}
        ]
        
        # Add loss ratio if we have financial history
        if game_state.financial_history:
            last_report = game_state.financial_history[-1]
            loss_ratio = last_report.loss_ratio
            metrics.append({
                "label": "Loss Ratio", 
                "value": f"{loss_ratio:.1%}",
                "color": Colors.SUCCESS if loss_ratio < 0.95 else (
                          Colors.WARNING if loss_ratio < 1.05 else Colors.DANGER)
            })
            
            # Add investment income
            metrics.append({
                "label": "Investment Value", 
                "value": f"${last_report.investment_value:,.2f}"
            })
        
        # Calculate metric width
        metric_width = (self.width - 40) / len(metrics)
        
        # Draw each metric
        for i, metric in enumerate(metrics):
            x = info_panel.rect.left + i * metric_width + metric_width/2
            
            # Draw label
            label_surface = self.small_font.render(metric["label"], True, Colors.TEXT_MUTED)
            label_rect = label_surface.get_rect(center=(x, info_panel.rect.top + 15))
            self.screen.blit(label_surface, label_rect)
            
            # Draw value with specified color or default
            value_color = metric.get("color", Colors.TEXT_DEFAULT)
            value_surface = self.main_font.render(metric["value"], True, value_color)
            value_rect = value_surface.get_rect(center=(x, info_panel.rect.bottom - 12))
            self.screen.blit(value_surface, value_rect)
    
    def show_turn_summary(self, game_state):
        """Show the turn summary popup."""
        self.showing_turn_summary = True
        self.turn_summary.update(game_state)
    
    def show_save_load_message(self, message, color=Colors.PRIMARY):
        """Show a temporary message at the bottom of the screen."""
        self.status_message = message
        self.status_message_color = color
        self.status_message_timer = 180  # Show for 3 seconds (60 FPS) 