from pycoingecko import CoinGeckoAPI
from github import Github
import pandas as pd
import os

def get_env_data():
    return os.environ.get('COIN'), os.environ.get('LOOK_BACK_DAYS'), os.environ.get('GH_ACCESS_TOKEN'), os.environ.get('GITHUB_REPOSITORY'), os.environ.get('HISTORY_DATA_PATH')  

def get_coin_data(coin='bitcoin', days=30):
    cg = CoinGeckoAPI()
    data = cg.get_coin_ohlc_by_id(id=coin, vs_currency="usd", days=days)
    cols= ["Time_in_ms", "Open", "High", "Low", "Close"]
    df = pd.DataFrame(data, columns=cols)   
    #df["Time"] = pd.to_datetime(df.Time, unit='ms')
    return df

def upload_data(df, github_access_token, repo_path, path):
    g = Github(github_access_token)
    repo = g.get_repo(repo_path)

    contents = repo.get_contents(path)
    content = df.to_csv(index=False)
    message = "Updated by Ingestion script using PyGithub API"
    
    repo.update_file(path, message, content, contents.sha , branch="main") 

def inject():
    
    coin,days,github_access_token,repo_path,history_file_path = get_env_data()
    df = get_coin_data(coin,days)
    upload_data(df, github_access_token, repo_path, history_file_path )
    print("Data Injected successfully")

if __name__ == '__main__':
    inject()