# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.

"""
Simple analytics module for tracking game usage.
In a browser environment, this can integrate with services like Google Analytics.
In a desktop environment, it's mostly a no-op.
"""

import platform
import time
import sys
import os
from typing import Dict, Any, List, Optional
import csv
import json

# Detect if we're running in a browser environment
IS_BROWSER = False
try:
    IS_BROWSER = platform.system() == 'Emscripten'
except:
    pass

# Track events locally if not in browser
local_events: List[Dict[str, Any]] = []

def track_pageview(screen_name: str) -> None:
    """Track a page view in the analytics system."""
    if IS_BROWSER:
        try:
            # In browser, use window.gtag if available (Google Analytics)
            import javascript
            if hasattr(javascript.window, 'gtag'):
                javascript.window.gtag('event', 'screen_view', {
                    'app_name': 'Insurance Simulation Game',
                    'screen_name': screen_name
                })
                javascript.console.log(f"Analytics: Tracked view of '{screen_name}'")
        except Exception as e:
            print(f"Analytics error: {e}")
    else:
        # In desktop, just store locally
        local_events.append({
            'type': 'pageview',
            'screen': screen_name,
            'timestamp': time.time()
        })

def track_event(category: str, action: str, label: Optional[str] = None, value: Optional[int] = None) -> None:
    """Track a custom event in the analytics system."""
    event_data = {
        'event_category': category,
        'event_action': action
    }
    
    if label:
        event_data['event_label'] = label
    if value is not None:
        event_data['value'] = value
    
    if IS_BROWSER:
        try:
            # In browser, use window.gtag if available (Google Analytics)
            import javascript
            if hasattr(javascript.window, 'gtag'):
                javascript.window.gtag('event', action, event_data)
                javascript.console.log(f"Analytics: Tracked event '{category}/{action}'")
        except Exception as e:
            print(f"Analytics error: {e}")
    else:
        # In desktop, just store locally
        local_events.append({
            'type': 'event',
            'category': category,
            'action': action,
            'label': label,
            'value': value,
            'timestamp': time.time()
        })

def inject_analytics_code() -> None:
    """
    Inject Google Analytics code into the HTML page.
    This would be done when building for web.
    """
    if IS_BROWSER:
        try:
            import javascript
            
            # Add Google Analytics tracking code (using a dummy ID here)
            analytics_code = """
            <!-- Replace UA-XXXXX-Y with your actual Google Analytics ID -->
            <script async src="https://www.googletagmanager.com/gtag/js?id=UA-XXXXX-Y"></script>
            <script>
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', 'UA-XXXXX-Y');
            </script>
            """
            
            # This would actually need to be done when building the HTML page
            # Not at runtime - this is just a placeholder
            javascript.console.log("Google Analytics code would be injected here in a real deployment")
        except Exception as e:
            print(f"Couldn't inject analytics code: {e}")

def save_local_events() -> None:
    """Save locally tracked events to a file (for desktop mode)."""
    if not IS_BROWSER and local_events:
        try:
            os.makedirs('analytics', exist_ok=True)
            filename = f"analytics/events_{int(time.time())}.txt"
            
            with open(filename, 'w') as f:
                for event in local_events:
                    f.write(f"{event}\n")
            
            print(f"Saved {len(local_events)} analytics events to {filename}")
            local_events.clear()
        except Exception as e:
            print(f"Error saving analytics data: {e}")

# Automatically save analytics data when the game exits (in desktop mode)
if not IS_BROWSER:
    import atexit
    atexit.register(save_local_events)

def format_number(value):
    """Format numeric values consistently for CSV output."""
    if isinstance(value, float):
        return round(value, 2)
    return value

