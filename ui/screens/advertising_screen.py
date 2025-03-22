import pygame
from ..components import Colors, Button

class AdvertisingScreen:
    def __init__(self, screen_rect, font, small_font):
        self.rect = screen_rect
        self.font = font
        self.small_font = small_font
        
        # Create table for advertising budgets
        self.table_rect = pygame.Rect(
            screen_rect.left + 20,
            screen_rect.top + 60,
            screen_rect.width - 40,
            screen_rect.height - 80
        )
        
        # Create input boxes for advertising budgets
        self.ad_input_boxes = {}
        self.active_ad_input = None
        
        # Create save button
        self.save_button = Button(
            pygame.Rect(screen_rect.centerx - 60, screen_rect.bottom - 50, 120, 40),
            "Save", font
        )
    
    def render(self, screen, game_state):
        """Render the advertising screen."""
        # Draw background
        pygame.draw.rect(screen, Colors.WHITE, self.rect)
        
        # Draw title
        title = self.font.render("Advertising Budgets", True, Colors.BLUE)
        screen.blit(title, (self.rect.centerx - title.get_width()//2, self.rect.top + 20))
        
        # Draw table headers
        headers = ["Line", "Current Budget", "Market Share", "Competitors' Avg", "New Budget"]
        col_width = self.table_rect.width // len(headers)
        for i, header in enumerate(headers):
            text = self.small_font.render(header, True, Colors.BLUE)
            screen.blit(text, (self.table_rect.left + i * col_width + 10, self.table_rect.top))
        
        # Draw separator line
        y = self.table_rect.top + 30
        pygame.draw.line(screen, Colors.BLACK, 
                        (self.table_rect.left, y), 
                        (self.table_rect.right, y))
        
        # Draw data rows
        y += 10
        row_height = 60
        
        for line_id, segment in game_state.market_segments.items():
            state_id = line_id.split("_")[0]
            if not game_state.unlocked_states[state_id]:
                continue
            
            x = self.table_rect.left
            
            # Draw line name
            text = self.small_font.render(segment.name, True, Colors.BLACK)
            screen.blit(text, (x + 10, y + 10))
            x += col_width
            
            # Draw current budget
            current_budget = game_state.player_company.advertising_budget.get(line_id, 0)
            text = self.small_font.render(f"${current_budget:,.0f}", True, Colors.BLACK)
            screen.blit(text, (x + 10, y + 10))
            x += col_width
            
            # Draw market share
            total_policies = sum(comp.policies_sold.get(line_id, 0) for comp in game_state.ai_competitors)
            total_policies += game_state.player_company.policies_sold.get(line_id, 0)
            market_share = (game_state.player_company.policies_sold.get(line_id, 0) / total_policies 
                          if total_policies > 0 else 0)
            text = self.small_font.render(f"{market_share:.1%}", True, Colors.BLACK)
            screen.blit(text, (x + 10, y + 10))
            x += col_width
            
            # Draw competitors' average advertising
            comp_budgets = [comp.advertising_budget.get(line_id, 0) for comp in game_state.ai_competitors]
            avg_comp_budget = sum(comp_budgets) / len(comp_budgets) if comp_budgets else 0
            text = self.small_font.render(f"${avg_comp_budget:,.0f}", True, Colors.BLACK)
            screen.blit(text, (x + 10, y + 10))
            x += col_width
            
            # Create/update input box for new budget
            input_rect = pygame.Rect(x + 10, y + 5, col_width - 20, 25)
            if line_id not in self.ad_input_boxes:
                self.ad_input_boxes[line_id] = {
                    "rect": input_rect,
                    "text": f"{current_budget:,.0f}",
                    "error": None
                }
            else:
                self.ad_input_boxes[line_id]["rect"] = input_rect
            
            # Draw input box
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
        """Handle mouse events for advertising budget inputs."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicked on an input box
            for line_id, input_box in self.ad_input_boxes.items():
                if input_box["rect"].collidepoint(event.pos):
                    self.active_ad_input = line_id
                    break
            else:
                self.active_ad_input = None
            
            # Check save button
            if self.save_button.handle_event(event):
                # Save advertising budgets
                for line_id, input_box in self.ad_input_boxes.items():
                    try:
                        amount = float(input_box["text"].replace(',', ''))
                        if amount < 0:
                            input_box["error"] = "Must be positive"
                            continue
                        elif amount > game_state.player_company.cash:
                            input_box["error"] = "Insufficient funds"
                            continue
                        game_state.player_company.advertising_budget[line_id] = amount
                        input_box["error"] = None
                    except ValueError:
                        input_box["error"] = "Invalid number"
                return "market_overview"
        
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