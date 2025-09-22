## **2025 QFin Sem1 Project**

### **Introduction**

Trading occurs in a simulated market environment that is turn based; all bots in the environment are called in a cycle that we just iterate through. In the first week only 1 product, "UEC" will be traded, although more products will be present in future weeks. The products are included in a Product class. Please note the difference between the Product and the ticker given by Product.ticker. The ticker is just the string, and typically used for all interaction with the exchange, whle the Product class contains all of the metadata

Your bot will recieve information in two forms. The first is the OrderBook object, every time your bot is called with the bot.send_messages() object. The book is comprised of Rest objects (resting orders). 

Additionally, every time any bot is called, all trades made are passed into your bots via the bot.process_trades() method. 

When your bot is called, you must return a list of messages to send back to the exchange. These messages can be of two types:
- Order
- Remove

, each with their own classes. These are then wrapped with the message class to be sent to the exchange.

These trades will then execute, and you and all the other bots will recieve back the trades completed in the form of Trade objects.

Below is a basic summary of the game flow that is present (this is not exact please don't try and hack this):

Bots is just a list of all the bots present in the exchange

```python
for _ in range(num_rounds):
    for bot in bots:
        messages = bot.send_messages(game.book)
        trades = []
        for msg in messages:
            trade = exchange.send(msg)  # send the message to the Exchange, gets trade, or None back
            if trade is not None:
                trades.append(trade)
        for bot in bots:
            bot.process_orders(trades)  # sends all the completed trades to the other bots
```

The code for all of the classes mentioned above can be found in the base.py file

Additionally, this is the first time this exact project has been run. P($\exists$ Bugs) ~ 0.99 so please let me know if you notice anything. In the game.py file, which you do not have access to, this code is included that will print every time you run the simulation:

```python
random_seed = random.randint(0, 10000000)
random.seed(random_seed)
np.random.seed(random_seed)

print("Random seed set to:", random_seed)
```

When letting me know of bugs, please include all of your code and the random seed that was used so that I can recreate the error if necessary.


### **Market Maker Behaviour**

A market maker exists in the market to provide liquidity the market maker quotes at a constant width and density about some midprice, with constant density/frequency of orders. Orders are refreshed every time the market maker is called. 

The midprice that the orders are centered about is a function of the net position of the market maker. Particularly, it does this in a manner so that the market maker updates as if it would if it quoted infinitely many levels. Below is an example of this

|   Price   |   Bid Size   |   Ask Size   |
|:---------:|:------------:|:------------:|
| 105.00    |              |  25          |
| 104.50    |              |  25          |
| 104.00    |              |  25          |
| 103.50    |              |  25          |
| 102.50    |  25          |              |
| 102.00    |  25          |              |
| 101.50    |  25          |              |
| 101.00    |  25          |              |

If 25 size was bought from the Market Maker, the mid would then shift to 103.50, and when next refreshed the market maker would be quoting

|   Price   |   Bid Size   |   Ask Size   |
|:---------:|:------------:|:------------:|
| 105.50    |              |  25          |
| 105.00    |              |  25          |
| 104.50    |              |  25          |
| 104.00    |              |  25          |
| 103.00    |  25          |              |
| 102.50    |  25          |              |
| 102.00    |  25          |              |
| 101.50    |  25          |              |

Note the quoting is of constant size at every level, and the levels are evenly spaced. Additionally, the market maker has what is called a linear fade.

If 13 size was now bought from the market maker, the mid would then shift up by 26c to 13.76, so the MM would now quote:

|   Price   |   Bid Size   |   Ask Size   |
|:---------:|:------------:|:------------:|
| 105.76    |              |  25          |
| 105.26    |              |  25          |
| 104.76    |              |  25          |
| 104.26    |              |  25          |
| 103.26    |     25       |              |
| 102.76    |     25       |              |
| 102.26    |     25       |              |
| 101.76    |     25       |              |


### **Settlement**

Excess position does not just settle at the final bid/ask. To prevent the (very dumb) strategy of buying heaps to force the price up and finishing with final price > average trade price, settlement is conducted by determining what the average price would be if all the size remaining was traded against the market maker given the final price.

Given the relative position limits, this doesn't have a huge effect, but something to consier

### **Fines**

There is no hard set position limit. However, at the end of every cycle for every 1 position over the limit of 200, your bot will be fined $20. This is very significant relevant to the total PnL in the game so be careful with this

### **Getting Started**

1) Create methods for tracking order ids, and play around with sending/cancelling orders

2) Think about how to visualise the data

3) Implement a method of tracking your current position

4) Think about how the you can export price data to a jupyter-notebook for better analysis

### **More General Tips and Tricks**

1) Think about how you will determine the expected pnl of a trading strategy when applied to new data. What is overfitting?

2) Spend a while reading through the different methods

3) Consult with mentors. The correlation between trading team competition performance and engagement with mentors is very high

4) Submit something for the preliminary round

5) If you are not familiar with classes/have never directly interacted with them talk with your mentors/me as becoming comfortable interacting with the market is key 




### **Submission**

#### **Format**

Email a single file to the email qfinorderbot@gmail.com containing your PlayerAlgorithm class. Ensure that your bot has a bot.name attribute with your team name, and also has the bot.team_members attribute with a list containing the names of your team members. The email must have the subject f"Project1 Submission_{team_name}" or f"Preliminary1 Submission_{team_name}".

#### **Dates**

Submission Date: Midnight on the 28th of August

Preliminary Submission Date: Midnight on the 20th of August

Preliminary submission is not compulsary but it will a) give you a reasonable sense for how your bot is doing relative to others and b) give us the ability to provide some feedback -> we can generally provide feedback but can do so more formally and give you the potential to update your bots. Additionally this is probably the only time that I (Josh) will do a full read through and review of a bot as opposed to answering more specific questions so take advantage of this.

### **Assessment**

I do not like variance. As such, when assessing the bots I will run them many times (~20 each) on an additional 20k "rounds" and take the average PnL. It will be annoying if this takes long because extremely inefficient code has been written. As such, if the average running time is > 2? (to be changed) minutes per iteration, I will deduct some number of points. I do not believe that is preventing anything that you would want to do anyway, but if this is causing problems please send me your code to your mentor/Me/Sithum and we can have a look at it.

Note this assessment function $\mathbb{E}[PnL]$ may change for future rounds. SIG recently did one of these with the loss function of $\mathbb{E}[PnL] - 0.1 * STD[PnL]$ that seemed reasonable so just pay attention for future weeks. 

### **Scoring**

**Final Submission**: There will be a pool of 800 points awarded to teams with PnL > 0 awarded proportionally to the number of points you get

**Preliminary Submission**: The same thing, but the pool size is 200 points