def export_financial_data(game_state, filename="game_data.csv"):
    """
    Export financial history data to CSV for analysis in R.
    
    Args:
        game_state: The current game state containing financial history
        filename: Name of the CSV file to create
    """
    # Ensure the analytics directory exists
    os.makedirs('analytics', exist_ok=True)
    
    # Full path for the CSV file
    filepath = os.path.join('analytics', filename)
    
    # Collect data from financial history
    data = []
    
    # Add header row with turn number
    for turn, report in enumerate(game_state.financial_history):
        row = {
            'turn': turn,
            'cash': format_number(report.cash),
            'revenue': format_number(report.premium_revenue),
            'claims': format_number(report.claims_paid),
            'loss_ratio': format_number(report.loss_ratio),
            'combined_ratio': format_number(report.combined_ratio),
            'profit': format_number(report.net_income),
            'investment_value': format_number(report.investment_value),
            'investment_income': format_number(report.investment_income),
            'total_assets': format_number(report.total_assets)
        }
        
        # Add policy counts for each line
        for line_id, count in report.policies_by_line.items():
            row[f'policies_{line_id}'] = count
            
        data.append(row)
    
    # Write to CSV
    if data:
        keys = data[0].keys()
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"Financial data exported to {filepath}")
        return filepath
    else:
        print("No financial data to export")
        return None

def export_market_data(game_state, filename="market_data.csv"):
    """
    Export market share and competitor data to CSV for analysis.
    
    Args:
        game_state: The current game state containing market information
        filename: Name of the CSV file to create
    """
    # Ensure the analytics directory exists
    os.makedirs('analytics', exist_ok=True)
    
    # Full path for the CSV file
    filepath = os.path.join('analytics', filename)
    
    # Collect data on market shares and pricing
    data = []
    
    # Get list of all available lines
    lines = []
    for state_id, is_unlocked in game_state.unlocked_states.items():
        if is_unlocked:
            lines.append(f"{state_id}_home")
            lines.append(f"{state_id}_auto")
    
    # For each line, collect market share and pricing data
    for line_id in lines:
        # Get competitor info for this line
        competitor_info = game_state.get_competitor_info(line_id)
        
        # Player data
        player_rate = game_state.player_company.premium_rates.get(line_id, 0)
        player_policies = game_state.player_company.policies_sold.get(line_id, 0)
        player_budget = game_state.player_company.advertising_budget.get(line_id, 0)
        
        # Calculate total policies in market
        total_policies = player_policies
        for comp in competitor_info:
            total_policies += comp["policies"]
        
        # Player market share
        player_share = player_policies / total_policies if total_policies > 0 else 0
        
        # Add player data
        row = {
            'line_id': line_id,
            'company': game_state.player_company.name,
            'premium_rate': format_number(player_rate),
            'policies': player_policies,
            'market_share': format_number(player_share),
            'advertising': format_number(player_budget),
            'turn': game_state.current_turn
        }
        data.append(row)
        
        # Add competitor data
        for comp in competitor_info:
            comp_share = comp["policies"] / total_policies if total_policies > 0 else 0
            comp_row = {
                'line_id': line_id,
                'company': comp["name"],
                'premium_rate': format_number(comp["rate"]),
                'policies': comp["policies"],
                'market_share': format_number(comp_share),
                'advertising': format_number(comp.get("advertising", 0)),
                'turn': game_state.current_turn
            }
            data.append(comp_row)
    
    # Write to CSV
    if data:
        keys = data[0].keys()
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"Market data exported to {filepath}")
        return filepath
    else:
        print("No market data to export")
        return None

