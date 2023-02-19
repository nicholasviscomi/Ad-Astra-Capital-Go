from util_bt import *
import matplotlib.pyplot as plt
import csv
import pandas as pd

SMOOTHING = 2

def Trend_Follow_Backtest(
    lEMA_len: int, sEMA_len: int,
    show_graphs: bool, save_fig: bool, save_analysis: bool, suppress: bool
    ):
    """
    Test a simple EMA trend following strategy.
    When a shorter moving average crosses up a longer one, an uptrend should be starting. 
    When a shorter moving average crosses down a longer one, a downtrend should be starting.
    lEMA = long EMA, sEMA = short EMA
    """
    tot_profit = None
    with open(one_hr_data_path, mode='r') as file:
        csv_file = csv.reader(file)

        contents = []
        for line in csv_file:
            contents.append(line)
        
        # used to loop through just specific years within the massive data file
        for year in year_ranges:
            trades = []
            tot_profit = 0
            inLongPos, inShortPos = False, False
            shortPosPrice, longPosPrice = 0.0, 0.0
            t_bought = ""

            moving_pts = []
            prev_lEMA, prev_sEMA = -1, -1
            prev_deltaEMA = -1 # used to track a crossing of ema

            start_i = -1
            # lema_y, sema_y, candles = [], [], []
            for i in range(year_ranges[year][0], year_ranges[year][1], -1):
                # loop through contents starting at the end
                line = contents[i]
                date, open_, high_, low_, close_ = line[1], float(line[3]), float(line[4]), float(line[5]), float(line[6])
                curr_candle = Candle(date, open_, high_, low_, close_)

                if len(moving_pts) < lEMA_len: 
                    # need enough points for long EMA (guarantees enough for short EMA)
                    moving_pts.append(close_)
                    continue

                if (prev_lEMA == -1 or prev_sEMA == -1) and len(moving_pts) == lEMA_len:
                    prev_lEMA = sum(moving_pts)/lEMA_len

                    short_EMA_pts = moving_pts[14:]
                    prev_sEMA = sum(short_EMA_pts)/sEMA_len

                assert prev_sEMA != -1 or prev_lEMA != -1

                curr_lEMA = (close_ * (SMOOTHING / (1 + lEMA_len))) + prev_lEMA * (1 - (SMOOTHING / (1 + lEMA_len)))
                curr_sEMA = (close_ * (SMOOTHING / (1 + sEMA_len))) + prev_sEMA * (1 - (SMOOTHING / (1 + sEMA_len)))
                
                 # if this > 1 and it used to be < 1, sEMA just crossed up lEMA    --> go long, exit short
                 # if this < 1 and it used to be > 1, sEMA just crossed down lEMA  --> go short, exit long
                curr_deltaEMA = curr_sEMA / curr_lEMA

                ##########################################################################################################
                # STOP LOSS
                ##########################################################################################################

                if inLongPos:
                    mock_trade = Trade(
                        bought=longPosPrice,
                        t_bought=t_bought,
                        sold=close_,
                        t_sold=date,
                        start_i=start_i,
                        end_i=i,
                        type_=IS_LONG
                    )
                    if mock_trade.percent_profit() < -3:
                        # already lost enough, exit now
                        trades.append(mock_trade)
                        inLongPos = False
                        prev_lEMA, prev_sEMA = curr_lEMA, curr_sEMA
                        prev_deltaEMA = curr_deltaEMA
                        continue

                if inShortPos:
                    mock_trade = Trade(
                        bought=shortPosPrice,
                        t_bought=t_bought,
                        sold=close_,
                        t_sold=date,
                        start_i=start_i,
                        end_i=i,
                        type_=IS_SHORT
                    )
                    if mock_trade.percent_profit() < -3:
                        # already lost enough, exit now
                        trades.append(mock_trade)
                        inShortPos = False
                        prev_lEMA, prev_sEMA = curr_lEMA, curr_sEMA
                        prev_deltaEMA = curr_deltaEMA
                        continue

                ##########################################################################################################
                # TRADING LOGIC
                ##########################################################################################################
                if not inLongPos and (prev_deltaEMA < 1 and curr_deltaEMA > 1):
                    # close short enter long
                    if inShortPos:
                        trades.append(Trade(
                            bought=shortPosPrice,
                            t_bought=t_bought,
                            sold=close_,
                            t_sold=date,
                            start_i=start_i,
                            end_i=i,
                            type_=IS_SHORT
                        ))
                        inShortPos = False

                    inLongPos = True
                    longPosPrice = close_
                    t_bought = date
                    start_i = i

                if not inShortPos and (prev_deltaEMA > 1 and curr_deltaEMA < 1):
                    # close long position, enter short
                    if inLongPos:
                        trades.append(Trade(
                            bought=longPosPrice,
                            t_bought=t_bought,
                            sold=close_,
                            t_sold=date,
                            start_i=start_i,
                            end_i=i,
                            type_=IS_LONG
                        ))
                        inLongPos = False
                    
                    inShortPos = True
                    shortPosPrice = close_
                    t_bought = date
                    start_i = i
                    
                # lema_y.append(curr_lEMA)
                # sema_y.append(curr_sEMA)
                # candles.append(curr_candle)

                prev_lEMA, prev_sEMA = curr_lEMA, curr_sEMA
                prev_deltaEMA = curr_deltaEMA
                ##########################################################################################################
            
            strat = None
            if save_analysis: strat = "TrendFollow"
            winners, losers, profit = run_basic_analysis(trades, year, contents, show_graphs, strat, suppress) # returns sorted lists
            
            tot_profit += profit

            if save_fig: strat = "TrendFollow"
            else: strat = None # Need this line to ensure that strat goes back to None if !save_fig
            analyze_trade_types(winners, losers, year, strat)
        
        return tot_profit
