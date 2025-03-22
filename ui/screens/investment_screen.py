import pygame
from ..components import Colors, Button

class InvestmentScreen:
    def __init__(self, screen_rect, font, small_font):
        self.rect = screen_rect
        self.font = font
        self.small_font = small_font
        self.buttons = {}
        self.input_boxes = {}
        self.active_input = None
        
        # Calculate section dimensions with padding
        padding = 20
        section_width = (screen_rect.width - 3 * padding) // 2
        
        # Create sections with proper spacing
        self.portfolio_rect = pygame.Rect(
            screen_rect.left + padding,
            screen_rect.top + 60,  # Leave room for title
            section_width,
            screen_rect.height - 80
        )
        
        self.market_rect = pygame.Rect(
            screen_rect.left + section_width + (2 * padding),
            screen_rect.top + 60,
            section_width,
            screen_rect.height - 80
        )

    def render(self, screen, game_state):
        """Render the investment screen."""
        # Draw background
        pygame.draw.rect(screen, Colors.WHITE, self.rect)
        
        # Draw title
        title = self.font.render("Investment Management", True, Colors.BLUE)
        screen.blit(title, (self.rect.centerx - title.get_width()//2, self.rect.top + 20))
        
        # Draw portfolio section
        self._draw_portfolio(screen, self.portfolio_rect, game_state)
        
        # Draw market section
        self._draw_market(screen, self.market_rect, game_state)
    
    def _draw_portfolio(self, screen, rect, game_state):
        """Draw the player's investment portfolio."""
        # Draw section header
        header = self.font.render("Your Portfolio", True, Colors.BLUE)
        screen.blit(header, (rect.left, rect.top))
        
        # Draw table headers
        headers = ["Asset", "Shares", "Value", "Return", "Actions"]
        col_widths = {
            "Asset": int(rect.width * 0.3),
            "Shares": int(rect.width * 0.15),
            "Value": int(rect.width * 0.2),
            "Return": int(rect.width * 0.15),
            "Actions": int(rect.width * 0.2)
        }
        
        # Draw headers
        x = rect.left
        y = rect.top + 40
        for header in headers:
            text = self.small_font.render(header, True, Colors.BLUE)
            screen.blit(text, (x, y))
            x += col_widths[header]
        
        # Draw separator line
        y += 25
        pygame.draw.line(screen, Colors.BLACK, (rect.left, y), (rect.right, y))
        y += 10
        
        # Draw portfolio data
        total_value = 0
        row_height = 40
        
        for asset_id, asset in game_state.investment_assets.items():
            shares = game_state.player_company.investments.get(asset_id, 0)
            value = shares * asset.current_price
            total_value += value
            
            x = rect.left
            
            # Asset name
            text = self.small_font.render(asset.name, True, Colors.BLACK)
            screen.blit(text, (x, y + 10))
            x += col_widths["Asset"]
            
            # Shares
            text = self.small_font.render(f"{shares:,}", True, Colors.BLACK)
            screen.blit(text, (x, y + 10))
            x += col_widths["Shares"]
            
            # Value
            text = self.small_font.render(f"${value:,.2f}", True, Colors.BLACK)
            screen.blit(text, (x, y + 10))
            x += col_widths["Value"]
            
            # Return
            if len(asset.price_history) > 1:
                price_change = (asset.current_price - asset.price_history[-2]) / asset.price_history[-2]
                color = Colors.GREEN if price_change >= 0 else Colors.RED
                text = self.small_font.render(f"{price_change:+.1%}", True, color)
                screen.blit(text, (x, y + 10))
            x += col_widths["Return"]
            
            # Input box and buttons
            button_width = 50
            button_height = 25
            input_width = 60
            button_spacing = 5
            
            # Create or update input box
            if asset_id not in self.input_boxes:
                self.input_boxes[asset_id] = {
                    "rect": pygame.Rect(x, y + 5, input_width, button_height),
                    "text": "100",
                    "error": None
                }
            else:
                self.input_boxes[asset_id]["rect"] = pygame.Rect(x, y + 5, input_width, button_height)
            
            # Draw input box
            input_box = self.input_boxes[asset_id]
            input_color = Colors.BLUE if self.active_input == asset_id else Colors.GRAY
            pygame.draw.rect(screen, input_color, input_box["rect"], 2)
            text_surface = self.small_font.render(input_box["text"], True, Colors.BLACK)
            screen.blit(text_surface, (input_box["rect"].left + 5, input_box["rect"].top + 5))
            
            # Draw error message if any
            if input_box["error"]:
                error_surface = self.small_font.render(input_box["error"], True, Colors.RED)
                screen.blit(error_surface, (input_box["rect"].left, input_box["rect"].bottom + 5))
            
            # Buy button
            buy_rect = pygame.Rect(x + input_width + button_spacing, y + 5, button_width, button_height)
            if asset_id not in self.buttons:
                self.buttons[asset_id] = {
                    "buy": Button(buy_rect, "Buy", self.small_font),
                    "sell": Button(
                        pygame.Rect(buy_rect.right + button_spacing, y + 5, button_width, button_height),
                        "Sell",
                        self.small_font
                    )
                }
            else:
                self.buttons[asset_id]["buy"].rect = buy_rect
                self.buttons[asset_id]["sell"].rect = pygame.Rect(
                    buy_rect.right + button_spacing, y + 5, button_width, button_height
                )
            
            self.buttons[asset_id]["buy"].draw(screen)
            if shares > 0:
                self.buttons[asset_id]["sell"].draw(screen)
            
            y += row_height
        
        # Draw total value
        if y < rect.bottom - 50:  # Only if there's space
            y += 10
            pygame.draw.line(screen, Colors.BLACK, (rect.left, y), (rect.right, y))
            y += 10
            text = self.small_font.render(f"Total Portfolio Value: ${total_value:,.2f}", True, Colors.BLUE)
            screen.blit(text, (rect.left, y))
    
    def _draw_market(self, screen, rect, game_state):
        """Draw market information and trends."""
        # Draw section header
        header = self.font.render("Market Overview", True, Colors.BLUE)
        screen.blit(header, (rect.left, rect.top))
        
        y = rect.top + 40
        
        # Draw market data in a table format
        for asset_id, asset in game_state.investment_assets.items():
            # Draw asset name and price
            price_text = f"{asset.name}: ${asset.current_price:,.2f}"
            text = self.small_font.render(price_text, True, Colors.BLACK)
            screen.blit(text, (rect.left, y))
            
            # Calculate and draw price change
            if len(asset.price_history) > 1:
                price_change = (asset.current_price - asset.price_history[-2]) / asset.price_history[-2]
                color = Colors.GREEN if price_change >= 0 else Colors.RED
                change_text = f"({price_change:+.1%})"
                text = self.small_font.render(change_text, True, color)
                screen.blit(text, (rect.left + 300, y))
            
            # Draw yield
            yield_text = f"Yield: {asset.dividend_yield:.1%}"
            text = self.small_font.render(yield_text, True, Colors.BLACK)
            screen.blit(text, (rect.right - text.get_width(), y))
            
            y += 35
    
    def handle_event(self, event, game_state):
        """Handle button clicks and input for buying/selling assets."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Handle input box selection
            clicked_input = None
            for asset_id, input_box in self.input_boxes.items():
                if input_box["rect"].collidepoint(event.pos):
                    clicked_input = asset_id
                    break
            self.active_input = clicked_input
            
            # Handle buy/sell buttons
            for asset_id, buttons in self.buttons.items():
                input_box = self.input_boxes[asset_id]
                try:
                    shares = int(input_box["text"])
                    if shares <= 0:
                        input_box["error"] = "Must be positive"
                        continue
                        
                    if buttons["buy"].handle_event(event):
                        # Buy shares
                        asset = game_state.investment_assets[asset_id]
                        cost = asset.current_price * shares
                        if cost <= game_state.player_company.cash:
                            game_state.player_company.cash -= cost
                            current_shares = game_state.player_company.investments.get(asset_id, 0)
                            game_state.player_company.investments[asset_id] = current_shares + shares
                            input_box["error"] = None
                            return True
                        else:
                            input_box["error"] = "Insufficient funds"
                    
                    elif buttons["sell"].handle_event(event):
                        # Sell shares
                        current_shares = game_state.player_company.investments.get(asset_id, 0)
                        if current_shares >= shares:
                            asset = game_state.investment_assets[asset_id]
                            proceeds = asset.current_price * shares
                            game_state.player_company.cash += proceeds
                            game_state.player_company.investments[asset_id] = current_shares - shares
                            input_box["error"] = None
                            return True
                        else:
                            input_box["error"] = "Not enough shares"
                
                except ValueError:
                    input_box["error"] = "Invalid number"
        
        elif event.type == pygame.KEYDOWN and self.active_input:
            input_box = self.input_boxes[self.active_input]
            if event.key == pygame.K_RETURN:
                self.active_input = None
            elif event.key == pygame.K_BACKSPACE:
                input_box["text"] = input_box["text"][:-1]
                input_box["error"] = None
            elif event.unicode.isnumeric():
                input_box["text"] += event.unicode
                # Limit length to prevent overflow
                if len(input_box["text"]) > 6:  # Limit to 999,999 shares
                    input_box["text"] = input_box["text"][:6]
                input_box["error"] = None
        
        return False 