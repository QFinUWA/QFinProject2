#!/usr/bin/env python3
"""
Visualizer Launch Utility

This module provides functionality to launch the trading game visualizer.
It handles server setup, browser opening, and fallback mechanisms.
"""

import webbrowser
import subprocess
import os
import time
import platform
import urllib.request


def launch_visualizer():
    """Launch the visualizer with auto-load in browser"""
    try:
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        visualizer_path = os.path.join(current_dir, 'visualizer', 'visualiser.html')

        # Try to kill any existing server on port 8000 (Windows compatible)
        if platform.system() == 'Windows':
            # On Windows, use netstat to find and kill process
            try:
                # Find process using port 8000
                result = subprocess.run('netstat -ano | findstr :8000',
                                      shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    # Extract PID from output
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'LISTENING' in line:
                            parts = line.split()
                            pid = parts[-1]
                            # Kill the process
                            subprocess.run(f'taskkill /F /PID {pid}', shell=True,
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            time.sleep(0.5)
            except:
                pass  # Ignore errors, server might not be running
        else:
            # Unix-like systems
            try:
                subprocess.run(['pkill', '-f', 'python.*http.server.*8000'],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.5)
            except:
                pass

        # Start a simple HTTP server in the background
        print("\nStarting local server for visualizer...")
        if platform.system() == 'Windows':
            # Windows: use python directly
            server_process = subprocess.Popen(
                ['python', '-m', 'http.server', '8000'],
                cwd=current_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == 'Windows' else 0
            )
        else:
            # Unix-like systems
            server_process = subprocess.Popen(
                ['python3', '-m', 'http.server', '8000'],
                cwd=current_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        # Give server time to start
        time.sleep(2)

        # Test if server is running (without opening in browser)
        try:
            # Use HEAD request to avoid any browser auto-open behavior
            req = urllib.request.Request('http://localhost:8000', method='HEAD')
            urllib.request.urlopen(req, timeout=2)
            server_running = True
        except:
            server_running = False

        if server_running:
            # Open browser with auto-load parameter and cache busting
            cache_bust = str(int(time.time() * 1000))
            url = f'http://localhost:8000/visualizer/visualiser.html?autoload=true&v={cache_bust}'
            print(f"Opening visualizer at: {url}")

            # Use open_new_tab to ensure we're not triggering any default page behavior
            # Add a small delay to ensure server is fully ready
            time.sleep(0.5)
            webbrowser.open_new_tab(url)

            print("\n[SUCCESS] Visualizer opened with auto-loaded data!")
            print("[INFO] The visualizer should now display your game data automatically.")
            print("[WARNING] Keep this terminal open while using the visualizer.")
            print("[INFO] To stop the server, close this terminal or press Ctrl+C.\n")

            return server_process
        else:
            # Fallback to file:// URL (without auto-load due to CORS)
            print("\n[WARNING] HTTP server couldn't start. Opening visualizer in manual mode...")
            file_url = f'file:///{visualizer_path.replace(os.sep, "/")}'
            webbrowser.open(file_url)
            print("[INFO] Please manually drag and drop the CSV files from the 'visualizer' folder:")
            print("   - log_orderbook_data.csv")
            print("   - log_trades_data.csv")
            print("   - log_game_record.csv\n")

            return None

    except Exception as e:
        print(f"\n[ERROR] Could not open browser automatically: {e}")
        print("[INFO] Please manually open: visualizer/visualiser.html")
        print("   Then drag and drop the CSV files from the 'visualizer' folder.\n")
        return None


def main():
    """Main function for running the visualizer standalone"""
    print("=== Trading Game Visualizer ===")
    print("Launching visualizer...")

    server_process = launch_visualizer()

    if server_process:
        try:
            # Keep the server running
            print("Server is running. Press Ctrl+C to stop.")
            server_process.wait()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            server_process.terminate()
            server_process.wait()
            print("Server stopped.")


if __name__ == "__main__":
    main()