def generate_r_visualization(game_state):
    """
    Generate visualizations using R.
    Exports the necessary data and runs an R script to create graphs.
    
    Returns:
        Path to the generated visualization file or None if failed
    """
    # First export the necessary data
    financial_csv = export_financial_data(game_state)
    market_csv = export_market_data(game_state)
    
    if not financial_csv or not market_csv:
        return None
    
    # Create R script file
    r_script_path = os.path.join('analytics', 'visualize.R')
    
    with open(r_script_path, 'w') as f:
        f.write("""# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.
# Script to visualize insurance game data

# Load libraries
library(ggplot2)
library(dplyr)
library(reshape2)

# Read data
financial_data <- read.csv("analytics/game_data.csv")
market_data <- read.csv("analytics/market_data.csv")

# Output directory
output_dir <- "analytics/plots"
dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

# Function to save plots
save_plot <- function(plot, filename) {
  ggsave(file.path(output_dir, filename), plot, width = 8, height = 6)
}

# 1. Financial Performance Over Time
financial_plot <- ggplot(financial_data, aes(x = turn)) +
  geom_line(aes(y = revenue, color = "Revenue"), size = 1) +
  geom_line(aes(y = claims, color = "Claims"), size = 1) +
  geom_line(aes(y = profit, color = "Profit"), size = 1) +
  scale_color_manual(values = c("Revenue" = "blue", "Claims" = "red", "Profit" = "green")) +
  labs(title = "Financial Performance Over Time",
       x = "Turn",
       y = "Amount ($)",
       color = "Metric") +
  theme_minimal()
save_plot(financial_plot, "financial_performance.png")

# 2. Loss Ratio Over Time
ratio_plot <- ggplot(financial_data, aes(x = turn)) +
  geom_line(aes(y = loss_ratio, color = "Loss Ratio"), size = 1) +
  geom_line(aes(y = combined_ratio, color = "Combined Ratio"), size = 1) +
  geom_hline(yintercept = 1, linetype = "dashed", color = "red", alpha = 0.5) +
  scale_color_manual(values = c("Loss Ratio" = "purple", "Combined Ratio" = "orange")) +
  labs(title = "Underwriting Ratios",
       subtitle = "Values below 1.0 indicate profitability",
       x = "Turn",
       y = "Ratio",
       color = "Metric") +
  theme_minimal()
save_plot(ratio_plot, "underwriting_ratios.png")

# 3. Market Share by Line (most recent turn)
latest_turn <- max(market_data$turn)
latest_market_data <- market_data %>% filter(turn == latest_turn)

market_share_plot <- ggplot(latest_market_data, aes(x = line_id, y = market_share, fill = company)) +
  geom_bar(stat = "identity", position = "stack") +
  coord_flip() +
  labs(title = "Market Share by Line of Business",
       subtitle = paste("Turn", latest_turn),
       x = "Line of Business",
       y = "Market Share",
       fill = "Company") +
  theme_minimal()
save_plot(market_share_plot, "market_share.png")

# 4. Premium Rate Comparison (most recent turn)
price_comparison <- ggplot(latest_market_data, aes(x = line_id, y = premium_rate, fill = company)) +
  geom_bar(stat = "identity", position = "dodge") +
  coord_flip() +
  labs(title = "Premium Rate Comparison",
       subtitle = paste("Turn", latest_turn),
       x = "Line of Business",
       y = "Premium Rate",
       fill = "Company") +
  theme_minimal()
save_plot(price_comparison, "premium_comparison.png")

# 5. Investment Value Over Time
investment_plot <- ggplot(financial_data, aes(x = turn)) +
  geom_line(aes(y = investment_value, color = "Investment Value"), size = 1) +
  geom_line(aes(y = investment_income, color = "Investment Income"), size = 1) +
  scale_color_manual(values = c("Investment Value" = "darkgreen", "Investment Income" = "darkblue")) +
  labs(title = "Investment Performance",
       x = "Turn",
       y = "Amount ($)",
       color = "Metric") +
  theme_minimal()
save_plot(investment_plot, "investment_performance.png")

# Generate a simple report with key metrics
cat("Insurance Game Analytics Report\n", 
    "================================\n",
    "Generated for turn: ", latest_turn, "\n\n",
    "Key Metrics:\n",
    "- Cash on hand: $", format(financial_data$cash[nrow(financial_data)], big.mark = ","), "\n",
    "- Total assets: $", format(financial_data$total_assets[nrow(financial_data)], big.mark = ","), "\n",
    "- Current loss ratio: ", financial_data$loss_ratio[nrow(financial_data)], "\n",
    "- Current combined ratio: ", financial_data$combined_ratio[nrow(financial_data)], "\n\n",
    "All visualizations saved to: ", normalizePath(output_dir), "\n",
    file = file.path(output_dir, "report.txt"))

# Return success message
cat("Visualizations generated successfully in", normalizePath(output_dir), "\n")
""")
    
    try:
        # Run the R script
        import subprocess
        r_exe = r"C:\Program Files\R\R-4.4.1\bin\Rscript.exe"
        result = subprocess.run([r_exe, r_script_path], 
                               capture_output=True, text=True, check=True)
        
        # Check if the output directory exists and contains files
        output_dir = os.path.join('analytics', 'plots')
        if os.path.exists(output_dir) and os.listdir(output_dir):
            print(f"R visualizations generated successfully in {output_dir}")
            return output_dir
        else:
            print("R script ran but no visualizations were generated")
            print(f"R output: {result.stdout}")
            print(f"R errors: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error running R visualization: {str(e)}")
        return None 