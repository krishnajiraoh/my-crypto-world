import talib
from my_talib import Constant

class MyTalib():

    def __init__(self, df):
        self.df = df

    def get_basic_indicators(self, col="Close"):
        return {
            Constant.TEXT_RSI : self.get_rsi(),
            Constant.TEXT_RSI_OVERBOUGHT : self.is_rsi_overbought(col),
            Constant.TEXT_RSI_OVERSOLD : self.is_rsi_oversold(col)
        }

    def get_rsi(self, col="Close", period=14):
        return round(talib.RSI(self.df[col], period).values[-1])

    def is_rsi_oversold(self,col="Close", period=14):
        rsi = self.get_rsi(col,period)
        return rsi < Constant.RSI_OVERSOLD_THRESHOLD

    def is_rsi_overbought(self, col="Close", period=14):
        rsi = self.get_rsi(col,period)
        return rsi > Constant.RSI_OVERBOUGHT_THRESHOLD
