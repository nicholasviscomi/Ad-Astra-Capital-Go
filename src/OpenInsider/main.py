import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
import pickle

# might just search openinsider.com for a ton of data, download the website and then scrape the links. 
# I could do the same with EDGAR I think?
# here's where to check the price change of the ticker: https://www.nasdaq.com/market-activity/stocks/aapl/historical

@dataclass
class Form:
    filing_date: str
    trade_date: str
    ticker: str
    price: float
    qty_bought: int

DAYS_AGO = "days_ago"
OWN_CHNG_LOW = "own_change_low"
N_PAGES = "n_pages"

def get_data(params):
    forms = []
    for page_number in range(1, params[N_PAGES] + 1): # plus one because upper range is not inclusive 
        URL = f"http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=730&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago={params[DAYS_AGO]}&xp=1&vl=&vh=&ocl={params[OWN_CHNG_LOW]}&och=&sic1=-1&sicl=100&sich=9999&isceo=1&iscfo=1&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page={page_number}"
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")

        # soup = BeautifulSoup(open("/Users/nickviscomi/Desktop/VSCode Projects/Python/AssetTradingAnalysis/src/OpenInsider/Assets/1.html", encoding="utf8"), "html.parser")
        
        table = soup.find("table", class_="tinytable").find("tbody")

        for row in table.find_all("tr"):
            form = Form("", "", "", -1, -1)
            for i, td in enumerate(row.find_all("td")):
                text = td.get_text().strip()
                if i == 1:
                    form.filing_date = text
                if i == 2:
                    form.trade_date = text
                if i == 3:
                    form.ticker = text
                if i == 8:
                    form.price = text
                if i == 9:
                    form.qty_bought = text
            forms.append(form)

        print(len(forms))
    return forms

def save_data(data, fname):
    with open(f"src/OpenInsider/Assets/{fname}.pkl", "wb") as file:
        pickle.dump(data, file)

def load_data(fname):
    with open("src/OpenInsider/Assets/Data.pkl", "rb") as file:
        data = pickle.load(file)
        return data

if __name__ == "__main__":
    days_ago = 3 # number of days between trading and filing
    own_change_low = "" # percent
    n_pages = 1
    params = {
        DAYS_AGO : days_ago,
        OWN_CHNG_LOW : own_change_low,
        N_PAGES : n_pages
    }

    # data = get_data(params)
    # save_data(data, "Data")

    data = load_data("Data")