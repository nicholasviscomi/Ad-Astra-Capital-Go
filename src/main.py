from CE_bt import CE_Backtest
from TrendFollow_bt import Trend_Follow_Backtest
import numpy as np

if __name__ == '__main__':
    
    # max_ = 0.0
    # max_mult = 0.0
    # for i in np.arange(1, 10, 0.1):
    #     profit = CE_Backtest(ce_mult=i, atr_len=1, show_graphs=False, save_fig=False, save_analysis=False)
    #     print(f"Profit: {profit} with mult = {i}")
    #     if profit > max_: 
    #         max_ = profit
    #         max_mult = i
    
    # print(f"Found the most profit ({max_}%) for 2018 with CE_MULT = {max_mult}")

    # CE_Backtest(ce_mult=1.85, atr_len=1, show_graphs=True, save_fig=True, save_analysis=True)
    
    Trend_Follow_Backtest(
        lEMA_len=26, sEMA_len=12,
        show_graphs=False, save_fig=True, save_analysis=True
    )