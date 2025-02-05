# Insurance Simulation Game

A business simulation game where you manage an insurance company, make strategic decisions about premium pricing, invest in various assets, and expand into new markets.

## Features

### Insurance Operations
- Set premium rates for different insurance lines (Home and Auto)
- Manage policies across multiple states (currently CA and FL)
- Handle regular claims and catastrophic events
- Track loss ratios and operating metrics

### Investment Management
- Trade various investment assets:
  - S&P 500 ETF (stocks)
  - Corporate Bond ETF
  - Long-Term Treasury ETF
  - Short-Term Treasury ETF
  - Real Estate Investment Trust (REIT)
- Earn quarterly dividends and interest
- Track unrealized gains/losses
- Monitor portfolio performance

### Market Dynamics
- State-specific market conditions
- Seasonal effects on demand
- Economic cycles
- Catastrophic events (earthquakes in CA, hurricanes in FL)
- Price sensitivity modeling

### Financial Reporting
- Quarterly financial statements
- Investment portfolio tracking
- Key performance metrics
- Turn-by-turn summaries

## Setup

1. Make sure you have Python 3.8+ installed
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Game

To start the game, run:
```bash
python main.py
```

## Gameplay Guide

1. **Starting the Game**
   - Choose your company name
   - Select your starting state (CA or FL)
   - Start with $1M in initial capital

2. **Insurance Operations**
   - Set premium rates relative to market rates
   - Monitor policy sales and claims
   - Track loss ratios
   - Expand to new states when ready

3. **Investment Management**
   - Buy and sell various assets
   - Monitor dividend/interest income
   - Track portfolio value
   - Balance risk and return

4. **Turn Structure**
   - Each turn represents one quarter
   - Review financial results
   - Adjust strategy based on performance
   - Monitor market conditions

## Development Status

Current features implemented:
- Basic insurance operations
- Investment system with multiple assets
- Two-state market system
- Financial reporting
- Market dynamics simulation

Under development:
- AI competitors
- Additional states
- Reinsurance system
- Save/Load functionality
- Macroeconomic factors 