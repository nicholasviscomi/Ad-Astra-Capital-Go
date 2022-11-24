from CE_bt import CE_Backtest
from TrendFollow_bt import Trend_Follow_Backtest

if __name__ == '__main__':
    CE_Backtest(show_graphs=False, save_fig=False, save_analysis=False)
    # Trend_Follow_Backtest(show_graphs=False, save_fig=False, save_analysis=False)
    

# ATR = // greatest of curr high - curr low, |curr high - prev close|, |curr low - prev close|
# Chandelier Exit Long: n-day Highest High – ATR (n) x Multiplier
# Chandelier Exit Short: n-day Lowest Low + ATR (n) x Multiplier