import pygame
import math
from ..components import Colors, Button, Panel, Slider

class InvestmentScreen:
    def __init__(self, screen_rect, font, small_font):
        self.rect = screen_rect
        self.font = font
        self.small_font = small_font
        self.buttons = {}
        self.input_boxes = {}
        self.active_input = None
        self.chart_animations = {}
        self.animation_frame = 0
        
        # Calculate section dimensions with padding
        padding = 20
        section_width = (screen_rect.width - 3 * padding) // 2
        
        # Create main panel
        self.main_panel = Panel(
            pygame.Rect(
                screen_rect.left + padding,
                screen_rect.top + 10,
                screen_rect.width - padding * 2,
                screen_rect.height - 20
            ),
            "Investment Management",
            font,
            bg_color=Colors.BG_PANEL,
            header_color=Colors.PRIMARY_DARK
        )
        
        content_rect = self.main_panel.get_content_rect()
        
        # Create panels for portfolio and market
        self.portfolio_panel = Panel(
            pygame.Rect(
                content_rect.left,
                content_rect.top,
                section_width,
                content_rect.height // 2 - padding // 2
            ),
            "Your Portfolio",
            small_font,
            bg_color=Colors.WHITE,
            header_color=Colors.PRIMARY
        )
        
        self.allocation_panel = Panel(
            pygame.Rect(
                content_rect.left,
                self.portfolio_panel.rect.bottom + padding,
                section_width,
                content_rect.height // 2 - padding // 2
            ),
            "Asset Allocation",
            small_font,
            bg_color=Colors.WHITE,
            header_color=Colors.PRIMARY
        )
        
        self.market_panel = Panel(
            pygame.Rect(
                content_rect.left + section_width + padding,
                content_rect.top,
                section_width,
                content_rect.height // 2 - padding // 2
            ),
            "Market Overview",
            small_font,
            bg_color=Colors.WHITE,
            header_color=Colors.PRIMARY
        )
        
        self.price_chart_panel = Panel(
            pygame.Rect(
                content_rect.left + section_width + padding,
                self.market_panel.rect.bottom + padding,
                section_width,
                content_rect.height // 2 - padding // 2
            ),
            "Price History",
            small_font,
            bg_color=Colors.WHITE,
            header_color=Colors.PRIMARY
        )
        
        # Selected asset for detailed view
        self.selected_asset_id = None

    def render(self, screen, game_state):
        """Render the investment screen."""
        # Update animation frame
        self.animation_frame = (self.animation_frame + 1) % 60  # 60 FPS animation cycle
        
        # Draw main panel
        self.main_panel.draw(screen)
        
        # Draw each section panel
        self.portfolio_panel.draw(screen)
        self.allocation_panel.draw(screen)
        self.market_panel.draw(screen)
        self.price_chart_panel.draw(screen)
        
        # Draw portfolio table
        self._draw_portfolio(screen, self.portfolio_panel.get_content_rect(), game_state)
        
        # Draw asset allocation chart (pie chart)
        self._draw_allocation_chart(screen, self.allocation_panel.get_content_rect(), game_state)
        
        # Draw market overview
        self._draw_market(screen, self.market_panel.get_content_rect(), game_state)
        
        # Draw price chart for selected asset
        self._draw_price_chart(screen, self.price_chart_panel.get_content_rect(), game_state)
    
    def _draw_portfolio(self, screen, rect, game_state):
        """Draw the player's investment portfolio."""
        # Draw table headers
        headers = ["Asset", "Shares", "Value", "Return", "Actions"]
        col_widths = {
            "Asset": int(rect.width * 0.3),
            "Shares": int(rect.width * 0.15),
            "Value": int(rect.width * 0.2),
            "Return": int(rect.width * 0.15),
            "Actions": int(rect.width * 0.2)
        }
        
        # Draw headers with background
        header_rect = pygame.Rect(rect.left, rect.top, rect.width, 25)
        pygame.draw.rect(screen, Colors.PRIMARY_LIGHTEST, header_rect, border_radius=3)
        
        x = rect.left + 5
        for header in headers:
            text = self.small_font.render(header, True, Colors.PRIMARY_DARK)
            screen.blit(text, (x, rect.top + 5))
            x += col_widths[header]
        
        # Draw portfolio data
        total_value = 0
        row_height = 45
        y = rect.top + 30
        asset_index = 0
        
        for asset_id, asset in game_state.investment_assets.items():
            shares = game_state.player_company.investments.get(asset_id, 0)
            value = shares * asset.current_price
            total_value += value
            
            # Draw row background (alternating colors)
            row_rect = pygame.Rect(rect.left, y, rect.width, row_height)
            row_color = Colors.WHITE if asset_index % 2 == 0 else Colors.GRAY_LIGHTEST
            
            # Highlight selected asset
            if asset_id == self.selected_asset_id:
                row_color = Colors.PRIMARY_LIGHTEST
            
            pygame.draw.rect(screen, row_color, row_rect, border_radius=3)
            
            x = rect.left + 5
            
            # Asset name
            text = self.small_font.render(asset.name, True, Colors.TEXT_DEFAULT)
            # Create clickable area for asset name
            asset_name_rect = pygame.Rect(x, y, col_widths["Asset"], row_height)
            if asset_id == self.selected_asset_id:
                pygame.draw.rect(screen, Colors.PRIMARY_LIGHT, asset_name_rect, 1, border_radius=3)
            
            text_rect = text.get_rect(midleft=(x + 5, y + row_height // 2))
            screen.blit(text, text_rect)
            x += col_widths["Asset"]
            
            # Shares
            text = self.small_font.render(f"{shares:,}", True, Colors.TEXT_DEFAULT)
            text_rect = text.get_rect(midright=(x + col_widths["Shares"] - 10, y + row_height // 2))
            screen.blit(text, text_rect)
            x += col_widths["Shares"]
            
            # Value
            text = self.small_font.render(f"${value:,.2f}", True, Colors.TEXT_DEFAULT)
            text_rect = text.get_rect(midright=(x + col_widths["Value"] - 10, y + row_height // 2))
            screen.blit(text, text_rect)
            x += col_widths["Value"]
            
            # Return (with arrow indicator)
            if len(asset.price_history) > 1:
                price_change = (asset.current_price - asset.price_history[-2]) / asset.price_history[-2]
                color = Colors.SUCCESS if price_change >= 0 else Colors.DANGER
                
                # Draw arrow
                arrow_rect = pygame.Rect(x, y + row_height // 2 - 8, 16, 16)
                if price_change >= 0:
                    # Up arrow
                    pygame.draw.polygon(screen, color, [
                        (arrow_rect.centerx, arrow_rect.top),
                        (arrow_rect.right, arrow_rect.bottom),
                        (arrow_rect.left, arrow_rect.bottom)
                    ])
                else:
                    # Down arrow
                    pygame.draw.polygon(screen, color, [
                        (arrow_rect.centerx, arrow_rect.bottom),
                        (arrow_rect.right, arrow_rect.top),
                        (arrow_rect.left, arrow_rect.top)
                    ])
                
                text = self.small_font.render(f"{abs(price_change):.1%}", True, color)
                text_rect = text.get_rect(midleft=(arrow_rect.right + 5, y + row_height // 2))
                screen.blit(text, text_rect)
            x += col_widths["Return"]
            
            # Trading interface
            button_width = 45
            button_height = 25
            input_width = 60
            button_spacing = 5
            
            # Create or update input box
            if asset_id not in self.input_boxes:
                self.input_boxes[asset_id] = {
                    "rect": pygame.Rect(x, y + (row_height - button_height) // 2, input_width, button_height),
                    "text": "100",
                    "error": None
                }
            else:
                self.input_boxes[asset_id]["rect"] = pygame.Rect(x, y + (row_height - button_height) // 2, input_width, button_height)
            
            # Draw input box
            input_box = self.input_boxes[asset_id]
            input_color = Colors.PRIMARY if self.active_input == asset_id else Colors.GRAY_MEDIUM
            pygame.draw.rect(screen, Colors.WHITE, input_box["rect"], border_radius=5)
            pygame.draw.rect(screen, input_color, input_box["rect"], 2, border_radius=5)
            
            # Format text
            try:
                display_value = f"{int(input_box['text']):,}"
            except:
                display_value = input_box["text"]
                
            text_surface = self.small_font.render(display_value, True, Colors.TEXT_DEFAULT)
            text_rect = text_surface.get_rect(center=input_box["rect"].center)
            screen.blit(text_surface, text_rect)
            
            # Draw error message if any
            if input_box["error"]:
                error_surface = self.small_font.render(input_box["error"], True, Colors.DANGER)
                error_rect = error_surface.get_rect(top=input_box["rect"].bottom + 2, centerx=input_box["rect"].centerx)
                screen.blit(error_surface, error_rect)
            
            # Buy button
            buy_rect = pygame.Rect(
                x + input_width + button_spacing,
                y + (row_height - button_height) // 2,
                button_width,
                button_height
            )
            
            if asset_id not in self.buttons:
                self.buttons[asset_id] = {
                    "buy": Button(
                        buy_rect,
                        "Buy",
                        self.small_font,
                        color=Colors.SUCCESS,
                        border_radius=5
                    ),
                    "sell": Button(
                        pygame.Rect(
                            buy_rect.right + button_spacing,
                            y + (row_height - button_height) // 2,
                            button_width,
                            button_height
                        ),
                        "Sell",
                        self.small_font,
                        color=Colors.DANGER,
                        border_radius=5
                    )
                }
            else:
                self.buttons[asset_id]["buy"].rect = buy_rect
                self.buttons[asset_id]["sell"].rect = pygame.Rect(
                    buy_rect.right + button_spacing,
                    y + (row_height - button_height) // 2,
                    button_width,
                    button_height
                )
            
            self.buttons[asset_id]["buy"].draw(screen)
            
            # Only show sell button if we have shares
            if shares > 0:
                self.buttons[asset_id]["sell"].draw(screen)
            
            y += row_height
            asset_index += 1
            
            # Stop if we're going beyond the panel
            if y + row_height > rect.bottom:
                break
        
        # Draw total value in a colored box at the bottom
        if y + 40 < rect.bottom:
            total_rect = pygame.Rect(rect.left, rect.bottom - 35, rect.width, 30)
            pygame.draw.rect(screen, Colors.PRIMARY_LIGHTEST, total_rect, border_radius=5)
            
            text = self.small_font.render(f"Total Portfolio Value:", True, Colors.PRIMARY_DARK)
            value_text = self.font.render(f"${total_value:,.2f}", True, Colors.PRIMARY_DARK)
            
            text_rect = text.get_rect(midleft=(total_rect.left + 10, total_rect.centery))
            value_rect = value_text.get_rect(midright=(total_rect.right - 10, total_rect.centery))
            
            screen.blit(text, text_rect)
            screen.blit(value_text, value_rect)
    
    def _draw_allocation_chart(self, screen, rect, game_state):
        """Draw pie chart showing asset allocation."""
        # Calculate center and radius of pie chart
        center_x = rect.left + rect.width // 2
        center_y = rect.top + rect.height // 2 + 10
        radius = min(rect.width, rect.height) // 2 - 20
        
        # Collect data for pie chart
        portfolio_data = []
        total_value = 0
        
        # Get total portfolio value and asset values
        for asset_id, asset in game_state.investment_assets.items():
            shares = game_state.player_company.investments.get(asset_id, 0)
            value = shares * asset.current_price
            if value > 0:
                total_value += value
                portfolio_data.append({
                    "asset_id": asset_id,
                    "asset_name": asset.name,
                    "value": value,
                    "shares": shares,
                    "color": self._get_asset_color(asset_id)
                })
        
        # Sort by value (largest first)
        portfolio_data.sort(key=lambda x: x["value"], reverse=True)
        
        # If no investments, show empty state
        if total_value == 0:
            text = self.font.render("No investments yet", True, Colors.TEXT_MUTED)
            text_rect = text.get_rect(center=(center_x, center_y))
            screen.blit(text, text_rect)
            return
            
        # Calculate animation target for each slice
        for asset in portfolio_data:
            if asset["asset_id"] not in self.chart_animations:
                self.chart_animations[asset["asset_id"]] = 0
            
            # Animate toward target (ratio of total)
            target = asset["value"] / total_value
            current = self.chart_animations[asset["asset_id"]]
            
            # Smoothly animate toward target
            if abs(target - current) > 0.001:
                self.chart_animations[asset["asset_id"]] += (target - current) * 0.2
            else:
                self.chart_animations[asset["asset_id"]] = target
                
        # Draw pie chart slices
        start_angle = 0
        for asset in portfolio_data:
            # Calculate slice angle based on asset value
            slice_angle = self.chart_animations[asset["asset_id"]] * 360
            end_angle = start_angle + slice_angle
            
            # Draw slice
            pygame.draw.arc(screen, asset["color"], 
                           pygame.Rect(center_x - radius, center_y - radius, radius * 2, radius * 2),
                           math.radians(start_angle), math.radians(end_angle), radius)
            
            # Draw pie sector as filled polygon
            points = [
                (center_x, center_y),  # Center
                (center_x + radius * math.cos(math.radians(start_angle)), 
                 center_y - radius * math.sin(math.radians(start_angle))),  # Start point
            ]
            
            # Add intermediate points for better filling
            steps = max(1, int(slice_angle / 10))
            for i in range(steps):
                angle = start_angle + (slice_angle * (i+1) / steps)
                points.append((
                    center_x + radius * math.cos(math.radians(angle)),
                    center_y - radius * math.sin(math.radians(angle))
                ))
            
            if len(points) > 2:
                pygame.draw.polygon(screen, asset["color"], points)
            
            # Add labels if slice is large enough
            if slice_angle > 15:
                # Calculate position for label (middle of slice)
                label_angle = math.radians(start_angle + slice_angle / 2)
                label_distance = radius * 0.7  # 70% of the way out
                label_x = center_x + label_distance * math.cos(label_angle)
                label_y = center_y - label_distance * math.sin(label_angle)
                
                # Determine color based on selected asset
                text_color = Colors.WHITE
                
                # Draw percentage
                percentage = asset["value"] / total_value * 100
                text = self.small_font.render(f"{percentage:.1f}%", True, text_color)
                text_rect = text.get_rect(center=(label_x, label_y))
                screen.blit(text, text_rect)
            
            start_angle = end_angle
        
        # Draw legend
        legend_y = rect.bottom - len(portfolio_data) * 20 - 10
        for asset in portfolio_data:
            # Draw color box
            color_rect = pygame.Rect(rect.left + 10, legend_y, 12, 12)
            pygame.draw.rect(screen, asset["color"], color_rect)
            
            # Draw asset name and value
            text = self.small_font.render(f"{asset['asset_name']}", True, Colors.TEXT_DEFAULT)
            value_text = self.small_font.render(f"${asset['value']:,.2f}", True, Colors.TEXT_DEFAULT)
            
            screen.blit(text, (color_rect.right + 5, legend_y))
            screen.blit(value_text, (rect.right - value_text.get_width() - 10, legend_y))
            
            legend_y += 20
    
    def _draw_market(self, screen, rect, game_state):
        """Draw market information and asset performance."""
        # Draw assets in a card-like layout
        card_width = rect.width - 20
        card_height = 70
        card_spacing = 10
        
        y = rect.top + 5
        
        for asset_id, asset in game_state.investment_assets.items():
            # Draw card background
            card_rect = pygame.Rect(rect.left + 10, y, card_width, card_height)
            
            # Highlight selected asset
            if asset_id == self.selected_asset_id:
                pygame.draw.rect(screen, Colors.PRIMARY_LIGHTEST, card_rect, border_radius=5)
                pygame.draw.rect(screen, Colors.PRIMARY, card_rect, 2, border_radius=5)
            else:
                pygame.draw.rect(screen, Colors.WHITE, card_rect, border_radius=5)
                pygame.draw.rect(screen, Colors.GRAY_LIGHT, card_rect, 1, border_radius=5)
            
            # Asset name with iconic symbol
            symbol_rect = pygame.Rect(card_rect.left + 15, card_rect.top + 10, 35, 35)
            pygame.draw.rect(screen, self._get_asset_color(asset_id), symbol_rect, border_radius=5)
            
            # Draw asset type icon/symbol
            symbol = asset_id[0] if asset_id else "?"
            symbol_text = self.font.render(symbol, True, Colors.WHITE)
            symbol_rect_center = symbol_text.get_rect(center=symbol_rect.center)
            screen.blit(symbol_text, symbol_rect_center)
            
            # Asset name and current price
            name_text = self.small_font.render(asset.name, True, Colors.PRIMARY_DARK)
            screen.blit(name_text, (symbol_rect.right + 10, card_rect.top + 10))
            
            price_text = self.font.render(f"${asset.current_price:,.2f}", True, Colors.TEXT_DEFAULT)
            screen.blit(price_text, (symbol_rect.right + 10, card_rect.top + 30))
            
            # Asset metrics on the right side
            metrics_x = card_rect.right - 100
            
            # Price change
            if len(asset.price_history) > 1:
                price_change = (asset.current_price - asset.price_history[-2]) / asset.price_history[-2]
                color = Colors.SUCCESS if price_change >= 0 else Colors.DANGER
                change_text = f"{price_change:+.1%}"
                
                # Add some animation to the change value if selected
                if asset_id == self.selected_asset_id:
                    pulse = (math.sin(self.animation_frame * 0.1) + 1) * 0.5  # Value between 0 and 1
                    color = self._interpolate_colors(color, Colors.WHITE, pulse * 0.3)
                
                change_surface = self.small_font.render(change_text, True, color)
                screen.blit(change_surface, (metrics_x, card_rect.top + 10))
            
            # Yield
            yield_text = f"Yield: {asset.dividend_yield:.1%}"
            yield_surface = self.small_font.render(yield_text, True, Colors.TEXT_DEFAULT)
            screen.blit(yield_surface, (metrics_x, card_rect.top + 30))
            
            # Mini sparkline chart
            if len(asset.price_history) > 1:
                sparkline_rect = pygame.Rect(card_rect.right - 70, card_rect.top + 15, 60, 40)
                self._draw_sparkline(screen, sparkline_rect, asset.price_history, 
                                    color=Colors.SUCCESS if price_change >= 0 else Colors.DANGER)
            
            y += card_height + card_spacing
            
            # Stop if we're going beyond the panel
            if y + card_height > rect.bottom:
                break
    
    def _draw_price_chart(self, screen, rect, game_state):
        """Draw price chart for the selected asset."""
        # Show message if no asset selected
        if not self.selected_asset_id or self.selected_asset_id not in game_state.investment_assets:
            text = self.font.render("Select an asset to view price history", True, Colors.TEXT_MUTED)
            text_rect = text.get_rect(center=(rect.centerx, rect.centery))
            screen.blit(text, text_rect)
            return
        
        # Get selected asset
        asset = game_state.investment_assets[self.selected_asset_id]
        
        # Get price history
        history = asset.price_history
        if len(history) < 2:
            text = self.font.render("Not enough price data yet", True, Colors.TEXT_MUTED)
            text_rect = text.get_rect(center=(rect.centerx, rect.centery))
            screen.blit(text, text_rect)
            return
        
        # Calculate chart dimensions
        chart_padding = 40
        chart_rect = pygame.Rect(
            rect.left + chart_padding,
            rect.top + chart_padding,
            rect.width - chart_padding * 2,
            rect.height - chart_padding * 2
        )
        
        # Find min and max values for scaling
        min_price = min(history)
        max_price = max(history)
        price_range = max_price - min_price
        
        # Ensure range is at least 10% of max for better visualization
        if price_range < 0.1 * max_price:
            price_range = 0.1 * max_price
            min_price = max_price - price_range
        
        # Draw chart background grid
        self._draw_chart_grid(screen, chart_rect, min_price, max_price)
        
        # Draw price line
        if len(history) > 1:
            points = []
            for i, price in enumerate(history):
                x = chart_rect.left + chart_rect.width * i / (len(history) - 1)
                y = chart_rect.bottom - chart_rect.height * (price - min_price) / price_range
                points.append((x, y))
            
            # Determine color based on price trend
            if history[-1] >= history[0]:
                line_color = Colors.SUCCESS
                area_color = Colors.SUCCESS_LIGHT
            else:
                line_color = Colors.DANGER
                area_color = Colors.DANGER_LIGHT
            
            # Draw area under the curve
            if len(points) > 1:
                area_points = points.copy()
                area_points.append((points[-1][0], chart_rect.bottom))
                area_points.append((points[0][0], chart_rect.bottom))
                pygame.draw.polygon(screen, area_color, area_points)
            
            # Draw the price line
            if len(points) > 1:
                pygame.draw.lines(screen, line_color, False, points, 2)
                
            # Draw points on the line
            for point in points:
                pygame.draw.circle(screen, line_color, point, 3)
        
        # Draw latest price value prominently
        latest_price = history[-1]
        price_text = f"${latest_price:,.2f}"
        price_surface = self.font.render(price_text, True, Colors.PRIMARY_DARK)
        screen.blit(price_surface, (rect.right - price_surface.get_width() - 10, rect.top + 10))
        
        # Draw price change
        if len(history) > 1:
            price_change = (history[-1] - history[-2]) / history[-2]
            change_color = Colors.SUCCESS if price_change >= 0 else Colors.DANGER
            change_text = f"{price_change:+.1%}"
            change_surface = self.small_font.render(change_text, True, change_color)
            screen.blit(change_surface, (rect.right - change_surface.get_width() - 10, rect.top + 40))

    def _draw_chart_grid(self, screen, rect, min_value, max_value):
        """Draw grid lines for a chart."""
        # Draw horizontal grid lines
        num_lines = 5
        for i in range(num_lines + 1):
            y = rect.bottom - i * rect.height / num_lines
            pygame.draw.line(screen, Colors.GRAY_LIGHT, (rect.left, y), (rect.right, y), 1)
            
            if i > 0:
                value = min_value + (max_value - min_value) * i / num_lines
                text = self.small_font.render(f"${value:,.2f}", True, Colors.TEXT_MUTED)
                screen.blit(text, (rect.left - text.get_width() - 5, y - text.get_height() / 2))
        
        # Draw vertical grid lines (quarters)
        for i in range(5):
            x = rect.left + i * rect.width / 4
            pygame.draw.line(screen, Colors.GRAY_LIGHT, (x, rect.top), (x, rect.bottom), 1)
            
            if i > 0:
                text = self.small_font.render(f"Q{i}", True, Colors.TEXT_MUTED)
                screen.blit(text, (x - text.get_width() / 2, rect.bottom + 5))
    
    def _draw_sparkline(self, screen, rect, data, color=Colors.PRIMARY):
        """Draw a small sparkline chart."""
        if len(data) < 2:
            return
            
        # Find min and max
        min_val = min(data)
        max_val = max(data)
        val_range = max_val - min_val
        
        # Ensure range is not zero
        if val_range == 0:
            val_range = max_val * 0.1 or 1.0
        
        # Draw the sparkline
        points = []
        for i, value in enumerate(data):
            x = rect.left + rect.width * i / (len(data) - 1)
            y = rect.bottom - rect.height * (value - min_val) / val_range
            points.append((x, y))
        
        if len(points) > 1:
            pygame.draw.lines(screen, color, False, points, 1)
            
            # Draw endpoint
            pygame.draw.circle(screen, color, points[-1], 2)
    
    def _get_asset_color(self, asset_id):
        """Get a color for an asset based on its ID."""
        # Use pre-defined colors from the Colors class for consistency
        colors = [
            Colors.PRIMARY,
            Colors.SUCCESS,
            Colors.INFO,
            Colors.WARNING,
            Colors.DANGER
        ]
        
        # Generate a predictable index based on asset ID
        index = hash(asset_id) % len(colors)
        return colors[index]
    
    def _interpolate_colors(self, color1, color2, ratio):
        """Interpolate between two colors."""
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        
        # If we have alpha channels
        if len(color1) > 3 and len(color2) > 3:
            a = int(color1[3] * (1 - ratio) + color2[3] * ratio)
            return (r, g, b, a)
            
        return (r, g, b)
    
    def handle_event(self, event, game_state):
        """Handle button clicks and input for buying/selling assets."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check for asset selection in portfolio
            content_rect = self.portfolio_panel.get_content_rect()
            x = content_rect.left + 5
            y = content_rect.top + 30
            row_height = 45
            asset_index = 0
            
            for asset_id, asset in game_state.investment_assets.items():
                # Create asset name clickable area
                asset_name_rect = pygame.Rect(x, y, content_rect.width * 0.3, row_height)
                if asset_name_rect.collidepoint(event.pos):
                    self.selected_asset_id = asset_id
                
                # Check next row
                y += row_height
                asset_index += 1
                
                # Stop if we're going beyond the panel
                if y + row_height > content_rect.bottom:
                    break
            
            # Check for asset selection in market overview
            content_rect = self.market_panel.get_content_rect()
            y = content_rect.top + 5
            card_width = content_rect.width - 20
            card_height = 70
            card_spacing = 10
            
            for asset_id, asset in game_state.investment_assets.items():
                card_rect = pygame.Rect(content_rect.left + 10, y, card_width, card_height)
                if card_rect.collidepoint(event.pos):
                    self.selected_asset_id = asset_id
                
                y += card_height + card_spacing
                
                if y + card_height > content_rect.bottom:
                    break
            
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
                    shares = int(input_box["text"].replace(",", ""))
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
            elif event.unicode.isnumeric() or event.unicode == ',':
                # Allow numbers and commas for formatting
                input_box["text"] += event.unicode
                input_box["error"] = None
        
        return None 