from CE_bt import CE_Backtest
from TrendFollow_bt import Trend_Follow_Backtest
import numpy as np

if __name__ == '__main__':
    
    max_ = 0.0
    max_mult = 0.0
    for i in np.arange(1, 10, 0.1):
        profit = CE_Backtest(ce_mult=i, atr_len=1, show_graphs=False, save_fig=False, save_analysis=False)
        print(f"Profit: {profit} with mult = {i}")
        if profit > max_: 
            max_ = profit
            max_mult = i
    
    print(f"Found the most profit ({max_}%) for 2018 with CE_MULT = {max_mult}")

    
    # Trend_Follow_Backtest(show_graphs=False, save_fig=True, save_analysis=True)
    

# ATR = // greatest of curr high - curr low, |curr high - prev close|, |curr low - prev close|
# Chandelier Exit Long: n-day Highest High – ATR (n) x Multiplier
# Chandelier Exit Short: n-day Lowest Low + ATR (n) x Multiplier