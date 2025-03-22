# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.

# Insurance Game Analytics

This module provides data visualization capabilities for the Insurance Simulation Game using R.

## Overview

The analytics module exports game data to CSV files and generates visualizations using R. These visualizations help players understand their company's performance, market position, and financial health.

## Features

- Financial performance tracking
- Market share analysis
- Premium rate comparison with competitors
- Loss ratio and combined ratio trends
- Investment performance tracking

## How to Use

### In-Game Access

1. During gameplay, click the "Analytics" button in the top navigation bar
2. Alternatively, press `Ctrl+A` to generate analytics at any time

### Output

Visualizations are saved in the `analytics/plots` directory and include:

- `financial_performance.png` - Revenue, claims, and profit over time
- `underwriting_ratios.png` - Loss ratio and combined ratio over time
- `market_share.png` - Market share by line of business
- `premium_comparison.png` - Premium rate comparison with competitors
- `investment_performance.png` - Investment value and income over time
- `report.txt` - A text summary of key metrics

## Requirements

- R 4.0+ with the following packages installed:
  - ggplot2
  - dplyr
  - reshape2

## Data Files

The module generates the following data files:

- `analytics/game_data.csv` - Historical financial data
- `analytics/market_data.csv` - Market share and competitor data

## For Developers

The analytics module consists of three main components:

1. **Data Export Functions** - Export game data to CSV files
2. **R Script Generation** - Create an R script for visualization
3. **Visualization Function** - Execute the R script and display results

To extend the analytics module, modify the `visualize.R` script template in `generate_r_visualization()` function. 