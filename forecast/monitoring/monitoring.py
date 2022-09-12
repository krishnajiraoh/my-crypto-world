from pycoingecko import CoinGeckoAPI
from github import Github
from sklearn.metrics import r2_score,mean_absolute_error,mean_squared_error,mean_absolute_percentage_error
import pandas as pd
import os,io,time

def get_forecasted_data():
    github_access_token = os.environ.get('GH_ACCESS_TOKEN') 
    g = Github(github_access_token)

    repo = g.get_repo("krishnajiraoh/my-crypto-world")    
    path = "forecast/data/Forecasted_Prices.csv"
    contents = repo.get_contents(path)
    data = contents.decoded_content.decode("utf-8") 
    
    return pd.read_csv(io.StringIO(data), sep=",")

def get_actual_data():
    data = cg.get_coin_ohlc_by_id(id='bitcoin', vs_currency="usd", days="30")
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

def get_history_monitoring_data(path="forecast/data/Monitoring.csv"):
    github_access_token = os.environ.get('GH_ACCESS_TOKEN') 
    g = Github(github_access_token)

    repo = g.get_repo("krishnajiraoh/my-crypto-world")    
    contents = repo.get_contents(path)
    data = contents.decoded_content.decode("utf-8") 
    
    return data

def concat_new_and_history_mon_data(data,df2):
    return data + df2.to_csv(index=False, header=False)

def update_monitoring_data(metrics_df, path="forecast/data/Monitoring.csv"):
    github_access_token = os.environ.get('GH_ACCESS_TOKEN') 
    g = Github(github_access_token)

    history_mon_data = get_history_monitoring_data()
    content = concat_new_and_history_mon_data(metrics_df, history_mon_data)
    print(content)

    repo = g.get_repo("krishnajiraoh/my-crypto-world")    
    contents = repo.get_contents(path)
    message = "Updated by Prediction script using PyGithub API"

    #content = pred.to_csv(index=False)
    repo.update_file(path, message, content, contents.sha , branch="main")

    df.to_csv(index=False, header=False)

def monitor():
    pred = get_forecasted_data()
    actual = get_actual_data()
    merge_df = actual.merge(pred, on="Time", how="inner")
    metrics_df = get_metrics(merge_df)
    update_monitoring_data(metrics_df)

if __name__ == '__main__':
    monitor()