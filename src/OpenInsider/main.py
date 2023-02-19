import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass



@dataclass
class Asset:
    filing_date: str
    trade_date: str
    ticker: str
    price: float
    qty_bought: int

if __name__ == "__main__":
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

    for a in assets:
        print(f"{a.ticker} @ {a.price}")