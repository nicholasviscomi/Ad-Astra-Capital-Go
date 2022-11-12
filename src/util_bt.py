from dataclasses import dataclass
CE_MULTIPLIER = 1.85
one_hr_data_path  = 'historical_data/Bitstamp_BTCUSD_1h.csv'
one_min_data_path = 'historical_data/Bitstamp_BTCUSD_2021_minute.csv'

@dataclass
class Candle:
    open_  : float
    high_  : float
    low_   : float
    close_ : float


SHORT_MULT = -1
LONG_MULT  =  1
@dataclass
class Trade:
    bought  : float
    sold    : float
    start_i : int # index of the start of the trade in the file
    end_i   : int # index of the end of the trade in the file
    mult    : int # -1 if shorting so profit calculations are correct

    def percent_profit(self):
        return ((self.sold / self.bought) - 1) * 100 * self.mult


def oneday_ATR(prev: Candle, curr: Candle):
    return max(
        (curr.high_ - curr.low_),
        (abs(curr.high_ - prev.close_)),
        (abs(curr.low_  - prev.close_))
    )
    
def print_analysis(trades: list, year: int):
    total = sum([
        trade.percent_profit() for trade in trades
    ])

    winners, losers = [], []
    for trade in trades:
        if trade.percent_profit() > 0: winners.append(trade)
        if trade.percent_profit() < 0: losers.append(trade)

    winners = [win.percent_profit() for win in winners]
    winners.sort(reverse=True)

    losers = [loss.percent_profit() for loss in losers]
    losers.sort()

    print(f"————{year} Results—————")
    print(f"Total: {total}")
    print(f"Num Trades: {len(trades)}\n")
    print(f"Num Winners: {len(winners)}")
    print(f"5 Biggest Wins: {winners[0:5]}")
    print(f"Average Win: {sum(winners)/len(winners)}\n")
    print(f"Num Losers: {len(losers)}")
    print(f"5 Biggest Loss: {losers[0:5]}")
    print(f"Average Loss: {sum(losers)/len(losers)}")

year_ranges = {
    2018: (39379, 33843),
    2019: (33842, 25083),
    2020: (25082, 16299),
    2021: (16298, 7539),
    2022: (7538, 0)
}