from backtest import *

if __name__ == '__main__':
    CE_Backtest()
    

# ATR = // greatest of curr high - curr low, |curr high - prev close|, |curr low - prev close|
# Chandelier Exit Long: n-day Highest High – ATR (n) x Multiplier
# Chandelier Exit Short: n-day Lowest Low + ATR (n) x Multiplier