
import time
import unittest

from datetime import datetime as datetime # lol
from datetime import timedelta as timedelta 

from http_monitor import monitor 
from http_monitor import log_utils
from http_monitor import display

class MockLogItemGenerator(object):
    def __init__(self):
        self.schedule = [ ] 
        self.items_sent = 0

    def set_schedule(self, schedule): self.schedule = schedule

    def generate_item(self, time):
        self.items_sent += 1
        return log_utils.LogItem(
                client='1.2.3.4', timestamp=time, method='GET',
                resource='/sql/index.php', protocol='HTTP/1.1', status=200,
                size=1234)

    def generate_items(self, amount):
        print('generate items')
        count = 0
        while count < amount:
            yield self.generate_item(datetime.now())
            count += 1

    def generate_nones(self, amount):
        print('generate nones')
        count = 0
        while count < amount:
            yield None
            count += 1

    def next_item(self):
        for time in self.schedule:
            while datetime.now() < time:
                print('none')
                yield None
            print('item')
            yield self.generate_item(time)

class MockDisplay(object):

    def __init__(self):
        self.schedule = [ ]
        self.display_updates = 0
        self.monitor = None

    def set_schedule(self, schedule):
        self.schedule = schedule

    def set_monitor(self, monitor):
        self.monitor = monitor

    def high_traffic_alert(self): print('high traffic')
    def low_traffic_alert(self): print('low traffic')
    def update_display(self):
        self.display_updates += 1
        for alert in self.monitor.alerts:
            print(alert.hits)

class MonitorTest(unittest.TestCase):
    
    def setUp(self):
        self.log_item_generator = MockLogItemGenerator()
        self.display = MockDisplay()

    def create_schedule(self, timedeltas):
        return [ datetime.now() + timedelta(seconds=seconds)
                 for seconds in timedeltas ]


    def test_monitor(self):
        timedeltas = [ 1, 1, 1, 1, 1, 121 ]
        schedule = self.create_schedule(timedeltas)

        self.log_item_generator.set_schedule(schedule)
        self.display.set_schedule(schedule)

        self.monitor = monitor.Monitor(
                self.log_item_generator.next_item(), self.display, threshold=5,
                frequency=10, verbose=True)

        self.monitor.start()

if __name__ == '__main__': unittest.main()
