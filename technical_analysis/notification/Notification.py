from pushbullet import PushBullet
from telegram import Bot
import os
import Constants


class Notification():

    def __init__(self):
        token = os.environ.get("PB_TOKEN")
        self.pb = PushBullet(token)

        bot_token = os.environ.get("TG_BOT_TOKEN")
        self.tg_channel_id = os.environ.get("TG_CHANNEL_ID")
        self.tg_bot = Bot(token=bot_token)

    def get_indi_notification_body(self, df):
        body = ""
        s = ","

        #Get coins that are oversold
        idx = list(df[df["IS_RSI_OVERSOLD"] == True].index)
        if len(idx) > 0:
            oversold_coins = s.join(list(idx))
            body += f"RSI oversold: {oversold_coins}"
            
        #Get coins that are overbought
        idx = list(df[df["IS_RSI_OVERBOUGHT"] == True].index)
        if len(idx) > 0:
            overbought_coins = s.join(list(idx))
            body += f"\nRSI Overbought: {overbought_coins}"

        
        #Get coins that are cross above sma20
        idx = list(df[df[Constants.TEXT_SMA20_CROSS_ABOVE] == True].index)
        if len(idx) > 0:
            sma20_cross_above_coins = s.join(list(idx))
            body += f"\nSMA20 CROSS ABOVE : {sma20_cross_above_coins}"

        #Get coins that are cross above sma50
        idx = list(df[df[Constants.TEXT_SMA50_CROSS_ABOVE] == True].index)
        if len(idx) > 0:
            sma50_cross_above_coins = s.join(list(idx))
            body += f"\nSMA50 CROSS ABOVE: {sma50_cross_above_coins}"

        #Get coins that are cross below sma20
        idx = list(df[df[Constants.TEXT_SMA20_CROSS_BELOW] == True].index)
        if len(idx) > 0:
            sma20_cross_below_coins = s.join(list(idx))
            body += f"\nSMA50 CROSS BELOW: {sma20_cross_below_coins}"

          #Get coins that are cross below sma50
        idx = list(df[df[Constants.TEXT_SMA50_CROSS_BELOW] == True].index)
        if len(idx) > 0:
            sma50_cross_below_coins = s.join(list(idx))
            body += f"\nSMA50 CROSS BELOW: {sma50_cross_below_coins}"

        return body

    
    def send_indi_notification(self,body):
        print(body)
        self.push_note(os.environ.get("PB_TITLE"), body)

    async def push_note(self,title="Title",body="Body"):
        self.pb.push_note(title,body)
        await self.bot.send_message(chat_id=self.tg_channel_id, text=body)
