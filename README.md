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

### Data Analytics & Visualization (New!)
- Generate beautiful data visualizations using R
- Track financial performance trends
- Analyze market share by line of business
- Compare premium rates with competitors
- Monitor loss ratio and combined ratio trends
- Visualize investment performance

### Browser & Mobile Support
- Play in any modern web browser
- Progressive Web App (PWA) support
- Install on home screens of mobile devices
- Touch screen controls
- Offline play capability
- Responsive design for all screen sizes

## Setup

1. Make sure you have Python 3.8+ installed
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```
3. For data visualization features, install R 4.0+ with these packages:
```R
install.packages(c("ggplot2", "dplyr", "reshape2"))
```

## Running the Game

### Desktop Version
To start the game on desktop, run:
```bash
python main.py
```

### Browser Version
You can now play the game in any modern web browser:

#### Running the development server:
```bash
# PowerShell
.\run_server.ps1

# Or run in background and automatically open browser:
.\run_server_background.ps1

# Or using Python directly
python -m pygbag --ume_block 0 --port 8000 .
```

Then open your browser to: http://localhost:8000

#### Building for web deployment:
```bash
# PowerShell
.\build_web.ps1

# Or using Python directly
python -m pygbag --ume_block 0 --build .
```

The deployable web version will be in the `build/web` directory. See `deployment_guide.html` for detailed hosting instructions.

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

4. **Using Analytics**
   - Click the "Analytics" button in the top menu
   - Alternatively, press Ctrl+A to generate reports
   - Review visualizations in the analytics/plots folder
   - Use insights to refine your strategy

5. **Turn Structure**
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
- Browser-based gameplay with Pygbag
- Game state saving/loading (desktop and browser localStorage)
- Progressive Web App (PWA) support
- Touch screen controls for mobile
- Offline play capability
- Data visualization and analytics with R

Under development:
- AI competitors
- Additional states
- Reinsurance system
- Macroeconomic factors

## Testing

For browser version testing, see `manual_test.md` which provides a systematic approach for verifying functionality.

For debugging help, run:
```bash
python browser_debug.py
```
This will create a debug version with extra logging to browser console.

## Analytics

The game includes powerful data visualization capabilities using R:

- Financial performance tracking
- Market share analysis
- Premium rate comparison with competitors
- Loss ratio and combined ratio trends
- Investment performance tracking

For more details, see `analytics/README.md`.

## Deployment

The browser version can be deployed to:
- GitHub Pages
- Netlify
- Any standard web hosting

See `deployment_guide.html` for detailed instructions. 