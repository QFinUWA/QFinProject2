# Trading Simulation - Intern Distribution

## Quick Start

1. **Run the simulation**: `python play_game.py`
2. **View results**: Open `visualizer/visualiser.html` in your browser and drag the generated CSV files

## Output Files

After running the simulation, you'll find these files in the `visualizer/` directory:

- **`log_game_record.csv`**: Your trading performance (positions, PnL, custom messages in PlayerAlgorithm_message column)
- **`log_orderbook_data.csv`**: Full market orderbook data (other traders anonymized)  
- **`log_trades_data.csv`**: All market trades (other traders anonymized)

## Player Algorithm Features

Edit `kaibot.py` to implement your trading strategy:

```python
# Add custom messages to your log (examples included in code)
# Note: Commas are automatically replaced with | for CSV compatibility
self.add_message("Position update | UEC: 0 | QFIN: -6 | GUILD: 0 | Cash: 6004.40")
self.add_message("Trade executed | maker buy 1 QFIN @ 1002.70")
self.add_message("Large short position | QFIN: -119 | adjusting skew to -0.97")

# Access your positions
current_position = self.positions["QFIN"]
current_cash = self.positions["Cash"]

# Your algorithm logic goes in the send_messages() method
```

### Example Messages Already Included:
- **Position updates** every 100 timestamps showing all positions and cash
- **Trade notifications** when you execute trades (as aggressor or maker)
- **Position alerts** when positions exceed ±100 shares with skew adjustments
- **Price movement alerts** when prices move >1% from previous levels

## Visualization

1. Open `visualizer/visualiser.html` in any web browser
2. Use the file selectors to load your CSV files
3. Analyze your trading performance and market activity

### Enhanced Features:
- **Improved Statistics**: Total P&L, Max Drawdown (dollar value), P&L per 1000 timestamps
- **Auto-Product Selection**: First product automatically selected when data loads
- **Extended Tick Sizes**: Now includes 10.0 tick size option
- **Player Messages**: View your custom messages below the orderbook for each timestamp

## Key Points

- Other traders appear as "ANONYMOUS" in your data
- Your positions and PnL are tracked automatically
- Full market data is available for analysis
- No automatic browser opening - manual file loading only