from pushbullet import PushBullet
import os

class Notification():

    def __init__(self):
        token = os.environ.get("PB_TOKEN")
        self.pb = PushBullet(token)
        self.forecast_channel = self.pb.channels[0]

    def get_forecast_notifications(self, forecasts):
        title = os.environ.get("PB_TITLE")
        body = ""
        for f in forecasts.keys():
            body = body + f + "\n"
            body+= forecasts[f].to_csv(index=False, header=False, sep="\t", date_format='%-I %p')
            body+= "\n"
        return title, body
        
    def send_forecast_notification(self, forecasts):
        title, body = self.get_forecast_notifications(forecasts)
        push = self.forecast_channel.push_note(title,body)
        print(f"Pushed returned: {push}")