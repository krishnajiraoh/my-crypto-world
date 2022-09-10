import coinmarketcapapi
from github import Github,InputGitAuthor
import pandas as pd
    

def inject():
    cmc_token = '6d84d06d-0978-4881-8be1-43a88c3f5e26'
    github_access_token = "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"    

    cmc = coinmarketcapapi.CoinMarketCapAPI(cmc_token)
    g = Github(github_access_token)

    data_listing = cmc.cryptocurrency_listings_latest()
    df = pd.DataFrame(data_listing.data)    

    repo = g.get_repo("krishnajiraoh/my-crypto-world")    
    path = "forecast/data/history_data.csv"
    contents = repo.get_contents(path)
    content = df.to_csv(index=False)
    message = "updated using PyGithub API"
    
    repo.update_file(path, message, content, contents.sha , branch="main") 
    print("Data Injected successfully")

if __name__ == '__main__':
    inject()