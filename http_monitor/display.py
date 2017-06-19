
from datetime import datetime as datetime # lol

class Display(object):

    def __init__(self):
        self.time_fmt = "%A, %d. %B %Y %I:%M%p"
        self.monitor = None

    def set_monitor(self, monitor):
        self.monitor = monitor 
        self.update_display()

    def high_traffic_alert(self):
        alert = self.monitor.get_latest_alert()
        time = alert.start_time.strftime(self.time_fmt)
        print("HIGH TRAFFIC ALERT: Triggered at %s" % time)

    def low_traffic_alert(self):
        alert = self.monitor.get_latest_alert()
        time = alert.end_time.strftime(self.time_fmt)
        print("TRAFFIC ALERT OVER: Expired at %s\n" % time)

    def update_display(self):
        print("update_display")

