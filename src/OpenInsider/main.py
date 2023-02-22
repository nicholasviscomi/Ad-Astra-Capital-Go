import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass

# might just search openinsider.com for a ton of data, download the website and then scrape the links. 
# I could do the same with EDGAR I think?
# here's where to check the price change of the ticker: https://www.nasdaq.com/market-activity/stocks/aapl/historical

URL_BASE = "https://www.sec.gov" # base of the url to be added before each link that is scraped
form_links = []

if __name__ == "__main__":
    soup = BeautifulSoup(open("/Users/nickviscomi/Desktop/VSCode Projects/Python/AssetTradingAnalysis/src/OpenInsider/Assets/1.html", encoding="utf8"), "html.parser")
    
    table = soup.find("body").find_all("table")[6]

    for i, row in enumerate(table.find_all("tr")):
        if i == 0 or i % 2 != 0: continue # don't want the first one and only want evens
        link = row.find_all("td")[1].find("a")["href"]
        form_links.append(URL_BASE + link)

    form = requests.get(form_links[0])
    soup = BeautifulSoup(form.content, "html.parser")
    print(soup.prettify())

    
    

    


