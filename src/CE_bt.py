import csv
from util_bt import *

def true_range(prev: Candle, curr: Candle):
    return max(
        (curr.high_ - curr.low_),
        (abs(curr.high_ - prev.close_)),
        (abs(curr.low_  - prev.close_))
    )

def calc_atr(atr_len: int, candles: list):
    true_ranges = []

    prev = None
    for candle in candles:
        if prev == None: 
            prev = candle
            continue
        true_ranges.append(true_range(prev, candle))

    assert len(true_ranges) == atr_len
    return sum(true_ranges)/len(true_ranges)

def calc_el_es(atr, ce_mult, prev_candle, curr_candle, prev_EL, prev_ES):
    curr_EL = curr_candle.close_ - (atr * ce_mult)
    curr_ES = curr_candle.close_ + (atr * ce_mult)
    if prev_candle.close_ > prev_EL:
        curr_EL = max(curr_EL, prev_EL)

    if prev_candle.close_ < prev_ES:
        curr_ES = min(curr_ES, prev_ES)
    return curr_EL, curr_ES 


def CE_Backtest(ce_mult: float, atr_len: int, show_graphs: bool, save_fig: bool, save_analysis: bool, suppress: bool=False):
    """
    Test the chandeleir exit strategy with variable ATR length and multiplier values\n
    Suppress dictates whether output will be printed or not (should supress if trying to optimize a parameter)
    """
    tot_profit = None
    with open(one_hr_data_path, mode='r') as file:
        csv_file = csv.reader(file)

        # gather contents
        contents = []
        for line in csv_file:
            contents.append(line)
        
        tot_profit = 0
        for year in year_ranges:
            trades = []

            prev_candle, curr_candle = None, None
            moving_candles = Queue() # keep track of the previous atr_len + 1 candles so the indicator can be calculated
            prev_EL, prev_ES = 0.0, 0.0
        
            inLongPos, inShortPos = False, False
            shortPosPrice, longPosPrice = 0.0, 0.0
            start_i = -1
            for i in range(year_ranges[year][0], year_ranges[year][1], -1):
                # loop through contents starting at the end
                line = contents[i]
                date, open_, high_, low_, close_ = line[1], float(line[3]), float(line[4]), float(line[5]), float(line[6])
                curr_candle = Candle(date, open_, high_, low_, close_)
                
                # fill up moving_candles with the previous (atr_len + 1) candles
                if moving_candles.length() < (atr_len + 1):
                    assert curr_candle != None
                    moving_candles.enqueue(curr_candle)
                    if moving_candles.length() != (atr_len + 1): 
                        # if the repository of points still needs to fill up, you don't want to run any of
                        # the logic below this block

                        # if it's filled up after enqueuing that one, then it's safe to run the logic below
                        continue
                
                atr = calc_atr(atr_len, list(moving_candles._elements))

                prev_candle = list(moving_candles._elements)[0] # change the queue elements to a list and grab first
                curr_EL, curr_ES = calc_el_es(atr, ce_mult, prev_candle, curr_candle, prev_EL, prev_ES)

                ##########################################################################################################
                # STOP LOSS
                ##########################################################################################################
                if inLongPos:
                    mock_trade = Trade(
                        bought=longPosPrice,
                        sold=close_,
                        start_i=start_i,
                        end_i=i,
                        type_=IS_LONG
                    )
                    if mock_trade.percent_profit() < -3:
                        # already lost enough, exit now
                        trades.append(mock_trade)
                        inLongPos = False
                        prev_ES, prev_EL = curr_ES, curr_EL
                        prev_candle = curr_candle
                        continue

                if inShortPos:
                    mock_trade = Trade(
                        bought=shortPosPrice,
                        sold=close_,
                        start_i=start_i,
                        end_i=i,
                        type_=IS_SHORT
                    )
                    if mock_trade.percent_profit() < -3:
                        # already lost enough, exit now
                        trades.append(mock_trade)
                        inShortPos = False
                        prev_ES, prev_EL = curr_ES, curr_EL
                        prev_candle = curr_candle
                        continue

                ##########################################################################################################
                # TRADING LOGIC
                ##########################################################################################################
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
                moving_candles.dequeue()

            strat = None
            if save_analysis: strat = "CE"
            winners, losers, profit = run_basic_analysis(trades, year, contents, show_graphs, strat, suppress)

            tot_profit += profit

            if save_fig: strat = "CE"
            else: strat = None # Need this line to ensure that strat goes back to None if !save_fig
            analyze_trade_types(winners, losers, year, strat)            
        
        return tot_profit if tot_profit != None else -1