import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
import pickle
from datetime import datetime as dt
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import numpy as np


@dataclass
class Form:
    filing_date: str
    trade_date: str
    ticker: str
    price: float
    qty_bought: int
    qty_owned: int
    delta_own: int # percentage
    buyer_title: str

DAYS_AGO = "days_ago"
OWN_CHNG_LOW = "own_change_low"
N_PAGES = "n_pages"

def get_data(params):
    forms = []
    for page_number in range(1, params[N_PAGES] + 1): # plus one because upper range is not inclusive 
        URL = f"http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=730&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=3&xp=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page={page_number}"
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")

        table = soup.find("table", class_="tinytable").find("tbody")

        for row in table.find_all("tr"):
            form = Form("", "", "", -1.0, -1, -1, -1, "")
            for i, td in enumerate(row.find_all("td")):
                text = td.get_text().strip()
                if i == 1:
                    form.filing_date = text.split(" ")[0]
                if i == 2:
                    form.trade_date = text.split(" ")[0] # dt.strptime(text.split(" ")[0], "%Y-%m-%d")
                if i == 3:
                    form.ticker = text
                if i == 6:
                    form.buyer_title = text
                if i == 8:
                    form.price = float(text[1:].replace(",", "")) # remove dollar sign and cast to float
                if i == 9:
                    form.qty_bought = int(text[1:].replace(",", "")) # remove plus sign at front of number and cast to int
                if i == 10:
                    form.qty_owned = int(text.replace(",", ""))
                
                if form.qty_owned - form.qty_bought == 0:
                    form.delta_own = 100
                else:
                    form.delta_own = int(form.qty_bought / (form.qty_owned - form.qty_bought)) * 100

            forms.append(form)

    return forms

def save_data(data, fname):
    with open(f"src/OpenInsider/Assets/{fname}.pkl", "wb") as file:
        pickle.dump(data, file)

def load_data(fname):
    with open(f"src/OpenInsider/Assets/{fname}.pkl", "rb") as file:
        data = pickle.load(file)
        return data

def tickers_from_data(data):
    tickers = []
    for form in data:
        if form.ticker not in tickers:
            tickers.append(form.ticker)
    return tickers


@dataclass
class Candle:
    date: str
    o: float
    c: float
    h: float
    l: float
    v: int

@dataclass
class Trade:
    form: Form
    candles: list[Candle]

    def calc_profit(self) -> float:
        d = ((self.candles[-1].c - self.candles[0].c) / self.candles[0].c) * 100
        print(f"First close: {self.candles[0].c} --> Last Close: {self.candles[-1].c} = {d : .2f}")
        return d

    def per_day_changes(self):
        deltas = []
        for c in self.candles:
            deltas.append(
                ((c.c - c.o) / c.o) * 100
            )
        return deltas

