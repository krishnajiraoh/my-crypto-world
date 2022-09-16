from pushbullet import PushBullet
import os


class Notification():

    def __init__(self):
        token = os.environ.get("PB_TOKEN")
        print(f"PB Token: {token}")
        self.pb = PushBullet(token)

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

        return body

    def send_indi_notification(self,body):
        self.push_note(os.environ.get("PB_TITLE"), body)

    def push_note(self,title="Title",body="Body"):
        self.pb.push_note(title,body)
