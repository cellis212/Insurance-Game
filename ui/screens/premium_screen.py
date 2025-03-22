import pygame
from ..components import Colors, Button, Panel, Slider

class PremiumScreen:
    def __init__(self, screen_rect, font, small_font):
        self.rect = screen_rect
        self.font = font
        self.small_font = small_font
        
        # Create main panel
        self.main_panel = Panel(
            pygame.Rect(
                screen_rect.left + 20,
                screen_rect.top + 20,
                screen_rect.width - 40,
                screen_rect.height - 80
            ),
            "Premium Rates & Advertising",
            font,
            bg_color=Colors.BG_PANEL,
            header_color=Colors.PRIMARY_DARK
        )
        
        # Create tables panel within main panel
        content_rect = self.main_panel.get_content_rect()
        
        # Create sliders for premium adjustment
        self.sliders = {}
        self.active_slider = None
        
        # Create input boxes for advertising budgets
        self.ad_input_boxes = {}
        self.active_ad_input = None
        
        # Create save button
        self.save_button = Button(
            pygame.Rect(screen_rect.centerx - 80, screen_rect.bottom - 60, 160, 40),
            "Save Changes", font,
            color=Colors.SUCCESS,
            hover_color=Colors.SUCCESS_DARK,
            border_radius=10
        )
    
    def render(self, screen, game_state):
        """Render the premium setting screen."""
        # Draw background
        pygame.draw.rect(screen, Colors.WHITE, self.rect)
        
        # Draw main panel
        self.main_panel.draw(screen)
        
        # Get content area
        content_rect = self.main_panel.get_content_rect()
        
        # Draw table headers with modern look
        headers = ["Line", "Base Rate", "Your Rate", "Market Avg", "Policies", "Market Share", "Ad Budget"]
        col_width = content_rect.width // len(headers)
        
        # Draw header background
        header_rect = pygame.Rect(
            content_rect.left,
            content_rect.top,
            content_rect.width,
            30
        )
        pygame.draw.rect(screen, Colors.PRIMARY_LIGHTEST, header_rect, border_radius=5)
        
        # Draw header text
        for i, header in enumerate(headers):
            text = self.small_font.render(header, True, Colors.PRIMARY_DARK)
            text_rect = text.get_rect(center=(content_rect.left + (i + 0.5) * col_width, header_rect.centery))
            screen.blit(text, text_rect)
        
        # Draw premium data for each line
        y = header_rect.bottom + 15
        row_height = 70
        
        for line_id, segment in game_state.market_segments.items():
            state_id = line_id.split("_")[0]
            if not game_state.unlocked_states[state_id]:
                continue
            
            # Get rates
            base_rate = game_state.base_market_rates[line_id]
            player_rate = game_state.player_company.premium_rates.get(line_id, base_rate)
            
            # Calculate market average (including AI competitors)
            all_rates = [player_rate]
            for competitor in game_state.ai_competitors:
                comp_rate = competitor.premium_rates.get(line_id, base_rate)
                all_rates.append(comp_rate)
            market_avg = sum(all_rates) / len(all_rates)
            
            # Calculate market share
            total_policies = sum(comp.policies_sold.get(line_id, 0) for comp in game_state.ai_competitors)
            total_policies += game_state.player_company.policies_sold.get(line_id, 0)
            market_share = (game_state.player_company.policies_sold.get(line_id, 0) / total_policies 
                          if total_policies > 0 else 0)
            
            # Draw row background (alternating colors)
            row_rect = pygame.Rect(
                content_rect.left,
                y,
                content_rect.width,
                row_height
            )
            row_color = Colors.WHITE if (line_id.count("_") % 2 == 0) else Colors.GRAY_LIGHTEST
            pygame.draw.rect(screen, row_color, row_rect, border_radius=5)
            
            x = content_rect.left
            
            # Draw line name with state badge
            line_color = Colors.PRIMARY_DARK if "home" in line_id else Colors.INFO_DARK
            line_bg_rect = pygame.Rect(x + 10, y + 10, col_width - 20, 30)
            pygame.draw.rect(screen, line_color, line_bg_rect, border_radius=15)
            
            text = self.small_font.render(segment.name, True, Colors.WHITE)
            text_rect = text.get_rect(center=line_bg_rect.center)
            screen.blit(text, text_rect)
            x += col_width
            
            # Draw base rate
            text = self.small_font.render(f"${base_rate:,.2f}", True, Colors.TEXT_DEFAULT)
            text_rect = text.get_rect(center=(x + col_width // 2, y + row_height // 2))
            screen.blit(text, text_rect)
            x += col_width
            
            # Create/update slider for premium rate
            slider_rect = pygame.Rect(
                x + 10,
                y + (row_height - 20) // 2,
                col_width - 20,
                20
            )
            
            if line_id not in self.sliders:
                # Create new slider
                slider = Slider(
                    slider_rect,
                    base_rate * 0.5,  # Min value
                    base_rate * 2.0,  # Max value
                    player_rate,      # Current value
                    label_font=self.small_font,
                    show_min_max=False,
                    value_format="${:.2f}"
                )
                self.sliders[line_id] = slider
            else:
                # Update existing slider position
                self.sliders[line_id].rect = slider_rect
                self.sliders[line_id].set_value(player_rate, trigger_callback=False)
            
            # Draw slider
            self.sliders[line_id].draw(screen)
            x += col_width
            
            # Draw market average
            if player_rate > market_avg:
                text_color = Colors.DANGER
            elif player_rate < market_avg:
                text_color = Colors.SUCCESS
            else:
                text_color = Colors.TEXT_DEFAULT
                
            text = self.small_font.render(f"${market_avg:,.2f}", True, text_color)
            text_rect = text.get_rect(center=(x + col_width // 2, y + row_height // 2))
            screen.blit(text, text_rect)
            x += col_width
            
            # Draw policies with pill background
            policies = game_state.player_company.policies_sold.get(line_id, 0)
            policy_text = f"{policies:,}"
            
            # Create pill background
            text_surf = self.small_font.render(policy_text, True, Colors.TEXT_DEFAULT)
            pill_width = text_surf.get_width() + 20
            pill_rect = pygame.Rect(
                x + (col_width - pill_width) // 2,
                y + (row_height - 30) // 2,
                pill_width,
                30
            )
            pygame.draw.rect(screen, Colors.GRAY_LIGHTEST, pill_rect, border_radius=15)
            
            # Add text to pill
            text_rect = text_surf.get_rect(center=pill_rect.center)
            screen.blit(text_surf, text_rect)
            x += col_width
            
            # Draw market share with bar visualization
            share_text = f"{market_share:.1%}"
            share_bar_width = int(col_width * 0.7)
            share_bar_height = 15
            
            # Draw background bar
            bar_bg_rect = pygame.Rect(
                x + (col_width - share_bar_width) // 2,
                y + row_height // 2 - share_bar_height // 2,
                share_bar_width,
                share_bar_height
            )
            pygame.draw.rect(screen, Colors.GRAY_LIGHT, bar_bg_rect, border_radius=share_bar_height//2)
            
            # Draw filled portion
            if market_share > 0:
                fill_width = int(share_bar_width * market_share)
                if fill_width > 0:
                    fill_rect = pygame.Rect(
                        bar_bg_rect.left,
                        bar_bg_rect.top,
                        fill_width,
                        share_bar_height
                    )
                    fill_color = Colors.SUCCESS if market_share > 0.3 else Colors.PRIMARY
                    pygame.draw.rect(screen, fill_color, fill_rect, 
                                   border_radius=share_bar_height//2)
            
            # Draw share text
            text = self.small_font.render(share_text, True, Colors.TEXT_DEFAULT)
            text_rect = text.get_rect(center=(x + col_width // 2, y + row_height // 2 + share_bar_height + 10))
            screen.blit(text, text_rect)
            x += col_width
            
            # Create/update advertising budget input box
            input_rect = pygame.Rect(x + 10, y + (row_height - 30) // 2, col_width - 20, 30)
            if line_id not in self.ad_input_boxes:
                current_budget = game_state.player_company.advertising_budget.get(line_id, 0)
                self.ad_input_boxes[line_id] = {
                    "rect": input_rect,
                    "text": f"{current_budget:,.0f}",
                    "error": None
                }
            else:
                self.ad_input_boxes[line_id]["rect"] = input_rect
            
            # Draw advertising budget input box
            input_box = self.ad_input_boxes[line_id]
            input_color = Colors.PRIMARY if self.active_ad_input == line_id else Colors.GRAY_MEDIUM
            pygame.draw.rect(screen, Colors.WHITE, input_box["rect"], border_radius=5)
            pygame.draw.rect(screen, input_color, input_box["rect"], 2, border_radius=5)
            
            # Format text with commas for display
            try:
                display_value = f"${float(input_box['text'].replace(',', '')):,.0f}"
            except ValueError:
                display_value = input_box["text"]
            
            text_surface = self.small_font.render(display_value, True, Colors.TEXT_DEFAULT)
            text_rect = text_surface.get_rect(center=input_box["rect"].center)
            screen.blit(text_surface, text_rect)
            
            # Draw error message if any
            if input_box["error"]:
                error_surface = self.small_font.render(input_box["error"], True, Colors.DANGER)
                error_rect = error_surface.get_rect(top=input_box["rect"].bottom + 2, centerx=input_box["rect"].centerx)
                screen.blit(error_surface, error_rect)
            
            y += row_height + 10  # Add spacing between rows
        
        # Draw save button
        self.save_button.draw(screen)
    
    def handle_event(self, event, game_state):
        """Handle mouse events for premium adjustment and advertising budgets."""
        # Check save button first
        if self.save_button.handle_event(event):
            # Save advertising budgets
            for line_id, input_box in self.ad_input_boxes.items():
                try:
                    amount = float(input_box["text"].replace(',', ''))
                    if game_state.set_advertising_budget(line_id, amount):
                        input_box["error"] = None
                    else:
                        input_box["error"] = "Invalid budget"
                except ValueError:
                    input_box["error"] = "Invalid number"
            return "market_overview"
        
        # Check sliders
        for line_id, slider in self.sliders.items():
            if slider.handle_event(event):
                # Update game state with new premium rate
                game_state.player_company.premium_rates[line_id] = slider.get_value()
                return None
        
        # Handle input boxes for advertising budgets
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicked on an advertising input box
            for line_id, input_box in self.ad_input_boxes.items():
                if input_box["rect"].collidepoint(event.pos):
                    self.active_ad_input = line_id
                    break
            else:
                self.active_ad_input = None
        
        elif event.type == pygame.KEYDOWN and self.active_ad_input:
            input_box = self.ad_input_boxes[self.active_ad_input]
            if event.key == pygame.K_RETURN:
                self.active_ad_input = None
            elif event.key == pygame.K_BACKSPACE:
                input_box["text"] = input_box["text"][:-1]
                input_box["error"] = None
            elif event.unicode.isnumeric() or event.unicode == ',':
                # Allow numbers and commas for formatting
                input_box["text"] += event.unicode
                input_box["error"] = None
                # Try to validate the number
                try:
                    amount = float(input_box["text"].replace(',', ''))
                    if amount < 0:
                        input_box["error"] = "Must be positive"
                    elif amount > game_state.player_company.cash:
                        input_box["error"] = "Insufficient funds"
                except ValueError:
                    input_box["error"] = "Invalid number"
        
        return None 