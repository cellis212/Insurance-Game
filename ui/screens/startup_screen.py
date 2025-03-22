import pygame
from ..components import Colors, Button

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