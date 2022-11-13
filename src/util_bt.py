from dataclasses import dataclass
from matplotlib.patches import Rectangle
import pandas as pd
import matplotlib.pyplot as plt

CE_MULTIPLIER = 1.85
one_hr_data_path  = 'historical_data/Bitstamp_BTCUSD_1h.csv'
one_min_data_path = 'historical_data/Bitstamp_BTCUSD_2021_minute.csv'

@dataclass
class Candle:
    open_  : float
    high_  : float
    low_   : float
    close_ : float


IS_SHORT =  1
IS_LONG  = -1
@dataclass
class Trade:
    bought  : float
    sold    : float
    start_i : int # index of the start of the trade in the file
    end_i   : int # index of the end of the trade in the file
    type_    : int # -1 if shorting so profit calculations are correct

    def percent_profit(self):
        return (self.bought - self.sold)/self.bought * 100 * self.type_

def oneday_ATR(prev: Candle, curr: Candle):
    return max(
        (curr.high_ - curr.low_),
        (abs(curr.high_ - prev.close_)),
        (abs(curr.low_  - prev.close_))
    )
    
def print_analysis(trades: list, year: int, contents, graphs: bool):
    total = sum([
        trade.percent_profit() for trade in trades
    ])
    # total = sum(trades)

    winners, losers = [], []
    for trade in trades:
        # if trade > 0: winners.append(trade)
        # if trade < 0: losers.append(trade)
        if trade.percent_profit() > 0: winners.append(trade)
        if trade.percent_profit() < 0: losers.append(trade)

    # show biggest win and loss
    winners.sort(key= lambda x: x.percent_profit(), reverse=True)
    if graphs: show_trade(winners[0], contents)

    losers.sort(key= lambda x: x.percent_profit())
    if graphs: show_trade(losers[0], contents)

    winners = [win.percent_profit() for win in winners]

    losers = [loss.percent_profit() for loss in losers]

    print(f"————{year} Results—————")
    print(f"Total: {total}")
    print(f"Num Trades: {len(trades)}\n")
    print(f"Num Winners: {len(winners)}")
    print(f"5 Biggest Wins: {winners[0:5]}")
    print(f"Average Win: {sum(winners)/len(winners)}\n")
    print(f"Num Losers: {len(losers)}")
    print(f"5 Biggest Loss: {losers[0:5]}")
    print(f"Average Loss: {sum(losers)/len(losers)}")

def show_trade(trade: Trade, contents):
    print("Type: ", end="")
    print("long" if trade.type_ == IS_LONG else "short")
    print(f"Profit: {trade.percent_profit()}")

    candles = []
    for i in range(trade.start_i + 5, trade.end_i - 5, -1):
        line = contents[i]
        open_, high_, low_, close_ = float(line[3]), float(line[4]), float(line[5]), float(line[6])
        candles.append(Candle(open_, high_, low_, close_))

    prices = pd.DataFrame({
        "open"  : [candle.open_  for candle in candles],
        "high"  : [candle.high_  for candle in candles],
        "low"   : [candle.low_   for candle in candles],
        "close" : [candle.close_ for candle in candles]
    })
    green = prices[prices.close >= prices.open] # green candles
    red   = prices[prices.close < prices.open] # red candles
    w1, w2 = 0.4, 0.04 # width of thick part and width of extrema

    _, ax = plt.subplots()
    # graph green candles (x, height, width, bottom, color)
    ax.bar(green.index, green.close - green.open, w1, green.open, color='green') # thick middle part
    ax.bar(green.index, green.high  - green.close, w2, green.close, color='green') # high price
    ax.bar(green.index, green.low  - green.open, w2, green.open, color='green') # low price
    
    ax.bar(red.index, red.close - red.open, w1, red.open, color='red') # thick middle part
    ax.bar(red.index, red.high  - red.open, w2, red.open, color='red') # high price
    ax.bar(red.index, red.low   - red.close, w2, red.close, color='red') # low price

    ax.hlines(
        trade.bought,
        xmin=5, xmax=5 + (trade.start_i - trade.end_i), 
        label='bought', color='orange'
    )
    ax.hlines(
        trade.sold, 
        xmin=5, xmax=5 + (trade.start_i - trade.end_i), 
        label='sold', color='purple'
    )

    above = trade.sold if trade.sold > trade.bought else trade.bought
    below = trade.sold if trade.sold < trade.bought else trade.bought
    ax.add_patch(
        Rectangle(
            (5, below), # start at the lowest left corner
            trade.start_i - trade.end_i, 
            above - below, 
            alpha=0.5,
            color='gray'
        )
    )

    title = f"{trade.percent_profit() : .2f}" + "% profit going " + ("long" if trade.type_ == IS_LONG else "short")
    ax.set_title(title)
    ax.legend()
    plt.show()

year_ranges = {
    2018: (39379, 33843),
    2019: (33842, 25083),
    2020: (25082, 16299),
    2021: (16298, 7539),
    2022: (7538, 0)
}