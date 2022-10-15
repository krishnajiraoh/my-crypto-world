from metaflow import FlowSpec, step
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler

print(tf__version__)

class CryptoForecastFlow(FlowSpec):
    """"
    A flow to generate and notify forecasted prices of crypto currencies
    
    It performs:
    It performs:
    1. Get the list of coins from the Env
    2. Fan-out over coins using foreach
    3. Use coingecko to fetch data for each coin
    4. Forecast prices for each coin
    5. Aggregate the forecasted prices and send out notification via PushBullet
    """

    @step
    def start(self):
        """
        1. Get the list of coins from the Env
        2. Fan-out over coins using foreach
        """
        import os

        # Read coins seperated by commas
        coins = os.environ.get("COINS")
        self.coins = list(coins.split(","))
        self.days = os.environ.get("LOOK_BACK_DAYS")
        
        self.next(self.fetch_data, foreach="coins")

    @step
    def fetch_data(self):
        """
        3. Use coingecko to fetch data for each coin
        """
        from pycoingecko import CoinGeckoAPI
        import pandas as pd

        self.coin = self.input
        cg = CoinGeckoAPI()
        data = cg.get_coin_ohlc_by_id(id=self.coin, vs_currency="usd", days=self.days)
        cols= ["Time_in_ms", "Open", "High", "Low", "Close"]
        self.df = pd.DataFrame(data, columns=cols)   
    
        self.next(self.forecast)

    @step
    def forecast(self):
        """
        4. Forecast prices for each coin
        """

        def create_dataset(dataset, look_back=1):
            dataX, dataY = [], []
            for i in range(len(dataset)-look_back-1):
                a = dataset[i:(i+look_back), 0]
                dataX.append(a)
                dataY.append(dataset[i + look_back, 0])
            return np.array(dataX), np.array(dataY)

        # load the dataset
        dataset = self.df[['Close']].values
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
        last_date = self.df.iloc[-1,0]

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
        self.pred = pd.DataFrame(np.vstack((dates, f))).T
        self.pred.columns = ["Time", "Forecasted Price"]
        self.pred["Time"] = pd.to_datetime(self.pred.Time, unit='ms')
        self.pred["Forecasted Price"] = round(self.pred["Forecasted Price"],2)

        self.pred.sort_values(by="Time", ascending=True, inplace=True)
        
        self.next(self.join)

    @step
    def join(self, inputs):
        """
        5.1 Merge the data
        """
        self.forecasts = {
                inp.coin : inp.pred 
                for inp in inputs
            }
        print("joined")
        self.next(self.notify)

    @step
    def notify(self):
        """
        5.2 Send out notifications if necessary 
        """
        
        from notification.Notification import Notification        
        noti = Notification()

        noti.send_forecast_notification(self.forecasts)

        self.next(self.end)

    @step
    def end(self):
        print("Done")

if __name__ == "__main__":
    CryptoForecastFlow()

