import os
import io
import numpy as np
import pandas as pd
import tensorflow as tf
from github import Github
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
def get_env_data():
    return os.environ.get('GH_ACCESS_TOKEN'), os.environ.get('GITHUB_REPOSITORY'), os.environ.get('HISTORY_DATA_PATH'), os.environ.get('FORECASTED_PRICES_FILE_PATH')  

def create_dataset(dataset, look_back=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-look_back-1):
		a = dataset[i:(i+look_back), 0]
		dataX.append(a)
		dataY.append(dataset[i + look_back, 0])
	return np.array(dataX), np.array(dataY)

def get_history_data(github_access_token,repo_path,file_path):
    g = Github(github_access_token)

    repo = g.get_repo(repo_path)    
    contents = repo.get_contents(file_path)
    data = contents.decoded_content.decode("utf-8") 
    
    return pd.read_csv(io.StringIO(data), sep=",")

def get_forecasted_history_data(github_access_token,repo_path,file_path):
    g = Github(github_access_token)

    repo = g.get_repo(repo_path)       
    contents = repo.get_contents(file_path)
    data = contents.decoded_content.decode("utf-8") 
    
    return pd.read_csv(io.StringIO(data), sep=",") 

def concat_new_and_history_data(pred,forc_history_df):
    df = pd.concat([pred, forc_history_df]).set_index(["Time"])
    #df.set_index(["Time"], inplace=True)
    df = df[~df.index.duplicated(keep='first')]
    df = df.reset_index()
    return df

def update_forecasted_data(pred,github_access_token,repo_path,file_path):
    g = Github(github_access_token)

    df = concat_new_and_history_data(pred, get_forecasted_history_data(github_access_token,repo_path,file_path))
    content = df.to_csv(index=False)
    
    repo = g.get_repo(repo_path)       
    contents = repo.get_contents(file_path)
    message = "Updated by Prediction script using PyGithub API"

    #content = pred.to_csv(index=False)
    repo.update_file(file_path, message, content, contents.sha , branch="main")

def predict():

    github_access_token,repo_path,file_path,forcasted_file_path = get_env_data()
    print(github_access_token,repo_path,file_path,forcasted_file_path)
    # load the dataset
    dataframe = get_history_data(github_access_token,repo_path,file_path)
    dataset = dataframe[['Close']].values
    dataset = dataset.astype('float32')
    dataset[:5]

    #---------------------------------------------------------#
    # normalize the dataset
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(dataset)
    dataset[:5]

    #---------------------------------------------------------#
    # split into train and test sets
    train_size = int(len(dataset) * 0.67)
    test_size = len(dataset) - train_size
    train, test = dataset[0:train_size,:], dataset[train_size:len(dataset),:]

    # reshape into X=t and Y=t+1
    look_back = 1
    trainX, trainY = create_dataset(train, look_back)
    testX, testY = create_dataset(test, look_back)

    # reshape input to be [samples, time steps, features]
    trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
    testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))

    #---------------------------------------------------------#
    # create and fit the LSTM network
    tf.random.set_seed(7)
    model = Sequential()
    model.add(LSTM(4, input_shape=(1, look_back)))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(trainX, trainY, epochs=100, batch_size=1, verbose=2)

    #---------------------------------------------------------#
    # make predictions
    trainPredict = model.predict(trainX)
    testPredict = model.predict(testX)

    ms_in_hour = 3.6e6
    last_date = dataframe.iloc[-1,0]

    X = testX[-1].reshape(1,1,1)

    y = np.array([])
    dates = np.array([])
    predictions = 6
    n = 0

    while(n<predictions):    
        y_pred = model.predict(X)
        y = np.append(y, y_pred)

        next_date = 4 * ms_in_hour + last_date
        dates = np.append(dates, next_date)    

        X=y_pred.reshape(1,1,1)
        last_date = next_date
        n+=1


    y = np.expand_dims(y, axis=0)
    f = scaler.inverse_transform(y)
    f = np.reshape(f,-1)

    #---------------------------------------------------------#
    pred = pd.DataFrame(np.vstack((dates, f))).T
    pred.columns = ["Time", "Forecasted Price"]
    #pred["Time"] = pd.to_datetime(pred.Time, unit='ms')
    update_forecasted_data(pred,github_access_token,repo_path,forcasted_file_path) #pred.to_csv("../data/Forecasted_Prices.csv")

    #---------------------------------------------------------#
    print("Prices Forecasted")

if __name__ == '__main__':
    predict()