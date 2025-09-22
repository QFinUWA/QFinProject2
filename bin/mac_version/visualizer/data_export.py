import csv
import webbrowser
import subprocess
import os
import time


def export_game_data(game):
    """Export game data to CSV files for visualization with player anonymization"""
    import os
    
    # Ensure we're in the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find player bot for anonymization
    player_bot = None
    player_name = None
    for bot in game.bots.values():
        if hasattr(bot, 'player_view_data'):
            player_bot = bot
            player_name = bot.name
            break
    
    # Export player-only game record (keeping consistent with existing structure)
    if hasattr(game, 'record') and game.record and player_name:
        with open(os.path.join(script_dir, 'log_game_record.csv'), 'w', newline='') as f:
            # Filter for player-specific columns only
            player_columns = []
            all_columns = list(game.record.keys())
            
            # Start with timestamp and loop
            player_columns = ['timestamp', 'Loop']
            
            # Add player-specific columns and market prices
            # Extract product names from player columns (e.g., PlayerAlgorithm_UEC -> UEC)
            product_names = set()
            for col in all_columns:
                if col.startswith(f'{player_name}_') and not col.endswith('_Cash') and not col.endswith('_PnL'):
                    product_name = col.replace(f'{player_name}_', '')
                    if product_name not in ['Cash', 'PnL']:
                        product_names.add(product_name)

            for col in all_columns:
                if (col.startswith(f'{player_name}_') or col in product_names):
                    player_columns.append(col)
            
            writer = csv.DictWriter(f, fieldnames=player_columns, quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()

            # Transpose the record data for player columns only
            num_rows = len(game.record['Loop'])
            for i in range(num_rows):
                row = {}
                for col in player_columns:
                    if col == 'timestamp':
                        # Add timestamp (same as Loop for now)
                        row[col] = game.record['Loop'][i] if i < len(game.record['Loop']) else i
                    elif col in game.record:
                        row[col] = game.record[col][i] if i < len(game.record[col]) else 0
                    else:
                        row[col] = ''
                writer.writerow(row)
    
    # Export orderbook data (anonymize non-player bot names)
    if hasattr(game, 'orderbook_history'):
        with open(os.path.join(script_dir, 'log_orderbook_data.csv'), 'w', newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['timestamp', 'ticker', 'side', 'price', 'size', 'bot_name'])
            
            for timestamp, book_state in enumerate(game.orderbook_history):
                for ticker, book in book_state.items():
                    for order in book['Bids']:
                        # Anonymize non-player bot names
                        bot_name = order.bot_name if order.bot_name == player_name else "ANONYMOUS"
                        writer.writerow([timestamp, ticker, 'bid', order.price, order.size, bot_name])
                    for order in book['Asks']:
                        bot_name = order.bot_name if order.bot_name == player_name else "ANONYMOUS"
                        writer.writerow([timestamp, ticker, 'ask', order.price, order.size, bot_name])
    
    # Export trades data (anonymize non-player bot names)
    if hasattr(game, 'all_trades'):
        with open(os.path.join(script_dir, 'log_trades_data.csv'), 'w', newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['timestamp', 'ticker', 'price', 'size', 'side', 'agg_bot', 'rest_bot'])
            
            for trade in game.all_trades:
                # Anonymize non-player bot names
                agg_bot = trade.agg_bot if trade.agg_bot == player_name else "ANONYMOUS"
                rest_bot = trade.rest_bot if trade.rest_bot == player_name else "ANONYMOUS"
                writer.writerow([
                    trade.loop_num, trade.ticker, trade.price, trade.size, 
                    trade.agg_dir.lower(), agg_bot, rest_bot
                ])
    
    print("Exported visualization data: log_game_record.csv, log_orderbook_data.csv, log_trades_data.csv")


def run_visualiser():
    """Launch the visualizer in Firefox"""
    
    # Kill any existing server on port 8000 more aggressively
    try:
        # Kill by port
        subprocess.run(['fuser', '-k', '8000/tcp'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.2)
        # Kill by process name
        subprocess.run(['pkill', '-f', 'python3 -m http.server 8000'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.5)
    except:
        pass
    
    # Start HTTP server from project root directory
    try:
        # Get the project root directory (parent of visualizer)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Start server from project root
        subprocess.Popen(['python3', '-m', 'http.server', '8000'], 
                        cwd=project_root,
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        time.sleep(2)  # Give server more time to start
        
        # Test if server is running
        import urllib.request
        try:
            urllib.request.urlopen('http://localhost:8000', timeout=2)
            server_running = True
        except:
            server_running = False
        
        if server_running:
            # Open visualizer in default browser with strong cache busting
            cache_bust = str(int(time.time() * 1000))  # Use milliseconds for more uniqueness
            webbrowser.open(f'http://localhost:8000/visualizer/book_state_visualizer.html?v={cache_bust}&nocache={cache_bust}&t={cache_bust}')
            
            print("Opening visualizer at http://localhost:8000/visualizer/book_state_visualizer.html")
            print("Server running from project root. Stop with 'pkill -f \"python3 -m http.server 8000\"'")
        else:
            raise Exception("Server failed to start")
        
    except Exception as e:
        # Fallback to file:// URL in default browser
        print(f"HTTP server failed ({e}), falling back to file:// URL")
        try:
            visualizer_path = os.path.abspath('visualizer/book_state_visualizer.html')
            webbrowser.open(f'file://{visualizer_path}')
            print(f"Opening visualizer: {visualizer_path}")
            print("Note: Auto-loading requires manual file selection due to browser security")
        except Exception as browser_error:
            print(f"Could not open browser: {browser_error}")
            print(f"Please manually open: {os.path.abspath('visualizer/book_state_visualizer.html')}")


