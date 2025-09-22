## **2025 QFin Sem1 Project Part 2**

### **Introduction**

The general exchange structure has not changed since Part 1 of the Project. The primary new feature of the exchange is the introduction of an ETF.

### **ETFs**

The ETF "GUILD" consists of 5 copies of "QFIN" and 5 copies of "UEC".

You have the ability to create/redeem with the ConversionRequest object in base.py.

- **CREATE**: Underlyings -> ETF
- **REDEEM**: ETF -> Underlyings

```python
class ConversionRequest:
    def __init__(self, ticker: str, size: int, direction: str, bot_name: str):
        self.ticker = ticker
        self.size = size
        self.direction = direction
        self.bot_name = bot_name
```

Here, ticker is the ETF (not the underlyings), direction is 'CREATE'/'REDEEM' and size refers to how many of the ETF are created/redeemed.

For example:

`ConversionRequest("GUILD", 5, "REDEEM", "PlayerAlgorithm")` sends a conversion request that:
- Reduces "GUILD" position by 5
- Increases "UEC" and "QFIN" positions by 25 each

### **Testing**

Your bot will be run 20 times over 20,000 iterations each to determine your score. Instead of in Round 1 where the score was merely the mean PnL, the score is now equal to:

**Score = Mean PnL - 0.1 × Standard Deviation of Test Runs**

### **Settlement**

PnL is determined as specified in the method for the 1st Project round (i.e. before it was changed to cash with position 0 due to the bug).

### **Quality of Life Changes**

1) You now have the option to receive your bot's current position with the book whenever `send_messages()` is called. You can change this with the `give_positions` argument in `run_game()`.

2) We have created a visualiser to allow for easier data analysis. This can be set on/off using the `visualiser` flag in the `play_game()` method. In your_algo, significant tracking functionality has been added. Please ask me if you have any questions re. these methods, but they shouldn't get in your way at all. The visualiser methods are available to you, so feel free to add functionality if you desire. 

3) We included the option to have a progress bar when a bot simulation is running, with the `progress_bar` flag in `run_game()`. I find this nice to have, but be careful of having any print statements in your bot if this is on -> it looks ugly.

4) When called, your bot can take num_timestamps as input to be fed in by the game engine

### **Submission**

#### **Format**

Email a single file to qfinorderbot@gmail.com containing your PlayerAlgorithm class. Your bot must be called PlayerAlgorithm, but please name the file itself with your team name. The email must have the subject `"Project2 Submission_{team_name}"`. This is an f string. Please do not have any quotation marks in the subject

#### **Requirements**

- Your bot must not print anything or create any CSVs
- Your bot must not interact with anything outside the program
- Violations will result in arbitrary fines

#### **Dates**

Submission Date: Thursday the 9th of October @ Midnight




