import pygame
from ..components import Colors, Button

class PortfolioTable:
    def __init__(self, rect, font, small_font):
        self.rect = rect
        self.font = font
        self.small_font = small_font
        self.buttons = {}
        
        # Configuration
        self.row_height = 50
        self.col_widths = {
            "Asset": 0.25,
            "Shares": 0.15,
            "Value": 0.2,
            "Return": 0.15,
            "Actions": 0.25
        }

    def draw(self, screen, game_state):
        # Draw table headers
        self._draw_headers(screen)
        
        # Draw portfolio items
        y = self.rect.top + 60
        for asset_id, asset in game_state.investment_assets.items():
            self._draw_portfolio_row(screen, asset, game_state, y)
            y += self.row_height

    def _draw_headers(self, screen):
        headers = ["Asset", "Shares", "Value", "Return", "Actions"]
        x = self.rect.left + 20
        y = self.rect.top + 20
        
        for header in headers:
            text = self.small_font.render(header, True, Colors.BLUE)
            screen.blit(text, (x, y))
            x += self.rect.width * self.col_widths[header]

    def _draw_portfolio_row(self, screen, asset, game_state, y):
        # Implementation similar to previous row drawing code
        # ... (omitted for brevity)

    def handle_events(self, event, game_state):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Handle button clicks similar to previous implementation
            # ... (omitted for brevity)
        return False 