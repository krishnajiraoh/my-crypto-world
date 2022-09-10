from pycoingecko import CoinGeckoAPI
from github import Github,InputGitAuthor
import pandas as pd
    

def inject():
    github_access_token = "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"    

    cg = CoinGeckoAPI()
    g = Github(github_access_token)

    data = cg.get_coin_ohlc_by_id(id='bitcoin', vs_currency="usd", days="30")
    cols= ["Time", "Open", "High", "Low", "Close"]
    df = pd.DataFrame(data, columns=cols)   
    df["Time"] = pd.to_datetime(df.Time, unit='ms')

    repo = g.get_repo("krishnajiraoh/my-crypto-world")    
    path = "forecast/data/history_data.csv"
    contents = repo.get_contents(path)
    content = df.to_csv(index=False)
    message = "updated using PyGithub API"
    
    repo.update_file(path, message, content, contents.sha , branch="main") 
    print("Data Injected successfully")

if __name__ == '__main__':
    inject()