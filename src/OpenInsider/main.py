import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass

# might just search openinsider.com for a ton of data, download the website and then scrape the links. 
# I could do the same with EDGAR I think?
# here's where to check the price change of the ticker: https://www.nasdaq.com/market-activity/stocks/aapl/historical

@dataclass
class Asset:
    filing_date: str
    trade_date: str
    ticker: str
    price: float
    qty_bought: int

if __name__ == "__main__":
    # going to download a couple pages of open insider with 1000 search results each
    # will then scrape those for the trades
    
    URL = "http://openinsider.com/"
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")

    table = soup.find("tbody")
    rows = table.find_all("tr")

    assets = []

    for row in rows:
        tds = row.find_all("td")
        asset = Asset("", "", "", -1, -1)
        for i, td in enumerate(tds):
            text = td.get_text()
            if i == 1:
                asset.filing_date = text
            if i == 2:
                asset.trade_date = text
            if i == 3:
                asset.ticker = text
            if i == 8:
                asset.price = text
            if i == 9:
                asset.qty_bought = text
        assets.append(asset)

    print(assets[0:10])