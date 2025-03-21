from pushbullet import PushBullet
from telegram import Bot
import os

class Notification():

    def __init__(self):
        token = os.environ.get("PB_TOKEN")
        self.pb = PushBullet(token)
        self.forecast_channel = self.pb.channels[0]

        bot_token = os.environ.get("TG_BOT_TOKEN")
        self.tg_channel_id = os.environ.get("TG_CHANNEL_ID")
        self.tg_bot = Bot(token=bot_token)

    def get_forecast_notifications(self, forecasts):
        title = os.environ.get("PB_TITLE")
        body = ""
        for f in forecasts.keys():
            body = body + f + "\n"
            body+= forecasts[f].to_csv(index=False, header=False, sep="\t", date_format='%-I %p')
            body+= "\n"
        return title, body
        
    async def send_forecast_notification(self, forecasts):
        title, body = self.get_forecast_notifications(forecasts)
        push = self.forecast_channel.push_note(title,body)
        print(f"Pushed returned: {push}")

        await self.bot.send_message(chat_id=self.tg_channel_id, text=body)
        print("Telegram message sent")