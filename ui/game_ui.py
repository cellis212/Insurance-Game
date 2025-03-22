import pygame
from .screens import (
    StartupScreen,
    PremiumScreen,
    InvestmentScreen,
    ReportsScreen,
    TurnSummaryPopup,
    AdvertisingScreen
)
from .components import Colors, Button

class GameUI:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Create startup screen
        self.startup_screen = StartupScreen(screen.get_rect(), self.font, self.small_font)
        self.in_startup = True
        self.game_state = None
        
        # Define UI regions
        self.header_height = 60
        self.sidebar_width = 300
        self.main_area = pygame.Rect(
            self.sidebar_width, self.header_height,
            self.width - self.sidebar_width, self.height - self.header_height
        )
        
        # Create screens
        self.current_screen = "market_overview"
        self.premium_screen = PremiumScreen(self.main_area, self.font, self.small_font)
        self.investment_screen = InvestmentScreen(self.main_area, self.font, self.small_font)
        self.reports_screen = ReportsScreen(self.main_area, self.font, self.small_font)
        self.advertising_screen = AdvertisingScreen(self.main_area, self.font, self.small_font)
        
        # Create turn summary popup
        self.turn_summary_popup = TurnSummaryPopup(screen.get_rect(), self.font, self.small_font)
        self.showing_turn_summary = False
        self.turn_summary = {}
        
        # Create menu buttons
        self.menu_buttons = {}
        menu_items = [
            ("market_overview", "Market Overview"),
            ("set_premiums", "Set Premiums"),
            ("advertising", "Advertising"),
            ("investments", "Investments"),
            ("reports", "Reports")
        ]
        for i, (screen_id, text) in enumerate(menu_items):
            button_rect = pygame.Rect(
                10, self.header_height + 10 + i * 50,
                self.sidebar_width - 20, 40
            )
            self.menu_buttons[screen_id] = Button(button_rect, text, self.small_font)
        
        # Create end turn button
        self.end_turn_button = Button(
            pygame.Rect(10, self.height - 60, self.sidebar_width - 20, 40),
            "End Turn", self.font, Colors.GREEN
        )
    
    def handle_event(self, event):
        """Handle UI events."""
        if self.in_startup:
            result = self.startup_screen.handle_event(event)
            if result:
                return result
            return None
        
        # Update button hover states
        if event.type == pygame.MOUSEMOTION:
            for button in self.menu_buttons.values():
                button.handle_event(event)
            self.end_turn_button.handle_event(event)
        
        if self.showing_turn_summary:
            if self.turn_summary_popup.handle_event(event):
                self.showing_turn_summary = False
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.end_turn_button.handle_event(event):
                self._end_turn()
                return
            
            for screen_id, button in self.menu_buttons.items():
                if button.handle_event(event):
                    self.current_screen = screen_id
                    return
        
        # Handle current screen events
        if self.current_screen == "investments":
            if self.investment_screen.handle_event(event, self.game_state):
                # Force redraw if changes occurred
                self.render(self.game_state)
        elif self.current_screen == "set_premiums":
            result = self.premium_screen.handle_event(event, self.game_state)
            if result:
                self.current_screen = result
        elif self.current_screen == "reports":
            result = self.reports_screen.handle_event(event, self.game_state)
            if result:
                self.current_screen = result
        elif self.current_screen == "advertising":
            result = self.advertising_screen.handle_event(event, self.game_state)
            if result:
                self.current_screen = result
    
    def render(self, game_state=None):
        """Render the game UI."""
        if self.in_startup:
            self.startup_screen.render(self.screen)
            return
        
        self.game_state = game_state
        self.screen.fill(Colors.WHITE)
        
        # Draw header
        self._draw_header(game_state)
        
        # Draw sidebar with menu
        self._draw_sidebar(game_state)
        
        # Draw current screen
        if self.current_screen == "set_premiums":
            self.premium_screen.render(self.screen, game_state)
        elif self.current_screen == "investments":
            self.investment_screen.render(self.screen, game_state)
        elif self.current_screen == "reports":
            self.reports_screen.render(self.screen, game_state)
        elif self.current_screen == "advertising":
            self.advertising_screen.render(self.screen, game_state)
        else:
            self._draw_main_area(game_state)
        
        # Draw company stats
        self._draw_company_stats(game_state)
        
        # Draw end turn button
        self.end_turn_button.draw(self.screen)
        
        # Draw turn summary popup if active
        if self.showing_turn_summary:
            self.turn_summary_popup.render(self.screen, self.turn_summary)
    
    def _draw_header(self, game_state):
        """Draw the header with basic game info."""
        pygame.draw.rect(self.screen, Colors.BLUE,
                        (0, 0, self.width, self.header_height))
        
        # Draw turn counter
        turn_text = f"Turn: {game_state.current_turn}"
        text_surface = self.font.render(turn_text, True, Colors.WHITE)
        self.screen.blit(text_surface, (20, 20))
        
        # Draw company name
        company_text = game_state.player_company.name
        text_surface = self.font.render(company_text, True, Colors.WHITE)
        self.screen.blit(text_surface, (self.width // 2 - text_surface.get_width() // 2, 20))
    
    def _draw_sidebar(self, game_state):
        """Draw the sidebar with actions and menus."""
        pygame.draw.rect(self.screen, Colors.GRAY,
                        (0, self.header_height, self.sidebar_width, self.height - self.header_height))
        
        # Draw menu buttons
        for button in self.menu_buttons.values():
            button.draw(self.screen)
    
    def _draw_main_area(self, game_state):
        """Draw the main content area."""
        pygame.draw.rect(self.screen, Colors.WHITE, self.main_area)
        
        # Draw market segments by state
        y_offset = self.header_height + 20
        for state_id, state_info in game_state.states.items():
            # Draw state header with lock status
            state_header = self.font.render(state_info["name"], True, Colors.BLUE)
            self.screen.blit(state_header, (self.sidebar_width + 20, y_offset))
            
            # Draw lock status and entry cost
            if not game_state.unlocked_states[state_id]:
                lock_text = f"Locked - Entry Cost: ${state_info['entry_cost']:,}"
                lock_surface = self.small_font.render(lock_text, True, Colors.RED)
                self.screen.blit(lock_surface, (self.sidebar_width + 250, y_offset + 5))
                
                # Add unlock button if player has enough cash
                if game_state.player_company.cash >= state_info["entry_cost"]:
                    unlock_button = Button(
                        pygame.Rect(self.sidebar_width + 500, y_offset, 100, 30),
                        "Unlock", self.small_font, Colors.GREEN
                    )
                    unlock_button.draw(self.screen)
                    
                    # Handle click
                    if pygame.mouse.get_pressed()[0]:  # Left mouse button
                        mouse_pos = pygame.mouse.get_pos()
                        if unlock_button.rect.collidepoint(mouse_pos):
                            game_state.unlock_state(state_id)
            
            y_offset += 40
            
            # Only show market details if state is unlocked
            if game_state.unlocked_states[state_id]:
                for line in ["home", "auto"]:
                    line_id = f"{state_id}_{line}"
                    segment = game_state.market_segments[line_id]
                    
                    # Draw line info
                    text = f"{segment.name}: {segment.current_demand}/{segment.market_size} policies"
                    text_surface = self.small_font.render(text, True, Colors.BLACK)
                    self.screen.blit(text_surface, (self.sidebar_width + 40, y_offset))
                    
                    # Draw current premium rate
                    premium = game_state.player_company.premium_rates.get(line_id, 0)
                    premium_text = f"Premium: ${premium:,.2f}"
                    premium_surface = self.small_font.render(premium_text, True, Colors.BLACK)
                    self.screen.blit(premium_surface, (self.sidebar_width + 400, y_offset))
                    
                    # Draw policies sold
                    policies = game_state.player_company.policies_sold.get(line_id, 0)
                    policies_text = f"Your Policies: {policies}"
                    policies_surface = self.small_font.render(policies_text, True, Colors.BLACK)
                    self.screen.blit(policies_surface, (self.sidebar_width + 600, y_offset))
                    
                    y_offset += 30
            
            y_offset += 20  # Extra space between states
    
    def _draw_company_stats(self, game_state):
        """Draw company statistics."""
        stats_rect = pygame.Rect(
            self.sidebar_width + 20, self.height - 100,
            self.width - self.sidebar_width - 40, 80
        )
        pygame.draw.rect(self.screen, Colors.GRAY, stats_rect)
        
        # Draw cash balance
        cash_text = f"Cash: ${game_state.player_company.cash:,.2f}"
        text_surface = self.font.render(cash_text, True, Colors.BLACK)
        self.screen.blit(text_surface, (stats_rect.left + 10, stats_rect.top + 10))
        
        # Draw total policies
        total_policies = sum(game_state.player_company.policies_sold.values())
        policies_text = f"Total Policies: {total_policies}"
        text_surface = self.font.render(policies_text, True, Colors.BLACK)
        self.screen.blit(text_surface, (stats_rect.left + 10, stats_rect.top + 45))
    
    def _end_turn(self):
        """Process end of turn and show summary."""
        # Get latest financial report before update
        old_report = self.game_state.financial_history[-1] if self.game_state.financial_history else None
        
        # Update game state
        self.game_state.update()
        
        # Get latest financial report after update
        if self.game_state.financial_history:
            report = self.game_state.financial_history[-1]
            
            # Prepare turn summary
            self.turn_summary = {
                "Premium Revenue": f"${report.revenue:,.2f}",
                "Claims Paid": f"${report.claims_paid:,.2f}",
                "Investment Income": f"${report.investment_returns:,.2f}",
                "Unrealized Gains": f"${report.unrealized_gains:,.2f}",
                "Operating Expenses": f"${report.operating_expenses:,.2f}",
                "Net Income": f"${report.net_income:,.2f}",
                "Loss Ratio": f"{(report.claims_paid / report.revenue * 100 if report.revenue > 0 else 0):.1f}%"
            }
        
        self.showing_turn_summary = True 