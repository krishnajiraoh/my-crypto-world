from pycoingecko import CoinGeckoAPI
from github import Github
from sklearn.metrics import r2_score,mean_absolute_error,mean_squared_error,mean_absolute_percentage_error
import pandas as pd
import os,io,time

def get_env_data():
    return os.environ.get('COIN'), os.environ.get('LOOK_BACK_DAYS'), os.environ.get('GH_ACCESS_TOKEN'), os.environ.get('GITHUB_REPOSITORY'), os.environ.get('FORECASTED_PRICES_FILE_PATH'), os.environ.get('MONITORING_FILE_PATH'), os.environ.get('ACTUALVSFORECASTED_FILEPATH')  
 
def get_forecasted_data(github_access_token, repo_path, path):
    g = Github(github_access_token)
    repo = g.get_repo(repo_path)    
    contents = repo.get_contents(path)
    data = contents.decoded_content.decode("utf-8") 
    
    return pd.read_csv(io.StringIO(data), sep=",")

def get_actual_data(coin,days):
    cg = CoinGeckoAPI()
    data = cg.get_coin_ohlc_by_id(id=coin, vs_currency="usd", days=days)
    cols= ["Time", "Open", "High", "Low", "Close"]
    df = pd.DataFrame(data, columns=cols)
    df = df[["Time","Close"]]
    return df

def get_metrics(df):
    y_true = df['Close']
    y_pred = df['Forecasted Price']

    metrics_dic = {
        "CalculationTIme" : round(time.time() * 1000),
        "R2" : r2_score(y_true, y_pred),
        "MAE" : mean_absolute_error(y_true,y_pred),
        "MSE": mean_squared_error(y_true,y_pred),
        "MAPE" : mean_absolute_percentage_error(y_true,y_pred)
    }
    return pd.DataFrame(metrics_dic, index=[0])

def get_history_monitoring_data(github_access_token, repo_path, path):
    g = Github(github_access_token)
    repo = g.get_repo(repo_path)    
    contents = repo.get_contents(path)
    data = contents.decoded_content.decode("utf-8") 
    
    return data

def concat_new_and_history_mon_data(metrics_df, data):
    return data + metrics_df.to_csv(index=False, header=False)

def update_monitoring_data(metrics_df, github_access_token, repo_path, path):
    g = Github(github_access_token)

    history_mon_data = get_history_monitoring_data(github_access_token, repo_path, path)
    content = concat_new_and_history_mon_data(metrics_df, history_mon_data)
    
    repo = g.get_repo(repo_path)    
    contents = repo.get_contents(path)
    message = "Updated by Monitoring script using PyGithub API"

    repo.update_file(path, message, content, contents.sha , branch="main")

def update_compared_data(df, github_access_token, repo_path, path):
    g = Github(github_access_token)
    
    repo = g.get_repo(repo_path)
    contents = repo.get_contents(path)
    message = "Updated by Monitoring script using PyGithub API"

    df["Time_String"] = pd.to_datetime(df["Time"], unit="ms")
    df = df[["Time", "Time_String", "Close","Forecasted Price"]]
    df.columns = ["Time", "TimeString", "Actual","Forecasted"]
    content = df.to_csv(index=False)
    repo.update_file(path, message, content, contents.sha , branch="main")

def monitor():

    coin,days,github_access_token,repo_path,forcasted_file_path,monitoring_file_path,actualvspredicted_file_path = get_env_data() 
    
    pred = get_forecasted_data(github_access_token,repo_path,forcasted_file_path)
    actual = get_actual_data(coin,days)
    
    merge_df = actual.merge(pred, on="Time", how="inner")
    merge_df.sort_values(by="Time", ascending=False, inplace=True)
    
    if merge_df.empty:
        print("No matches found during merge")
    else:
        metrics_df = get_metrics(merge_df)
        update_monitoring_data(metrics_df,github_access_token,repo_path,monitoring_file_path)
        update_compared_data(merge_df,github_access_token,repo_path,actualvspredicted_file_path)

if __name__ == '__main__':
    monitor()