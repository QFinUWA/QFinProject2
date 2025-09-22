from bots1 import Msg
from base import Exchange, Trade, Order, Product
import numpy as np

class PlayerAlgorithm:
    """
    Base trading algorithm with tracking functionality only.

    Features:
    - Position tracking: All positions and PnL are automatically tracked
    - Data export: Player data is exported to log_game.csv with anonymized market data
    - Order management utilities: Helper functions for placing/canceling orders

    To create a trading strategy, inherit from this class and override send_messages().
    """
    def __init__(self, products, num_timestamps, visualisation = True):
        self.products = products
        self.name = "PlayerAlgorithm"
        self.position_limits = {product.ticker: product.pos_limit for product in products}
        self.fines = {product.ticker: product.fine for product in products}

        self.sent_orders = {product.ticker: [] for product in products} # for cancelation
        self.positions = {product.ticker: 0 for product in products}
        self.positions["Cash"] = 0.0
        self.timestamp = 0
        self.visualisation = visualisation
        self.memory = {
            "last_mids": {product.ticker: 1000.0 for product in products},  # Initialize with default price
        }

        self.num_timestamps = num_timestamps
        self.idx = 0  # Initialize order ID counter

        # Player tracking data for CSV export
        self.player_view_data = {
            'orderbook_snapshots': [],
            'visible_trades': [],
            'position_history': [],
            'pnl_history': []
        }

    # ===== Main Method - Override this in your trading strategy =====
    def send_messages(self, book):
        """
        Main method called each timestamp. Override this in your trading algorithm.

        Args:
            book: Dictionary containing orderbook data for all products

        Returns:
            List of messages (orders, cancellations, etc.)
        """
  

        # Track player data for this timestamp
        messages = []

        if self.visualisation:
            self.update_fines()
            self.update_memory(book)
            self._track_player_data(book)



        self.timestamp += 1

        return messages

    

    # ===== Helper Functions =====
    def update_fines(self):
        """Apply position limit fines"""
        for ticker, pos in self.positions.items():
            if ticker == 'Cash':
                continue
            if ticker in self.position_limits and abs(pos) > self.position_limits[ticker]:
                self.positions['Cash'] -= self.fines[ticker] * (abs(pos) - self.position_limits[ticker])

    def mid_price(self, book, ticker, weights=1):
        """ Get the best guess at mid price, optionally weighted by size """
        bids = book[ticker]["Bids"]
        asks = book[ticker]["Asks"]

        if not bids or not asks:
            last_mid = self.memory["last_mids"][ticker]
            if bids:
                return min(last_mid, bids[0].price)
            elif asks:
                return max(last_mid, asks[0].price)
            return last_mid

        # Calculate weighted prices
        total_bid_size = total_ask_size = 0
        bid_price = ask_price = 0

        for bid in bids:
            if total_bid_size >= weights: break
            size = min(bid.size, weights - total_bid_size)
            bid_price += bid.price * size
            total_bid_size += size

        for ask in asks:
            if total_ask_size >= weights: break
            size = min(ask.size, weights - total_ask_size)
            ask_price += ask.price * size
            total_ask_size += size

        bid_price /= total_bid_size if total_bid_size > 0 else 1
        ask_price /= total_ask_size if total_ask_size > 0 else 1

        return (bid_price + ask_price) / 2

    def update_memory(self, book):
        """ Update the memory with the latest values from book """
        for ticker, data in book.items():
            if data['Bids'] and data['Asks']:
                mid_price = self.mid_price(book, ticker)
                self.memory["last_mids"][ticker] = mid_price

    def create_order(self, ticker, price, size, agg_dir):
        """Create and track a new order"""
        order = Order(ticker=ticker, price=price, size=size, order_id=self.idx, agg_dir=agg_dir, bot_name=self.name)
        self.sent_orders[ticker].append(self.idx)
        self.idx += 1
        return Msg("ORDER", order)

    def cancel_order(self, ticker, order_id):
        """Cancel a specific order"""
        cancel_msg = Msg("REMOVE", order_id)
        self.sent_orders[ticker].remove(order_id)
        return cancel_msg

    def cancel_all_orders(self):
        """Cancel all outstanding orders"""
        msgs = []
        for ticker, order_ids in self.sent_orders.items():
            # Create a copy of the list to avoid modifying while iterating
            for order_id in list(order_ids):
                msgs.append(self.cancel_order(ticker, order_id))
        return msgs

    def round_to_mpv(self, price, mpv, round_type="nearest"):
        """Round price to nearest MPV."""
        funcs = {"nearest": round, "up": np.ceil, "down": np.floor}
        # Handle complex numbers by taking the real part
        price_real = price.real if isinstance(price, complex) else price
        mpv_real = mpv.real if isinstance(mpv, complex) else mpv
        result = funcs[round_type](price_real / mpv_real) * mpv_real
        return round(result, 4)

    def set_idx(self, idx):
        """Set the order ID counter"""
        self.idx = idx

    def process_trades(self, trades):
        """Process executed trades and update positions"""
        for trade in trades:
            # Track visible trades for player view
            self.player_view_data['visible_trades'].append({
                'timestamp': self.timestamp,
                'ticker': trade.ticker,
                'price': trade.price,
                'size': trade.size,
                'agg_dir': trade.agg_dir,
                'agg_bot': trade.agg_bot,
                'rest_bot': trade.rest_bot,
                'involves_player': (trade.agg_bot == self.name or trade.rest_bot == self.name)
            })


            # Update positions based on trade
            if trade.agg_bot == self.name:
                # If we were aggressor, position changes in direction of aggression
                if trade.agg_dir == "Buy":
                    self.positions[trade.ticker] += trade.size
                    self.positions["Cash"] -= trade.price * trade.size
                else:
                    self.positions[trade.ticker] -= trade.size
                    self.positions["Cash"] += trade.price * trade.size
            elif trade.rest_bot == self.name:
                # If we were resting, position changes opposite to aggressor direction
                if trade.agg_dir == "Buy":
                    self.positions[trade.ticker] -= trade.size
                    self.positions["Cash"] += trade.price * trade.size
                else:
                    self.positions[trade.ticker] += trade.size
                    self.positions["Cash"] -= trade.price * trade.size

    # ===== Player Tracking Methods =====
    def _track_player_data(self, book):
        """Track player-specific data for each timestamp"""
        # Store orderbook snapshot with player perspective
        book_snapshot = {
            'timestamp': self.timestamp,
            'book': {}
        }

        for ticker, data in book.items():
            book_snapshot['book'][ticker] = {
                'Bids': [{
                    'price': order.price,
                    'size': order.size,
                    'bot_name': order.bot_name,
                    'is_own': order.bot_name == self.name
                } for order in data['Bids']],
                'Asks': [{
                    'price': order.price,
                    'size': order.size,
                    'bot_name': order.bot_name,
                    'is_own': order.bot_name == self.name
                } for order in data['Asks']]
            }

        self.player_view_data['orderbook_snapshots'].append(book_snapshot)

        # Track position and PnL history
        position_snapshot = {'timestamp': self.timestamp}
        pnl = self.positions["Cash"]  # Start with cash

        for product in self.products:
            ticker = product.ticker
            position_snapshot[ticker] = self.positions[ticker]
            # Calculate mark-to-market PnL if we have mid price
            if ticker in book and book[ticker]['Bids'] and book[ticker]['Asks']:
                mid_price = (book[ticker]['Bids'][0].price + book[ticker]['Asks'][0].price) / 2
                pnl += self.positions[ticker] * mid_price

        position_snapshot['Cash'] = self.positions["Cash"]
        position_snapshot['PnL'] = pnl

        self.player_view_data['position_history'].append(position_snapshot)