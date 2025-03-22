# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.

import pygame
from .colors import Colors
from .button import Button

class ShareDialog:
    """Dialog for sharing game progress on social media and via links."""
    
    def __init__(self, screen_rect, font, small_font, company_data=None):
        self.rect = pygame.Rect(
            screen_rect.centerx - 300,
            screen_rect.centery - 200,
            600,
            400
        )
        self.font = font
        self.small_font = small_font
        self.company_data = company_data or {}
        
        # Create buttons
        button_width = 180
        button_height = 40
        self.buttons = {}
        
        # Close button
        self.buttons["close"] = Button(
            pygame.Rect(self.rect.right - 100, self.rect.top + 20, 80, 30),
            "Close",
            small_font,
            color=Colors.GRAY
        )
        
        # Share buttons
        x_pos = self.rect.left + (self.rect.width - button_width * 2 - 20) // 2
        y_pos = self.rect.bottom - 60
        
        self.buttons["twitter"] = Button(
            pygame.Rect(x_pos, y_pos, button_width, button_height),
            "Share on Twitter",
            small_font,
            color=(29, 161, 242)  # Twitter blue
        )
        
        self.buttons["copy"] = Button(
            pygame.Rect(x_pos + button_width + 20, y_pos, button_width, button_height),
            "Copy to Clipboard",
            small_font,
            color=Colors.BLUE
        )
        
        self.message_timer = 0
        self.message = ""
        self.message_color = Colors.BLACK
    
    def update_company_data(self, company_data):
        """Update the company data to share."""
        self.company_data = company_data
    
    def get_share_text(self):
        """Generate text to share about company performance."""
        if not self.company_data or not self.company_data.get('name'):
            return "Check out my insurance company in Insurance Simulation Game!"
        
        company = self.company_data
        name = company.get('name', 'My Insurance Company')
        cash = company.get('cash', 0)
        policies = company.get('total_policies', 0)
        states = company.get('states', ['CA'])
        turn = company.get('turn', 1)
        
        return f"I'm managing {name} with ${cash:,.0f} in capital and {policies:,} policies across {len(states)} states after {turn} quarters! Play Insurance Simulation Game to build your own company."
    
    def get_share_url(self):
        """Get the URL to share."""
        # In browser mode this would get the actual URL
        # For now just return a placeholder
        return "https://github.com/your-username/insurance-game"
    
    def handle_event(self, event):
        """Handle events related to the share dialog."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button_id, button in self.buttons.items():
                if button.handle_event(event):
                    if button_id == "close":
                        return "close"
                    elif button_id == "twitter":
                        self._share_on_twitter()
                        return None
                    elif button_id == "copy":
                        self._copy_to_clipboard()
                        return None
        return None
    
    def _share_on_twitter(self):
        """Share progress on Twitter."""
        share_text = self.get_share_text()
        share_url = self.get_share_url()
        try:
            # In browser environment, this would open a new tab
            if "platform" in globals() and platform.system() == 'Emscripten':
                import javascript
                tweet_url = f"https://twitter.com/intent/tweet?text={javascript.encodeURIComponent(share_text)}&url={javascript.encodeURIComponent(share_url)}"
                javascript.window.open(tweet_url, "_blank")
                self.show_message("Opening Twitter...", Colors.GREEN)
            else:
                # In desktop mode, show a message that this only works in browser
                self.show_message("Twitter sharing only available in browser", Colors.ORANGE)
        except Exception as e:
            print(f"Error sharing on Twitter: {e}")
            self.show_message("Error sharing on Twitter", Colors.RED)
    
    def _copy_to_clipboard(self):
        """Copy share text to clipboard."""
        share_text = self.get_share_text() + " " + self.get_share_url()
        try:
            # In browser environment, this would use the clipboard API
            if "platform" in globals() and platform.system() == 'Emscripten':
                import javascript
                javascript.navigator.clipboard.writeText(share_text)
                self.show_message("Copied to clipboard!", Colors.GREEN)
            else:
                # In desktop mode, this is not easily possible without additional libraries
                self.show_message("Clipboard copy only available in browser", Colors.ORANGE)
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            self.show_message("Error copying to clipboard", Colors.RED)
    
    def show_message(self, message, color=Colors.BLACK):
        """Show a temporary message."""
        self.message = message
        self.message_color = color
        self.message_timer = 120  # 2 seconds at 60 FPS
    
    def render(self, screen):
        """Render the share dialog."""
        # Draw dialog background
        pygame.draw.rect(screen, Colors.WHITE, self.rect)
        pygame.draw.rect(screen, Colors.GRAY, self.rect, 2)
        
        # Draw title
        title = self.font.render("Share Your Progress", True, Colors.BLUE)
        title_rect = title.get_rect(center=(self.rect.centerx, self.rect.top + 30))
        screen.blit(title, title_rect)
        
        # Draw share text preview
        share_text = self.get_share_text()
        text_surface = self.small_font.render(share_text, True, Colors.BLACK)
        
        # If text is too long, split into multiple lines
        if text_surface.get_width() > self.rect.width - 40:
            words = share_text.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = current_line + [word]
                test_surface = self.small_font.render(" ".join(test_line), True, Colors.BLACK)
                if test_surface.get_width() <= self.rect.width - 40:
                    current_line = test_line
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(" ".join(current_line))
            
            for i, line in enumerate(lines):
                text_surface = self.small_font.render(line, True, Colors.BLACK)
                y_offset = self.rect.top + 100 + i * 25
                screen.blit(text_surface, (self.rect.left + 20, y_offset))
        else:
            screen.blit(text_surface, (self.rect.left + 20, self.rect.top + 100))
        
        # Draw URL
        url_text = self.get_share_url()
        url_surface = self.small_font.render(url_text, True, Colors.BLUE)
        screen.blit(url_surface, (self.rect.left + 20, self.rect.top + 150))
        
        # Draw information text
        info_text = "Share your insurance company progress with friends!"
        info_surface = self.small_font.render(info_text, True, Colors.GRAY)
        screen.blit(info_surface, (self.rect.left + 20, self.rect.top + 200))
        
        # Draw note about browser functionality
        note_text = "Note: Social sharing features work best in browser"
        note_surface = self.small_font.render(note_text, True, Colors.ORANGE)
        screen.blit(note_surface, (self.rect.left + 20, self.rect.top + 230))
        
        # Draw buttons
        for button in self.buttons.values():
            button.draw(screen)
        
        # Draw message if active
        if self.message and self.message_timer > 0:
            message_surface = self.small_font.render(self.message, True, self.message_color)
            message_rect = message_surface.get_rect(center=(self.rect.centerx, self.rect.bottom - 100))
            screen.blit(message_surface, message_rect)
            self.message_timer -= 1 