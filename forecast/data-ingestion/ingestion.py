from pycoingecko import CoinGeckoAPI
from github import Github
import pandas as pd
import os
    

def upload_data(df):
    github_access_token = os.environ.get('GH_ACCESS_TOKEN') 
    print(github_access_token)
    g = Github(github_access_token)

    repo_path = os.environ.get('GITHUB_REPOSITORY') 
    repo = g.get_repo(repo_path)

    path = os.environ.get('HISTORY_DATA_PATH') 
    contents = repo.get_contents(path)
    content = df.to_csv(index=False)
    message = "Updated by Ingestion script using PyGithub API"
    
    repo.update_file(path, message, content, contents.sha , branch="main") 
    print("Data Injected successfully")

def inject():
    cg = CoinGeckoAPI()
    
    coin = os.environ.get('COIN') 
    print(coin)
    days = os.environ.get('LOOK_BACK_DAYS') 
    data = cg.get_coin_ohlc_by_id(id=coin, vs_currency="usd", days=days)
    cols= ["Time_in_ms", "Open", "High", "Low", "Close"]
    df = pd.DataFrame(data, columns=cols)   
    #df["Time"] = pd.to_datetime(df.Time, unit='ms')
    upload_data(df)
    
if __name__ == '__main__':
    inject()