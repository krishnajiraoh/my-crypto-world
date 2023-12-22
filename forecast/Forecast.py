from metaflow import FlowSpec, step
import numpy as np
import pandas as pd
"""import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler

print(tf.__version__)"""

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
        4. Forecast prices for each coin using prophet library
        """

        def get_predictions(coin='bitcoin', days=30, pred_periods=6):
            from pycoingecko import CoinGeckoAPI
            import pandas as pd
            import numpy as np
            from prophet import Prophet

            cg = CoinGeckoAPI()

            data = cg.get_coin_ohlc_by_id(id=coin, vs_currency="usd", days=days)

            cols= ["ds", "Open", "High", "Low", "y"]
            df = pd.DataFrame(data, columns=cols)  
            df = df[["ds", "y"]] 
            df['ds'] = pd.to_datetime(df['ds'], unit='ms')    

            m = Prophet()
            m.fit(df)

            future = m.make_future_dataframe(periods=pred_periods, freq='4H')
            fcst = m.predict(future)

            #fig = m.plot(fcst)
            fcst = fcst[["ds", "yhat"]].iloc[-pred_periods:,:]
            fcst["yhat"] = np.round(fcst["yhat"],4)

            return fcst

        self.fcst = get_predictions(coin=self.coin, days=30, pred_periods=6)
        
        self.next(self.join)

    @step
    def join(self, inputs):
        """
        5.1 Merge the data
        """
        self.forecasts = {
                inp.coin : inp.fcst 
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

        #noti.send_forecast_notification(self.forecasts)

        async def my_coroutine():
            await noti.push_note("CryptoTAFlow Notifications", self.body)
            return "Coroutine executed"
            # Create a new event loop
            loop = asyncio.new_event_loop()
            # Set the event loop for the current context
            asyncio.set_event_loop(loop)
            try:
                # run the coroutine
                result = loop.run_until_complete(my_coroutine())
                print(result)
            finally:
                # close the event loop
                loop.close()

        self.next(self.end)

    @step
    def end(self):
        print("Done")


if __name__ == "__main__":
    CryptoForecastFlow()

