import pygame
from game_logic import GameState
import numpy as np

class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    BLUE = (0, 100, 200)
    GREEN = (0, 200, 0)
    RED = (200, 0, 0)
    LIGHT_BLUE = (100, 150, 255)

class Button:
    def __init__(self, rect, text, font, color=Colors.BLUE, hover_color=Colors.LIGHT_BLUE):
        self.rect = rect
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        text_surface = self.font.render(self.text, True, Colors.WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.is_hovered = self.rect.collidepoint(mouse_pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                return True
        return False

class Slider:
    def __init__(self, rect, min_value=0.8, max_value=1.5, initial_value=1.0):
        self.rect = rect
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.handle_radius = 8
        self.is_dragging = False
        
        # Calculate handle position
        self.handle_x = self._value_to_x(initial_value)
    
    def _value_to_x(self, value):
        """Convert a value to x position"""
        ratio = (value - self.min_value) / (self.max_value - self.min_value)
        return self.rect.left + int(ratio * self.rect.width)
    
    def _x_to_value(self, x):
        """Convert x position to value"""
        ratio = (x - self.rect.left) / self.rect.width
        return self.min_value + ratio * (self.max_value - self.min_value)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            handle_rect = pygame.Rect(
                self.handle_x - self.handle_radius,
                self.rect.centery - self.handle_radius,
                self.handle_radius * 2,
                self.handle_radius * 2
            )
            if handle_rect.collidepoint(mouse_pos):
                self.is_dragging = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False
        
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            mouse_x = pygame.mouse.get_pos()[0]
            # Constrain to slider bounds
            mouse_x = max(self.rect.left, min(self.rect.right, mouse_x))
            self.handle_x = mouse_x
            self.value = self._x_to_value(mouse_x)
            # Round to 2 decimal places
            self.value = round(self.value, 2)
            return True
        
        return False
    
    def draw(self, screen):
        # Draw track
        pygame.draw.rect(screen, Colors.GRAY, self.rect, 2)
        
        # Draw handle
        pygame.draw.circle(screen, Colors.BLUE, (self.handle_x, self.rect.centery), self.handle_radius)

class PremiumSettingScreen:
    def __init__(self, screen_rect, font, small_font):
        self.rect = screen_rect
        self.font = font
        self.small_font = small_font
        
        # Create state selection buttons at the top
        self.state_buttons = {}
        button_width = 150
        x_offset = self.rect.left + 20
        for state_id in ["CA", "FL"]:
            button_rect = pygame.Rect(
                x_offset,
                self.rect.top + 20,
                button_width,
                40
            )
            self.state_buttons[state_id] = Button(button_rect, f"{state_id} Premiums", small_font)
            x_offset += button_width + 20
        
        # Create sliders for each insurance line
        self.premium_sliders = {}
        for state_id in ["CA", "FL"]:
            self.premium_sliders[state_id] = {}
            for line in ["home", "auto"]:
                slider_rect = pygame.Rect(
                    self.rect.left + 200,
                    self.rect.top + 200 + (100 if line == "home" else 200),  # Space between sliders
                    200,  # Width of slider
                    4     # Height of slider track
                )
                self.premium_sliders[state_id][f"{line}"] = Slider(slider_rect)
        
        # Create save button
        self.save_button = Button(
            pygame.Rect(self.rect.centerx - 60, self.rect.bottom - 50, 120, 40),
            "Save", font
        )
        
        self.current_state = None
        self.error_message = None
    
    def handle_event(self, event, game_state):
        # Handle state selection
        if event.type == pygame.MOUSEBUTTONDOWN:
            for state_id, button in self.state_buttons.items():
                if button.handle_event(event):
                    if game_state.unlocked_states[state_id]:
                        self.current_state = state_id
                        self.error_message = None
                    else:
                        self.error_message = f"You must unlock {game_state.states[state_id]['name']} first!"
                    return None
            
            # Handle save button
            if self.save_button.handle_event(event):
                return "market_overview"
        
        # Only handle slider events if a state is selected and unlocked
        if self.current_state and game_state.unlocked_states[self.current_state]:
            for line, slider in self.premium_sliders[self.current_state].items():
                if slider.handle_event(event):
                    # Update premium rates immediately
                    self._update_premium_rate(game_state, f"{self.current_state}_{line}")
        
        return None
    
    def _update_premium_rate(self, game_state, line_id):
        """Update premium rate based on slider value (expected loss ratio)"""
        state_id, line = line_id.split("_")
        base_rate = game_state.base_market_rates[line_id]
        expected_loss_ratio = self.premium_sliders[state_id][line].value
        game_state.player_company.premium_rates[line_id] = base_rate * expected_loss_ratio
    
    def render(self, screen, game_state):
        pygame.draw.rect(screen, Colors.WHITE, self.rect)
        
        # Draw title
        title = self.font.render("Set Premium Rates", True, Colors.BLACK)
        screen.blit(title, (self.rect.centerx - title.get_width()//2, self.rect.top + 20))
        
        # Draw state selection buttons
        y_offset = self.rect.top + 80
        for state_id, button in self.state_buttons.items():
            # Update button color based on lock status
            if game_state.unlocked_states[state_id]:
                button.color = Colors.BLUE if state_id == self.current_state else Colors.GRAY
            else:
                button.color = Colors.RED
            button.draw(screen)
        
        # Draw error message if any
        if self.error_message:
            error_surface = self.small_font.render(self.error_message, True, Colors.RED)
            screen.blit(error_surface, (self.rect.centerx - error_surface.get_width()//2, y_offset + 30))
        
        # Only draw premium settings if a state is selected and unlocked
        if self.current_state and game_state.unlocked_states[self.current_state]:
            state_info = game_state.states[self.current_state]
            
            # Draw state header
            state_header = self.font.render(f"{state_info['name']} Premium Settings", True, Colors.BLUE)
            screen.blit(state_header, (self.rect.centerx - state_header.get_width()//2, y_offset + 60))
            
            # Draw explanation
            explanation = self.small_font.render("Adjust sliders to set premium rates as percentage of expected losses", True, Colors.GRAY)
            screen.blit(explanation, (self.rect.centerx - explanation.get_width()//2, y_offset + 90))
            
            # Draw sliders for each line
            y_offset = self.rect.top + 200
            for line in ["home", "auto"]:
                line_id = f"{self.current_state}_{line}"
                slider = self.premium_sliders[self.current_state][line]
                
                # Draw line name
                line_name = f"{line.title()} Insurance"
                name_surface = self.font.render(line_name, True, Colors.BLACK)
                screen.blit(name_surface, (self.rect.left + 40, y_offset - 20))
                
                # Draw slider
                slider.draw(screen)
                
                # Draw current multiplier and resulting premium
                multiplier_text = f"{slider.value:.2f}x"
                premium_amount = game_state.base_market_rates[line_id] * slider.value
                rate_text = f"Annual Premium: ${premium_amount:,.2f}"
                
                # Draw texts
                multiplier_surface = self.small_font.render(multiplier_text, True, Colors.BLUE)
                rate_surface = self.small_font.render(rate_text, True, Colors.BLACK)
                
                screen.blit(multiplier_surface, (slider.rect.right + 20, y_offset - 10))
                screen.blit(rate_surface, (slider.rect.right + 100, y_offset - 10))
                
                # Draw base rate and risk info
                base_text = f"Expected Annual Claims: ${game_state.base_market_rates[line_id]:,.2f}"
                risk_text = f"Claim Frequency: {game_state.market_segments[line_id].base_risk*100:.1f}% per year"
                
                # Add catastrophe risk info for home insurance
                if line == "home":
                    cat_risk = state_info["catastrophe_risk"] * 100
                    cat_text = f"Catastrophe Risk: {cat_risk:.1f}% per year"
                    cat_surface = self.small_font.render(cat_text, True, Colors.RED)
                    screen.blit(cat_surface, (self.rect.left + 40, y_offset + 40))
                
                base_surface = self.small_font.render(base_text, True, Colors.GRAY)
                risk_surface = self.small_font.render(risk_text, True, Colors.GRAY)
                
                screen.blit(base_surface, (self.rect.left + 40, y_offset + 20))
                screen.blit(risk_surface, (self.rect.left + 300, y_offset + 20))
                
                y_offset += 100
            
            # Draw save button
            self.save_button.draw(screen)

class InvestmentScreen:
    def __init__(self, screen_rect, font, small_font):
        self.rect = screen_rect
        self.font = font
        self.small_font = small_font
        
        # Create buy/sell buttons for each asset
        button_width = 80
        button_height = 30
        self.buy_buttons = {}
        self.sell_buttons = {}
        
        # Create input boxes for share amounts
        self.share_inputs = {}
        for asset_id in ["SP500", "CORP_BONDS", "LONG_TREASURY", "SHORT_TREASURY", "REIT"]:
            # Create buy button
            buy_rect = pygame.Rect(
                self.rect.right - 200,
                0,  # Y position will be set during rendering
                button_width,
                button_height
            )
            self.buy_buttons[asset_id] = Button(buy_rect, "Buy", small_font, Colors.GREEN)
            
            # Create sell button
            sell_rect = pygame.Rect(
                self.rect.right - 100,
                0,  # Y position will be set during rendering
                button_width,
                button_height
            )
            self.sell_buttons[asset_id] = Button(sell_rect, "Sell", small_font, Colors.RED)
            
            # Create share input
            self.share_inputs[asset_id] = {
                "rect": pygame.Rect(
                    self.rect.right - 300,
                    0,  # Y position will be set during rendering
                    80,
                    button_height
                ),
                "text": "0",
                "active": False
            }
        
        self.error_message = None
    
    def handle_event(self, event, game_state):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Handle share input box clicks
            for asset_id, input_box in self.share_inputs.items():
                if input_box["rect"].collidepoint(event.pos):
                    input_box["active"] = True
                else:
                    input_box["active"] = False
            
            # Handle buy/sell button clicks
            for asset_id in game_state.investment_assets:
                # Handle buy button
                if self.buy_buttons[asset_id].handle_event(event):
                    try:
                        shares = int(self.share_inputs[asset_id]["text"])
                        if shares > 0:
                            if game_state.buy_asset(asset_id, shares):
                                self.error_message = None
                                self.share_inputs[asset_id]["text"] = "0"
                            else:
                                self.error_message = "Insufficient funds for purchase"
                        else:
                            self.error_message = "Please enter a positive number of shares"
                    except ValueError:
                        self.error_message = "Please enter a valid number of shares"
                
                # Handle sell button
                if self.sell_buttons[asset_id].handle_event(event):
                    try:
                        shares = int(self.share_inputs[asset_id]["text"])
                        if shares > 0:
                            if game_state.sell_asset(asset_id, shares):
                                self.error_message = None
                                self.share_inputs[asset_id]["text"] = "0"
                            else:
                                self.error_message = "Insufficient shares to sell"
                        else:
                            self.error_message = "Please enter a positive number of shares"
                    except ValueError:
                        self.error_message = "Please enter a valid number of shares"
        
        elif event.type == pygame.KEYDOWN:
            # Handle share input box typing
            for input_box in self.share_inputs.values():
                if input_box["active"]:
                    if event.key == pygame.K_RETURN:
                        input_box["active"] = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_box["text"] = input_box["text"][:-1]
                    elif event.unicode.isnumeric():
                        input_box["text"] += event.unicode
        
        return None
    
    def render(self, screen, game_state):
        pygame.draw.rect(screen, Colors.WHITE, self.rect)
        
        # Draw title
        title = self.font.render("Investment Portfolio", True, Colors.BLACK)
        screen.blit(title, (self.rect.left + 20, self.rect.top + 20))
        
        # Draw cash balance
        cash_text = f"Available Cash: ${game_state.player_company.cash:,.2f}"
        cash_surface = self.font.render(cash_text, True, Colors.BLUE)
        screen.blit(cash_surface, (self.rect.left + 20, self.rect.top + 60))
        
        # Draw column headers
        y_offset = self.rect.top + 100
        headers = ["Asset", "Price", "Yield", "Your Shares", "Market Value", "Shares to Trade"]
        x_positions = [20, 200, 300, 400, 500, 650]
        for header, x in zip(headers, x_positions):
            header_surface = self.small_font.render(header, True, Colors.GRAY)
            screen.blit(header_surface, (self.rect.left + x, y_offset))
        
        # Draw assets and their details
        y_offset += 40
        for asset_id, asset in game_state.investment_assets.items():
            # Update button and input box positions
            self.buy_buttons[asset_id].rect.y = y_offset - 5
            self.sell_buttons[asset_id].rect.y = y_offset - 5
            self.share_inputs[asset_id]["rect"].y = y_offset - 5
            
            # Get current holdings
            shares = game_state.player_company.investments.get(asset_id, 0)
            market_value = shares * asset.current_price
            
            # Draw asset details
            details = [
                (asset.name, Colors.BLACK),
                (f"${asset.current_price:,.2f}", Colors.BLACK),
                (f"{asset.dividend_yield*100:.1f}%", Colors.GREEN),
                (str(shares), Colors.BLACK),
                (f"${market_value:,.2f}", Colors.BLUE)
            ]
            
            for (text, color), x in zip(details, x_positions):
                text_surface = self.small_font.render(text, True, color)
                screen.blit(text_surface, (self.rect.left + x, y_offset))
            
            # Draw share input box
            input_box = self.share_inputs[asset_id]
            color = Colors.BLUE if input_box["active"] else Colors.GRAY
            pygame.draw.rect(screen, color, input_box["rect"], 2)
            text_surface = self.small_font.render(input_box["text"], True, Colors.BLACK)
            screen.blit(text_surface, (input_box["rect"].left + 5, input_box["rect"].centery - text_surface.get_height()//2))
            
            # Draw buy/sell buttons
            self.buy_buttons[asset_id].draw(screen)
            self.sell_buttons[asset_id].draw(screen)
            
            y_offset += 50
        
        # Draw error message if any
        if self.error_message:
            error_surface = self.small_font.render(self.error_message, True, Colors.RED)
            screen.blit(error_surface, (self.rect.centerx - error_surface.get_width()//2, self.rect.bottom - 40))
        
        # Draw portfolio summary
        total_value = game_state.player_company.cash
        for asset_id, asset in game_state.investment_assets.items():
            shares = game_state.player_company.investments.get(asset_id, 0)
            total_value += shares * asset.current_price
        
        summary_text = f"Total Portfolio Value: ${total_value:,.2f}"
        summary_surface = self.font.render(summary_text, True, Colors.BLUE)
        screen.blit(summary_surface, (self.rect.left + 20, self.rect.bottom - 80))

class ReportsScreen:
    def __init__(self, screen_rect, font, small_font):
        self.rect = screen_rect
        self.font = font
        self.small_font = small_font
        
        # Create tab buttons
        self.tabs = {
            "income": Button(
                pygame.Rect(self.rect.left + 20, self.rect.top + 20, 150, 40),
                "Income Statement", small_font
            ),
            "balance": Button(
                pygame.Rect(self.rect.left + 180, self.rect.top + 20, 150, 40),
                "Balance Sheet", small_font
            ),
            "metrics": Button(
                pygame.Rect(self.rect.left + 340, self.rect.top + 20, 150, 40),
                "Key Metrics", small_font
            )
        }
        self.current_tab = "income"
    
    def handle_event(self, event, game_state):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Handle tab switching
            for tab_id, button in self.tabs.items():
                if button.handle_event(event):
                    self.current_tab = tab_id
                    return None
        return None
    
    def render(self, screen, game_state):
        pygame.draw.rect(screen, Colors.WHITE, self.rect)
        
        # Draw tabs
        for tab_id, button in self.tabs.items():
            if tab_id == self.current_tab:
                button.color = Colors.BLUE
                button.hover_color = Colors.BLUE
            else:
                button.color = Colors.GRAY
                button.hover_color = Colors.LIGHT_BLUE
            button.draw(screen)
        
        # Draw content based on current tab
        content_rect = pygame.Rect(
            self.rect.left + 20,
            self.rect.top + 80,
            self.rect.width - 40,
            self.rect.height - 100
        )
        
        if self.current_tab == "income":
            self._draw_income_statement(screen, content_rect, game_state)
        elif self.current_tab == "balance":
            self._draw_balance_sheet(screen, content_rect, game_state)
        else:
            self._draw_key_metrics(screen, content_rect, game_state)
    
    def _draw_income_statement(self, screen, rect, game_state):
        y_offset = rect.top
        
        # Get the latest financial report
        if game_state.financial_history:
            report = game_state.financial_history[-1]
            
            # Draw revenue section
            self._draw_section_header(screen, "Revenue", y_offset)
            y_offset += 40
            
            revenue_items = [
                ("Premium Revenue", report.revenue),
                ("Investment Income", report.investment_returns),
                ("Total Revenue", report.revenue + report.investment_returns)
            ]
            
            for label, value in revenue_items:
                self._draw_financial_line(screen, label, value, y_offset)
                y_offset += 30
            
            y_offset += 20
            
            # Draw expenses section
            self._draw_section_header(screen, "Expenses", y_offset)
            y_offset += 40
            
            expense_items = [
                ("Claims Paid", report.claims_paid),
                ("Operating Expenses", report.operating_expenses),
                ("Total Expenses", report.claims_paid + report.operating_expenses)
            ]
            
            for label, value in expense_items:
                self._draw_financial_line(screen, label, value, y_offset)
                y_offset += 30
            
            y_offset += 20
            
            # Draw net income
            pygame.draw.line(screen, Colors.BLACK, 
                           (rect.left, y_offset), (rect.right, y_offset))
            y_offset += 10
            self._draw_financial_line(screen, "Net Income", report.net_income, y_offset,
                                    color=Colors.GREEN if report.net_income >= 0 else Colors.RED)
        else:
            text = self.font.render("No financial data available", True, Colors.GRAY)
            screen.blit(text, (rect.centerx - text.get_width()//2, rect.centery))
    
    def _draw_balance_sheet(self, screen, rect, game_state):
        y_offset = rect.top
        
        # Assets section
        self._draw_section_header(screen, "Assets", y_offset)
        y_offset += 40
        
        # Cash
        self._draw_financial_line(screen, "Cash", game_state.player_company.cash, y_offset)
        y_offset += 30
        
        # Investments by type
        total_investments = 0
        for asset_id, asset in game_state.investment_assets.items():
            shares = game_state.player_company.investments.get(asset_id, 0)
            if shares > 0:
                market_value = shares * asset.current_price
                total_investments += market_value
                self._draw_financial_line(screen, f"{asset.name} ({shares} shares)", market_value, y_offset)
                y_offset += 30
        
        # Total Assets
        y_offset += 10
        pygame.draw.line(screen, Colors.BLACK, 
                        (rect.left, y_offset), (rect.right, y_offset))
        y_offset += 10
        total_assets = game_state.player_company.cash + total_investments
        self._draw_financial_line(screen, "Total Assets", total_assets, y_offset)
    
    def _draw_key_metrics(self, screen, rect, game_state):
        y_offset = rect.top
        
        if game_state.financial_history:
            report = game_state.financial_history[-1]
            
            metrics = [
                ("Loss Ratio", f"{(report.claims_paid / report.revenue * 100 if report.revenue > 0 else 0):.1f}%"),
                ("Operating Ratio", f"{((report.claims_paid + report.operating_expenses) / report.revenue * 100 if report.revenue > 0 else 0):.1f}%"),
                ("Investment Return", f"{(report.investment_returns / sum(game_state.player_company.investments.values()) * 100 if game_state.player_company.investments else 0):.1f}%"),
                ("Market Share", f"{sum(game_state.player_company.policies_sold.values()) / sum(segment.market_size for segment in game_state.market_segments.values()) * 100:.1f}%")
            ]
            
            for label, value in metrics:
                text = self.font.render(f"{label}: {value}", True, Colors.BLACK)
                screen.blit(text, (rect.left, y_offset))
                y_offset += 50
        else:
            text = self.font.render("No metrics available", True, Colors.GRAY)
            screen.blit(text, (rect.centerx - text.get_width()//2, rect.centery))
    
    def _draw_section_header(self, screen, text, y_offset):
        header = self.font.render(text, True, Colors.BLUE)
        screen.blit(header, (self.rect.left + 20, y_offset))
    
    def _draw_financial_line(self, screen, label, value, y_offset, color=Colors.BLACK):
        # Draw label
        label_surface = self.small_font.render(label, True, color)
        screen.blit(label_surface, (self.rect.left + 40, y_offset))
        
        # Draw value
        value_text = f"${value:,.2f}"
        value_surface = self.small_font.render(value_text, True, color)
        screen.blit(value_surface, (self.rect.right - value_surface.get_width() - 40, y_offset))

class TurnSummaryPopup:
    def __init__(self, screen_rect, font, small_font):
        self.rect = pygame.Rect(
            screen_rect.centerx - 300,
            screen_rect.centery - 200,
            600,
            400
        )
        self.font = font
        self.small_font = small_font
        
        # Create buttons
        self.continue_button = Button(
            pygame.Rect(self.rect.centerx - 60, self.rect.bottom - 50, 120, 40),
            "Continue", font
        )
    
    def render(self, screen, turn_summary):
        # Draw semi-transparent background
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # Draw popup background
        pygame.draw.rect(screen, Colors.WHITE, self.rect)
        pygame.draw.rect(screen, Colors.BLUE, self.rect, 2)
        
        # Draw title
        title = self.font.render("Turn Summary", True, Colors.BLACK)
        screen.blit(title, (self.rect.centerx - title.get_width()//2, self.rect.top + 20))
        
        # Draw summary content
        y_offset = self.rect.top + 80
        for label, value in turn_summary.items():
            text = self.small_font.render(f"{label}: {value}", True, Colors.BLACK)
            screen.blit(text, (self.rect.left + 40, y_offset))
            y_offset += 30
        
        # Draw continue button
        self.continue_button.draw(screen)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.continue_button.handle_event(event):
                return True
        return False

class StartupScreen:
    def __init__(self, screen_rect, font, small_font):
        self.rect = screen_rect
        self.font = font
        self.small_font = small_font
        
        # Create input box for company name
        self.name_input = {
            "rect": pygame.Rect(screen_rect.centerx - 150, screen_rect.centery - 100, 300, 40),
            "text": "Player Insurance Co.",
            "active": False
        }
        
        # Create state selection buttons
        self.state_buttons = {}
        y_offset = screen_rect.centery
        for state_id in ["CA", "FL"]:
            button_rect = pygame.Rect(
                screen_rect.centerx - 100,
                y_offset,
                200,
                40
            )
            self.state_buttons[state_id] = Button(button_rect, f"Start in {state_id}", font)
            y_offset += 60
        
        self.selected_state = None
        self.error_message = None
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Handle name input box
            if self.name_input["rect"].collidepoint(event.pos):
                self.name_input["active"] = True
            else:
                self.name_input["active"] = False
            
            # Handle state selection
            for state_id, button in self.state_buttons.items():
                if button.handle_event(event):
                    if not self.name_input["text"].strip():
                        self.error_message = "Please enter a company name"
                        return None
                    self.selected_state = state_id
                    return {
                        "state": state_id,
                        "name": self.name_input["text"]
                    }
        
        elif event.type == pygame.KEYDOWN and self.name_input["active"]:
            if event.key == pygame.K_RETURN:
                self.name_input["active"] = False
            elif event.key == pygame.K_BACKSPACE:
                self.name_input["text"] = self.name_input["text"][:-1]
            elif event.unicode:  # Check if the key produces a character
                # Filter out non-printable characters
                if event.unicode.isprintable():
                    self.name_input["text"] += event.unicode
                    # Limit the length to prevent overflow
                    if self.font.size(self.name_input["text"])[0] > self.name_input["rect"].width - 20:
                        self.name_input["text"] = self.name_input["text"][:-1]
        
        return None
    
    def render(self, screen):
        # Draw background
        pygame.draw.rect(screen, Colors.WHITE, self.rect)
        
        # Draw title
        title = self.font.render("Insurance Company Setup", True, Colors.BLUE)
        screen.blit(title, (self.rect.centerx - title.get_width()//2, self.rect.top + 100))
        
        # Draw name input label
        name_label = self.font.render("Company Name:", True, Colors.BLACK)
        screen.blit(name_label, (self.name_input["rect"].left, self.name_input["rect"].top - 30))
        
        # Draw name input box
        color = Colors.BLUE if self.name_input["active"] else Colors.GRAY
        pygame.draw.rect(screen, color, self.name_input["rect"], 2)
        text_surface = self.font.render(self.name_input["text"], True, Colors.BLACK)
        # Center the text vertically and align left with padding
        text_pos = (self.name_input["rect"].left + 10, 
                   self.name_input["rect"].centery - text_surface.get_height()//2)
        screen.blit(text_surface, text_pos)
        
        # Draw cursor when input is active
        if self.name_input["active"]:
            cursor_x = text_pos[0] + text_surface.get_width() + 2
            pygame.draw.line(screen, Colors.BLACK,
                           (cursor_x, text_pos[1]),
                           (cursor_x, text_pos[1] + text_surface.get_height()))
        
        # Draw state selection label
        state_label = self.font.render("Select Starting State:", True, Colors.BLACK)
        screen.blit(state_label, (self.state_buttons["CA"].rect.left, self.state_buttons["CA"].rect.top - 30))
        
        # Draw state buttons
        for state_id, button in self.state_buttons.items():
            button.draw(screen)
        
        # Draw error message if any
        if self.error_message:
            error_surface = self.small_font.render(self.error_message, True, Colors.RED)
            screen.blit(error_surface, (self.rect.centerx - error_surface.get_width()//2, self.rect.bottom - 100))

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
        self.premium_screen = PremiumSettingScreen(self.main_area, self.font, self.small_font)
        self.investment_screen = InvestmentScreen(self.main_area, self.font, self.small_font)
        self.reports_screen = ReportsScreen(self.main_area, self.font, self.small_font)
        
        # Create turn summary popup
        self.turn_summary_popup = TurnSummaryPopup(screen.get_rect(), self.font, self.small_font)
        self.showing_turn_summary = False
        self.turn_summary = {}
        
        # Create menu buttons
        self.menu_buttons = {}
        menu_items = [
            ("market_overview", "Market Overview"),
            ("set_premiums", "Set Premiums"),
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
            # Update menu button hover states
            for button in self.menu_buttons.values():
                button.handle_event(event)
            # Update end turn button hover state
            self.end_turn_button.handle_event(event)
        
        # Handle turn summary popup if it's showing
        if self.showing_turn_summary:
            if self.turn_summary_popup.handle_event(event):
                self.showing_turn_summary = False
            return
        
        # Handle mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Handle end turn button
            if self.end_turn_button.handle_event(event):
                self._end_turn()
                return
            
            # Handle menu button clicks
            for screen_id, button in self.menu_buttons.items():
                if button.handle_event(event):
                    print(f"Switching to screen: {screen_id}")  # Debug print
                    self.current_screen = screen_id
                    return
        
        # Handle current screen events
        if self.current_screen == "set_premiums":
            result = self.premium_screen.handle_event(event, self.game_state)
            if result:
                self.current_screen = result
        elif self.current_screen == "investments":
            result = self.investment_screen.handle_event(event, self.game_state)
            if result:
                self.current_screen = result
        elif self.current_screen == "reports":
            result = self.reports_screen.handle_event(event, self.game_state)
            if result:
                self.current_screen = result
    
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