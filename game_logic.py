from typing import List, Dict
import numpy as np
from models import Company, MarketSegment, FinancialReport, AICompetitor
from asset import Asset
from market_dynamics import MarketDynamics

class GameState:
    """Manages the overall game state and progression."""
    
    def __init__(self, initial_state="CA", company_name="Player Insurance Co."):
        self.current_turn = 0
        self.player_company = Company(
            name=company_name,
            cash=1000000.0,  # Starting with $1M
            investments={},  # Will store {asset_name: shares}
            policies_sold={},
            claims_history=[],
            premium_rates={},
            advertising_budget={}  # New: advertising budget per line
        )
        
        # Initialize AI competitors
        self.ai_competitors = [
            AICompetitor("Aggressive Insurance Co.", cash=1000000.0, risk_profile="aggressive"),
            AICompetitor("Balanced Insurance Co.", cash=1000000.0, risk_profile="balanced"),
            AICompetitor("Conservative Insurance Co.", cash=1000000.0, risk_profile="conservative")
        ]
        
        # Initialize market dynamics
        self.market = MarketDynamics()
        
        # Track which states are unlocked
        self.unlocked_states = {state_id: False for state_id in self.market.states}
        self.unlocked_states[initial_state] = True  # First state is free
        
        # Initialize advertising budgets for AI competitors
        for competitor in self.ai_competitors:
            competitor.advertising_budget = {}
            for state_id in self.market.states:
                for line in ["home", "auto"]:
                    line_id = f"{state_id}_{line}"
                    if competitor.risk_profile == "aggressive":
                        competitor.advertising_budget[line_id] = 50000  # Spends more on advertising
                    elif competitor.risk_profile == "conservative":
                        competitor.advertising_budget[line_id] = 20000  # Spends less on advertising
                    else:
                        competitor.advertising_budget[line_id] = 35000  # Balanced spending
        
        # Initialize investment assets
        self.investment_assets = {
            "SP500": Asset(
                name="S&P 500 ETF",
                current_price=450.0,
                dividend_yield=0.015,  # 1.5% dividend yield
                volatility=0.15  # 15% annual volatility
            ),
            "CORP_BONDS": Asset(
                name="Corporate Bond ETF",
                current_price=100.0,
                dividend_yield=0.045,  # 4.5% yield
                volatility=0.08  # 8% annual volatility
            ),
            "LONG_TREASURY": Asset(
                name="Long-Term Treasury ETF",
                current_price=90.0,
                dividend_yield=0.035,  # 3.5% yield
                volatility=0.12  # 12% annual volatility
            ),
            "SHORT_TREASURY": Asset(
                name="Short-Term Treasury ETF",
                current_price=50.0,
                dividend_yield=0.02,  # 2% yield
                volatility=0.03  # 3% annual volatility
            ),
            "REIT": Asset(
                name="Real Estate Investment Trust ETF",
                current_price=80.0,
                dividend_yield=0.06,  # 6% dividend yield
                volatility=0.20  # 20% annual volatility
            )
        }
        
        # Get states from market dynamics
        self.states = self.market.states
        
        # Get market segments from market dynamics
        self.market_segments = self.market.market_segments
        
        # Get base market rates from market dynamics
        self.base_market_rates = self.market.base_market_rates
        
        # Get claim distributions from market dynamics
        self.claim_distributions = {}
        for state_id, state_info in self.states.items():
            for line in ["home", "auto"]:
                line_id = f"{state_id}_{line}"
                self.claim_distributions[line_id] = self.market.get_claim_distribution(line_id)
        
        self.financial_history: List[FinancialReport] = []
    
    def unlock_state(self, state_id: str) -> bool:
        """Attempt to unlock a new state. Returns True if successful."""
        if state_id not in self.states or self.unlocked_states[state_id]:
            return False
        
        entry_cost = self.states[state_id]["entry_cost"]
        if self.player_company.cash >= entry_cost:
            self.player_company.cash -= entry_cost
            self.unlocked_states[state_id] = True
            return True
        
        return False
    
    def update(self):
        """Update game state for the current turn."""
        # Update AI competitors first
        for competitor in self.ai_competitors:
            competitor.make_decisions(self)
        
        # Collect all advertising budgets
        advertising_budgets = {
            self.player_company.name: self.player_company.advertising_budget
        }
        for competitor in self.ai_competitors:
            advertising_budgets[competitor.name] = competitor.advertising_budget
        
        # Update market with new consumer model
        self.market.update_market(self.player_company, self.ai_competitors, advertising_budgets)
        
        self._generate_claims()
        self._calculate_investment_returns()
        self._generate_financial_report()
        
        # Deduct advertising costs
        self._process_advertising_costs()
        
        self.current_turn += 1
    
    def _process_advertising_costs(self):
        """Process advertising costs for all companies."""
        # Player company
        for line_id, budget in self.player_company.advertising_budget.items():
            self.player_company.cash -= budget
        
        # AI competitors
        for competitor in self.ai_competitors:
            for line_id, budget in competitor.advertising_budget.items():
                competitor.cash -= budget
    
    def set_advertising_budget(self, line_id: str, amount: float) -> bool:
        """Set advertising budget for a specific line. Returns True if successful."""
        if amount < 0:
            return False
        
        state_id = line_id.split("_")[0]
        if not self.unlocked_states[state_id]:
            return False
        
        if amount > self.player_company.cash:
            return False
        
        self.player_company.advertising_budget[line_id] = amount
        return True
    
    def get_market_share(self, line_id: str) -> float:
        """Calculate market share for a specific line."""
        total_policies = sum(
            comp.policies_sold.get(line_id, 0) 
            for comp in [self.player_company] + self.ai_competitors
        )
        
        if total_policies == 0:
            return 0.0
        
        return self.player_company.policies_sold.get(line_id, 0) / total_policies
    
    def get_competitor_info(self, line_id: str) -> List[Dict]:
        """Get competitor information for a specific line."""
        info = []
        for company in [self.player_company] + self.ai_competitors:
            info.append({
                "name": company.name,
                "premium": company.premium_rates.get(line_id, self.market.base_market_rates[line_id]),
                "policies": company.policies_sold.get(line_id, 0),
                "advertising": company.advertising_budget.get(line_id, 0)
            })
        return info
    
    def _generate_claims(self):
        """Generate insurance claims based on line characteristics and catastrophes."""
        # Process claims for player company
        self._process_company_claims(self.player_company)
        
        # Process claims for AI competitors
        for competitor in self.ai_competitors:
            self._process_company_claims(competitor)
    
    def _process_company_claims(self, company):
        """Process claims for a specific company."""
        # First, collect premium revenue for the quarter
        premium_revenue = sum(
            company.premium_rates.get(line_id, self.base_market_rates[line_id]) * policies
            for line_id, policies in company.policies_sold.items()
        ) / 4  # Quarterly revenue
        
        # Add premium revenue to cash
        company.cash += premium_revenue
        
        claims = []
        
        # Generate regular claims
        for line_id, policies in company.policies_sold.items():
            if policies <= 0:
                continue
                
            state_id = line_id.split("_")[0]
            segment = self.market_segments[line_id]
            base_risk = segment.base_risk
            
            # Calculate quarterly claim frequency (divide annual risk by 4)
            quarterly_risk = base_risk / 4
            claim_count = np.random.poisson(quarterly_risk * policies)
            
            # Generate regular claims
            dist = self.claim_distributions[line_id]
            for _ in range(claim_count):
                claim_amount = np.random.lognormal(
                    mean=dist["mean"],
                    sigma=dist["sigma"]
                )
                
                claims.append({
                    "line": line_id,
                    "amount": claim_amount,
                    "turn": self.current_turn,
                    "type": "regular"
                })
            
            # Generate catastrophe claims for home insurance
            if "_home" in line_id:  # Only home insurance has catastrophe risk
                if self.market.generate_catastrophe(state_id):
                    # Affect 10-30% of policies in the state
                    affected_ratio = np.random.uniform(0.1, 0.3)
                    affected_policies = int(policies * affected_ratio)
                    
                    for _ in range(affected_policies):
                        claim_amount = np.random.lognormal(
                            mean=dist["cat_mean"],
                            sigma=0.5  # Less variation in catastrophe claims
                        )
                        
                        claims.append({
                            "line": line_id,
                            "amount": claim_amount,
                            "turn": self.current_turn,
                            "type": "catastrophe"
                        })
        
        company.process_claims(claims)
    
    def _calculate_investment_returns(self):
        """Calculate returns from investments including dividends/interest and price changes."""
        total_income = 0
        unrealized_gains = 0
        
        # Update asset prices and calculate income
        for asset_name, asset in self.investment_assets.items():
            shares = self.player_company.investments.get(asset_name, 0)
            if shares > 0:
                # Calculate quarterly income (dividends/interest)
                income = asset.get_quarterly_income(shares)
                total_income += income
                
                # Update price and calculate unrealized gains
                old_price = asset.current_price
                asset.update_price()
                price_change = asset.current_price - old_price
                unrealized_gains += price_change * shares
        
        # Add income to cash (dividends/interest are realized)
        self.player_company.cash += total_income
        
        return total_income, unrealized_gains
    
    def _generate_financial_report(self):
        """Generate a financial report for the current turn."""
        # Generate report for player company
        self.financial_history.append(self._generate_company_report(self.player_company))
        
        # Generate reports for AI competitors
        for competitor in self.ai_competitors:
            competitor.financial_history.append(self._generate_company_report(competitor))
    
    def _generate_company_report(self, company):
        """Generate a financial report for a specific company."""
        # Calculate revenue from premiums
        premium_revenue = sum(
            company.premium_rates.get(line_id, self.base_market_rates[line_id]) * policies
            for line_id, policies in company.policies_sold.items()
        ) / 4  # Quarterly revenue
        
        # Calculate investment returns
        investment_income = 0
        unrealized_gains = 0
        
        # Update asset prices and calculate income
        for asset_name, asset in self.investment_assets.items():
            shares = company.investments.get(asset_name, 0)
            if shares > 0:
                # Calculate quarterly income (dividends/interest)
                income = asset.get_quarterly_income(shares)
                investment_income += income
                
                # Update price and calculate unrealized gains
                old_price = asset.current_price
                asset.update_price()
                price_change = asset.current_price - old_price
                unrealized_gains += price_change * shares
        
        # Add income to cash (dividends/interest are realized)
        company.cash += investment_income
        
        # Calculate claims from this turn
        current_claims = sum(
            claim["amount"]
            for claim in company.claims_history
            if claim.get("turn") == self.current_turn
        )
        
        # Generate report
        return FinancialReport(
            period=self.current_turn,
            revenue=premium_revenue,
            claims_paid=current_claims,
            investment_returns=investment_income,  # Only realized income
            unrealized_gains=unrealized_gains,    # Track separately
            operating_expenses=50000  # Fixed quarterly operating expenses
        )
    
    def buy_asset(self, asset_name: str, shares: int) -> bool:
        """Attempt to buy shares of an asset. Returns True if successful."""
        if asset_name not in self.investment_assets:
            return False
        
        asset = self.investment_assets[asset_name]
        cost = asset.current_price * shares
        
        if cost > self.player_company.cash:
            return False
        
        self.player_company.cash -= cost
        current_shares = self.player_company.investments.get(asset_name, 0)
        self.player_company.investments[asset_name] = current_shares + shares
        
        # Record the trade for market pressure
        asset.record_trade(shares)
        return True
    
    def sell_asset(self, asset_name: str, shares: int) -> bool:
        """Attempt to sell shares of an asset. Returns True if successful."""
        if asset_name not in self.investment_assets:
            return False
        
        current_shares = self.player_company.investments.get(asset_name, 0)
        if shares > current_shares:
            return False
        
        asset = self.investment_assets[asset_name]
        proceeds = asset.current_price * shares
        
        self.player_company.cash += proceeds
        self.player_company.investments[asset_name] = current_shares - shares
        
        # Record the trade for market pressure (negative for sells)
        asset.record_trade(-shares)
        return True

    def _update_policies(self):
        """Legacy method, no longer used. Marketing dynamics now handled by MarketDynamics class."""
        pass 