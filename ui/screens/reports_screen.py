import pygame
from ..components import Colors, Button

class ReportsScreen:
    def __init__(self, screen_rect, font, small_font):
        self.rect = screen_rect
        self.font = font
        self.small_font = small_font
        
        # Create sub-sections
        section_height = screen_rect.height // 3
        self.income_rect = pygame.Rect(
            screen_rect.left + 20,
            screen_rect.top + 20,
            screen_rect.width // 2 - 30,
            section_height - 20
        )
        
        self.balance_rect = pygame.Rect(
            screen_rect.centerx + 10,
            screen_rect.top + 20,
            screen_rect.width // 2 - 30,
            section_height - 20
        )
        
        self.metrics_rect = pygame.Rect(
            screen_rect.left + 20,
            screen_rect.top + section_height + 10,
            screen_rect.width // 2 - 30,
            section_height - 20
        )
        
        self.competitors_rect = pygame.Rect(
            screen_rect.centerx + 10,
            screen_rect.top + section_height + 10,
            screen_rect.width // 2 - 30,
            section_height * 2 - 30
        )
    
    def render(self, screen, game_state):
        """Render the reports screen."""
        # Draw background
        pygame.draw.rect(screen, Colors.WHITE, self.rect)
        
        # Draw sections
        self._draw_income_statement(screen, self.income_rect, game_state)
        self._draw_balance_sheet(screen, self.balance_rect, game_state)
        self._draw_key_metrics(screen, self.metrics_rect, game_state)
        self._draw_competitors(screen, self.competitors_rect, game_state)
    
    def _draw_income_statement(self, screen, rect, game_state):
        """Draw income statement section."""
        self._draw_section_header(screen, "Income Statement", rect.top)
        y = rect.top + 40
        
        if game_state.financial_history:
            report = game_state.financial_history[-1]
            items = [
                ("Premium Revenue", f"${report.revenue:,.2f}"),
                ("Claims Paid", f"${report.claims_paid:,.2f}"),
                ("Investment Income", f"${report.investment_returns:,.2f}"),
                ("Operating Expenses", f"${report.operating_expenses:,.2f}"),
                ("Net Income", f"${report.net_income:,.2f}")
            ]
            
            for label, value in items:
                text = self.small_font.render(f"{label}:", True, Colors.BLACK)
                screen.blit(text, (rect.left + 10, y))
                
                value_text = self.small_font.render(value, True, Colors.BLUE)
                screen.blit(value_text, (rect.right - value_text.get_width() - 10, y))
                
                y += 30
    
    def _draw_balance_sheet(self, screen, rect, game_state):
        """Draw balance sheet section."""
        self._draw_section_header(screen, "Balance Sheet", rect.top)
        y = rect.top + 40
        
        # Calculate total assets
        cash = game_state.player_company.cash
        investments = sum(
            shares * game_state.investment_assets[asset_id].current_price
            for asset_id, shares in game_state.player_company.investments.items()
        )
        total_assets = cash + investments
        
        items = [
            ("Cash", f"${cash:,.2f}"),
            ("Investments", f"${investments:,.2f}"),
            ("Total Assets", f"${total_assets:,.2f}")
        ]
        
        for label, value in items:
            text = self.small_font.render(f"{label}:", True, Colors.BLACK)
            screen.blit(text, (rect.left + 10, y))
            
            value_text = self.small_font.render(value, True, Colors.BLUE)
            screen.blit(value_text, (rect.right - value_text.get_width() - 10, y))
            
            y += 30
    
    def _draw_key_metrics(self, screen, rect, game_state):
        """Draw key metrics section."""
        self._draw_section_header(screen, "Key Metrics", rect.top)
        y = rect.top + 40
        
        if game_state.financial_history:
            report = game_state.financial_history[-1]
            loss_ratio = report.claims_paid / report.revenue * 100 if report.revenue > 0 else 0
            
            items = [
                ("Loss Ratio", f"{loss_ratio:.1f}%"),
                ("Total Policies", f"{sum(game_state.player_company.policies_sold.values()):,}"),
                ("States Active", f"{sum(1 for v in game_state.unlocked_states.values() if v)}")
            ]
            
            for label, value in items:
                text = self.small_font.render(f"{label}:", True, Colors.BLACK)
                screen.blit(text, (rect.left + 10, y))
                
                value_text = self.small_font.render(value, True, Colors.BLUE)
                screen.blit(value_text, (rect.right - value_text.get_width() - 10, y))
                
                y += 30
    
    def _draw_competitors(self, screen, rect, game_state):
        """Draw competitor information."""
        self._draw_section_header(screen, "Market Competition", rect.top)
        y_offset = rect.top + 40
        
        # Draw column headers
        headers = ["Company", "Market Share", "Avg Premium", "Cash"]
        col_width = rect.width // len(headers)
        for i, header in enumerate(headers):
            text = self.small_font.render(header, True, Colors.BLUE)
            screen.blit(text, (rect.left + i * col_width + 10, y_offset))
        y_offset += 30
        
        # Draw separator line
        pygame.draw.line(screen, Colors.BLACK, 
                        (rect.left, y_offset), 
                        (rect.right, y_offset))
        y_offset += 10
        
        # Calculate total market size and prepare company data
        total_market_size = sum(segment.market_size for segment in game_state.market_segments.values())
        companies = [game_state.player_company] + game_state.ai_competitors
        
        for company in companies:
            # Calculate market share
            company_policies = sum(company.policies_sold.values())
            market_share = company_policies / total_market_size if total_market_size > 0 else 0
            
            # Calculate average premium rate
            premium_rates = [rate for rate in company.premium_rates.values()]
            avg_premium = sum(premium_rates) / len(premium_rates) if premium_rates else 0
            
            # Draw company row
            color = Colors.BLUE if company == game_state.player_company else Colors.BLACK
            
            # Company name
            text = self.small_font.render(company.name, True, color)
            screen.blit(text, (rect.left + 10, y_offset))
            
            # Market share
            text = self.small_font.render(f"{market_share:.1%}", True, color)
            screen.blit(text, (rect.left + col_width + 10, y_offset))
            
            # Average premium
            text = self.small_font.render(f"${avg_premium:,.2f}", True, color)
            screen.blit(text, (rect.left + col_width * 2 + 10, y_offset))
            
            # Cash
            text = self.small_font.render(f"${company.cash:,.2f}", True, color)
            screen.blit(text, (rect.left + col_width * 3 + 10, y_offset))
            
            y_offset += 30
        
        # Draw market share chart
        chart_rect = pygame.Rect(
            rect.left + 20,
            y_offset + 20,
            rect.width - 40,
            100
        )
        self._draw_market_share_chart(screen, chart_rect, companies, total_market_size)
    
    def _draw_market_share_chart(self, screen, rect, companies, total_market_size):
        """Draw a horizontal bar chart showing market share distribution."""
        colors = [Colors.BLUE, Colors.GREEN, Colors.ORANGE, Colors.RED]
        
        # Draw chart background
        pygame.draw.rect(screen, Colors.WHITE, rect, 0)
        pygame.draw.rect(screen, Colors.BLACK, rect, 1)
        
        # Calculate market shares
        x = rect.left
        for i, company in enumerate(companies):
            company_policies = sum(company.policies_sold.values())
            share = company_policies / total_market_size if total_market_size > 0 else 0
            width = int(share * rect.width)
            
            # Draw market share bar
            if width > 0:
                bar_rect = pygame.Rect(x, rect.top, width, rect.height)
                pygame.draw.rect(screen, colors[i % len(colors)], bar_rect)
                
                # Draw company name if bar is wide enough
                if width > 60:
                    text = self.small_font.render(f"{share:.1%}", True, Colors.WHITE)
                    text_x = x + (width - text.get_width()) // 2
                    text_y = rect.centery - text.get_height() // 2
                    screen.blit(text, (text_x, text_y))
                
                x += width
    
    def _draw_section_header(self, screen, text, y_offset):
        """Draw a section header."""
        header = self.font.render(text, True, Colors.BLUE)
        screen.blit(header, (self.rect.left + 20, y_offset))
    
    def handle_event(self, event, game_state):
        """Handle any events for the reports screen."""
        return None  # No special event handling needed for reports screen 