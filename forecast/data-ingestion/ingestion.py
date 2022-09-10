import coinmarketcapapi
import pandas as pd
    

def inject():
    cmc = coinmarketcapapi.CoinMarketCapAPI('6d84d06d-0978-4881-8be1-43a88c3f5e26')

    data_listing = cmc.cryptocurrency_listings_latest()

    df = pd.DataFrame(data_listing.data)
    print(df.head())


if __name__ == '__main__':
    inject()