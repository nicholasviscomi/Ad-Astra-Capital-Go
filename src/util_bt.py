from dataclasses import dataclass
from matplotlib.patches import Rectangle
import pandas as pd
import matplotlib.pyplot as plt

CE_MULTIPLIER = 1.85
one_hr_data_path  = 'historical_data/Bitstamp_BTCUSD_1h.csv'
one_min_data_path = 'historical_data/Bitstamp_BTCUSD_2021_minute.csv'

@dataclass
class Candle:
    date   : str
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

    # Kraken has a 0.9% fee per transaction
    def percent_profit(self):
        return ((self.bought - self.sold)/self.bought * 100 * self.type_)

def true_range(prev: Candle, curr: Candle):
    return max(
        (curr.high_ - curr.low_),
        (abs(curr.high_ - prev.close_)),
        (abs(curr.low_  - prev.close_))
    )
    
def run_analysis(trades: list, year: int, contents, show_graphs: bool, strat=None, suppress=False):
    """
    Gives a brief analysis of the trades. Can choose to show the graphs and save the output to a file
    Returns the winners, losers as lists of trade objects and the total profit
    """

    total = sum([
        trade.percent_profit() for trade in trades
    ])
    # total = sum(trades)

    ret = None
    winners, losers = [], []
    for trade in trades:
        # if trade > 0: winners.append(trade)
        # if trade < 0: losers.append(trade)
        if trade.percent_profit() > 0: winners.append(trade)
        if trade.percent_profit() < 0: losers.append(trade)

    # show biggest win and loss
    winners.sort(key= lambda x: x.percent_profit(), reverse=True)
    if show_graphs: show_trade(winners[0], contents)

    losers.sort(key= lambda x: x.percent_profit())
    if show_graphs: show_trade(losers[0], contents)

    # Save winners and losers list while they still have trade objects
    ret = (winners, losers, total)

    winners = [win.percent_profit() for win in winners]
    losers = [loss.percent_profit() for loss in losers]

    longs = list(filter(lambda x: x.type_ == IS_LONG, trades))
    longs_total = sum([
        trade.percent_profit() for trade in longs
    ])

    shorts = list(filter(lambda x: x.type_ == IS_SHORT, trades))
    shorts_total = sum([
        trade.percent_profit() for trade in shorts
    ])

    content = f"""
————{year} Results—————
Total: {total}
Num Trades: {len(trades)}

Long Total: {longs_total}
Num longs: {len(longs)}

Short Total: {shorts_total}
Num shorts: {len(shorts)}

Num Winners: {len(winners)}
5 Biggest Wins: {winners[0:5]}
Average Win: {sum(winners)/len(winners)}

Num Losers: {len(losers)}
5 Biggest Loss: {losers[0:5]}
Average Loss: {sum(losers)/len(losers)}
"""

    if strat != None:
        if year == 2018:
            with open(f"backtest_results/{strat}/analysis.txt", 'w') as out:
                out.write(content)
        else:
            with open(f"backtest_results/{strat}/analysis.txt", 'a') as out:
                out.write(content)
    if not suppress: print(content)

    return ret

def analyze_trade_types(winners, losers, year: int, strat=None):
    if strat == None: return

    long_winners = list(filter(lambda x: x.type_ == IS_LONG, winners))
    short_winners = list(filter(lambda x: x.type_ == IS_SHORT, winners))

    long_losers = list(filter(lambda x: x.type_ == IS_LONG, losers))
    short_losers = list(filter(lambda x: x.type_ == IS_SHORT, losers))

    _, ax = plt.subplots(nrows=1, ncols=2)

    ax[0].pie([len(long_winners), len(short_winners)], labels=['Long', 'Short'], autopct='%1.1f%%')
    ax[0].set_title(f"Winning Trades {year}")

    ax[1].pie([len(long_losers), len(short_losers)], labels=['Long', 'Short'], autopct='%1.1f%%')
    ax[1].set_title(f"Losing Trades {year}")

    plt.savefig(f"backtest_results/{strat}/{year}-Trade_Type_Analysis.png")

    # ax[0].clear()
    # ax[1].clear()
    # plt.show()

def show_trade(trade: Trade, contents, zoom: int = 5):
    """
    Create a matplot of the trade
    It will show (zoom)-number of candles before and after the trade
    """

    candles = []
    for i in range(trade.start_i + zoom, trade.end_i - zoom, -1):
        line = contents[i]
        date, open_, high_, low_, close_ = line[1], float(line[3]), float(line[4]), float(line[5]), float(line[6])
        candles.append(Candle(date, open_, high_, low_, close_))

    prices = pd.DataFrame({
        "high"  : [candle.high_  for candle in candles],
        "low"   : [candle.low_   for candle in candles],
        "open"  : [candle.open_  for candle in candles],
        "close" : [candle.close_ for candle in candles]
    })
    green  = prices[prices.close >= prices.open] # green candles
    red    = prices[prices.close < prices.open] # red candles
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
        xmin=zoom, xmax=zoom + (trade.start_i - trade.end_i), 
        label='bought', color='orange'
    )
    ax.hlines(
        trade.sold, 
        xmin=zoom, xmax=zoom + (trade.start_i - trade.end_i), 
        label='sold', color='purple'
    )

    above = trade.sold if trade.sold > trade.bought else trade.bought
    below = trade.sold if trade.sold < trade.bought else trade.bought
    ax.add_patch(
        Rectangle(
            (zoom, below), # start at the lowest left corner
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