from pushbullet import PushBullet
import os

class Notification():

    def __init__(self):
        token = os.environ.get("PB_TOKEN")
        self.pb = PushBullet(token)
        self.forecast_channel = self.pb.channels[0]

    def send_forecast_notification(self, title, body):
        self.forecast_channel.push_note("123","body")