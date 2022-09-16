from metaflow import FlowSpec, step, IncludeFile

class CryptoTAFlow(FlowSpec):
    """
    A flow to generate certain indicators on the crypto data

    It performs:
    1. Get the list of coins from the Env
    2. Fan-out over coins using foreach
    3. Use coingecko to fetch data for each coin
    4. Compute indicators for each coin
    5. Merge the data and send out notifications if necessary 
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
    
        self.next(self.compute_indicators)

    @step
    def compute_indicators(self):
        """
        4. Compute indicators for each coin
        """
        from my_talib.MyTalib import MyTalib

        ta = MyTalib(self.df)
        self.basic_indicators = ta.get_basic_indicators()

        self.next(self.join)

    @step
    def join(self, inputs):
        """
        5.1 Merge the data
        """
        import pandas as pd

        rsi = {
                inp.coin : inp.basic_indicators 
                for inp in inputs
            }
        self.df_indicators = pd.DataFrame(rsi).T
        self.next(self.notify)

    @step
    def notify(self):
        """
        5.2 Send out notifications if necessary 
        """
        
        import pandas as pd
        from notification.Notification import Notification
        
        noti = Notification()
        self.body = noti.get_indi_notification_body(self.df_indicators)
        
        if len(self.body) > 0:
            noti.push_note("CryptoTAFlow Notifications", self.body)

        self.next(self.end)

    @step
    def end(self):

        print("Done")

if __name__ == "__main__":
    CryptoTAFlow()