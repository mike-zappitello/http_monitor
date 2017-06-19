
from datetime import datetime as datetime # lol

class Display(object):
    def __init__(self):
        self.time_fmt = "%A, %d. %B %Y %I:%M%p"
        self.log_items = [ ]

    def high_traffic_alert(self, start_time):
        message =  "HIGH TRAFFIC ALERT\n\tTriggered at %s" % \
                start_time.strftime(self.time_fmt)
        print(message)

    def low_traffic_alert(self, expired_time):
        message = "TRAFFIC ALERT OVER\n\tTriggered at %s" % \
                expired_time.strftime(self.time_fmt)
        print(message)

    def update_display(self):
        print("update display")

    def display_stats(self):
        print("display stat")
        # do some processing for display
        for i, item in enumerate(self.log_items):
            a = "a"

