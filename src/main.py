from CE_bt import CE_Backtest
from TrendFollow_bt import Trend_Follow_Backtest
import numpy as np


kwargs = {
    "show_graphs": False,
    "save_fig" : False,
    "save_analysis" : False,
    "suppress" : False
}

if __name__ == '__main__':
    
    # max_ = 0.0
    # max_params = (0.0, 0)
    # for atr_len in range(1, 31, 1):
    #     for ce_mult in np.arange(1, 5, 0.1):
    #         profit = CE_Backtest(ce_mult, atr_len, **kwargs)
    #         if profit > max_:
    #             max_ = profit
    #             max_params = (ce_mult, atr_len)
    #     print(f"{atr_len/30*100:.2f}%\tFinished")
    
    # print(f"Maximal profit ({max_}%) with ATR Len = {max_params[1]}, CE_MULT = {max_params[0]}")

    # CE_Backtest(ce_mult=1.85, atr_len=1, **kwargs)
    
    Trend_Follow_Backtest(lEMA_len=26, sEMA_len=12, **kwargs)
    # print("aslkdfnsdlkfn")