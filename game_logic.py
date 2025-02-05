from typing import List, Dict
from models import Company, MarketSegment, FinancialReport
import numpy as np

class Asset:
    """Represents a specific investment asset with price and income characteristics."""
    def __init__(self, name, current_price, dividend_yield, volatility):
        self.name = name
        self.current_price = current_price
        self.dividend_yield = dividend_yield  # Annual yield
        self.volatility = volatility  # Standard deviation for price changes
        self.price_history = [current_price]

    def update_price(self):
        """Update the asset price with random walk and volatility."""
        # Random walk with drift
        drift = 0.05  # 5% annual expected return
        daily_drift = drift / 252  # Convert to daily
        daily_vol = self.volatility / np.sqrt(252)  # Convert to daily
        
        # Generate random return
        random_return = np.random.normal(daily_drift, daily_vol)
        self.current_price *= (1 + random_return)
        self.price_history.append(self.current_price)
    
    def get_quarterly_income(self, shares):
        """Calculate quarterly dividend/interest income."""
        return (self.dividend_yield * self.current_price * shares) / 4

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
            premium_rates={}
        )
        
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
        
        # Define states and their characteristics
        self.states = {
            "CA": {
                "name": "California",
                "catastrophe_risk": 0.01,  # 1% chance of earthquake per year
                "cat_severity": np.log(500000),  # Average catastrophe claim $500k
                "market_size_multiplier": 1.5,  # Larger market
                "entry_cost": 500000  # $500k to enter
            },
            "FL": {
                "name": "Florida",
                "catastrophe_risk": 0.05,  # 5% chance of hurricane per year
                "cat_severity": np.log(250000),  # Average catastrophe claim $250k
                "market_size_multiplier": 1.0,  # Base market size
                "entry_cost": 300000  # $300k to enter
            }
        }
        
        # Track which states are unlocked
        self.unlocked_states = {state_id: False for state_id in self.states}
        self.unlocked_states[initial_state] = True  # First state is free
        
        # Define insurance lines with their characteristics for each state
        self.market_segments = {}
        for state_id, state_info in self.states.items():
            # Home insurance in this state
            self.market_segments[f"{state_id}_home"] = MarketSegment(
                name=f"Home Insurance - {state_info['name']}",
                base_risk=0.05,  # 5% chance of regular claim per year
                price_sensitivity=1.2,
                market_size=int(2000 * state_info["market_size_multiplier"]),
                current_demand=int(1500 * state_info["market_size_multiplier"])
            )
            # Auto insurance in this state
            self.market_segments[f"{state_id}_auto"] = MarketSegment(
                name=f"Auto Insurance - {state_info['name']}",
                base_risk=0.15,  # 15% chance of claim per year
                price_sensitivity=1.5,
                market_size=int(5000 * state_info["market_size_multiplier"]),
                current_demand=int(4000 * state_info["market_size_multiplier"])
            )
        
        # Initialize base market rates for each line in each state
        self.base_market_rates = {}
        for state_id, state_info in self.states.items():
            # Add catastrophe risk loading to home insurance
            cat_loading = state_info["catastrophe_risk"] * np.exp(state_info["cat_severity"])
            
            self.base_market_rates[f"{state_id}_home"] = 1200 + cat_loading
            self.base_market_rates[f"{state_id}_auto"] = 900
        
        # Define claim severity distributions for each line
        self.claim_distributions = {}
        for state_id, state_info in self.states.items():
            # Regular claims for home insurance
            self.claim_distributions[f"{state_id}_home"] = {
                "mean": np.log(24000),  # Average home claim $24,000
                "sigma": 0.7,           # Higher variation in home claims
                "cat_mean": state_info["cat_severity"],  # Catastrophe severity
                "cat_risk": state_info["catastrophe_risk"]  # Catastrophe frequency
            }
            # Auto insurance claims
            self.claim_distributions[f"{state_id}_auto"] = {
                "mean": np.log(6000),   # Average auto claim $6,000
                "sigma": 0.5            # Lower variation in auto claims
            }
        
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
        self._update_policies()
        self._generate_claims()
        self._update_market_demand()
        self._calculate_investment_returns()
        self._generate_financial_report()
        self.current_turn += 1
    
    def _update_policies(self):
        """Update the number of policies based on premium rates and market conditions."""
        new_policies = {}
        
        for line_id, segment in self.market_segments.items():
            state_id = line_id.split("_")[0]
            # Only update policies for unlocked states
            if self.unlocked_states[state_id]:
                # Get player's premium rate for this line
                premium_rate = self.player_company.premium_rates.get(line_id, self.base_market_rates[line_id])
                
                # Calculate relative price compared to market average
                relative_price = premium_rate / self.base_market_rates[line_id]
                
                # Calculate potential policies based on price sensitivity
                potential_policies = segment.calculate_demand(premium_rate, [self.base_market_rates[line_id]])
                
                # Add random variation (±10%)
                variation = np.random.uniform(0.9, 1.1)
                new_policies[line_id] = int(potential_policies * variation)
            else:
                new_policies[line_id] = 0
        
        self.player_company.policies_sold = new_policies
    
    def _generate_claims(self):
        """Generate insurance claims based on line characteristics and catastrophes."""
        # First, collect premium revenue for the quarter
        premium_revenue = sum(
            self.player_company.premium_rates.get(line_id, self.base_market_rates[line_id]) * policies
            for line_id, policies in self.player_company.policies_sold.items()
        ) / 4  # Quarterly revenue
        
        # Add premium revenue to cash
        self.player_company.cash += premium_revenue
        
        claims = []
        
        # Generate regular claims
        for line_id, policies in self.player_company.policies_sold.items():
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
                state_id = line_id.split("_")[0]
                cat_risk = self.states[state_id]["catastrophe_risk"] / 4  # Quarterly risk
                
                if np.random.random() < cat_risk:  # Catastrophe occurs
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
        
        self.player_company.process_claims(claims)
    
    def _update_market_demand(self):
        """Update market demand based on various factors."""
        for state_id, state_info in self.states.items():
            for line in ["home", "auto"]:
                segment = self.market_segments[f"{state_id}_{line}"]
                
                # Economic cycle effect (simple sine wave)
                economic_cycle = np.sin(self.current_turn / 8) * 0.1
                
                # State-specific seasonal effects
                if state_id == "FL":
                    # Florida has stronger seasonal effects (snowbirds)
                    seasonal_effect = np.sin(self.current_turn / 4) * 0.15
                else:
                    seasonal_effect = np.sin(self.current_turn / 4) * 0.05
                
                # Random market fluctuation
                market_fluctuation = np.random.normal(0, 0.05)
                
                # Combined effect
                total_effect = 1 + economic_cycle + seasonal_effect + market_fluctuation
                
                # Update demand with limits
                new_demand = int(segment.current_demand * total_effect)
                segment.current_demand = max(0, min(segment.market_size, new_demand))
    
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
        # Calculate revenue from premiums
        premium_revenue = sum(
            self.player_company.premium_rates.get(line_id, self.base_market_rates[line_id]) * policies
            for line_id, policies in self.player_company.policies_sold.items()
        ) / 4  # Quarterly revenue
        
        # Calculate investment returns
        investment_income, unrealized_gains = self._calculate_investment_returns()
        
        # Calculate claims from this turn
        current_claims = sum(
            claim["amount"]
            for claim in self.player_company.claims_history
            if claim.get("turn") == self.current_turn
        )
        
        # Generate report
        report = FinancialReport(
            period=self.current_turn,
            revenue=premium_revenue,
            claims_paid=current_claims,
            investment_returns=investment_income,  # Only realized income
            unrealized_gains=unrealized_gains,    # Track separately
            operating_expenses=50000  # Fixed quarterly operating expenses
        )
        
        self.financial_history.append(report)
        return report
    
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
        return True 