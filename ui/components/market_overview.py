import pygame
from ..components import Colors

class MarketOverview:
    def __init__(self, rect, font, small_font):
        self.rect = rect
        self.font = font
        self.small_font = small_font
        self.col_widths = {
            "Asset": 0.5,
            "Price": 0.3,
            "Yield": 0.2
        }

    def draw(self, screen, game_state):
        self._draw_headers(screen)
        y = self.rect.top + 50
        
        for asset_id, asset in game_state.investment_assets.items():
            self._draw_market_row(screen, asset, y)
            y += 35

    def _draw_headers(self, screen):
        headers = ["Asset", "Price", "Yield"]
        x = self.rect.left + 20
        y = self.rect.top + 20
        
        for header in headers:
            text = self.small_font.render(header, True, Colors.BLUE)
            screen.blit(text, (x, y))
            x += self.rect.width * self.col_widths[header]

    def _draw_market_row(self, screen, asset, y):
        # Implementation similar to previous market row drawing
        # ... (omitted for brevity) 