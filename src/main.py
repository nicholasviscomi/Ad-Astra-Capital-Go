from CE_bt import CE_Backtest
from TrendFollow_bt import Trend_Follow_Backtest

if __name__ == '__main__':
    CE_Backtest()
    # Trend_Follow_Backtest()
    

# ATR = // greatest of curr high - curr low, |curr high - prev close|, |curr low - prev close|
# Chandelier Exit Long: n-day Highest High – ATR (n) x Multiplier
# Chandelier Exit Short: n-day Lowest Low + ATR (n) x Multiplier