def get_trades_from_data(forms: list[Form]):
    trades = []

    for i, form in enumerate(forms):
        # print(f"{i / len(forms) * 100}%")
        to_date = dt.today()
        url = f"https://api.nasdaq.com/api/quote/{form.ticker}/historical?assetclass=stocks&fromdate=2020-02-27&limit=9999&todate={date(to_date.year, to_date.month, to_date.day)}"
        print(f"Request sent to: {url}")
        headers = {
            "authority": "api.nasdaq.com",
            "method": "GET",
            "path": "/api/quote/AAPL/historical?assetclass=stocks&fromdate=2023-01-22&limit=9999&todate=2023-02-22",
            "scheme": "https",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.5",
            "origin": "https://www.nasdaq.com",
            "referer": "https://www.nasdaq.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"NASDAQ API Request Status: {response.status_code}")

            if response.status_code != 200: 
                print(f"Failed status code: {form.ticker}")
                continue
            if response.json()["data"] is None or response.json()["data"]["tradesTable"] is None or response.json()["data"]["tradesTable"]["rows"] is None: 
                print(f"Json response was none: {form.ticker}; url: {url}")
                continue
            
            trade = Trade(form, [])
            for row in response.json()["data"]["tradesTable"]["rows"]:

                o = row["open"][1:].replace(",", "")
                cl = row["close"][1:].replace(",", "")
                h = row["high"][1:].replace(",", "")
                l = row["low"][1:].replace(",", "")
                v = row["volume"].replace(",", "")

                c = Candle(
                    row["date"], 
                    float(o)  if o  != 'N/A' else -1,
                    float(cl) if cl != 'N/A' else -1, 
                    float(h)  if h  != 'N/A' else -1, 
                    float(l)  if l  != 'N/A' else -1, 
                    int(v)    if v  != 'N/A' else -1
                )
                trade.candles.append(c)

            # find the index of the filing date within trade.candles
            dates = [candle.date for candle in trade.candles]
            fd_components = form.filing_date.replace("-", "/").split("/")

            #NOTE: make sure the data is starting at the filing date!
            new_date = f"{fd_components[1]}/{fd_components[2]}/{fd_components[0]}"
            i = dates.index(new_date)
            # print(f"{new_date} @ {i}")

            data_spread = 100
            if (i - data_spread) >= 0 and (i - data_spread) < len(trade.candles):
                trade.candles = trade.candles[i - data_spread : i]
            else:
                trade.candles = trade.candles[0 : i]

            trade.candles = trade.candles[::-1]
            trades.append(trade)

        except requests.exceptions.RequestException:
            pass
        except ValueError:
            pass
        except:
            pass

    return trades

def sum_(data):
    s: float = 0.0
    for d in data:
        s += d
    return s

def moving_avg(data: list, length: int):
    new_data = []
    window = []
    for d in data:
        if len(window) <= length:
            window.append(d)
        else:
            window = window[1:]
            window.append(d)

        new_data.append(sum_(window)/len(window))
    return new_data


def show_trade(trade: Trade):
    prices = pd.DataFrame({
        "high"  : [candle.h  for candle in trade.candles],
        "low"   : [candle.l  for candle in trade.candles],
        "open"  : [candle.o  for candle in trade.candles],
        "close" : [candle.c  for candle in trade.candles]
    })
    green  = prices[prices.close >= prices.open] # green candles
    red    = prices[prices.close < prices.open] # red candles
    w1, w2 = 0.4, 0.02 # width of thick part and width of extrema

    _, ax = plt.subplots()
    # graph green candles (x, height, width, bottom, color)
    ax.bar(green.index, green.close - green.open, w1, green.open, color='green') # thick middle part
    ax.bar(green.index, green.high  - green.close, w2, green.close, color='black') # high price
    ax.bar(green.index, green.low  - green.open, w2, green.open, color='black') # low price
    
    ax.bar(red.index, red.close - red.open, w1, red.open, color='red') # thick middle part
    ax.bar(red.index, red.high  - red.open, w2, red.open, color='black') # high price
    ax.bar(red.index, red.low   - red.close, w2, red.close, color='black') # low price

    ma = moving_avg(list(prices.close.array), 7)
    ax.plot(ma)

    dist = 7
    height_multiplier = 1.05
    peaks, _ = find_peaks(ma, distance=dist, height=ma[0] * height_multiplier) # one week between peaks and peak must be a 5% increase from day 0
    for peak in peaks:
        ax.plot(peak, ma[peak], "bo")

    # if the price didn't go up enough to find a peak with a 5% increase, remove
    # the height multiplier and slowly decrease the distance between peaks until
    # a peak is found. This is necesarry for stagnating stock data (seen in trades[1500:1600:20])
    while len(peaks) == 0:
        dist -= 1
        peaks, _ = find_peaks(ma, distance=dist, height=ma[0]) # one week between peaks and peak must be a 5% increase from day 0
        for peak in peaks:
            ax.plot(peak, ma[peak], "bo")

    title = f"{trade.form.ticker} @ {trade.candles[0].date} (FD: {trade.form.filing_date}, TD: {trade.form.trade_date})"
    ax.set_title(title)
    plt.show()

@dataclass
class Profit:
    trade: Trade
    abs_profit: float # percent increase from first day close to close on 20th day


if __name__ == "__main__":
    params = {
        DAYS_AGO : 3,
        OWN_CHNG_LOW : "",
        N_PAGES : 4,
    }

    # forms = get_data(params)
    # save_data(forms, "Forms")

    # forms = load_data("Forms")
    # trades = get_trades_from_data(forms)
    # save_data(trades, "Trades")

    trades : list[Trade] = load_data("Trades")
    
    for t in trades[1500:1600:20]:
        show_trade(t)