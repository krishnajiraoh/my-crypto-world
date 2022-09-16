from cgitb import small
from fileinput import close
import talib
import Constants

class MyTalib():

    def __init__(self, df):
        self.df = df

    def get_basic_indicators(self, col="Close"):
        return {
            Constants.TEXT_RSI : self.get_last_rsi(),
            Constants.TEXT_RSI_OVERBOUGHT : self.is_rsi_overbought(col),
            Constants.TEXT_RSI_OVERSOLD : self.is_rsi_oversold(col),
            Constants.TEXT_SMA20 : self.get_last_sma(col),
            Constants.TEXT_SMA20_CROSS_ABOVE: self.is_sma_cross_above(col),
            Constants.TEXT_SMA20_CROSS_BELOW: self.is_sma_cross_above(col),
            Constants.TEXT_SMA50 : self.get_last_sma(col, period=50),
            Constants.TEXT_SMA50_CROSS_ABOVE: self.is_sma_cross_above(col,period=50),
            Constants.TEXT_SMA50_CROSS_BELOW: self.is_sma_cross_above(col,period=50, is_above=False)
        }

    def get_last_rsi(self, col="Close", period=14):
        return round(talib.RSI(self.df[col], period).values[-1])

    def get_sma(self, col="Close", period=20):
        return talib.SMA(self.df[col], period).values

    def get_last_sma(self, col="Close", period=20):
        return self.get_sma(col,period)[-1]

    def is_rsi_oversold(self,col="Close", period=14):
        rsi = self.get_last_rsi(col,period)
        return rsi < Constants.RSI_OVERSOLD_THRESHOLD

    def is_rsi_overbought(self, col="Close", period=14):
        rsi = self.get_last_rsi(col,period)
        return rsi > Constants.RSI_OVERBOUGHT_THRESHOLD

    def is_sma_cross_above(self,col="Close",period=20, is_above=True):
        n=10
        sma_n =  self.get_sma(col, period)[-n:]
        close_n = self.df[col].iloc[-n:]

        #print(sma_n)
        #print(close_n)

        if is_above:
            cross = close_n > sma_n
        else:
            cross = close_n < sma_n

        cross.reset_index(drop=True,inplace=True)
        cross = cross[cross == True]
        
        if len(cross) > 0 and cross.index[0] == period-1:
            return True
        else:    
            return False
