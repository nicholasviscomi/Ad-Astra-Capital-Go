import csv
from util_bt import *

def CE_Backtest():
    """
    Test the chandeleir exit strategy with ATR length = 1, multiplier = 1.85
    """
    with open(one_hr_data_path, mode='r') as file:
        csv_file = csv.reader(file)

        # gather contents
        contents = []
        for line in csv_file:
            contents.append(line)
        
        # used to loop through just specific years within the massive data file
        trades = []

        for year in year_ranges:
            prev_candle = None
            prev_EL, prev_ES = 0.0, 0.0
            inLongPos, inShortPos = False, False
            shortPosPrice, longPosPrice = 0.0, 0.0
            start_i = -1
            for i in range(year_ranges[year][0], year_ranges[year][1], -1):
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
                        # trades.append((shortPosPrice/close_ - 1) * 100)
                        trades.append(Trade(
                            bought=shortPosPrice,
                            sold=close_,
                            start_i=start_i,
                            end_i=i,
                            type_=IS_SHORT
                        ))

                    inLongPos = True
                    longPosPrice = close_
                    start_i = i

                if not inShortPos and close_ < prev_EL:
                    # exit long FIRST then short bitcoin
                    if inLongPos:
                        inLongPos = False
                        # trades.append((close_/longPosPrice - 1) * 100)
                        trades.append(Trade(
                            bought=longPosPrice,
                            sold=close_,
                            start_i=start_i,
                            end_i=i,
                            type_=IS_LONG
                        ))

                    inShortPos = True
                    shortPosPrice = close_
                    start_i = i

                prev_ES, prev_EL = curr_ES, curr_EL
                prev_candle = curr_candle

            print_analysis(trades, year, contents, graphs=False)

            # input()