import platform
import sys
import os

original_sys_path = sys.path.copy()

current_dir = os.path.dirname(os.path.abspath(__file__))
os_name = platform.system()

if os_name == "Linux":
    sys.path.insert(0, os.path.join(current_dir, "bin/linux_version"))
    from bin.linux_version.game_setup import run_game
elif os_name == "Windows":
    sys.path.insert(0, os.path.join(current_dir, "bin/windows_version"))
    from bin.windows_version.game_setup import run_game
elif os_name == "Darwin":
    sys.path.insert(0, os.path.join(current_dir, "bin/mac_version"))
    from bin.mac_version.game_setup import run_game
else:
    raise ValueError("Unsupported OS")

from base import Product

print("Imports Completed")

sys.path = original_sys_path

# ======================Do Not Change Anything above here====================
from launch_visualizer import launch_visualizer
from base_algo import PlayerAlgorithm
# Product setup

uec = Product("UEC", mpv=0.1, pos_limit=200, fine=200, fee_type="SetFee", trade_fee=0)
qfin = Product("QFIN", mpv=0.1, pos_limit=1000, fine=200, fee_type="SetFee", trade_fee=0)
sober = Product("SOBER", mpv=0.01, pos_limit=1000, fine=20, fee_type="SetFee", trade_fee=0)

converts = {"UEC": 5, "QFIN": 5}
guild = Product("GUILD", mpv = 1, pos_limit=10, fine = 1000, conversions=converts, fee_type='SetFee', trade_fee=0)

products = [uec, qfin, sober, guild]


# Game parameters
num_timestamps = 10000


# Main game execution
player_pnl = run_game(PlayerAlgorithm, num_timestamps, products, print_limits=False, visualiser=True, give_positions=False, progress_bar=True)

print(player_pnl)


