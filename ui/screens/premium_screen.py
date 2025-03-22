import pygame
from ..components import Colors, Button

class PremiumScreen:
    def __init__(self, screen_rect, font, small_font):
        self.rect = screen_rect
        self.font = font
        self.small_font = small_font
        
        # Create table for premium rates
        self.table_rect = pygame.Rect(
            screen_rect.left + 20,
            screen_rect.top + 60,
            screen_rect.width - 40,
            screen_rect.height - 80
        )
        
        # Create sliders for premium adjustment
        self.sliders = {}
        self.active_slider = None
        
        # Create input boxes for advertising budgets
        self.ad_input_boxes = {}
        self.active_ad_input = None
        
        # Create save button
        self.save_button = Button(
            pygame.Rect(screen_rect.centerx - 60, screen_rect.bottom - 50, 120, 40),
            "Save", font
        )
    
    def render(self, screen, game_state):
        """Render the premium setting screen."""
        # Draw background
        pygame.draw.rect(screen, Colors.WHITE, self.rect)
        
        # Draw title
        title = self.font.render("Premium Rates & Advertising", True, Colors.BLUE)
        screen.blit(title, (self.rect.centerx - title.get_width()//2, self.rect.top + 20))
        
        # Draw table headers
        headers = ["Line", "Base Rate", "Your Rate", "Market Avg", "Policies", "Market Share", "Ad Budget"]
        col_width = self.table_rect.width // len(headers)
        for i, header in enumerate(headers):
            text = self.small_font.render(header, True, Colors.BLUE)
            screen.blit(text, (self.table_rect.left + i * col_width + 10, self.table_rect.top))
        
        # Draw separator line
        y = self.table_rect.top + 30
        pygame.draw.line(screen, Colors.BLACK, 
                        (self.table_rect.left, y), 
                        (self.table_rect.right, y))
        
        # Draw premium data for each line
        y += 10
        row_height = 60
        
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
            
            x = self.table_rect.left
            
            # Draw line name
            text = self.small_font.render(segment.name, True, Colors.BLACK)
            screen.blit(text, (x + 10, y + 10))
            x += col_width
            
            # Draw base rate
            text = self.small_font.render(f"${base_rate:,.2f}", True, Colors.BLACK)
            screen.blit(text, (x + 10, y + 10))
            x += col_width
            
            # Create/update slider for premium rate
            slider_rect = pygame.Rect(
                x + 10,
                y + 5,
                col_width - 20,
                20
            )
            if line_id not in self.sliders:
                self.sliders[line_id] = {
                    "rect": slider_rect,
                    "value": player_rate,
                    "min": base_rate * 0.5,
                    "max": base_rate * 2.0
                }
            else:
                self.sliders[line_id]["rect"] = slider_rect
            
            # Draw slider
            slider = self.sliders[line_id]
            pygame.draw.rect(screen, Colors.LIGHT_GRAY, slider["rect"])
            
            # Draw slider handle
            handle_x = slider["rect"].left + (slider["value"] - slider["min"]) / (slider["max"] - slider["min"]) * slider["rect"].width
            handle_rect = pygame.Rect(handle_x - 5, slider["rect"].top - 5, 10, slider["rect"].height + 10)
            pygame.draw.rect(screen, Colors.BLUE, handle_rect)
            
            # Draw current value
            text = self.small_font.render(f"${slider['value']:,.2f}", True, Colors.BLACK)
            screen.blit(text, (slider["rect"].left, slider["rect"].bottom + 5))
            x += col_width
            
            # Draw market average
            text = self.small_font.render(f"${market_avg:,.2f}", True, Colors.BLACK)
            screen.blit(text, (x + 10, y + 10))
            x += col_width
            
            # Draw policies
            policies = game_state.player_company.policies_sold.get(line_id, 0)
            text = self.small_font.render(f"{policies:,}", True, Colors.BLACK)
            screen.blit(text, (x + 10, y + 10))
            x += col_width
            
            # Draw market share
            text = self.small_font.render(f"{market_share:.1%}", True, Colors.BLACK)
            screen.blit(text, (x + 10, y + 10))
            x += col_width
            
            # Create/update advertising budget input box
            input_rect = pygame.Rect(x + 10, y + 5, col_width - 20, 25)
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
            input_color = Colors.BLUE if self.active_ad_input == line_id else Colors.GRAY
            pygame.draw.rect(screen, input_color, input_box["rect"], 2)
            
            # Format text with commas for display
            try:
                display_value = f"${float(input_box['text'].replace(',', '')):,.0f}"
            except ValueError:
                display_value = input_box["text"]
            
            text_surface = self.small_font.render(display_value, True, Colors.BLACK)
            screen.blit(text_surface, (input_box["rect"].left + 5, input_box["rect"].top + 5))
            
            # Draw error message if any
            if input_box["error"]:
                error_surface = self.small_font.render(input_box["error"], True, Colors.RED)
                screen.blit(error_surface, (input_box["rect"].left, input_box["rect"].bottom + 5))
            
            y += row_height
        
        # Draw save button
        self.save_button.draw(screen)
    
    def handle_event(self, event, game_state):
        """Handle mouse events for premium adjustment and advertising budgets."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicked on a slider
            for line_id, slider in self.sliders.items():
                if slider["rect"].collidepoint(event.pos):
                    self.active_slider = line_id
                    self.active_ad_input = None
                    # Update slider value based on click position
                    self._update_slider_value(event.pos[0], line_id)
                    game_state.player_company.premium_rates[line_id] = self.sliders[line_id]["value"]
            
            # Check if clicked on an advertising input box
            for line_id, input_box in self.ad_input_boxes.items():
                if input_box["rect"].collidepoint(event.pos):
                    self.active_ad_input = line_id
                    self.active_slider = None
                    break
            else:
                self.active_ad_input = None
            
            # Check save button
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
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.active_slider = None
        
        elif event.type == pygame.MOUSEMOTION and self.active_slider:
            # Update slider value based on drag position
            self._update_slider_value(event.pos[0], self.active_slider)
            game_state.player_company.premium_rates[self.active_slider] = self.sliders[self.active_slider]["value"]
        
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
    
    def _update_slider_value(self, x_pos, line_id):
        """Update slider value based on mouse position."""
        slider = self.sliders[line_id]
        # Clamp x position to slider bounds
        x = max(slider["rect"].left, min(x_pos, slider["rect"].right))
        # Calculate value based on position
        value_ratio = (x - slider["rect"].left) / slider["rect"].width
        slider["value"] = slider["min"] + value_ratio * (slider["max"] - slider["min"])
        # Round to nearest cent
        slider["value"] = round(slider["value"], 2) 