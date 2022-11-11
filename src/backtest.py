import csv
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

def CE_Backtest():
    with open(one_hr_data_path, mode='r') as file:
        csv_file = csv.reader(file)

        # gather contents
        contents = []
        for line in csv_file:
            contents.append(line)
        
        prev_candle = None
        prev_EL, prev_ES = 0.0, 0.0
        inLongPos, inShortPos = False, False
        shortPosPrice, longPosPrice = 0.0, 0.0
        trades = []

        for i in range(len(contents) - 1, 0, -1):
            # loop through contents starting at the end
            line = contents[i]
            open_, high_, low_, close_ = float(line[3]), float(line[4]), float(line[5]), float(line[6])
            curr_candle = Candle(open_, high_, low_, close_)

            if prev_candle == None:
                prev_candle = curr_candle
                continue

            atr = oneday_ATR(prev_candle, curr_candle)

            curr_EL = curr_candle.close_ - (atr * CE_MULTIPLIER)
            curr_ES = curr_candle.close_ + (atr * CE_MULTIPLIER)
            if prev_candle.close_ > prev_EL:
                curr_EL = max(curr_EL, prev_EL)

            if prev_candle.close_ < prev_ES:
                curr_ES = min(curr_ES, prev_ES)

            ##########################################################################
            # TRADING LOGIC HERE
            if not inLongPos and close_ > prev_ES:
                # exit long FIRST then long bitcoin
                if inShortPos: 
                    inShortPos = False
                    trades.append((shortPosPrice/close_ - 1) * 100)

                inLongPos = True
                longPosPrice = close_

            if not inShortPos and close_ < prev_EL:
                # exit long FIRST then short bitcoin
                if inLongPos:
                    inLongPos = False
                    trades.append((close_/longPosPrice - 1) * 100)

                inShortPos = True
                shortPosPrice = close_

            prev_ES, prev_EL = curr_ES, curr_EL
            prev_candle = curr_candle

        total = sum(trades)
        print(f"Total: {total}")

def oneday_ATR(prev: Candle, curr: Candle):
    return max(
        (curr.high_ - curr.low_),
        (abs(curr.high_ - prev.close_)),
        (abs(curr.low_  - prev.close_))
    )

