import pygame
from ..components import Colors, Button

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
        
        # Create continue button
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